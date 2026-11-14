"""Testes da ontologia DicBio com o ROBOT (http://robot.obolibrary.org).

Complementa os testes feitos com o HermiT via Owlready2 e a validação SHACL
(scripts/validate_graph.py). Roda dois cenários:

  1. ontologia  — só data/dicbio-ontology.ttl (com as importações);
  2. dados      — ontologia + sources.ttl + authors.ttl + verbetes escolhidos
                  (por padrão, só data/entries/adiposo.ttl, o único já revisado
                  com o SHACL).

Em cada cenário, o ROBOT faz:

  a. validate-profile  — o conjunto está no perfil OWL 2 DL? (pré-requisito
                         para que o raciocínio do HermiT seja completo);
  b. reason (HermiT)   — consistência e classes insatisfazíveis; se houver
                         problema, roda explain para mostrar a causa;
  c. tipos inferidos   — (só no cenário "dados") que classes o HermiT
                         atribui a cada recurso além das afirmadas;
  d. report            — checagens de qualidade: regras do ROBOT adequadas a
                         uma ontologia não OBO + consultas SPARQL próprias
                         (scripts/robot_consultas/*.rq);
  e. measure           — métricas (número de classes, axiomas etc.);
  f. vocabulários      — os termos lexinfo:, bibo: e foaf: usados nos dados
                         existem de fato nesses vocabulários? (eles não são
                         importados pela ontologia, de propósito; a conferência
                         é feita em Python, contra cópias locais, sem ROBOT).

Uso (da raiz do projeto):
    python scripts/testes_robot.py                       # ontologia + adiposo
    python scripts/testes_robot.py --verbetes antera arvore
    python scripts/testes_robot.py --so-ontologia
    python scripts/testes_robot.py --todos-verbetes      # inclui não revisados

Na primeira execução, o script baixa o robot.jar e cópias locais das
ontologias importadas (algumas não respondem mais nos IRIs oficiais) para
ferramentas/robot/. Depois disso, roda sem internet. Requer Java 11+.

Os resultados ficam em relatorios/robot/<cenário>/ e o resumo em
relatorios/robot/resumo.md.
"""

import argparse
import csv
import datetime as dt
import re
import shutil
import subprocess
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ----------------------------------------------------------------------------
# Caminhos
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ENTRIES = DATA / "entries"
ONTOLOGIA = DATA / "dicbio-ontology.ttl"
AUXILIARES = [DATA / "sources.ttl", DATA / "authors.ttl"]
VERBETES_REVISADOS = ["adiposo"]  # atualizar conforme a revisão SHACL avança
# Arquivos da pasta entries que não são verbetes individuais
NAO_VERBETES = {"DicionarioBiologia.ttl"}

CONSULTAS = ROOT / "scripts" / "robot_consultas"
FERRAMENTAS = ROOT / "ferramentas" / "robot"
ROBOT_JAR = FERRAMENTAS / "robot.jar"
IMPORTS = FERRAMENTAS / "imports"
CATALOGO = IMPORTS / "catalog-v001.xml"
SAIDA_PADRAO = ROOT / "relatorios" / "robot"

DICBIO = "https://dicbio.fflch.usp.br/"
DICBIO_ONT = DICBIO + "ontology/"

# ----------------------------------------------------------------------------
# Download (só na primeira vez)
# ----------------------------------------------------------------------------
ROBOT_VERSAO = "1.9.11"
ROBOT_URL = f"https://github.com/ontodev/robot/releases/download/v{ROBOT_VERSAO}/robot.jar"

