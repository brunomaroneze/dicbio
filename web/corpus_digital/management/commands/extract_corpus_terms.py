import csv
import re
from pathlib import Path
from lxml import etree
import codecs

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
# from corpus_digital.models import Obra # Não precisa mais aqui, Obra será importado por outro comando
# from django.utils.text import slugify # Não precisa mais aqui se Obra foi movido

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
            return # Sai do comando se não for para regenerar

        self.stdout.write(self.style.HTTP_INFO('Iniciando extração de termos de XMLs para CSV...'))

        all_rows = []
        
        for file_path in xml_files:
            rows_for_current_file = [] 
            try:
                self.stdout.write(f'  Processando: {file_path.name}')
                
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

                # Remover PIs e comentários da árvore
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

                # Extrair título limpo
                title_el = tree.find('.//tei:teiHeader//tei:sourceDesc//tei:bibl/tei:title', namespaces=ns)
                raw_title = title_el.text if title_el is not None else '(Sem título)'
                title = re.sub(r'\s+', ' ', raw_title).strip()

                slug_obra = file_path.stem.lower()

                terms = tree.xpath('//tei:term', namespaces=ns)
                if not terms:
                    self.stdout.write(self.style.WARNING(f'    Nenhum <term> encontrado em {file_path.name}.'))
                    continue

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
                    
                    # --- RECUPERANDO A SENTENÇA COM DESTAQUE NO TOKEN ---
                    # Para garantir que pegamos o texto *literal* do parent, incluindo a posição do termo,
                    # e que substituímos apenas o token.
                    sentence_text_raw = ''.join(parent.itertext(with_tail=True)).strip()

                    highlighted_token = f"[[b]]{token}[[/b]]"
                    sentence_with_highlight = sentence_text_raw.replace(token, highlighted_token, 1)

                    anchor_url = f"/corpus/{slug_obra}#pagina_{page}"
                    # O texto do link da obra na citação (ex: Anatomia do Corpo Humano, p. 55)
                    # Lembre-se que 'title' é o título da obra, 'page' é o número da página
                    citation_text = f"{title}, p. {page}"

                    final_sentence_for_csv = sentence_with_highlight

                
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

                    # Página
                    nearest_pb_el = term.xpath('./preceding::tei:pb[1]', namespaces=ns)
                    page = nearest_pb_el[0].get('n', '?') if nearest_pb_el else '?'
                    
                    full_sentence = f'{sentence_text} ({author_surname}, {date}, {title}, p. {page})'

                    rows_for_current_file.append([
                        token,
                        headword,
                        orth,
                        gram,
                        sense_number,
                        final_sentence_for_csv,
                        author_surname,
                        date,
                        title,
                        page,
                        slug_obra
                    ])

                all_rows.extend(rows_for_current_file)

            except etree.ParseError as e:
                self.stderr.write(self.style.ERROR(f'Erro ao parsear XML {file_path.name}: {e}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Erro inesperado ao processar {file_path.name}: {e}'))
                import traceback; traceback.print_exc()

        if not all_rows:
            self.stdout.write(self.style.WARNING('Nenhum termo extraído para gerar o CSV. O arquivo de saída pode estar vazio.'))
        else: # <<< ESTE É O ELSE CORRIGIDO! Alinhado com o 'if not all_rows:'
            output_csv_path.parent.mkdir(parents=True, exist_ok=True) 

            try:
                with open(output_csv_path, mode='w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "token", "Headword", "orth", "gram", "SenseNumber",
                        "sentence", "author_surname", "date", "title", "page", "slug_obra"
                    ])
                    writer.writerows(all_rows)
                self.stdout.write(self.style.SUCCESS(f'✔️ CSV gerado com sucesso: {output_csv_path}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Erro ao escrever termos_extraidos.csv: {e}'))
        # REMOVIDO: else: que estava aqui antes. A indentação estava errada.

        self.stdout.write(self.style.SUCCESS('Comando extract_corpus_terms concluído.'))