import rdflib

g = rdflib.Graph()
try:
    # Tente carregar o arquivo
    g.parse("data/dicionario_organizado.ttl", format="turtle")
    print("O arquivo está perfeito!")
except Exception as e:
    print("Erro encontrado!")
    print(e)