_ONTOLEX_GH = "https://raw.githubusercontent.com/ontolex/ontolex/master/Ontologies/"
# arquivo local -> (URL de origem, IRIs que ele resolve no catálogo)
# Observações:
#  - O servidor do W3C devolve o arquivo do OntoLex para quase todos os IRIs
#    em /ns/lemon/ (inclusive morph e all) quando se pede RDF; por isso os
#    módulos vêm do repositório oficial no GitHub.
#  - lemonEty e NIF não respondem mais nos IRIs oficiais.
#  - PROV: usa-se só o PROV-O (o IRI prov# devolve um pacote com seis
#    importações adicionais).
IMPORTACOES = {
    "ontolex.owl": (_ONTOLEX_GH + "ontolex.owl", ["http://www.w3.org/ns/lemon/ontolex"]),
    "vartrans.owl": (_ONTOLEX_GH + "vartrans.owl", ["http://www.w3.org/ns/lemon/vartrans"]),
    "synsem.owl": (_ONTOLEX_GH + "synsem.owl", ["http://www.w3.org/ns/lemon/synsem"]),
    "decomp.owl": (_ONTOLEX_GH + "decomp.owl", ["http://www.w3.org/ns/lemon/decomp"]),
    "lime.owl": (_ONTOLEX_GH + "lime.owl", ["http://www.w3.org/ns/lemon/lime"]),
    "all.owl": (_ONTOLEX_GH + "all.owl", ["http://www.w3.org/ns/lemon/all"]),
    "morph.ttl": (
        "https://raw.githubusercontent.com/ontolex/morph/master/morph.ttl",
        ["http://www.w3.org/ns/lemon/morph#", "http://www.w3.org/ns/lemon/morph"],
    ),
    "lemonEty.ttl": (
        "https://raw.githubusercontent.com/anasfkhan81/lemonEty/master/lemonEty.ttl",
        ["http://lari-datasets.ilc.cnr.it/lemonEty#"],
    ),
    "skos.rdf": (
        "http://www.w3.org/2004/02/skos/core",
        ["http://www.w3.org/2004/02/skos/core#", "http://www.w3.org/2004/02/skos/core"],
    ),
    "dcterms.ttl": ("http://purl.org/dc/terms/", ["http://purl.org/dc/terms/"]),
    "prov-o.ttl": (
        "http://www.w3.org/ns/prov-o",
        ["http://www.w3.org/ns/prov#", "http://www.w3.org/ns/prov-o#"],
    ),
    "nif-core.ttl": (
        "https://raw.githubusercontent.com/NLP2RDF/ontologies/master/nif-core/nif-core.ttl",
        ["http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#"],
    ),
    "its.rdf": ("http://www.w3.org/2005/11/its/rdf", ["http://www.w3.org/2005/11/its/rdf#"]),
}


# Vocabulários usados só nos DADOS e que a ontologia não importa de propósito
# (importá-los traria construções fora do OWL 2 DL e importações em cascata).
# Não entram no raciocínio: servem só para conferir se os termos usados nos
# dados existem de fato no vocabulário (pega erros de digitação).
# prefixo -> (namespace, arquivo local, URL de origem)
VOCAB_NAO_IMPORTADOS = {
    "lexinfo": (
        "http://www.lexinfo.net/ontology/3.0/lexinfo#",
        "lexinfo.owl",
        "https://raw.githubusercontent.com/ontolex/lexinfo/master/ontology/3.0/lexinfo.owl",
    ),
    "bibo": ("http://purl.org/ontology/bibo/", "bibo.rdf", "http://purl.org/ontology/bibo/"),
    "foaf": ("http://xmlns.com/foaf/0.1/", "foaf.rdf", "http://xmlns.com/foaf/spec/index.rdf"),
}
VOCABULARIOS = FERRAMENTAS / "vocabularios"


