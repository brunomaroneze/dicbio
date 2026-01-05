import os
from lxml import etree

def converter_corpus_tei(pasta_entrada, pasta_saida):
    # Cria a pasta de saída se não existir
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    # Base da URI
    BASE_URI = "http://dicbio.fflch.usp.br/recurso/sense_"

    # Percorre todos os arquivos na pasta
    for nome_arquivo in os.listdir(pasta_entrada):
        if nome_arquivo.endswith(".xml"):
            caminho_input = os.path.join(pasta_entrada, nome_arquivo)
            print(f"Processando: {nome_arquivo}...")

            # Carrega o XML (preservando comentários e CDATA)
            parser = etree.XMLParser(remove_blank_text=False)
            tree = etree.parse(caminho_input, parser)
            root = tree.getroot()

            # Namespace do TEI (geralmente necessário em arquivos TEI)
            # Se o seu XML não tiver namespace, isso será ignorado
            ns = {"tei": root.nsmap.get(None, "")}
            
            # Localiza todos os elementos <term>
            # Usamos //term para pegar em qualquer profundidade
            for term in root.xpath("//term") if not ns["tei"] else root.xpath("//tei:term", namespaces=ns):
                
                # 1. Obtém o senseNumber (obrigatório para a URI)
                sense_num = term.get("senseNumber")
                if sense_num is None:
                    continue # Pula se não tiver número de sentido

                # 2. Determina o Lema
                # Se tiver atributo @lemma, usa ele. Se não, usa o texto dentro da tag.
                lema = term.get("lemma")
                if lema is None:
                    lema = term.text.strip() if term.text else ""

                # 3. Normaliza o Lema para a URI (espaços por underscores)
                lema_uri = lema.replace(" ", "_")

                # 4. Constrói a URI completa
                nova_uri = f"{BASE_URI}{lema_uri}_{sense_num}"

                # 5. Atualiza os atributos
                term.set("ref", nova_uri)
                
                # Opcional: remover o senseNumber já que agora está na URI
                # del term.attrib["senseNumber"]

            # Salva o arquivo convertido
            caminho_output = os.path.join(pasta_saida, nome_arquivo)
            tree.write(caminho_output, encoding="utf-8", xml_declaration=True, pretty_print=False)

    print("\nConversão concluída com sucesso!")

# --- CONFIGURAÇÃO ---
# Coloque o caminho das suas pastas aqui
converter_corpus_tei(
    pasta_entrada='../corpus_digital/obras', 
    pasta_saida='../corpus_digital/obras_convertidas'
)