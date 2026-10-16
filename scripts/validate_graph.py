# Código gerado pelo ChatGPT e complementado pelo Claude para validar o grafo RDF usando SHACL
"""Valida arquivos TTL do DicBio contra as shapes SHACL e mostra um relatório curto.

Uso:
    python scripts/validate_graph.py data/entries/auricula.ttl
    python scripts/validate_graph.py data/entries            # todos os .ttl da pasta
    python scripts/validate_graph.py data/entries/a*.ttl     # vários arquivos

Opções:
    --erros   mostra só os erros (esconde os avisos)
    --tudo    mostra também os erros "derivados" (ver nota abaixo)

Erros "derivados": o pySHACL, ao validar uma acepção ou hipótese, repete os erros
de tudo que está ligado a ela (cadeia etimológica). Esses ecos são escondidos por
padrão, porque somem sozinhos quando a causa real é corrigida.
"""

import argparse
import re
import sys
import warnings
from pathlib import Path
from pyshacl import validate
from pyshacl.errors import ShapeRecursionWarning
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

# O ciclo etimologia <-> étimo é intencional; o aviso de recursão é só ruído.
warnings.filterwarnings("ignore", category=ShapeRecursionWarning)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SH = Namespace("http://www.w3.org/ns/shacl#")
ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
DICBIO = Namespace("https://dicbio.fflch.usp.br/ontology/")

# Pastas e arquivos (relativos à raiz do projeto: a pasta acima de scripts/)
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SHACL_FILE = DATA_DIR / "dicbio-shacl-shapes.ttl"
ONTOLOGY_FILE = DATA_DIR / "dicbio-ontology.ttl"
# Triplas auxiliares: necessárias para a validação, mas não validadas diretamente
AUX_FILES = [DATA_DIR / "sources.ttl", DATA_DIR / "authors.ttl"]


# ----------------------------------------------------------------------------
# Carregamento
# ----------------------------------------------------------------------------
def parse_into(graph, path):
    graph.parse(str(path), format="turtle")


def load_base():
    """Ontologia + fontes + autores, carregados uma vez só."""
    base = Graph()
    parse_into(base, ONTOLOGY_FILE)
    for aux in AUX_FILES:
        if aux.exists():
            parse_into(base, aux)
        else:
            print(f"AVISO: arquivo auxiliar não encontrado: {aux}")
    shapes = Graph()
    parse_into(shapes, SHACL_FILE)
    return base, shapes


# ----------------------------------------------------------------------------
# Leitura do relatório
# ----------------------------------------------------------------------------
def short(graph, term):
    """IRI -> forma com prefixo (dbres:entry_x); literais entre aspas."""
    if term is None:
        return ""
    if isinstance(term, BNode):
        inv = graph.value(term, SH.inversePath)
        if inv is not None:
            return "^" + short(graph, inv)
        return "(caminho)"
    if isinstance(term, Literal):
        return f'"{term}"'
    return graph.namespace_manager.normalizeUri(term)


def read_result(rg, data, node):
    comp = rg.value(node, SH.sourceConstraintComponent)
    return {
        "severity": "erro" if rg.value(node, SH.resultSeverity) == SH.Violation else "aviso",
        "component": str(comp).split("#")[-1] if comp else "",
        "focus": rg.value(node, SH.focusNode),
        "path": rg.value(node, SH.resultPath),
        "value": rg.value(node, SH.value),
        "message": str(rg.value(node, SH.resultMessage) or ""),
        "details": list(rg.objects(node, SH.detail)),
    }


def flatten(rg, data, node, seen=None):
    """Troca resultados-'embrulho' (sh:node) pelos erros detalhados dentro deles."""
    seen = seen or set()
    if node in seen:
        return []
    seen.add(node)
    r = read_result(rg, data, node)
    if r["details"]:
        out = []
        for d in r["details"]:
            out += flatten(rg, data, d, seen)
        return out
    return [r]


def translate(data, r):
    """Mensagens genéricas do pySHACL (em inglês) -> português curto.

    Mensagens escritas nas shapes (sh:message) são mantidas; só trocamos os
    textos padrão do pySHACL. IRIs longos dentro da mensagem viram prefixados.
    """
    msg, comp = r["message"], r["component"]
    path = short(data, r["path"]) if r["path"] else ""
    value = short(data, r["value"]) if r["value"] is not None else ""
    out = msg
    if comp == "PatternConstraintComponent" and msg.startswith("Value does not match pattern"):
        m = re.search(r"pattern '(.+)'", msg)
        padrao = m.group(1) if m else "?"
        padrao = re.sub(r"^\^", "", padrao).replace("\\.", ".")
        if r["value"] is not None and r["value"] != r["focus"]:
            out = f"{path}: o valor {value} não segue o padrão {padrao}"
        else:
            out = f"o identificador não segue a convenção de nome (esperado começar por {padrao})"
    elif comp == "ClassConstraintComponent" and msg.startswith("Value does not have class"):
        classe = msg.rsplit(" ", 1)[-1]
        out = f"{path} aponta para {value}, que não é do tipo {classe}"
    elif comp == "MinCountConstraintComponent" and msg.startswith("Less than"):
        out = f"falta a propriedade {path}"
    elif comp == "MaxCountConstraintComponent" and msg.startswith("More than"):
        out = f"{path} tem valores demais (máximo permitido: {msg.split()[2]})"
    elif comp == "DatatypeConstraintComponent" and msg.startswith("Value is not Literal"):
        out = f"{path}: o valor {value} não tem o tipo de dado esperado ({msg})"
    elif comp == "InConstraintComponent" and msg.startswith("Value is not in"):
        out = f"{path}: o valor {value} não está entre os valores permitidos"
    # IRIs completos dentro da mensagem -> forma com prefixo
    return re.sub(
        r"https?://[^\s,;)]+",
        lambda m: short(data, URIRef(m.group(0))),
        out,
    )