def baixar(url, destino, accept=None):
    print(f"  baixando {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "dicbio-testes-robot"})
    if accept:
        req.add_header("Accept", accept)
    with urllib.request.urlopen(req, timeout=120) as resp, open(destino, "wb") as f:
        shutil.copyfileobj(resp, f)


def preparar():
    if shutil.which("java") is None:
        sys.exit("ERRO: Java não encontrado no PATH (o ROBOT precisa de Java 11 ou mais novo).")
    IMPORTS.mkdir(parents=True, exist_ok=True)
    if not ROBOT_JAR.exists():
        print(f"Baixando o ROBOT {ROBOT_VERSAO} (~80 MB)...")
        baixar(ROBOT_URL, ROBOT_JAR)
    faltando = [n for n in IMPORTACOES if not (IMPORTS / n).exists()]
    if faltando:
        print("Baixando cópias locais das ontologias importadas...")
        for nome in faltando:
            url, _ = IMPORTACOES[nome]
            accept = "text/turtle" if nome.endswith(".ttl") else "application/rdf+xml"
            baixar(url, IMPORTS / nome, accept)
    VOCABULARIOS.mkdir(parents=True, exist_ok=True)
    for _, arquivo, url in VOCAB_NAO_IMPORTADOS.values():
        if not (VOCABULARIOS / arquivo).exists():
            print("Baixando vocabulário usado nos dados (não importado)...")
            baixar(url, VOCABULARIOS / arquivo, "application/rdf+xml")
    if not CATALOGO.exists() or faltando:
        linhas = [
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
            '<catalog prefer="public" xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">',
        ]
        for nome, (_, iris) in IMPORTACOES.items():
            linhas += [f'  <uri name="{iri}" uri="{nome}"/>' for iri in iris]
        linhas.append("</catalog>")
        CATALOGO.write_text("\n".join(linhas) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------
# Execução do ROBOT
# ----------------------------------------------------------------------------
def robot(*args, log=None):
    """Roda o ROBOT; devolve (código de saída, saída combinada)."""
    cmd = ["java", "-Xmx4G", "-Dfile.encoding=UTF-8", "-jar", str(ROBOT_JAR), *map(str, args)]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    saida = (proc.stdout or "") + (proc.stderr or "")
    if log is not None:
        with open(log, "a", encoding="utf-8") as f:
            f.write("$ robot " + " ".join(map(str, args)) + "\n" + saida + "\n")
    return proc.returncode, saida


def ultima_mensagem(saida):
    linhas = [l for l in saida.strip().splitlines() if l.strip() and not l.startswith("Use the -")]
    return linhas[-1] if linhas else ""


# ----------------------------------------------------------------------------
# Montagem da entrada
# ----------------------------------------------------------------------------
def juntar(arquivos, destino):
    """Junta os .ttl com rdflib (e não com o ROBOT merge) de propósito.

    Ao carregar RDF, o OWLAPI (usado pelo ROBOT) cria sozinho declarações para
    termos não declarados — por exemplo, transforma lexinfo:partOfSpeech em
    owl:AnnotationProperty. Juntando antes com rdflib, a checagem de perfil
    OWL 2 DL ainda enxerga esses termos como "não declarados".
    """
    g = Graph()
    for a in arquivos:
        g.parse(a, format="turtle")
    # prefixos só para deixar os relatórios mais legíveis
    g.bind("semiotics", "http://www.ontologydesignpatterns.org/cp/owl/semiotics.owl#")
    g.bind("dc", "http://purl.org/dc/elements/1.1/")
    g.bind("dcterms", "http://purl.org/dc/terms/")
    g.bind("bibo", "http://purl.org/ontology/bibo/")
    g.bind("foaf", "http://xmlns.com/foaf/0.1/")
    g.bind("lexinfo", "http://www.lexinfo.net/ontology/3.0/lexinfo#")
    # só o cabeçalho da ontologia DicBio deve sobrar
    for ont in list(g.subjects(RDF.type, OWL.Ontology)):
        if str(ont) != DICBIO_ONT:
            print(f"  aviso: cabeçalho owl:Ontology extra ignorado: {ont}")
    g.serialize(destino, format="turtle")
    return g


# ----------------------------------------------------------------------------
# a. Perfil OWL 2 DL
# ----------------------------------------------------------------------------
RE_IRI = re.compile(r"<(https?://[^>]+)>")
RE_NAO_DECL = re.compile(
    r"^Use of undeclared (class|object property|data property|annotation property|datatype):\s*(<[^>]+>|\S+)"
)
TIPOS_PT = {
    "class": "classe",
    "object property": "propriedade de objeto",
    "data property": "propriedade de dado",
    "annotation property": "propriedade de anotação",
    "datatype": "tipo de dado",
}


# Violações do perfil OWL 2 DL conhecidas e aceitas por decisão de modelagem.
# Cada item: (nome curto, função que reconhece a linha, justificativa).
# Só valem para os casos exatos descritos; um uso novo do mesmo problema em
# outra propriedade continua aparecendo como violação a examinar.
VIOLACOES_ACEITAS = [
    (
        "xsd:gYear em dicbio:attestationDate",
        lambda l: "xsd:gYear" in l and f"<{DICBIO_ONT}attestationDate>" in l,
        "xsd:gYear não faz parte do mapa de tipos de dados do OWL 2, mas é o tipo "
        "semanticamente correto para um ano de atestação e o esperado em dados "
        "abertos. O HermiT do `reason` ignora o tipo; a validade do valor é "
        "conferida pelo SHACL (`sh:datatype xsd:gYear`).",
    ),
]


def vocab_nao_importado(iri):
    """Prefixo do vocabulário não importado a que o IRI pertence (ou None)."""
    for prefixo, (ns, _, _) in VOCAB_NAO_IMPORTADOS.items():
        if iri.startswith(ns):
            return prefixo
    return None


def termo_principal(linha):
    """Primeiro IRI da linha: o termo de que a violação trata."""
    m = RE_IRI.search(linha)
    return m.group(1) if m else ""


def tipo_violacao(linha):
    m = re.match(r"^([^:\[\"<]+)", linha)
    return m.group(1).strip() if m else linha[:60]


def resumir_perfil(arquivo_txt):
    """Separa violações que envolvem termos/dados DicBio das que vêm só das importações."""
    if not arquivo_txt.exists():
        return None
    linhas = arquivo_txt.read_text(encoding="utf-8", errors="replace").splitlines()
    if not linhas or "NOT in profile" not in linhas[0]:
        return {"ok": True}
    dicbio, importacoes = [], []
    for l in linhas[1:]:
        # linhas de violação terminam em "]"; as demais são continuação de
        # literais longos (comentários das ontologias importadas)
        if not l[:1].isupper() or not l.rstrip().endswith("]") or "[" not in l:
            continue
        corpo = re.sub(r"in OntologyID\(.*", "", l)  # tira a atribuição à ontologia
        if DICBIO in corpo:
            dicbio.append(l)
        else:
            importacoes.append(l)
    # violações cujo termo é de vocabulário não importado de propósito: esperadas
    esperadas = [l for l in dicbio if vocab_nao_importado(termo_principal(l))]
    dicbio = [l for l in dicbio if l not in esperadas]
    # violações aceitas por decisão de modelagem
    aceitas = Counter()
    restantes = []
    for l in dicbio:
        nome = next((n for n, reconhece, _ in VIOLACOES_ACEITAS if reconhece(l)), None)
        if nome:
            aceitas[nome] += 1
        else:
            restantes.append(l)
    dicbio = restantes
    nao_declarados = defaultdict(set)
    for l in dicbio:
        m = RE_NAO_DECL.match(l)
        if m:
            nao_declarados[TIPOS_PT[m.group(1)]].add(m.group(2).strip("<>"))
    return {
        "ok": False,
        "dicbio": dicbio,
        "esperadas": esperadas,
        "aceitas": aceitas,
        "importacoes": importacoes,
        "tipos_dicbio": Counter(tipo_violacao(l) for l in dicbio),
        "vocab_esperados": Counter(vocab_nao_importado(termo_principal(l)) for l in esperadas),
        "tipos_importacoes": Counter(tipo_violacao(l) for l in importacoes),
        "nao_declarados": nao_declarados,
    }


def passo_perfil(entrada, grafo, pasta, log, md):
    saida = pasta / "perfil_owl2dl.txt"
    robot("validate-profile", "--catalog", CATALOGO, "-i", entrada, "--profile", "DL", "-o", saida, log=log)
    r = resumir_perfil(saida)
    md.append("### a. Perfil OWL 2 DL (`validate-profile`)\n")
    if r is None:
        md.append("Não foi possível gerar o relatório (ver `robot.log`).\n")
        return False
    if r["ok"]:
        md.append("✓ O conjunto (com importações) está no perfil OWL 2 DL.\n")
        return True
    n_aceitas = sum(r["aceitas"].values())
    total = len(r["dicbio"]) + len(r["esperadas"]) + n_aceitas + len(r["importacoes"])
    md.append(
        f"✗ Fora do perfil OWL 2 DL: {total} violações —\n\n"
        f"- **{len(r['dicbio'])}** envolvem termos ou dados do DicBio (a examinar);\n"
        f"- {n_aceitas} são conhecidas e aceitas por decisão de modelagem (ver abaixo);\n"
        f"- {len(r['esperadas'])} se devem a vocabulários usados nos dados e não importados "
        "de propósito (esperadas; a existência desses termos é conferida na etapa f);\n"
        f"- {len(r['importacoes'])} vêm só das ontologias importadas.\n"
    )
    if r["aceitas"]:
        md.append("Violações aceitas:\n")
        for nome, reconhece, justificativa in VIOLACOES_ACEITAS:
            if r["aceitas"][nome]:
                md.append(f"- **{nome}** ({r['aceitas'][nome]}): {justificativa}")
        md.append("")
    if r["vocab_esperados"]:
        md.append(
            "Esperadas, por vocabulário: "
            + ", ".join(f"`{p}:` {n}" for p, n in sorted(r["vocab_esperados"].items()))
            + ".\n"
        )
    if r["tipos_dicbio"]:
        md.append("Violações que envolvem o DicBio (exceto as esperadas), por tipo:\n")
        for t, n in r["tipos_dicbio"].most_common():
            md.append(f"- {n} × {t}")
        md.append("")
    if r["nao_declarados"]:
        md.append(
            "Termos usados pelo DicBio e não declarados em nenhuma ontologia importada "
            "(o reasoner os trata como anotações ou os ignora):\n"
        )
        for tipo, termos in sorted(r["nao_declarados"].items()):
            nomes = sorted(t if ":" in t and "//" not in t else compactar(grafo, t) for t in termos)
            md.append(f"- {tipo}: " + ", ".join(f"`{t}`" for t in nomes))
        md.append("")
        if any(t.startswith("http://purl.org/dc/terms/") for ts in r["nao_declarados"].values() for t in ts):
            md.append(
                "Dica: o dcterms não é importado; cada propriedade `dcterms:` usada precisa "
                "estar declarada como `owl:AnnotationProperty` em `dicbio-ontology.ttl`.\n"
            )
        proprios = sorted(
            t for ts in r["nao_declarados"].values() for t in ts if t.startswith(DICBIO_ONT)
        )
        if proprios:
            md.append(
                "**Atenção:** termos do próprio namespace `dicbio:` sem declaração na "
                "ontologia (erro de digitação ou termo faltando): "
                + ", ".join(f"`{compactar(grafo, t)}`" for t in proprios) + "\n"
            )
    if r["tipos_importacoes"]:
        md.append("Violações só das importações, por tipo (as 8 mais frequentes):\n")
        for t, n in r["tipos_importacoes"].most_common(8):
            md.append(f"- {n} × {t}")
        md.append("")
    (pasta / "perfil_owl2dl_dicbio.txt").write_text("\n".join(r["dicbio"]) + "\n", encoding="utf-8")
    md.append(f"Lista completa: `perfil_owl2dl.txt`; só as do DicBio: `perfil_owl2dl_dicbio.txt`.\n")
    return False


# ----------------------------------------------------------------------------
# b. Raciocínio (consistência e classes insatisfazíveis)
# ----------------------------------------------------------------------------
def passo_raciocinio(entrada, pasta, log, md):
    md.append("### b. Raciocínio com HermiT (`reason`)\n")
    insat = pasta / "classes_insatisfaziveis.owl"
    cod, saida = robot(
        "reason", "--catalog", CATALOGO, "-i", entrada, "--reasoner", "hermit",
        "--dump-unsatisfiable", insat, "-o", pasta / "raciocinado.owl", log=log,
    )
    if cod == 0:
        md.append("✓ Consistente; nenhuma classe insatisfazível.\n")
        return True
    msg = ultima_mensagem(saida)
    texto = saida.lower()
    if "inconsistent" in texto:
        md.append(f"✗ **Ontologia inconsistente.** ({msg})\n")
        modo, extra = "inconsistency", []
    elif "unsatisfiable" in texto:
        md.append(f"✗ **Há classes insatisfazíveis** (lista em `{insat.name}`). ({msg})\n")
        modo, extra = "unsatisfiability", ["--unsat", "all"]
    else:
        md.append(f"✗ O raciocínio falhou: `{msg}` (detalhes em `robot.log`).\n")
        return False
    expl = pasta / f"explicacao_{modo}.md"
    # O explain usa o HermiT em modo estrito, que recusa tipos de dado fora do
    # mapa do OWL 2 (como xsd:gYear e xsd:date). Nesse caso, tenta o ELK, que
    # é menos expressivo mas costuma bastar para achar a causa.
    for reasoner in ("hermit", "elk"):
        cod, saida = robot(
            "explain", "--catalog", CATALOGO, "-i", entrada, "--reasoner", reasoner,
            "-M", modo, *extra, "--explanation", expl, log=log,
        )
        if expl.exists():
            md.append(f"Explicação (axiomas responsáveis, via {reasoner}): `{expl.name}`.\n")
            break
        if "not part of the OWL 2 datatype map" in saida:
            md.append(
                "O `explain` com HermiT recusou um tipo de dado fora do mapa do OWL 2 "
                "(ver `robot.log`); tentando com o ELK.\n"
            )
    else:
        md.append("Não foi possível gerar a explicação (ver `robot.log`).\n")
    return False


# ----------------------------------------------------------------------------
# c. Tipos inferidos para os recursos dos dados
# ----------------------------------------------------------------------------
CONSULTA_TIPOS = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?recurso ?classe WHERE {
  ?recurso rdf:type ?classe .
  FILTER(isIRI(?recurso) && isIRI(?classe) && STRSTARTS(STR(?recurso), "%s")
         && !STRSTARTS(STR(?recurso), "%s"))
} ORDER BY ?recurso ?classe
""" % (DICBIO, DICBIO_ONT)

IGNORAR_TIPOS = {str(OWL.Thing), str(OWL.NamedIndividual)}


def compactar(g, iri):
    try:
        return g.namespace_manager.normalizeUri(URIRef(iri))
    except Exception:
        return f"<{iri}>"


def passo_tipos_inferidos(entrada, grafo, pasta, log, md):
    md.append("### c. Tipos inferidos pelo HermiT para os recursos dos dados\n")
    inferidos = pasta / "tipos_inferidos.ttl"
    cod, saida = robot(
        "reason", "--catalog", CATALOGO, "-i", entrada, "--reasoner", "hermit",
        "--axiom-generators", "ClassAssertion", "--include-indirect", "true",
        "--create-new-ontology", "true", "-o", inferidos, log=log,
    )
    if cod != 0:
        md.append(f"Não foi possível materializar os tipos: `{ultima_mensagem(saida)}`.\n")
        return
    consulta = pasta / "_tipos.rq"
    consulta.write_text(CONSULTA_TIPOS, encoding="utf-8")
    tsv = pasta / "_tipos.tsv"
    robot("query", "-i", inferidos, "--query", consulta, tsv, log=log)
    consulta.unlink(missing_ok=True)
    if not tsv.exists():
        md.append("A consulta aos tipos inferidos falhou (ver `robot.log`).\n")
        return
    afirmados = {(str(s), str(o)) for s, o in grafo.subject_objects(RDF.type)}
    novos = defaultdict(list)
    with open(tsv, encoding="utf-8") as f:
        for linha in list(csv.reader(f, delimiter="\t"))[1:]:
            if len(linha) < 2:
                continue
            rec, cls = linha[0].strip("<>"), linha[1].strip("<>")
            if cls in IGNORAR_TIPOS or (rec, cls) in afirmados:
                continue
            novos[rec].append(cls)
    tsv.unlink(missing_ok=True)
    if not novos:
        md.append("Nenhum tipo novo além dos afirmados.\n")
        return
    contagem = Counter(c for cs in novos.values() for c in cs)
    md.append(
        f"{sum(contagem.values())} tipos novos em {len(novos)} recursos. "
        "Confira se cada inferência faz sentido — um tipo inesperado costuma "
        "indicar propriedade usada com o sujeito ou o objeto errado.\n"
    )
    md.append("| classe inferida | recursos |\n|---|---|")
    for cls, n in contagem.most_common():
        md.append(f"| `{compactar(grafo, cls)}` | {n} |")
    md.append("")
    with open(pasta / "tipos_inferidos.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["recurso", "classe_inferida"])
        for rec in sorted(novos):
            for cls in sorted(novos[rec]):
                w.writerow([compactar(grafo, rec), compactar(grafo, cls)])
    md.append("Lista por recurso: `tipos_inferidos.tsv`.\n")


# ----------------------------------------------------------------------------
# d. Relatório de qualidade
# ----------------------------------------------------------------------------
# Regras do ROBOT mantidas. As regras pensadas para ontologias OBO (IAO:0000115
# como definição, multiple_labels que ignora a língua, missing_superclass etc.)
# ficam de fora; as consultas próprias cobrem rótulos e definições bilíngues.
REGRAS_ROBOT = [
    ("ERROR", "equivalent_pair"),
    ("ERROR", "missing_ontology_title"),
    ("ERROR", "missing_ontology_description"),
    ("WARN", "missing_ontology_license"),
    ("WARN", "duplicate_label"),
    ("WARN", "label_whitespace"),
    ("WARN", "annotation_whitespace"),
    ("WARN", "multiple_equivalent_classes"),
    ("WARN", "deprecated_class_reference"),
]
NIVEL_CONSULTA = {"rotulo_repetido_mesma_lingua": "ERROR"}  # demais: WARN


def passo_relatorio(entrada, pasta, log, md):
    md.append("### d. Relatório de qualidade (`report`)\n")
    perfil = pasta / "_perfil_report.txt"
    linhas = [f"{n}\t{r}" for n, r in REGRAS_ROBOT]
    for rq in sorted(CONSULTAS.glob("*.rq")):
        linhas.append(f"{NIVEL_CONSULTA.get(rq.stem, 'WARN')}\t{rq.resolve().as_uri()}")
    perfil.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    # o report roda sobre a ontologia já mesclada com as importações, para que
    # as consultas enxerguem a hierarquia de classes do OntoLex, PROV etc.
    mesclado = pasta / "mesclado.owl"
    cod, saida = robot(
        "merge", "--catalog", CATALOGO, "-i", entrada,
        "--collapse-import-closure", "true", "-o", mesclado, log=log,
    )
    if cod != 0:
        md.append(f"Falha ao mesclar as importações: `{ultima_mensagem(saida)}`.\n")
        return False
    relatorio = pasta / "relatorio_qualidade.tsv"
    robot(
        "report", "-i", mesclado, "--profile", perfil, "--base-iri", DICBIO,
        "--fail-on", "none", "-o", relatorio, log=log,
    )
    perfil.unlink(missing_ok=True)
    if not relatorio.exists():
        md.append("O relatório não foi gerado (ver `robot.log`).\n")
        return False
    with open(relatorio, encoding="utf-8") as f:
        linhas = list(csv.reader(f, delimiter="\t"))[1:]
    if not linhas:
        md.append("✓ Nenhum problema encontrado.\n")
        return True
    por_regra = Counter((l[0], l[1]) for l in linhas if len(l) > 1)
    md.append("| nível | regra | ocorrências |\n|---|---|---|")
    for (nivel, regra), n in sorted(por_regra.items(), key=lambda x: (x[0][0] != "ERROR", x[0][1])):
        md.append(f"| {nivel} | {regra} | {n} |")
    md.append(f"\nDetalhes: `{relatorio.name}`. As consultas próprias estão em `scripts/robot_consultas/`.\n")
    return not any(n == "ERROR" for n, _ in por_regra)


# ----------------------------------------------------------------------------
# e. Métricas
# ----------------------------------------------------------------------------
METRICAS_DESTAQUE = [
    "axiom_count", "logical_axiom_count", "class_count", "obj_prop_count",
    "dataprop_count", "annotation_prop_count", "individual_count",
    "axiom_count_incl", "class_count_incl", "expressivity",
]


def passo_metricas(entrada, pasta, log, md):
    md.append("### e. Métricas (`measure`)\n")
    saida = pasta / "metricas.tsv"
    robot(
        "measure", "--catalog", CATALOGO, "-i", entrada, "--metrics", "extended",
        "--format", "tsv", "-o", saida, log=log,
    )
    if not saida.exists():
        md.append("Não foi possível calcular as métricas (ver `robot.log`).\n")
        return
    valores = {}
    with open(saida, encoding="utf-8") as f:
        for l in csv.reader(f, delimiter="\t"):
            if len(l) >= 2:
                valores.setdefault(l[0], l[1])
    md.append("| métrica | valor |\n|---|---|")
    for m in METRICAS_DESTAQUE:
        if m in valores:
            md.append(f"| {m} | {valores[m]} |")
    md.append(f"\nTodas as métricas: `{saida.name}` (sufixo `_incl` = com importações).\n")


# ----------------------------------------------------------------------------
# f. Termos de vocabulários não importados (lexinfo, bibo, foaf)
# ----------------------------------------------------------------------------
def termos_usados(grafo, ns):
    """IRIs do namespace usados como predicado ou objeto, com contagem e um exemplo de sujeito."""
    usos = defaultdict(list)
    for s, p, o in grafo:
        for termo in (p, o):
            if isinstance(termo, URIRef) and str(termo).startswith(ns):
                usos[str(termo)].append(s)
    return usos


def passo_vocabularios(grafo, pasta, md):
    md.append("### f. Termos de vocabulários usados nos dados e não importados\n")
    inexistentes = []
    resumo = []
    for prefixo, (ns, arquivo, _) in VOCAB_NAO_IMPORTADOS.items():
        usos = termos_usados(grafo, ns)
        if not usos:
            continue
        vocab = Graph()
        vocab.parse(VOCABULARIOS / arquivo)
        definidos = set(map(str, vocab.subjects()))
        faltam = sorted(t for t in usos if t not in definidos)
        resumo.append(f"`{prefixo}:` {len(usos)} termo(s) usado(s), {len(faltam)} inexistente(s)")
        for t in faltam:
            inexistentes.append((compactar(grafo, t), len(usos[t]), compactar(grafo, str(usos[t][0]))))
    if not resumo:
        md.append("Nenhum termo desses vocabulários nos arquivos testados.\n")
        return True
    md.append("; ".join(resumo) + ".\n")
    if not inexistentes:
        md.append("✓ Todos os termos usados existem nos vocabulários.\n")
        return True
    md.append(
        "✗ Termos que **não existem** no vocabulário (provável erro de digitação):\n\n"
        "| termo | usos | exemplo de recurso |\n|---|---|---|"
    )
    for termo, n, exemplo in inexistentes:
        md.append(f"| `{termo}` | {n} | `{exemplo}` |")
    md.append("")
    with open(pasta / "termos_inexistentes.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["termo", "usos", "exemplo_de_recurso"])
        w.writerows(inexistentes)
    return False


# ----------------------------------------------------------------------------
# Cenários
# ----------------------------------------------------------------------------
def rodar_cenario(nome, arquivos, saida_base, md, com_tipos):
    pasta = saida_base / nome
    pasta.mkdir(parents=True, exist_ok=True)
    # apaga os arquivos da execução anterior (sem remover a pasta, que o
    # OneDrive às vezes mantém travada)
    for antigo in pasta.iterdir():
        try:
            if antigo.is_file():
                antigo.unlink()
        except OSError as e:
            print(f"  aviso: não foi possível apagar {antigo.name}: {e}")
    log = pasta / "robot.log"
    print(f"\n=== Cenário: {nome} ({len(arquivos)} arquivo(s)) ===")
    md.append(f"## Cenário: {nome}\n")
    md.append("Arquivos: " + ", ".join(f"`{a.relative_to(ROOT).as_posix()}`" for a in arquivos) + "\n")

    entrada = pasta / "entrada.ttl"
    grafo = juntar(arquivos, entrada)

    resultados = {}
    print("  a. perfil OWL 2 DL...")
    resultados["perfil DL"] = passo_perfil(entrada, grafo, pasta, log, md)
    print("  b. raciocínio (HermiT)...")
    resultados["consistência"] = passo_raciocinio(entrada, pasta, log, md)
    if com_tipos and resultados["consistência"]:
        print("  c. tipos inferidos...")
        passo_tipos_inferidos(entrada, grafo, pasta, log, md)
    print("  d. relatório de qualidade...")
    resultados["relatório"] = passo_relatorio(entrada, pasta, log, md)
    print("  e. métricas...")
    passo_metricas(entrada, pasta, log, md)
    print("  f. termos de vocabulários não importados...")
    resultados["vocabulários"] = passo_vocabularios(grafo, pasta, md)
    for k, ok in resultados.items():
        print(f"    {'✓' if ok else '✗'} {k}")
    return resultados


def escolher_verbetes(args):
    if args.todos_verbetes:
        return sorted(p for p in ENTRIES.glob("*.ttl") if p.name not in NAO_VERBETES)
    nomes = args.verbetes or VERBETES_REVISADOS
    arquivos = []
    for n in nomes:
        p = ENTRIES / (n if n.endswith(".ttl") else n + ".ttl")
        if not p.exists():
            sys.exit(f"ERRO: verbete não encontrado: {p}")
        arquivos.append(p)
    return arquivos


def main():
    ap = argparse.ArgumentParser(description="Testes da ontologia DicBio com o ROBOT.")
    ap.add_argument("--verbetes", nargs="+", metavar="NOME",
                    help=f"verbetes de data/entries a incluir (padrão: {', '.join(VERBETES_REVISADOS)})")
    ap.add_argument("--todos-verbetes", action="store_true",
                    help="inclui todos os verbetes da pasta (inclusive os ainda não revisados)")
    ap.add_argument("--so-ontologia", action="store_true", help="roda só o cenário da ontologia")
    ap.add_argument("--saida", type=Path, default=SAIDA_PADRAO, help="pasta dos relatórios")
    args = ap.parse_args()

    preparar()
    args.saida.mkdir(parents=True, exist_ok=True)
    _, versao = robot("--version")

    md = [
        "# Testes da ontologia DicBio com o ROBOT\n",
        f"- Data: {dt.datetime.now():%Y-%m-%d %H:%M}",
        f"- {versao.strip()}; reasoner HermiT (embutido no ROBOT)",
        "- Importações resolvidas por cópias locais (`ferramentas/robot/imports/`)\n",
    ]
    geral = {}
    geral["ontologia"] = rodar_cenario("ontologia", [ONTOLOGIA], args.saida, md, com_tipos=False)

    if not args.so_ontologia:
        verbetes = escolher_verbetes(args)
        nao_revisados = [v.stem for v in verbetes if v.stem not in VERBETES_REVISADOS]
        if nao_revisados:
            aviso = (
                f"**Atenção:** {len(nao_revisados)} verbete(s) incluído(s) ainda não foram "
                "revisados com o SHACL; problemas neles podem ser de dados, não da ontologia."
            )
            print("\n" + aviso.replace("**", ""))
            md.append(aviso + "\n")
        aux = [a for a in AUXILIARES if a.exists()]
        geral["dados"] = rodar_cenario("dados", [ONTOLOGIA, *aux, *verbetes], args.saida, md, com_tipos=True)

    md.insert(4, "## Resultado geral\n")
    tabela = [
        "| cenário | perfil OWL 2 DL | consistência | relatório (sem ERROR) | termos lexinfo/bibo/foaf |",
        "|---|---|---|---|---|",
    ]
    colunas = ("perfil DL", "consistência", "relatório", "vocabulários")
    for cen, r in geral.items():
        tabela.append(f"| {cen} | " + " | ".join("✓" if r[k] else "✗" for k in colunas) + " |")
    md[5:5] = tabela + [""]

    resumo = args.saida / "resumo.md"
    resumo.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nResumo: {resumo}")
    sys.exit(0 if all(all(r.values()) for r in geral.values()) else 1)


if __name__ == "__main__":
    main()
