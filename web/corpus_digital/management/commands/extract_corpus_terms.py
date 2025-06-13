import csv
import re
from pathlib import Path
from lxml import etree # Seu script original usa lxml, então manteremos.

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings # Para acessar CORPUS_XML_ROOT e BASE_DIR

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
        
        # Caminho da pasta onde estão os arquivos XML
        # Usamos settings.CORPUS_XML_ROOT que já está configurado no settings.py
        base_dir_xml = settings.CORPUS_XML_ROOT 
        
        if not base_dir_xml.exists():
            raise CommandError(f"Diretório XML do corpus não encontrado: {base_dir_xml}. Verifique settings.CORPUS_XML_ROOT.")

        xml_files = list(base_dir_xml.glob('*.xml'))
        
        if not xml_files:
            self.stdout.write(self.style.WARNING('Nenhum arquivo XML encontrado para extração de termos.'))
            return

        # Caminho completo para o arquivo CSV de saída
        output_csv_path = settings.BASE_DIR / output_dir_name / "termos_extraidos.csv"

        if output_csv_path.exists() and not force_regen:
            self.stdout.write(self.style.NOTICE(f'Arquivo CSV {output_csv_path.name} já existe. Use --force-regen para forçar regeneração.'))
            return # Sai do comando se não for para regenerar

        self.stdout.write(self.style.HTTP_INFO('Iniciando extração de termos de XMLs para CSV...'))

        all_rows = []
        
        for file_path in xml_files:
            # Re-implementa a lógica do seu script extrTermos.py aqui
            # Usando etree.parse() como no seu script original que funciona
            # Se o erro "Extra content" persistir, a causa está no XML mesmo.
            try:
                self.stdout.write(f'  Processando: {file_path.name}')
                tree = etree.parse(str(file_path)) # Seu script original usa parse()
                terms = tree.xpath('//tei:term', namespaces=ns)
                rows_for_current_file = []

                # Extrair título limpo
                title_el = tree.find('.//tei:teiHeader//tei:sourceDesc//tei:bibl/tei:title', namespaces=ns)
                raw_title = title_el.text if title_el is not None else '(Sem título)'
                title = re.sub(r'\s+', ' ', raw_title).strip()

                # Slug da obra
                slug_obra = file_path.stem.lower()

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
                    # A lógica de destacar o token com <b> no CSV (sentence_text)
                    # Essa parte foi a fonte de alguns erros de parsing e _Comment.
                    # Vamos simplificar aqui e apenas pegar o texto puro da sentença
                    # ou tentar uma reimplmentação mais segura.
                    # A sua original:
                    # sentence_raw = ''.join(parent.itertext()).strip()
                    # sentence_text = sentence_raw.replace(token, f'<b>{token}</b>', 1)
                    
                    # Uma versão mais segura que evita o erro _Comment:
                    # Tenta copiar o elemento parent e injetar <b> nele, depois extrai o texto.
                    # Se o erro de _Comment voltou, esta lógica pode precisar de revisão.
                    # Para fins de extração para CSV, é mais seguro pegar apenas o texto sem destaque HTML.
                    
                    # Vamos pegar apenas o texto limpo da sentença, e o destaque será feito no frontend se necessário.
                    # Se a coluna 'sentence' PRECISA ter HTML, então a lógica precisa ser mais robusta.
                    # Por enquanto, pegando o texto.
                    sentence_text_raw = ''.join(parent.itertext()).strip()
                    # Se o CSV precisa do <b>, o problema de _Comment virá de volta.
                    # Melhor passar o token separado e a frase sem destaque, e montar no frontend.
                    # Ou, se a frase já vem com destaque do XML TEI, manter.
                    
                    # Sua definição original de full_sentence é:
                    # full_sentence = f'{sentence_text} ({author}, {date}, {link}, p. {page})'
                    # Vamos manter sentence_text como o texto da sentença, e adicionar os metadados.
                    
                    # No seu extrTermos.py, a lógica era:
                    # sentence_text = ''.join(parent.itertext()).strip()
                    # sentence_text = sentence_text.replace(token, f'<b>{token}</b>', 1)
                    # O erro de _Comment acontecia nessa linha ou na lógica de copiar o parent.

                    # Para evitar problemas aqui, vamos pegar o texto da sentença do pai do termo.
                    # Se o `term` em si contiver texto, ele também será incluído.
                    # Isso é mais seguro contra nós de comentário ou PI dentro da sentença.
                    sentence_text_from_parent = ''.join(parent.xpath('.//text()')).strip() # Pega só nós de texto
                    # Se você REALMENTE precisa do token em <b> aqui, é mais complexo e pode reintroduzir o erro.
                    # Por ora, mantemos o texto puro e destacamos no frontend.
                    sentence_text = sentence_text_from_parent


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
                    
                    # Aqui, a `full_sentence` para o CSV deve conter o que você quer ver na ocorrência.
                    # Se for o texto da sentença com os dados de citação, OK.
                    full_sentence = f'{sentence_text} ({author_surname}, {date}, {title}, p. {page})'

                    rows_for_current_file.append([
                        token,
                        headword,
                        orth,
                        gram,
                        sense_number,
                        full_sentence, # Conteúdo da sentença para o CSV
                        author_surname,
                        date,
                        title,
                        slug_obra
                    ])

                all_rows.extend(rows_for_current_file)

            except etree.ParseError as e:
                self.stderr.write(self.style.ERROR(f'Erro ao parsear XML {file_path.name}: {e}'))
                # NÃO levante CommandError aqui, apenas logue e continue para o próximo arquivo.
                # Se for um erro fatal, o comando irá parar.
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Erro inesperado ao processar {file_path.name}: {e}'))
                import traceback; traceback.print_exc()

        if not all_rows:
            self.stdout.write(self.style.WARNING('Nenhum termo extraído para gerar o CSV. O arquivo de saída pode estar vazio.'))
        
        # Garante que a pasta 'data' existe
        output_csv_path.parent.mkdir(parents=True, exist_ok=True) 

        try:
            with open(output_csv_path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "token", "Headword", "orth", "gram", "SenseNumber",
                    "sentence", "author_surname", "date", "title", "slug_obra"
                ])
                writer.writerows(all_rows)
            self.stdout.write(self.style.SUCCESS(f'✔️ CSV gerado com sucesso: {output_csv_path}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao escrever termos_extraidos.csv: {e}'))

        self.stdout.write(self.style.SUCCESS('Comando extract_corpus_terms concluído.'))

        # --- Parte 2: Importar/Atualizar Obras para o Modelo Obra (MOVIDA para o outro comando) ---
        # Remova a lógica de importação de obras daqui, ela será parte de import_dictionary_data
        # ou, se você precisa que Obra seja populado pelos XMLs, ela precisaria ser
        # uma etapa separada e cuidadosa neste comando, mas sem a lógica de Termos.
        # Por enquanto, vamos considerar que Obra é populada APENAS aqui.
        # A função extrair_titulo_autor_obra deve ser local a este comando ou movida para um util.
        # Eu vou movê-la para fora da classe Command para ser usada na etapa de Obra abaixo.

    # --- Se a importação de Obra ainda for neste comando, mantenha esta função aqui ---
    # Definição da função extrair_titulo_autor_obra fora do handle
    # para ser usada no loop de importação de Obra
    def extrair_titulo_autor_obra(self, xml_path, ns): # self e ns como parâmetros
        try:
            # etree.parse() é geralmente mais robusto para PIs e declarações iniciais
            tree = etree.parse(str(xml_path)) 
            # Limpeza de PIs e comentários na árvore, se necessário
            root_obra = tree.getroot()
            for node in list(root_obra.xpath('./node()')):
                if isinstance(node, etree._ProcessingInstruction) and not node.tag.startswith('xml'):
                    root_obra.remove(node)
                if isinstance(node, etree._Comment):
                    root_obra.remove(node)
            for el in root_obra.iter():
                 for child in list(el.xpath('./node()')):
                    if isinstance(child, etree._ProcessingInstruction) and not child.tag.startswith('xml'):
                        el.remove(child)
                    if isinstance(child, etree._Comment):
                        el.remove(child)
        except etree.ParseError as e:
            raise CommandError(f'Erro de parsing XML para obra {xml_path.name}: {e}')
        except Exception as e:
            raise CommandError(f'Erro inesperado ao abrir ou parsear XML para obra {xml_path.name}: {e}')

        bibl = tree.find('.//tei:teiHeader//tei:sourceDesc//tei:bibl', namespaces=ns)
        if bibl is not None:
            title = bibl.findtext('tei:title', default='(Sem título)', namespaces=ns)
            author = bibl.findtext('tei:author', default='(Sem autor)', namespaces=ns)
            title = re.sub(r'\s+', ' ', title).strip()
            author = re.sub(r'\s+', ' ', author).strip()
            return title, author
        return '(Sem título)', '(Sem autor)'
        