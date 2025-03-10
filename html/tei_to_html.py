from lxml import etree
from lxml.etree import Comment

def process_element(element):
    if element.tag is etree.Comment:  # Ignorar comentários XML
        return ""
    
    tag = element.tag.split('}')[-1]  # Remover namespace
    text = (element.text or "").strip()
    
    if tag == "pb" and "facs" in element.attrib:
        page_number = element.attrib.get("n", "?")
        img_link = element.attrib["facs"]
        return f'<a href="{img_link}" target="_blank">[Página {page_number}]</a>'
    
    if tag == "term":
        return f'<span class="term">{text}</span>'
    
    return text

def tei_to_html(xml_path, output_path):
    tree = etree.parse(xml_path)
    root = tree.getroot()
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    html_content = []
    
    for elem in root.iter():
        if isinstance(elem, etree._Element):  # Garante que não é um comentário
            print(f'Processando: {type(elem)} - {elem.tag}')
            html_content.append(process_element(elem))
    
    html_output = """
    <!DOCTYPE html>
    <html lang='pt'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Compêndio de Botânica</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .term { color: blue; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Compêndio de Botânica</h1>
        <div>
    """ + " ".join(html_content) + """
        </div>
    </body>
    </html>
    """
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)

# Exemplo de uso:
tei_to_html('../data/compendio1brotero.xml', 'compendio.html')