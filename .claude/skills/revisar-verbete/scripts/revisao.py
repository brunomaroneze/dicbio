"""Apoio à skill revisar-verbete: lote, contexto, nomes livres e progresso.

Rodar da raiz do projeto:

    python .claude/skills/revisar-verbete/scripts/revisao.py proximos 10
    python .claude/skills/revisar-verbete/scripts/revisao.py contexto caule
    python .claude/skills/revisar-verbete/scripts/revisao.py nome-livre entry_caulis form_caulis
    python .claude/skills/revisar-verbete/scripts/revisao.py validar caule
    python .claude/skills/revisar-verbete/scripts/revisao.py marcar caule revisado-skill "obs curta"
    python .claude/skills/revisar-verbete/scripts/revisao.py resumo

Progresso em relatorios/revisao_verbetes.csv (verbete;status;data;observacoes).
Status: pendente → revisado-skill → conferido (este último, só a pessoa marca).
"""

import csv
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[4]
ENTRIES = ROOT / "data" / "entries"
SOURCES = ROOT / "data" / "sources.ttl"
PROGRESSO = ROOT / "relatorios" / "revisao_verbetes.csv"
DBRES = "https://dicbio.fflch.usp.br/recurso/"
DBSRC = "https://dicbio.fflch.usp.br/fontes/"
GLOTTO = "https://glottolog.org/resource/languoid/id/"
ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
DCT = Namespace("http://purl.org/dc/terms/")
DICBIO = Namespace("https://dicbio.fflch.usp.br/ontology/")

sys.path.insert(0, str(ROOT / "scripts"))


# ----------------------------------------------------------------------------
# progresso
# ----------------------------------------------------------------------------
def ler_progresso():
    verbetes = sorted(f.stem for f in ENTRIES.glob("*.ttl"))
    dados = {v: {"verbete": v, "status": "pendente", "data": "", "observacoes": ""} for v in verbetes}
    if PROGRESSO.exists():
        with open(PROGRESSO, encoding="utf-8-sig", newline="") as fh:
            for l in csv.DictReader(fh, delimiter=";"):
                if l["verbete"] in dados:
                    dados[l["verbete"]] = l
    return dados


def gravar_progresso(dados):
    PROGRESSO.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESSO, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["verbete", "status", "data", "observacoes"], delimiter=";")
        w.writeheader()
        w.writerows(dados[v] for v in sorted(dados))


def cmd_proximos(n="10"):
    dados = ler_progresso()
    pend = [v for v, l in sorted(dados.items()) if l["status"] == "pendente"]
    print(" ".join(pend[: int(n)]))
    print(f"({len(pend)} pendentes no total)", file=sys.stderr)


def cmd_marcar(verbete, status, *obs):
    dados = ler_progresso()
    if verbete not in dados:
        sys.exit(f"verbete desconhecido: {verbete}")
    dados[verbete].update(status=status, data=dt.date.today().isoformat(), observacoes=" ".join(obs))
    gravar_progresso(dados)
    print(f"{verbete}: {status}")


def cmd_resumo():
    dados = ler_progresso()
    cont = {}
    for l in dados.values():
        cont[l["status"]] = cont.get(l["status"], 0) + 1
    for s, n in sorted(cont.items()):
        print(f"{n:4d}  {s}")


# ----------------------------------------------------------------------------
# nomes
# ----------------------------------------------------------------------------
def cmd_nome_livre(*nomes):
    usados = {}
    for f in list(ENTRIES.glob("*.ttl")) + [SOURCES]:
        try:
            g = Graph().parse(f)
        except Exception as e:  # arquivo quebrado não pode esconder colisões
            print(f"!! {f.name} não pôde ser lido: {e}")
            continue
        for s in set(g.subjects()) | set(o for o in g.objects() if isinstance(o, URIRef)):
            if isinstance(s, URIRef):
                usados.setdefault(str(s), set()).add(f.name)
    for n in nomes:
        n = n.split(":", 1)[-1]
        alvos = [base + n for base in (DBRES, DBSRC)]
        achou = {arq for a in alvos for arq in usados.get(a, ())}
        print(f"{n}: " + (f"JÁ USADO em {', '.join(sorted(achou))}" if achou else "livre"))


