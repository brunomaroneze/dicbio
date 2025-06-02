import os
import csv
import re
from lxml import etree
from pathlib import Path

# Caminho da pasta onde estão os arquivos XML
base_dir = Path('web/corpus_digital/obras')
xml_files = list(base_dir.glob('*.xml'))

ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

def process_tei_file(file_path):
    tree = etree.parse(str(file_path))
    terms = tree.xpath('//tei:term', namespaces=ns)
    rows = []

    # Extrair título limpo
    title_el = tree.find('.//tei:teiHeader//tei:sourceDesc//tei:bibl/tei:title', namespaces=ns)
    raw_title = title_el.text if title_el is not None else '(Sem título)'
    title = re.sub(r'\s+', ' ', raw_title).strip()

    # Slug da obra = nome do arquivo sem extensão
    slug_obra = file_path.stem.lower()
    link = f'<a href="/corpus/{slug_obra}">{title}</a>'

    for term in terms:
        token = (term.text or '').strip()
        headword = term.get('lemma', token)
        orth = term.get('norm', headword)
        gram = term.get('msd', '')
        sense_number = term.get('senseNumber', '1')

        # Texto da sentença com destaque no <b>
        parent = term.getparent()
        sentence_text = ''.join(parent.itertext()).strip()
        sentence_text = sentence_text.replace(token, f'<b>{token}</b>', 1)

        # Autor
        author_el = term.xpath('.//ancestor::tei:TEI//tei:author', namespaces=ns)
        if author_el and ',' in author_el[0].text:
            author = author_el[0].text.strip().split(',')[0]
        else:
            author = author_el[0].text.strip().split()[-1] if author_el else 'AutorDesconhecido'
        author_surname = author.upper()

        # Data
        date_el = term.xpath('.//ancestor::tei:TEI//tei:date', namespaces=ns)
        date = date_el[0].text.strip() if date_el else 's.d.'

        # Página
        pb_inside = parent.xpath('.//tei:pb', namespaces=ns)
        if pb_inside:
            pb_now = pb_inside[0].get('n', '')
            pb_before_el = pb_inside[0].xpath('./preceding::tei:pb[1]', namespaces=ns)
            pb_before = pb_before_el[0].get('n') if pb_before_el else ''
            page = f'{pb_before}-{pb_now}' if pb_before else pb_now
        else:
            pb_before_el = parent.xpath('./preceding::tei:pb[1]', namespaces=ns)
            page = pb_before_el[0].get('n') if pb_before_el else ''

        full_sentence = f'{sentence_text} ({author}, {date}, {link}, p. {page})'

        rows.append([
            token,
            headword,
            orth,
            gram,
            sense_number,
            full_sentence,
            author_surname,
            date,
            title,
            slug_obra
        ])

    return rows

# Geração do CSV
all_rows = []
for file in xml_files:
    if file.exists():
        all_rows.extend(process_tei_file(file))

output_file = "data/termos_extraidos.csv"
with open(output_file, mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        "token", "Headword", "orth", "gram", "SenseNumber",
        "sentence", "author_surname", "date", "title", "slug_obra"
    ])
    writer.writerows(all_rows)

print(f"✔️ CSV gerado com sucesso: {output_file}")
