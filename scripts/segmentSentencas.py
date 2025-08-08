"""
Este código usa spaCy para segmentar as sentenças que estão dentro
de um elemento <p>. Foi escrito pelo Guilherme Mendes Vieira.
O código precisa ser corrigido porque não está segmentando adequadamente
quando dentro do parágrafo há outros elementos como <s> e <pb/>.
"""
import spacy
import xml.etree.ElementTree as ET

# Carrega o modelo spaCy corretamente
nlp = spacy.load("en_core_web_sm")

# Caminhos dos arquivos
caminho_entrada = "compendio1brotero.xml"
caminho_saida = "compendio1brotero_processado.xml"

# Função para remover namespaces indesejados
def remove_namespaces(element):
    for elem in element.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]  # Remove o namespace do início da tag

# Função para processar o XML e manter a estrutura
def processar_xml(caminho_entrada, caminho_saida):
    tree = ET.parse(caminho_entrada)
    root = tree.getroot()

    # Namespace do TEI
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    # Busca todos os elementos <p> dentro de <text>
    for elem in root.findall(".//tei:text//tei:p", ns):
        if elem.text and elem.text.strip():  # Garante que há texto válido
            doc = nlp(elem.text.strip())  # Processa o texto com spaCy
            elem.clear()  # Limpa o conteúdo do elemento <p>

            # Adiciona cada sentença como um novo elemento <s>
            for sent in doc.sents:
                s_elem = ET.Element("s")
                s_elem.text = sent.text
                elem.append(s_elem)

    # Remove namespaces extras
    remove_namespaces(root)

    # Converte a árvore XML para string
    xml_string = ET.tostring(root, encoding="utf-8", method="xml").decode()

    # Escreve o arquivo de saída corretamente
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(xml_string)

# Executa o processamento
processar_xml(caminho_entrada, caminho_saida)

print(f"Arquivo XML processado salvo em: {caminho_saida}")