# ----------------------------------------------------------------------------
# contexto
# ----------------------------------------------------------------------------
def cmd_validar(verbete):
    arq = ENTRIES / f"{verbete}.ttl"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_graph.py"), str(arq)],
                       capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    # tira os avisos de colaboradores (dbauth:/ORCID), que não são deste verbete
    linhas = [l for l in r.stdout.splitlines() if "ORCID" not in l and not l.startswith("dbauth:")]
    saida = re.sub(r"\n{3,}", "\n\n", "\n".join(linhas))
    print(saida)
    if r.returncode not in (0, 1):
        print(r.stderr)


def ls_contexto(lemas):
    try:
        from datas_atestacoes import LS_ARQ, indexar_ls, analisar_ls, norm, ALIASES
    except Exception as e:
        print(f"(L&S indisponível: {e})")
        return
    if not LS_ARQ.exists():
        print("(L&S não baixado: rode scripts/datas_atestacoes.py uma vez)")
        return
    chaves = {ALIASES.get(norm(l), norm(l)): l for l in lemas}
    idx = indexar_ls(set(chaves))
    for k, lema in chaves.items():
        if k not in idx:
            print(f"  {lema}: não está no L&S")
            continue
        for chave, corpo in idx[k]:
            cab = re.sub(r"<[^>]+>", "", re.split(r"<sense ", corpo, maxsplit=1)[0])
            cab = " ".join(cab.split())[:220]
            print(f"  {lema} [{chave}] {cab}")
        _, por_acepcao = analisar_ls(idx[k])
        for parte in por_acepcao.split(" | "):
            if parte:
                print(f"      {parte}")


def cmd_contexto(verbete):
    arq = ENTRIES / f"{verbete}.ttl"
    texto = arq.read_text(encoding="utf-8")
    g = Graph().parse(arq)
    print(f"=== {arq.relative_to(ROOT)} ===\n")

    print("--- Comentários REVISAR / NOTA ---")
    for i, l in enumerate(texto.splitlines(), 1):
        if re.search(r"#\s*(REVISAR|NOTA)", l):
            print(f"  {i:4d}: {l.strip()}")

    print("\n--- Hipóteses (argumentação na íntegra) ---")
    for h in sorted(g.subjects(RDF.type, URIRef("http://lari-datasets.ilc.cnr.it/lemonEty#Etymology"))):
        print(f"\n  {g.namespace_manager.normalizeUri(h)}")
        for p, o in sorted(g.predicate_objects(h)):
            if p == DICBIO.etymologicalArgumentation:
                continue
            print(f"    {g.namespace_manager.normalizeUri(p)} {o.n3(g.namespace_manager)}")
        for arg in g.objects(h, DICBIO.etymologicalArgumentation):
            print(f"    argumentação: {arg}")

    print("\n--- Fontes existentes em sources.ttl ---")
    fontes = Graph().parse(SOURCES)
    for s in sorted(set(fontes.subjects())):
        if str(s).startswith(DBSRC):
            t = fontes.value(s, DCT.title) or fontes.value(s, URIRef("http://xmlns.com/foaf/0.1/name")) or ""
            d = fontes.value(s, DCT.issued) or ""
            print(f"  dbsrc:{str(s)[len(DBSRC):]:40s} {t} {d}")

    lemas = []
    for e in g.subjects(RDF.type, ONTOLEX.LexicalEntry):
        if str(g.value(e, DCT.language)) == GLOTTO + "lati1261":
            for f in g.objects(e, ONTOLEX.canonicalForm):
                lemas += [str(w) for w in g.objects(f, ONTOLEX.writtenRep)]
    if lemas:
        print("\n--- Lewis & Short (étimos latinos: cabeçalho e acepções com autores) ---")
        ls_contexto(lemas)

    print("\n--- SHACL ---")
    cmd_validar(verbete)


COMANDOS = {"proximos": cmd_proximos, "contexto": cmd_contexto, "nome-livre": cmd_nome_livre,
            "validar": cmd_validar, "marcar": cmd_marcar, "resumo": cmd_resumo}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDOS:
        sys.exit(__doc__)
    COMANDOS[sys.argv[1]](*sys.argv[2:])
