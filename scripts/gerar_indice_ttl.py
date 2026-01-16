import rdflib
from rdflib import Namespace, Literal, RDF, URIRef
from lxml import etree
import os
import unicodedata

# Namespaces
DICBIO = Namespace("http://dicbio.fflch.usp.br/recurso/")
NIF = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
ITSRDF = Namespace("http://www.w3.org/2005/11/its/rdf#")

def slugify(text):
    if not text:
        return ""
    # Normaliza o texto (ex: 'â' vira 'a' + '̂')
    nfkd_form = unicodedata.normalize('NFKD', text)
    # Filtra apenas os caracteres que não são acentos (non-spacing marks)
    # e converte para minúsculas, substituindo espaços por sublinhados
    text_slug = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return text_slug.lower().replace(" ", "_")

def gerar_nif_index(arquivos_xml, arquivo_saida):
    g = rdflib.Graph()
    g.bind("dicbio", DICBIO)
    g.bind("nif", NIF)
    g.bind("itsrdf", ITSRDF)

    parser = etree.XMLParser(remove_blank_text=True)

    for xml_file in arquivos_xml:
        if not os.path.exists(xml_file): continue
        
        tree = etree.parse(xml_file, parser)
        # Busca todos os <term> que tenham xml:id
        termos = tree.xpath("//tei:term[@xml:id]", namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

        for termo in termos:
            xml_id = termo.get("{http://www.w3.org/XML/1998/namespace}id")
            texto_exato = termo.text if termo.text else ""
            lema = termo.get("lemma", "")
            
            # Lógica da Acepção (Prioridade: @ref > @senseNumber > default sense1)
            ref = termo.get("ref")
            sense_num = termo.get("senseNumber", "1")
            
            if ref:
                uri_acepcao = URIRef(ref)
            else:
                # Se não tem ref, monta a URI baseada no lema e no senseNumber
                # Ex: entry_disco#sense2
                slug_lema = slugify(lema)
                uri_acepcao = DICBIO[f"entry_{slug_lema}#sense{sense_num}"]

            # Cria a URI da ocorrência (token)
            uri_token = DICBIO[xml_id]

            # Adiciona triplas ao grafo
            g.add((uri_token, RDF.type, NIF.Word))
            g.add((uri_token, NIF.anchorOf, Literal(texto_exato, lang="pt")))
            g.add((uri_token, NIF.lemma, Literal(lema, lang="pt")))
            g.add((uri_token, ITSRDF.taIdentRef, uri_acepcao))
            
            # Tenta pegar o ID do parágrafo pai (contexto)
            pai = termo.getparent()
            while pai is not None and "{http://www.w3.org/XML/1998/namespace}id" not in pai.attrib:
                pai = pai.getparent()
            
            if pai is not None:
                id_pai = pai.get("{http://www.w3.org/XML/1998/namespace}id")
                g.add((uri_token, NIF.referenceContext, DICBIO[id_pai]))

    # Salva o arquivo Turtle
    g.serialize(destination=arquivo_saida, format="turtle")
    print(f"Índice NIF gerado: {arquivo_saida}")

# Lista de seus arquivos
meus_arquivos = [
    "corpus_digital/obras_convertidas/anatomiasantucci.xml", "corpus_digital/obras_convertidas/compendio1brotero.xml", "corpus_digital/obras_convertidas/compendio2brotero.xml",
    "corpus_digital/obras_convertidas/diciovandelli.xml", "corpus_digital/obras_convertidas/observSemmedo.xml"
]

gerar_nif_index(meus_arquivos, "corpus_index.ttl")