"""Gera uma planilha com as atestações sem data e sugestões de data.

Para cada dicbio:Attestation sem dicbio:attestationDate, a sugestão vem de:

  1. ano escrito na própria fonte, quando ela está em texto livre
     ("Systema Naturae" de Lineu, de 1748 → 1748);
  2. dcterms:issued da fonte em sources.ttl, quando a fonte é uma obra
     primária (não bibo:ReferenceSource) — ex.: Vandelli, 1788;
  3. para fontes secundárias (OLD, Gaffiot, Houaiss...): o autor antigo
     mais antigo citado no verbete do Lewis & Short (Perseus, TEI) e/ou do
     Gaffiot (Digital Gaffiot, HTML, só A–F), datado por uma tabela
     aproximada de autores (AUTORES, abaixo).

A data por autor é aproximada (floruit / obra principal): serve para
situar a atestação ("latim da Antiguidade", séc. I d.C. etc.), não como
datação filológica. Anos a.C. são negativos (xsd:gYear "-0160").

A planilha (CSV com ';', UTF-8 com BOM, abre direto no Excel) tem a coluna
"ano" vazia, para ser preenchida/confirmada.

Uso:
    python scripts/datas_atestacoes.py
    python scripts/datas_atestacoes.py --saida relatorios/datas.csv
"""

import argparse
import csv
import html
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "data" / "entries"
SOURCES = ROOT / "data" / "sources.ttl"
LEXICOS = ROOT / "ferramentas" / "lexicos"
LS_ARQ = LEXICOS / "lewisandshort" / "lat.ls.perseus-eng2.xml"
LS_URL = ("https://raw.githubusercontent.com/PerseusDL/lexica/master/"
          "CTS_XML_TEI/perseus/pdllex/lat/ls/lat.ls.perseus-eng2.xml")
GAFFIOT_DIRS = [LEXICOS / "gaffiot", ROOT / "data" / "ferramentas" / "lexicos" / "gaffiot"]
SAIDA_PADRAO = ROOT / "relatorios" / "datas_atestacoes.csv"

DICBIO = Namespace("https://dicbio.fflch.usp.br/ontology/")
DCT = Namespace("http://purl.org/dc/terms/")
ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
BIBO = Namespace("http://purl.org/ontology/bibo/")

