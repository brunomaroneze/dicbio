import csv
from rdflib import Graph, Literal, Namespace, URIRef, BNode
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS, SKOS

# 1. Configuração de Namespaces
DICBIO = Namespace("http://dicbio.fflch.usp.br/recurso/")
ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
LEXINFO = Namespace("http://www.lexinfo.net/ontology/2.0/lexinfo#")
ETYM = Namespace("http://lari-datasets.ilc.cnr.it/lemonEty#")
AUTHOR = Namespace("http://dicbio.fflch.usp.br/autor/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

def converter_arquivos_locais(caminho_dados, caminho_defs, caminho_termos, arquivo_saida):
    g = Graph()
    g.bind("dicbio", DICBIO)
    g.bind("ontolex", ONTOLEX)
    g.bind("lexinfo", LEXINFO)
    g.bind("etym", ETYM)
    g.bind("dcterms", DCTERMS)
    g.bind("skos", SKOS)
    g.bind("foaf", FOAF)
    g.bind("author", AUTHOR)

    map_pos = {
        "adjetivo": LEXINFO.adjective,
        "substantivo": LEXINFO.noun,
        "verbo": LEXINFO.verb
    }

    entradas = {}
    senses = {}

    # --- PROCESSAR TABELA 1: DadosDoDicionario.csv ---
    with open(caminho_dados, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            headword = row['Headword'].strip()
            # Substituindo espaços por underscores para URIs válidas
            headword_uri = headword.replace(" ", "_")
            uri_entry = DICBIO[f"entry_{headword_uri}"]
            entradas[headword] = uri_entry

            g.add((uri_entry, RDF.type, ONTOLEX.LexicalEntry))
            
            pos = map_pos.get(row['WClass'].lower(), LEXINFO.adjective)
            g.add((uri_entry, LEXINFO.partOfSpeech, pos))

            uri_form = DICBIO[f"form_{headword_uri}"]
            g.add((uri_entry, ONTOLEX.canonicalForm, uri_form))
            g.add((uri_form, RDF.type, ONTOLEX.Form))
            g.add((uri_form, ONTOLEX.writtenRep, Literal(headword, lang="pt")))

            uri_etym = DICBIO[f"etym_{headword_uri}"]
            g.add((uri_entry, ETYM.etymology, uri_etym))
            g.add((uri_etym, RDF.type, ETYM.Etymology))
            g.add((uri_etym, RDFS.comment, Literal(row['Etymology'], lang="pt")))

            for autor in row['Credits'].split(';'):
                g.add((uri_entry, DCTERMS.creator, Literal(autor.strip())))
            g.add((uri_entry, DCTERMS.created, Literal(row['DateOfCreation'], datatype=XSD.string)))

    # --- PROCESSAR TABELA 2: Definitions.csv ---
    with open(caminho_defs, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            headword = row['Headword'].strip()
            headword_uri = headword.replace(" ", "_")
            sense_num = row['SenseNumber']
            uri_entry = entradas.get(headword)
            if not uri_entry: continue

            uri_sense = DICBIO[f"sense_{headword_uri}_{sense_num}"]
            senses[(headword, sense_num)] = uri_sense

            g.add((uri_entry, ONTOLEX.sense, uri_sense))
            g.add((uri_sense, RDF.type, ONTOLEX.LexicalSense))
            g.add((uri_sense, SKOS.definition, Literal(row['Definition'], lang="pt")))

            # Étimo
            uri_etym = DICBIO[f"etym_{headword_uri}"]
            etymon_label = row['Etymon'].replace(" ", "_")
            uri_etymon = DICBIO[f"etymon_{etymon_label}"]
            g.add((uri_etym, ETYM.etymon, uri_etymon))
            g.add((uri_etymon, RDF.type, ETYM.Etymon))
            g.add((uri_etymon, ONTOLEX.writtenRep, Literal(row['Etymon'])))
            g.add((uri_etymon, DCTERMS.language, Literal(row['EtymonLanguage'])))
            g.add((uri_etymon, DCTERMS.source, Literal(row['EtymonSource'])))

    # --- PROCESSAR TABELA 3: termos extraídos.csv ---
    with open(caminho_termos, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            headword = row['Headword'].strip()
            headword_uri = headword.replace(" ", "_")
            sense_num = row['SenseNumber']
            token = row['token']
            uri_sense = senses.get((headword, sense_num))
            if not uri_sense: continue

            uri_usage = DICBIO[f"usage_{headword_uri}_{i}"]
            g.add((uri_sense, ONTOLEX.usage, uri_usage))
            g.add((uri_usage, RDF.type, ONTOLEX.UsageExample))
            g.add((uri_usage, RDF.value, Literal(row['sentence'], lang="pt")))
            
            g.add((uri_usage, DCTERMS.creator, Literal(row['author_surname'])))
            g.add((uri_usage, DCTERMS.date, Literal(row['date'])))
            g.add((uri_usage, DCTERMS.bibliographicCitation, 
                   Literal(f"{row['title']}, p. {row['page_num']} (Ref: {row['slug_obra']})")))

            if token.lower() != headword.lower():
                uri_entry = entradas.get(headword)
                token_uri = token.replace(" ", "_")
                uri_other_form = DICBIO[f"form_{token_uri}"]
                g.add((uri_entry, ONTOLEX.otherForm, uri_other_form))
                g.add((uri_other_form, RDF.type, ONTOLEX.Form))
                g.add((uri_other_form, ONTOLEX.writtenRep, Literal(token, lang="pt")))
                if row['gram']:
                    g.add((uri_other_form, RDFS.label, Literal(row['gram'], lang="pt")))

    # 2. Comando para SALVAR em arquivo
    g.serialize(destination=arquivo_saida, format="turtle", encoding="utf-8")
    print(f"Sucesso! Arquivo '{arquivo_saida}' gerado.")

# --- EXECUÇÃO DO SCRIPT ---
# Coloque aqui os nomes exatos dos seus arquivos .csv
converter_arquivos_locais(
    caminho_dados='data/DadosDoDicionario.csv', 
    caminho_defs='data/Definitions.csv', 
    caminho_termos='data/termos_extraidos.csv', 
    arquivo_saida='data/DicionarioBiologia.ttl'
)