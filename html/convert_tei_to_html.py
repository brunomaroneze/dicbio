from lxml import etree

# Função para gerar o HTML de uma página
def gerar_html_pagina(numero_pagina, url_imagem, conteudo, anterior, seguinte):
    html = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Página {numero_pagina}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; display: flex; flex-direction: column; }}
            .container {{ display: flex; width: 100%; }}
            .imagem {{ flex: 1; padding: 10px; }}
            .texto {{ flex: 1; padding: 10px; }}
            .navegacao {{ text-align: center; margin-top: 20px; }}
            .navegacao a {{ margin: 0 10px; text-decoration: none; color: blue; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="imagem">
                <img src="{url_imagem}" alt="Página {numero_pagina}" style="max-width: 100%; height: auto;">
            </div>
            <div class="texto">
                {conteudo}
            </div>
        </div>
        <div class="navegacao">
            {"<a href='" + anterior + "'>Anterior</a>" if anterior else ""}
            {"<a href='" + seguinte + "'>Seguinte</a>" if seguinte else ""}
        </div>
    </body>
    </html>
    """
    return html

# Carregar o arquivo XML
arquivo_xml = "../data/compendio1brotero.xml"
tree = etree.parse(arquivo_xml)
root = tree.getroot()

# Namespace TEI (se necessário)
TEI_NS = "http://www.tei-c.org/ns/1.0"
ns = {"tei": TEI_NS}

# Extrair todas as páginas (<pb>) e o conteúdo entre elas
paginas = root.xpath("//tei:pb", namespaces=ns)
conteudos = []
for i, pb in enumerate(paginas):
    # Obter o número da página e a URL da imagem
    numero_pagina = pb.get("n")
    url_imagem = pb.get("facs")
    
    # Extrair o conteúdo entre o <pb> atual e o próximo
    if i < len(paginas) - 1:
        proximo_pb = paginas[i + 1]
        conteudo = "".join(etree.tostring(child, encoding="unicode") for child in pb.itersiblings(preceding=False) if child != proximo_pb)
    else:
        conteudo = "".join(etree.tostring(child, encoding="unicode") for child in pb.itersiblings(preceding=False))
    
    conteudos.append((numero_pagina, url_imagem, conteudo))

# Gerar arquivos HTML para cada página
for i, (numero_pagina, url_imagem, conteudo) in enumerate(conteudos):
    # Definir links de navegação
    anterior = f"pagina_{i}.html" if i > 0 else None
    seguinte = f"pagina_{i + 2}.html" if i < len(conteudos) - 1 else None
    
    # Gerar o HTML da página
    html = gerar_html_pagina(numero_pagina, url_imagem, conteudo, anterior, seguinte)
    
    # Salvar o arquivo HTML
    nome_arquivo = f"pagina_{i + 1}.html"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Arquivo {nome_arquivo} gerado com sucesso.")