# ----------------------------------------------------------------------------
# Tabela aproximada de datas por autor (ano; negativo = a.C.).
# Chave: abreviatura como aparece no L&S ("LS") ou no Gaffiot ("G"); as
# abreviaturas iguais nos dois ficam em "*". Atenção: "Cat." é Catulo no
# L&S e Catão no Gaffiot.
# ----------------------------------------------------------------------------
AUTORES = {
    "*": {
        "Plaut.": ("Plauto", -200), "Ter.": ("Terêncio", -160), "Cato": ("Catão", -160),
        "Caecil.": ("Cecílio Estácio", -180), "Lucil.": ("Lucílio", -130),
        "Varr.": ("Varrão", -40), "Cic.": ("Cícero", -55), "Caes.": ("César", -50),
        "Lucr.": ("Lucrécio", -55), "Sall.": ("Salústio", -40), "Nep.": ("Cornélio Nepos", -35),
        "Verg.": ("Virgílio", -25), "Hor.": ("Horácio", -20), "Tib.": ("Tibulo", -20),
        "Prop.": ("Propércio", -20), "Vitr.": ("Vitrúvio", -20), "Liv.": ("Tito Lívio", 1),
        "Ov.": ("Ovídio", 5), "Auct. Priap.": ("Priapeia", 10), "Phaedr.": ("Fedro", 30),
        "Cels.": ("Celso", 30), "Val. Max.": ("Valério Máximo", 30), "Scrib.": ("Escribônio Largo", 47),
        "Sen.": ("Sêneca", 50), "Curt.": ("Quinto Cúrcio", 50), "Col.": ("Columela", 60),
        "Pers.": ("Pérsio", 60), "Petr.": ("Petrônio", 60), "Auct. Aetn.": ("Aetna", 60),
        "Luc.": ("Lucano", 62), "Plin.": ("Plínio, o Velho", 77), "Val. Fl.": ("Valério Flaco", 80),
        "Mart.": ("Marcial", 90), "Quint.": ("Quintiliano", 90), "Stat.": ("Estácio", 90),
        "Sil.": ("Sílio Itálico", 90), "Plin. Ep.": ("Plínio, o Jovem", 100), "Tac.": ("Tácito", 100),
        "Front.": ("Frontino/Frontão", 100), "Hyg.": ("Higino", 100), "Juv.": ("Juvenal", 120),
        "Suet.": ("Suetônio", 120), "Gai.": ("Gaio", 160), "App.": ("Apuleio", 160),
        "Apul.": ("Apuleio", 160), "Gell.": ("Aulo Gélio", 170), "Fest.": ("Festo", 180),
        "P.Fest.": ("Festo (epítome de Paulo Diácono)", 180), "Just.": ("Justino", 200),
        "Tert.": ("Tertuliano", 200), "Ser. Samm.": ("Sereno Samônico", 210), "Sol.": ("Solino", 250),
        "Flor.": ("Floro", 120), "Arn.": ("Arnóbio", 300), "Jul. Val.": ("Júlio Valério", 330),
        "Aur. Vict.": ("Aurélio Vítor", 360), "Aus.": ("Ausônio", 370), "Ambros.": ("Ambrósio", 380),
        "Spart.": ("Esparciano (Hist. Aug.)", 390), "Amm.": ("Amiano Marcelino", 390),
        "Veg.": ("Vegécio", 390), "Hier.": ("Jerônimo", 390), "Vulg.": ("Vulgata", 400),
        "Aug.": ("Agostinho", 400), "Claud.": ("Claudiano", 400), "Prud.": ("Prudêncio", 400),
        "Paul. Nol.": ("Paulino de Nola", 400), "Non.": ("Nônio Marcelo", 400), "Serv.": ("Sérvio", 400),
        "Pall.": ("Paládio", 400), "Apic.": ("Apício", 400), "Rhem. Fan.": ("Remio Fânio", 400),
        "Macr.": ("Macróbio", 430), "Cael. Aur.": ("Célio Aureliano", 450), "C.-Aur.": ("Célio Aureliano", 450),
        "Sid.": ("Sidônio Apolinário", 470), "Prisc.": ("Prisciano", 500), "Fulg.": ("Fulgêncio", 500),
        "Cod. Just.": ("Código de Justiniano", 529), "Cassiod.": ("Cassiodoro", 540), "Isid.": ("Isidoro de Sevilha", 620),
    },
    "LS": {"Cat.": ("Catulo", -55)},
    "G": {
        "Cat.": ("Catão", -160), "Catul.": ("Catulo", -55), "Pl.": ("Plauto", -200),
        "Virg.": ("Virgílio", -25), "Cæs.": ("César", -50), "Phæd.": ("Fedro", 30),
    },
}

# Lemas do DicBio que o L&S registra com outra grafia ou outra forma.
ALIASES = {"dorsalis": "dorsualis", "glandula": "glandulae", "radicem": "radix", "sementem": "sementis", "truncum": "truncus"}


def autor(abrev, dic):
    abrev = abrev.strip()
    return AUTORES[dic].get(abrev) or AUTORES["*"].get(abrev)


def fmt_ano(a):
    return f"{-a} a.C." if a < 0 else f"{a} d.C."


def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\d+$", "", s.lower().replace("j", "i").replace("v", "u").strip())


def sem_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


# ----------------------------------------------------------------------------
# Lewis & Short
# ----------------------------------------------------------------------------
def baixar_ls():
    if LS_ARQ.exists():
        return
    LS_ARQ.parent.mkdir(parents=True, exist_ok=True)
    print(f"Baixando o Lewis & Short (≈77 MB) de {LS_URL} ...")
    urllib.request.urlretrieve(LS_URL, LS_ARQ)


def citacoes(trecho, dic, ultimo=None):
    """Lista (abrev, nome, ano) dos autores citados; 'id.' repete o anterior."""
    saida = []
    if dic == "LS":
        abrevs = re.findall(r"<bibl[^>]*>\s*<author>([^<]+)</author>", trecho)
    else:
        abrevs = re.findall(r'<span class="auth">([^<]+)</span>', trecho)
    for a in abrevs:
        a = html.unescape(a).strip()
        if a in ("id.", "ib.", "id. ib."):
            if ultimo:
                saida.append(ultimo)
            continue
        info = autor(a, dic)
        ultimo = (a, *info) if info else (a, None, None)
        saida.append(ultimo)
    return saida, ultimo


