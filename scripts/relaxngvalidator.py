"""
Este script foi escrito pelo ChatGPT e alterado depois. Serve para validar
um arquivo XML usando o modelo RELAX-NG. Neste caso, serve para validar
o arquivo do córpus (XML-TEI) usando o próprio modelo RELAX-NG criado
pelo ROMA-TEI.
"""

from lxml import etree

def validar_xml_com_relaxng(arquivo_xml, arquivo_rng):
    """
    Valida um arquivo XML contra um esquema RELAX NG.

    Parâmetros:
        arquivo_xml (str): Caminho do arquivo XML a ser validado.
        arquivo_rng (str): Caminho do arquivo RELAX NG usado para validação.

    Retorna:
        bool: True se o XML for válido, False caso contrário.
    """
    try:
        # Carregar o esquema RELAX NG
        with open(arquivo_rng, "rb") as rng_file:
            relaxng_tree = etree.parse(rng_file)
            relaxng = etree.RelaxNG(relaxng_tree)

        # Carregar o XML a ser validado
        with open(arquivo_xml, "rb") as xml_file:
            xml_tree = etree.parse(xml_file)

        # Validar o XML
        if relaxng.validate(xml_tree):
            print("O XML é válido.")
            return True
        else:
            print("O XML é inválido.")
            print(relaxng.error_log)
            return False

    except Exception as e:
        print(f"Erro ao validar XML: {e}")
        return False

# Exemplo de uso
arquivo_xml = "data/compendio1brotero.xml"
arquivo_rng = "data/tei_dhtb.rng"

validar_xml_com_relaxng(arquivo_xml, arquivo_rng)