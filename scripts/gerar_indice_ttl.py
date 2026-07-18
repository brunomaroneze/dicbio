import os
import unicodedata
import rdflib

from rdflib import Namespace, Literal, RDF, URIRef
from lxml import etree

# Namespaces
DICBIO = Namespace("http://dicbio.fflch.usp.br/recurso/")
NIF = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
ITSRDF = Namespace("http://www.w3.org/2005/11/its/rdf#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
# PROV = Namespace("http://www.w3.org/ns/prov#")


def slugify(text):
    if not text:
        return ""

    nfkd_form = unicodedata.normalize("NFKD", text)
    text_slug = "".join(
        c for c in nfkd_form
        if not unicodedata.combining(c)
    )

    return text_slug.lower().replace(" ", "_")


def gerar_nif_index(arquivos_xml, arquivo_saida):

    g = rdflib.Graph()

    g.bind("dbres", DICBIO)
    g.bind("nif", NIF)
    g.bind("itsrdf", ITSRDF)
    g.bind("dcterms", DCTERMS)
    # g.bind("prov", PROV)

    parser = etree.XMLParser(remove_blank_text=True)

    contextos_gerados = set()

    ns = {"tei": "http://www.tei-c.org/ns/1.0"}

    for xml_file in arquivos_xml:

        if not os.path.exists(xml_file):
            continue

        tree = etree.parse(xml_file, parser)

        nome_obra = os.path.splitext(os.path.basename(xml_file))[0]

        uri_obra = DICBIO[f"work_{nome_obra}"]

        uri_documento = URIRef(
            f"http://dicbio.fflch.usp.br/corpus_digital/{os.path.basename(xml_file)}"
        )

        termos = tree.xpath("//tei:term[@xml:id]", namespaces=ns)

        for termo in termos:

            xml_id = termo.get("{http://www.w3.org/XML/1998/namespace}id")

            texto_exato = "".join(termo.itertext()).strip()

            lema = termo.get("lemma", "")

            ref = termo.get("ref")
            sense_num = termo.get("senseNumber", "1")

            if ref:
                uri_acepcao = URIRef(ref)
            else:
                slug_lema = slugify(lema)
                uri_acepcao = DICBIO[f"entry_{slug_lema}_sense{sense_num}"]

            uri_token = DICBIO[xml_id]

            g.add((uri_token, RDF.type, NIF.Word))
            g.add((uri_token, NIF.anchorOf, Literal(texto_exato, lang="pt")))
            g.add((uri_token, NIF.lemma, Literal(lema, lang="pt")))
            g.add((uri_token, ITSRDF.taIdentRef, uri_acepcao))

            #
            # Procura primeiro a sentença (<s>)
            #

            contexto = termo.xpath("ancestor::tei:s[@xml:id][1]", namespaces=ns)

            if contexto:

                contexto = contexto[0]

            else:

                contexto = termo.xpath("ancestor::tei:p[@xml:id][1]", namespaces=ns)

                if contexto:
                    contexto = contexto[0]
                else:
                    contexto = None

            if contexto is None:
                continue

            id_contexto = contexto.get("{http://www.w3.org/XML/1998/namespace}id")

            uri_contexto = DICBIO[id_contexto]

            g.add((uri_token, NIF.referenceContext, uri_contexto))

            #
            # Gera a sentença apenas uma vez
            #

            if id_contexto not in contextos_gerados:

                texto_contexto = " ".join(
                    "".join(contexto.itertext()).split()
                )

                tipo = NIF.Sentence if contexto.tag.endswith("s") else NIF.Paragraph

                g.add((uri_contexto, RDF.type, tipo))
                g.add((uri_contexto,
                       NIF.isString,
                       Literal(texto_contexto, lang="pt")))

                g.add((uri_contexto,
                       DCTERMS.isPartOf,
                       uri_obra))

                # g.add((uri_contexto,
                #        PROV.wasQuotedFrom,
                #        uri_documento))

                contextos_gerados.add(id_contexto)

    g.serialize(destination=arquivo_saida, format="turtle")

    print(f"Índice NIF gerado: {arquivo_saida}")


meus_arquivos = [
    "corpus_digital/obras/anatomiasantucci.xml",
    "corpus_digital/obras/compendio1brotero.xml",
    "corpus_digital/obras/compendio2brotero.xml",
    "corpus_digital/obras/diciovandelli.xml",
    "corpus_digital/obras/observSemmedo.xml",
]

gerar_nif_index(meus_arquivos, "data/corpus_index.ttl")