def resumo(cits, n=3):
    """'Catão (160 a.C.), Columela (60 d.C.)' — os n mais antigos, sem repetir."""
    vistos, out = set(), []
    datados = sorted({c for c in cits if c[2] is not None}, key=lambda c: c[2])
    for a, nome, ano in datados:
        if nome in vistos:
            continue
        vistos.add(nome)
        out.append(f"{nome} ({fmt_ano(ano)})")
        if len(out) == n:
            break
    return ", ".join(out)


def indexar_ls(lemas):
    texto = LS_ARQ.read_text(encoding="utf-8")
    idx = {}
    for m in re.finditer(r'<entryFree [^>]*key="([^"]+)"[^>]*>(.*?)</entryFree>', texto, re.S):
        k = norm(m.group(1))
        if k in lemas:
            idx.setdefault(k, []).append((m.group(1), m.group(2)))
    return idx


def analisar_ls(entradas):
    """(todas as citações, texto por acepção) de uma ou mais entradas do L&S."""
    todas, partes = [], []
    for chave, corpo in entradas:
        if len(entradas) > 1:
            partes.append(f"[{chave}]")
        cab = re.split(r"<sense ", corpo, maxsplit=1)[0]
        cits, ultimo = citacoes(cab, "LS")
        todas += cits
        for s in re.finditer(r'<sense [^>]*n="([^"]*)"[^>]*>(.*?)</sense>', corpo, re.S):
            cs, ultimo = citacoes(s.group(2), "LS", ultimo)
            todas += cs
            gl = re.search(r'<hi rend="ital">(.*?)</hi>', s.group(2), re.S)
            gl = sem_tags(gl.group(1))[:40] if gl else sem_tags(s.group(2))[:40]
            r = resumo(cs, 2)
            if r:
                partes.append(f"{s.group(1)}. {gl}: {r}")
    return todas, " | ".join(partes)


# ----------------------------------------------------------------------------
# Gaffiot (Digital Gaffiot, HTML)
# ----------------------------------------------------------------------------
def indexar_gaffiot(lemas):
    pasta = next((p for p in GAFFIOT_DIRS if p.exists()), None)
    if not pasta:
        return {}, None
    idx = {}
    for f in sorted(pasta.glob("*.html")):
        texto = f.read_text(encoding="utf-8")
        for m in re.finditer(r'<span class="key">#([^#]+)#<br></span>(.*?)(?=<div class="entry">|\Z)', texto, re.S):
            # o lema e os sublemas (ex.: bifidus dentro do verbete bifidatus)
            chaves = {norm(html.unescape(m.group(1)))}
            for sub in re.findall(r'<span class="sublemma">([^<]+)</span>', m.group(2)):
                sub = re.sub(r"[^\w\s]", "", html.unescape(sub)).strip()
                if sub:
                    chaves.add(norm(sub))
            for k in chaves & lemas:
                idx.setdefault(k, []).append(m.group(2))
    letras = "".join(sorted(f.stem for f in pasta.glob("*.html")))
    return idx, letras


# ----------------------------------------------------------------------------
# Atestações sem data
# ----------------------------------------------------------------------------
def atestacoes_sem_data():
    fontes = Graph().parse(SOURCES)
    linhas = []
    for f in sorted(ENTRIES.glob("*.ttl")):
        g = Graph().parse(f)
        pm = g.namespace_manager.normalizeUri
        for a in sorted(g.subjects(RDF.type, DICBIO.Attestation)):
            if g.value(a, DICBIO.attestationDate) is not None:
                continue
            fonte = g.value(a, DCT.source)
            lema, definicao, lingua = "", "", ""
            for sentido in g.subjects(DICBIO.hasAttestation, a):
                definicao = str(g.value(sentido, SKOS.definition) or "")
                for e in g.subjects(ONTOLEX.sense, sentido):
                    forma = g.value(e, ONTOLEX.canonicalForm)
                    lema = str(g.value(forma, ONTOLEX.writtenRep) or "")
                    lingua = str(g.value(e, DCT.language) or "").rsplit("/", 1)[-1]
            linhas.append(dict(
                arquivo=f.name, atestacao=pm(a), lema=lema, lingua=lingua,
                definicao_etimo=definicao,
                fonte=pm(fonte) if isinstance(fonte, URIRef) else str(fonte or ""),
                _fonte=fonte, _fontes=fontes,
            ))
    return linhas