def is_derived(data, r):
    """Eco de outro erro: um sh:or/sh:node cujo valor já é validado por conta própria."""
    if r["component"] not in ("OrConstraintComponent", "NodeConstraintComponent"):
        return False
    v = r["value"]
    if v is None:
        return False
    tipos = set(data.objects(v, RDF.type))
    return bool(tipos & {ONTOLEX.LexicalSense, DICBIO.SemanticEtymon})


def collect(rg, data):
    results = []
    for top in rg.objects(None, SH.result):
        results += flatten(rg, data, top)
    # remove duplicatas exatas
    unicos, vistos = [], set()
    for r in results:
        chave = (r["severity"], r["focus"], r["path"], r["value"], translate(data, r))
        if chave not in vistos:
            vistos.add(chave)
            unicos.append(r)
    return unicos


# ----------------------------------------------------------------------------
# Execução
# ----------------------------------------------------------------------------
def validate_file(data_file, base, shapes, show_all, only_errors):
    data = Graph()
    for prefix, ns in base.namespaces():
        data.bind(prefix, ns, override=True)
    data += base
    parse_into(data, data_file)

    conforms, rg, _ = validate(
        data,
        shacl_graph=shapes,
        inference="none",
        advanced=True,
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
    )

    results = collect(rg, data)
    derived = [r for r in results if is_derived(data, r)]
    shown = results if show_all else [r for r in results if r not in derived]
    only_derived = (
        not show_all
        and derived
        and not any(r["severity"] == "erro" for r in shown)
    )
    if only_derived:
        # Não há erro "de verdade" a mostrar, mas o pySHACL reprovou o grafo:
        # é um aviso (ex.: argumentação faltando) escalado por um sh:node.
        shown = results
    if only_errors:
        shown = [r for r in shown if r["severity"] == "erro"]

    n_err = sum(1 for r in shown if r["severity"] == "erro")
    n_warn = sum(1 for r in shown if r["severity"] == "aviso")
    ok = not any(r["severity"] == "erro" for r in results)

    print("=" * 70)
    status = "✓ OK" if ok else "✗ COM ERROS"
    print(f"{data_file}  —  {status}  ({n_err} erro(s), {n_warn} aviso(s))")
    print("=" * 70)

    por_entidade = {}
    for r in shown:
        por_entidade.setdefault(short(data, r["focus"]), []).append(r)
    for entidade in sorted(por_entidade):
        print(f"\n{entidade}")
        for r in sorted(por_entidade[entidade], key=lambda x: (x["severity"] != "erro", x["message"])):
            marca = "ERRO " if r["severity"] == "erro" else "aviso"
            print(f"  [{marca}] {translate(data, r)}")

    if only_derived:
        print(
            "\nNota: só há erros derivados. Eles vêm de AVISOS em itens ligados "
            "(por exemplo, uma hipótese etimológica sem argumentação); "
            "corrigir os avisos acima resolve."
        )
    elif derived and not show_all:
        print(f"\n({len(derived)} erro(s) derivado(s) escondido(s); use --tudo para vê-los)")
    print()
    return ok


def find_files(args):
    files = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            files += sorted(p.rglob("*.ttl"))
        elif p.exists():
            files.append(p)
        else:
            print(f"Arquivo não encontrado: {p}")
    return files


def main():
    ap = argparse.ArgumentParser(description="Valida verbetes DicBio (SHACL).")
    ap.add_argument("caminhos", nargs="+", help="arquivos .ttl ou pastas")
    ap.add_argument("--erros", action="store_true", help="mostrar só erros")
    ap.add_argument("--tudo", action="store_true", help="mostrar também erros derivados")
    args = ap.parse_args()

    files = find_files(args.caminhos)
    if not files:
        sys.exit(1)

    base, shapes = load_base()
    resultados = {f: validate_file(f, base, shapes, args.tudo, args.erros) for f in files}

    if len(files) > 1:
        print("RESUMO")
        for f, ok in resultados.items():
            print(f"  {'✓' if ok else '✗'} {f}")
    sys.exit(0 if all(resultados.values()) else 1)


if __name__ == "__main__":
    main()