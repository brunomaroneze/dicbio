import rdflib
from rdflib import Namespace, URIRef, Literal, RDF
import unicodedata
import re

# 1. Configuração dos Namespaces
DICBIO = Namespace("http://dicbio.fflch.usp.br/recurso/")
ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")

def slugify(uri):
    """Transforma a parte final da URI em minúscula e sem acentos."""
    uri_str = str(uri)
    # Pegamos apenas a parte após o último / ou :
    base_part = uri_str.split('/')[-1]
    
    # Separamos o prefixo (ex: entry_, form_) do nome
    if '_' in base_part:
        prefix, name = base_part.split('_', 1)
    else:
        prefix, name = "", base_part

    # Remove acentos
    name_clean = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    # Lowercase e limpeza de caracteres não permitidos
    name_clean = name_clean.lower().replace(" ", "_")
    
    new_local = f"{prefix}_{name_clean}" if prefix else name_clean
    return DICBIO[new_local]

def fix_dictionary(input_file, output_file):
    # Carrega o grafo original
    g_old = rdflib.Graph()
    g_old.parse(input_file, format="turtle")
    
    # Cria um novo grafo para os dados limpos
    g_new = rdflib.Graph()
    
    # Copia todos os prefixos do grafo antigo para o novo
    for prefix, ns in g_old.namespaces():
        g_new.bind(prefix, ns)

    # Dicionário para guardar o texto original extraído das URIs de Formas
    # Isso garante que não perderemos "Bractéas" se a URI virar "bracteas"
    
    for s, p, o in g_old:
        # Slugifica Sujeito e Objeto se pertencerem ao dicbio
        new_s = slugify(s) if s.startswith(DICBIO) else s
        new_o = slugify(o) if o.startswith(DICBIO) else o
        
        # Adiciona a tripla ao novo grafo
        g_new.add((new_s, p, new_o))
        
        # Regra especial: Se o sujeito era uma Forma, garantimos o writtenRep
        if (s, RDF.type, ONTOLEX.Form) in g_old:
            # Extraímos o nome original da URI antiga para ser o writtenRep
            label_original = str(s).split('/')[-1].split('_', -1)[-1]
            g_new.add((new_s, ONTOLEX.writtenRep, Literal(label_original, lang="pt")))

    # Salva o resultado
    g_new.serialize(destination=output_file, format="turtle")
    print(f"Sucesso! Arquivo salvo em: {output_file}")

# Execute o script
fix_dictionary("./data/entries/DicionarioBiologia.ttl", "./data/entries/dicionario_limpo.ttl")