def sugerir(l, ls_idx, gf_idx):
    fonte, fontes = l["_fonte"], l["_fontes"]
    # 1. texto livre com ano
    if fonte is not None and not isinstance(fonte, URIRef):
        anos = re.findall(r"\b(1[4-9]\d\d)\b", str(fonte))
        if anos:
            return int(anos[0]), "ano escrito na fonte (texto livre)"
    # 2. obra primária com data em sources.ttl
    if isinstance(fonte, URIRef) and (fonte, RDF.type, BIBO.ReferenceSource) not in fontes:
        issued = fontes.value(fonte, DCT.issued)
        if issued is not None:
            return int(str(issued)[:4]), "data da obra (dcterms:issued em sources.ttl)"
    # 3. autor mais antigo nos dicionários
    k = norm(l["lema"])
    k = ALIASES.get(k, k)
    candidatos = []
    if k in gf_idx:
        cits = [c for corpo in gf_idx[k] for c in citacoes(corpo, "G")[0] if c[2] is not None]
        if cits:
            candidatos.append(("Gaffiot", min(cits, key=lambda c: c[2])))
    if k in ls_idx:
        cits = [c for c in analisar_ls(ls_idx[k])[0] if c[2] is not None]
        if cits:
            candidatos.append(("L&S", min(cits, key=lambda c: c[2])))
    if not candidatos:
        return None, "sem sugestão (nenhum autor antigo datado no L&S nem no Gaffiot A–F)"
    # se a fonte é o Gaffiot, prefere o Gaffiot; senão, o mais antigo
    if "gaffiot" in str(fonte).lower() and candidatos[0][0] == "Gaffiot":
        dic, (_, nome, ano) = candidatos[0]
    else:
        dic, (_, nome, ano) = min(candidatos, key=lambda c: c[1][2])
    return ano, f"autor mais antigo citado no {dic}: {nome}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    args = ap.parse_args()

    baixar_ls()
    linhas = atestacoes_sem_data()
    lemas = {norm(l["lema"]) for l in linhas} | set(ALIASES.values())
    ls_idx = indexar_ls(lemas)
    gf_idx, letras = indexar_gaffiot(lemas)

    colunas = ["arquivo", "atestacao", "lema", "lingua", "fonte", "definicao_etimo",
               "ano_sugerido", "base_da_sugestao", "autores_LS_por_acepcao", "autores_Gaffiot",
               "ano", "nota"]
    sem_aut = set()
    for l in linhas:
        ano, base = sugerir(l, ls_idx, gf_idx)
        l["ano_sugerido"] = "" if ano is None else str(ano)
        l["base_da_sugestao"] = base
        k = ALIASES.get(norm(l["lema"]), norm(l["lema"]))
        if k in ls_idx:
            todas, por_acepcao = analisar_ls(ls_idx[k])
            l["autores_LS_por_acepcao"] = por_acepcao or "(no L&S, sem autor datado)"
            sem_aut |= {c[0] for c in todas if c[2] is None}
        else:
            l["autores_LS_por_acepcao"] = "(não está no L&S)"
        if k in gf_idx:
            cits = [c for corpo in gf_idx[k] for c in citacoes(corpo, "G")[0]]
            l["autores_Gaffiot"] = resumo(cits, 4) or (
                "(no Gaffiot, sem autor datado: " + ", ".join(sorted({c[0] for c in cits})) + ")"
                if cits else "(no Gaffiot, sem citação)")
            sem_aut |= {c[0] for c in cits if c[2] is None}
        else:
            l["autores_Gaffiot"] = "" if letras and k[:1].upper() not in letras else "(não está no Gaffiot)"
        l["ano"] = ""
        l["nota"] = ""

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with open(args.saida, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=colunas, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)

    com = sum(1 for l in linhas if l["ano_sugerido"])
    print(f"{len(linhas)} atestações sem data; {com} com sugestão.")
    bases = {}
    for l in linhas:
        b = l["base_da_sugestao"].split(":")[0]
        bases[b] = bases.get(b, 0) + 1
    for b, n in sorted(bases.items(), key=lambda x: -x[1]):
        print(f"  {n:4d}  {b}")
    if sem_aut:
        print("Abreviaturas sem data na tabela AUTORES (ignoradas):", ", ".join(sorted(sem_aut)))
    print(f"Planilha: {args.saida}")


if __name__ == "__main__":
    main()
