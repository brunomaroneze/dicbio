import csv
import re
from pathlib import Path
from lxml import etree
import codecs

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
# Não precisamos importar Obra ou slugify aqui, pois este comando apenas gera CSV.

class Command(BaseCommand):
    help = 'Extrai termos e metadados de arquivos XML TEI e gera termos_extraidos.csv.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-regen',
            action='store_true',
            help='Força a regeneração do termos_extraidos.csv, mesmo que já exista.',
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='data', # Pasta padrão para o CSV de saída
            help='Diretório de saída para o CSV, relativo à raiz do projeto Django.',
        )

    def handle(self, *args, **options):
        force_regen = options['force_regen']
        output_dir_name = options['output_dir']

        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        
        base_dir_xml = settings.CORPUS_XML_ROOT 
        output_csv_path = settings.BASE_DIR / output_dir_name / "termos_extraidos.csv"

        if not base_dir_xml.exists():
            raise CommandError(f"Diretório XML do corpus não encontrado: {base_dir_xml}. Verifique settings.CORPUS_XML_ROOT.")

        xml_files = list(base_dir_xml.glob('*.xml'))
        
        if not xml_files:
            self.stdout.write(self.style.WARNING('Nenhum arquivo XML encontrado para extração de termos.'))
            return

        if output_csv_path.exists() and not force_regen:
            self.stdout.write(self.style.NOTICE(f'Arquivo CSV {output_csv_path.name} já existe. Use --force-regen para forçar regeneração.'))
            return
        else:
            all_rows = []
            for file_path in xml_files:
                rows_for_current_file = [] 
                try:
                    self.stdout.write(f'  Processando: {file_path.name}')
                    
                    # --- Lógica de parsing XML (robusta contra problemas de codificação/PIs) ---
                    try:
                        tree = etree.parse(str(file_path)) 
                    except etree.ParseError as e:
                        xml_string_content_raw = None
                        try:
                            with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                xml_string_content_raw = f.read()
                        except Exception as e_read_initial:
                            try:
                                with codecs.open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                                    xml_string_content_raw = f.read()
                            except Exception as e_read_latin:
                                raise CommandError(f'Falha ao ler XML {file_path.name} com qualquer codificação: {e_read_latin}')
                        
                        if not xml_string_content_raw:
                            raise CommandError(f"Arquivo XML {file_path.name} vazio ou ilegível.")

                        try:
                            tree = etree.fromstring(xml_string_content_raw.encode('utf-8'))
                        except Exception as e_fromstring:
                            raise CommandError(f'Falha ao parsear XML {file_path.name} após decodificação: {e_fromstring}')
                    except Exception as e:
                        raise CommandError(f'Erro inesperado ao abrir ou parsear XML {file_path.name}: {e}')

                    # Remover PIs e comentários da árvore (para um XML mais limpo)
                    root = tree.getroot()
                    for node in list(root.xpath('./node()')):
                        if isinstance(node, etree._ProcessingInstruction) and not node.tag.startswith('xml'):
                            root.remove(node)
                        if isinstance(node, etree._Comment):
                            root.remove(node)
                    for el in root.iter():
                         for child in list(el.xpath('./node()')):
                            if isinstance(child, etree._ProcessingInstruction) and not child.tag.startswith('xml'):
                                el.remove(child)
                            if isinstance(child, etree._Comment):
                                el.remove(child)
                    # --- Fim da lógica de parsing XML ---


                    # Extrair título e slug da obra (metadados da obra atual)
                    title_el = tree.find('.//tei:teiHeader//tei:sourceDesc//tei:bibl/tei:title', namespaces=ns)
                    raw_title = title_el.text if title_el is not None else '(Sem título)'
                    title = re.sub(r'\s+', ' ', raw_title).strip()
                    slug_obra = file_path.stem.lower()

                    terms = tree.xpath('//tei:term', namespaces=ns)
                    if not terms:
                        self.stdout.write(self.style.WARNING(f'    Nenhum <term> encontrado em {file_path.name}.'))
                        continue # Pula para o próximo arquivo se não houver termos

                    for term in terms:
                        token = (term.text or '').strip()
                        headword = term.get('lemma', token)
                        orth = term.get('norm', headword)
                        gram = term.get('msd', '')
                        sense_number = term.get('senseNumber', '1')

                        parent = term.getparent()
                        if parent is None:
                            self.stderr.write(self.style.WARNING(f"    Termo '{token}' sem pai em {file_path.name}. Pulando sentença."))
                            continue
                        
                        # --- INÍCIO DA LÓGICA DE GERAÇÃO DA SENTENÇA PARA O CSV ---
                        # Página da ocorrência (primeiro, para ser usada na sentença e coluna)
                        nearest_pb_el = term.xpath('./preceding::tei:pb[1]', namespaces=ns)
                        page = nearest_pb_el[0].get('n', '?') if nearest_pb_el else '?'

                        # Sentença com destaque do token usando marcação intermediária [[b]]
                        sentence_text_raw = ''.join(parent.itertext(with_tail=True)).strip()
                        highlighted_token = f"[[b]]{token}[[/b]]"
                        # Substitui apenas a primeira ocorrência do token na sentença para destaque
                        sentence_with_highlight = sentence_text_raw.replace(token, highlighted_token, 1)
                        # --- FIM DA LÓGICA DE GERAÇÃO DA SENTENÇA PARA O CSV ---
                        
                        # Autor
                        author_el = term.xpath('.//ancestor::tei:TEI//tei:author', namespaces=ns)
                        if author_el and author_el[0].text:
                            author_raw = author_el[0].text.strip()
                            if ',' in author_raw:
                                author_surname = author_raw.split(',')[0].upper()
                            else:
                                author_surname = author_raw.split()[-1].upper()
                        else:
                            author_surname = 'AUTOR_DESCONHECIDO'

                        # Data
                        date_el = term.xpath('.//ancestor::tei:TEI//tei:date', namespaces=ns)
                        date = date_el[0].text.strip() if date_el and date_el[0].text else 's.d.'

                        # Adiciona todos os dados relevantes para o CSV
                        rows_for_current_file.append([
                            token,
                            headword,
                            orth,
                            gram,
                            sense_number,
                            sentence_with_highlight, # Coluna 'sentence' com a marcação [[b]]
                            author_surname,
                            date,
                            title,       # Título da Obra
                            slug_obra,   # Slug da Obra
                            page         # Número da Página (para a coluna 'page_num')
                        ])

                    all_rows.extend(rows_for_current_file)

                except etree.ParseError as e:
                    self.stderr.write(self.style.ERROR(f'Erro ao parsear XML {file_path.name}: {e}'))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Erro inesperado ao processar {file_path.name}: {e}'))
                    import traceback; traceback.print_exc()

            if not all_rows:
                self.stdout.write(self.style.WARNING('Nenhum termo extraído para gerar o CSV. O arquivo de saída pode estar vazio.'))
            else:
                output_csv_path.parent.mkdir(parents=True, exist_ok=True) 

                try:
                    with open(output_csv_path, mode='w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            "token", "Headword", "orth", "gram", "SenseNumber",
                            "sentence", "author_surname", "date", "title", "slug_obra", "page_num" # Header do CSV
                        ])
                        writer.writerows(all_rows)
                    self.stdout.write(self.style.SUCCESS(f'✔️ CSV gerado com sucesso: {output_csv_path}'))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Erro ao escrever termos_extraidos.csv: {e}'))
        #else:
         #   self.stdout.write(self.style.NOTICE(f'Geração de termos_extraidos.csv pulada (--skip-regen).'))

        self.stdout.write(self.style.SUCCESS('Comando extract_corpus_terms concluído.'))