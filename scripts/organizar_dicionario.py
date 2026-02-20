# Este script organiza o dicionário RDF em blocos legíveis
# agrupando entradas, etimologias, formas e sentidos juntos.

import rdflib
from rdflib import Namespace, RDF, RDFS, SKOS, DCTERMS

# 1. Definição MANUAL dos Namespaces que não são nativos da RDFLib
DICBIO = Namespace("http://dicbio.fflch.usp.br/recurso/")
ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
ETYM = Namespace("http://lari-datasets.ilc.cnr.it/lemonEty#")

def organizar_dicionario(arquivo_input, arquivo_output):
    g = rdflib.Graph()
    # Tenta carregar o arquivo
    g.parse(arquivo_input, format="turtle")

    # Lista para controlar o que já foi escrito (evitar duplicatas)
    escritos = set()

    with open(arquivo_output, "w", encoding="utf-8") as f:
        # Escrever os Prefixos no topo do arquivo
        f.write("@prefix dcterms: <http://purl.org/dc/terms/> .\n")
        f.write("@prefix dicbio: <http://dicbio.fflch.usp.br/recurso/> .\n")
        f.write("@prefix ontolex: <http://www.w3.org/ns/lemon/ontolex#> .\n")
        f.write("@prefix etym: <http://lari-datasets.ilc.cnr.it/lemonEty#> .\n")
        f.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
        f.write("@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n")
        f.write("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n")
        f.write("\n")

        # Buscar todas as entradas lexicais e ordenar
        entries = sorted(list(g.subjects(RDF.type, ONTOLEX.LexicalEntry)))

        for entry in entries:
            term_name = str(entry).split('/')[-1].replace("entry_", "")
            f.write(f"### --- VERBETE: {term_name.upper()} ---\n\n")
            
            def write_subject_block(s):
                if s in escritos or not s.startswith(DICBIO): 
                    return
                
                # Cria um mini-grafo para formatar apenas este bloco
                mini_g = rdflib.Graph()
                for prefix, ns in g.namespaces():
                    mini_g.bind(prefix, ns)
                
                # Adiciona as triplas do sujeito
                has_data = False
                for p, o in g.predicate_objects(s):
                    mini_g.add((s, p, o))
                    has_data = True
                
                if has_data:
                    # O serialize retorna uma string no formato Turtle
                    # decode('utf-8') se for necessário em versões antigas, mas o RDFLib moderno retorna string
                    bloco = mini_g.serialize(format="turtle")
                    # Remove prefixos repetidos que o serialize coloca em cada bloco
                    linhas = [l for l in bloco.split('\n') if not l.startswith('@prefix')]
                    f.write("\n".join(linhas).strip() + "\n\n")
                    escritos.add(s)

            # --- Sequência de Escrita para Agrupar o Verbete ---
            
            # 1. A Entrada Principal
            write_subject_block(entry)

            # 2. Etimologia e Étimos
            for ety in g.objects(entry, ETYM.etymology):
                write_subject_block(ety)
                for etymon in g.objects(ety, ETYM.etymon):
                    write_subject_block(etymon)

            # 3. Formas (Canônica e outras)
            for form in g.objects(entry, ONTOLEX.canonicalForm):
                write_subject_block(form)
            for form in g.objects(entry, ONTOLEX.otherForm):
                write_subject_block(form)

            # 4. Sentidos
            for sense in g.objects(entry, ONTOLEX.sense):
                write_subject_block(sense)

            f.write("#" + "-" * 60 + "\n\n")

    print(f"Sucesso! Dicionário organizado salvo em: {arquivo_output}")

# Execute
organizar_dicionario("./data/dicionario_limpo.ttl", "./data/dicionario_organizado.ttl")