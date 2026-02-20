# Este script percorre os arquivos XML TEI no diretório especificado
# e numera as tags de interesse que não possuem um atributo xml:id,
# seguindo o padrão definido, garantindo unicidade e continuidade.

import os
from lxml import etree

# 1. Configuração dos arquivos e seus respectivos "Slugs" de obra
# Isso resolve o problema de autores com mais de um livro.
MAPA_OBRAS = {
    "anatomiasantucci.xml": "santucci",
    "compendio1brotero.xml": "brotero1",
    "compendio2brotero.xml": "brotero2",
    "diciovandelli.xml": "vandelli",
    "observSemmedo.xml": "semmedo"
}
DIRETORIO_CORPUS = "corpus_digital/obras/"

# Tags que queremos numerar e seus respectivos prefixos de ID
TAGS_INTERESSE = {
    "term": "t",
    "p": "p",
    "s": "s",
    "head": "h",
    "sense": "sn",
    "item": "i",
    "note": "n"
}

# Namespaces padrão do TEI e XML
NS = {'tei': 'http://www.tei-c.org/ns/1.0'}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

def processar_arquivos():
    for nome_arquivo, slug_obra in MAPA_OBRAS.items():
        caminho_completo = os.path.join(DIRETORIO_CORPUS, nome_arquivo)
        if not os.path.exists(caminho_completo):
            print(f"Arquivo {nome_arquivo} não encontrado. Pulando...")
            continue

        print(f"Processando {nome_arquivo} (Obra: {slug_obra})...")
        
        # Carrega o XML
        parser = etree.XMLParser(remove_blank_text=False)
        tree = etree.parse(caminho_completo, parser)
        root = tree.getroot()

        # Localiza a tag <text> (para ignorar o header)
        texto_corpo = root.find(".//tei:text", NS)
        if texto_corpo is None:
            print(f"Erro: <text> não encontrado em {nome_arquivo}")
            continue

        # Passo 1: Descobrir o maior número já existente para cada prefixo
        # Isso evita que o script reinicie a contagem se você apagar algo no meio
        contadores = {prefixo: 0 for prefixo in TAGS_INTERESSE.values()}
        
        # Varremos o arquivo inteiro em busca de xml:id já existentes
        for elemento in root.xpath(".//*[@xml:id]"):
            id_atual = elemento.get(XML_ID)
            # Tenta extrair o número do final do ID (ex: t_santucci_0042 -> 42)
            try:
                partes = id_atual.split('_')
                if len(partes) >= 3:
                    prefixo = partes[0]
                    numero = int(partes[-1])
                    if prefixo in contadores:
                        if numero > contadores[prefixo]:
                            contadores[prefixo] = numero
            except ValueError:
                continue

        # Passo 2: Atribuir novos IDs apenas onde não existe
        total_novos = 0
        # Iteramos apenas sobre as tags dentro de <text>
        for tag_nome, prefixo in TAGS_INTERESSE.items():
            elementos = texto_corpo.xpath(f".//tei:{tag_nome}", namespaces=NS)
            
            for el in elementos:
                if el.get(XML_ID) is None:
                    contadores[prefixo] += 1
                    novo_id = f"{prefixo}_{slug_obra}_{contadores[prefixo]:04d}"
                    el.set(XML_ID, novo_id)
                    total_novos += 1

        # Salva o arquivo de volta
        if total_novos > 0:
            tree.write(caminho_completo, encoding="utf-8", xml_declaration=True, pretty_print=False)
            print(f"Concluído: {total_novos} novos IDs gerados.")
        else:
            print("Nenhuma alteração necessária.")

if __name__ == "__main__":
    processar_arquivos()