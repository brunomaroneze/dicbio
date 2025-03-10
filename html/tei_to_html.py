# Este código foi elaborado pelo ChatGPT e pelo DeepSeek para converter
# um arquivo XML no padrão TEI para um arquivo HTML a ser exibido
# no site com links clicáveis para as imagens.
# Ainda falta incluir a funcionalidade de clicar no termo e abrir
# o verbete correspondente.

from lxml import etree
from lxml.etree import Comment

def process_element(element):
    # Ignorar comentários XML
    if element.tag is etree.Comment:
        return ""
    
    # Remover namespace da tag
    tag = element.tag.split('}')[-1]
    
    # Processar elementos específicos
    if tag == "pb" and "facs" in element.attrib:
        page_number = element.attrib.get("n", "?")
        img_link = element.attrib["facs"]
        return f'<a href="{img_link}" target="_blank">[Página {page_number}]</a>'
    
    if tag == "term":
        text = (element.text or "").strip()
        return f'<span class="term">{text}</span>'
    
    if tag == "head":
        text = (element.text or "").strip()
        return f'<h2>{text}</h2>'  # Usar <h2> para cabeçalhos
    
    if tag == "p":
        result = []
        if element.text:
            result.append(element.text.strip())
        
        for child in element:
            result.append(process_element(child))
            if child.tail:  # Capturar o texto após o filho
                result.append(child.tail.strip())
        
        return f'<p>{" ".join(result)}</p>'  # Envolver o conteúdo em <p>
    
    if tag == "note":
        result = []
        if element.text:
            result.append(element.text.strip())
        
        for child in element:
            result.append(process_element(child))
            if child.tail:  # Capturar o texto após o filho
                result.append(child.tail.strip())
        
        # Usar <details> e <summary> para notas de rodapé
        return f'<details><summary>Nota</summary>{" ".join(result)}</details>'
    
    # Processar outros elementos genéricos
    result = []
    if element.text:
        result.append(element.text.strip())
    
    for child in element:
        result.append(process_element(child))
        if child.tail:  # Capturar o texto após o filho
            result.append(child.tail.strip())
    
    return " ".join(result)

def tei_to_html(xml_path, output_path):
    tree = etree.parse(xml_path)
    root = tree.getroot()
    
    html_content = []
    
    for elem in root.iter():
        if isinstance(elem, etree._Element):  # Garante que não é um comentário
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
            h2 { color: darkgreen; font-size: 1.5em; margin-top: 20px; }
            p { margin-bottom: 15px; line-height: 1.6; }
            details { 
                margin-bottom: 10px; 
                padding: 5px; 
                background-color: #f9f9f9; 
                border: 1px solid #ddd; 
                border-radius: 4px; 
            }
            summary { 
                font-weight: bold; 
                cursor: pointer; 
            }
        </style>
    </head>
    <body>
        <h1>Compêndio de Botânica</h1>
        <div>
    """ + "".join(html_content) + """
        </div>
    </body>
    </html>
    """
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)

# Exemplo de uso:
tei_to_html('../data/compendio1brotero.xml', 'compendio.html')