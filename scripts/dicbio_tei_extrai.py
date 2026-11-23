#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dicbio_tei_extrai.py: extrai os <term> de uma obra em TEI-XML e prepara
verbetes provisórios para o DicBio.

Uso básico:
  python dicbio_tei_extrai.py obra.xml --verbetes verbetes.csv --definicoes definicoes.csv

Fluxo em duas rodadas:
  1) Primeira rodada: gera tudo e uma fila de revisão (lemmas_revisao.csv) com os
     termos sem @lemma, para os quais o script só *sugere* um lema moderno.
  2) Você preenche a coluna lemma_final e roda de novo com
     --lemmas-revisados saida_provisorios/lemmas_revisao.csv
     (opcional: --tei-saida obra_com_lemmas.xml grava os lemas confirmados no TEI).

Saídas (pasta --saida, padrão saida_provisorios/):
  ocorrencias.csv            uma linha por <term>, com página, seção e contexto
  verbetes_provisorios.csv   só os lemas que ainda não existem nos seus CSVs
  verbetes_provisorios.ttl   o mesmo, como esqueleto RDF
  lemmas_revisao.csv         fila de revisão de lemas
  relatorio.txt              resumo e cruzamento com o dicionário existente
"""
import argparse
import csv
import datetime
import html
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
MESES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
COLUNAS_VERBETES = ["ID", "Headword", "FirstAttestationDate", "FirstAttestationExampleMD",
                    "Etymology", "WClass", "Credits", "DateOfCreation", "DateOfUpdate"]
COLUNAS_EXTRA = ["Status", "TermType", "Variants"]

# AJUSTE ao padrão de URIs do seu RDF. Campos disponíveis: {slug}, {id}
PADRAO_URI_ENTRADA = "entrada_{slug}"

# Regras de modernização gráfica (só sugestão! acentos e hifens não são recuperáveis por regra)
REGRAS = [(r"ph", "f"), (r"th", "t"), (r"y", "i"), (r"ll", "l"),
          (r"([bdfgmnpt])\1", r"\1")]  # consoantes dobradas, exceto rr, ss, cc


# ---------------------------------------------------------------- utilidades
def nome_local(el):
    return etree.QName(el).localname if isinstance(el.tag, str) else None


def norm_espacos(s):
    return re.sub(r"\s+", " ", s).strip()


def nfc(s):
    return unicodedata.normalize("NFC", s)


def sem_acentos(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def chave(s):
    return sem_acentos(nfc(s).lower())


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", sem_acentos(s.lower())).strip("_")


def modernizar(forma):
    s = forma.lower()
    for padrao, subst in REGRAS:
        s = re.sub(padrao, subst, s)
    return s


def esc_ttl(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


# ---------------------------------------------------------------- extração TEI
def metadados(raiz):
    def q(xp):
        r = raiz.xpath(xp)
        return norm_espacos("".join(r[0].itertext())).rstrip(".") if r else ""
    bibl = "//*[local-name()='sourceDesc']//*[local-name()='bibl']"
    datas = raiz.xpath(bibl + "//*[local-name()='date']/@when")
    return {"autor": q(bibl + "/*[local-name()='author']"),
            "titulo": q(bibl + "/*[local-name()='title']"),
            "local": q(bibl + "/*[local-name()='pubPlace']"),
            "ano": datas[0][:4] if datas else ""}


def texto_marcado(el, alvo):
    """Texto do elemento, com o <term> alvo entre \\x00 e \\x01 e sem o conteúdo de notas alheias."""
    partes = [el.text or ""]
    for filho in el:
        if not isinstance(filho.tag, str):
            pass
        elif filho is alvo:
            partes.append("\x00" + "".join(filho.itertext()) + "\x01")
        elif nome_local(filho) == "note" and alvo not in list(filho.iter()):
            pass
        else:
            partes.append(texto_marcado(filho, alvo))
        partes.append(filho.tail or "")
    return "".join(partes)


def janela_html(txt, raio=180):
    txt = norm_espacos(txt)
    i, j = txt.index("\x00"), txt.index("\x01")
    ini, fim = max(0, i - raio), min(len(txt), j + raio)
    if ini > 0:
        k = txt.find(" ", ini, i)
        ini = k + 1 if k != -1 else ini
    if fim < len(txt):
        k = txt.rfind(" ", j, fim)
        fim = k if k != -1 else fim
    trecho = html.escape(txt[ini:fim], quote=False)
    trecho = trecho.replace("\x00", "<b>").replace("\x01", "</b>")
    return ("… " if ini > 0 else "") + trecho + (" …" if fim < len(txt) else "")


def ocorrencia(el, pagina):
    anc = list(el.iterancestors())
    secao = ""
    for a in anc:
        if nome_local(a) == "div":
            heads = [c for c in a if nome_local(c) == "head"]
            if heads:
                secao = norm_espacos("".join(heads[0].itertext()))
                break
    cont = next((a for a in anc if nome_local(a) in ("p", "head", "note", "item", "l", "cell", "quote")),
                el.getparent())
    return {
        "xml_id": el.get(XML_ID, ""),
        "forma": norm_espacos("".join(el.itertext())),
        "tipo": el.get("type", ""),
        "lemma_tei": (el.get("lemma") or "").strip(),
        "pagina": pagina or "",
        "secao": secao,
        "em_nota": any(nome_local(a) == "note" for a in anc),
        "contexto_html": janela_html(texto_marcado(cont, el)),
        "_el": el,
    }


def extrair(caminho):
    arvore = etree.parse(str(caminho))
    raiz = arvore.getroot()
    textos = raiz.xpath("//*[local-name()='text']")
    corpo = textos[0] if textos else raiz
    pagina, ocs = None, []
    for el in corpo.iter():
        n = nome_local(el)
        if n == "pb":
            pagina = el.get("n") or pagina
        elif n == "term":
            ocs.append(ocorrencia(el, pagina))
    return arvore, metadados(raiz), ocs


# ---------------------------------------------------------------- lemas
def detectar_obra(ocs):
    for o in ocs:
        m = re.match(r"t_([A-Za-z0-9]+)_\d+", o["xml_id"])
        if m:
            return m.group(1)
    return "obra"


def ler_revisados(caminho):
    mapa = {}
    with open(caminho, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            lf = (r.get("lemma_final") or "").strip()
            if lf:
                mapa[norm_espacos(r["forma"]).lower()] = nfc(lf).lower()
    return mapa


def resolver_lemmas(ocs, revisados):
    """Prioridade: @lemma do TEI > revisado por você > propagado de mesma forma > sugerido por regras."""
    por_forma = defaultdict(set)
    for o in ocs:
        if o["lemma_tei"]:
            por_forma[o["forma"].lower()].add(nfc(o["lemma_tei"]).lower())
    for o in ocs:
        f = o["forma"].lower()
        if o["lemma_tei"]:
            o["lemma"], o["origem"] = nfc(o["lemma_tei"]).lower(), "tei"
        elif f in revisados:
            o["lemma"], o["origem"] = revisados[f], "revisado"
        elif len(por_forma.get(f, ())) == 1:
            o["lemma"], o["origem"] = next(iter(por_forma[f])), "propagado"
        else:
            o["lemma"], o["origem"] = modernizar(f), "sugerido"


# ---------------------------------------------------------------- cruzamento com o dicionário
def carregar_existentes(verbetes, definicoes):
    exist, maxid = {}, 0
    if verbetes:
        with open(verbetes, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                exist[nfc(r["Headword"]).lower()] = r.get("ID", "")
                try:
                    maxid = max(maxid, int(r["ID"]))
                except (ValueError, KeyError):
                    pass
    if definicoes:
        with open(definicoes, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                exist.setdefault(nfc(r["Headword"]).lower(), "")
    return exist, maxid


def classificar(lemma, exist, exist_sa):
    k = nfc(lemma).lower()
    if k in exist:
        return "existente", exist[k]
    if sem_acentos(k) in exist_sa:
        return "possivel", exist_sa[sem_acentos(k)]
    return "novo", ""


# ---------------------------------------------------------------- saídas
def referencia(meta):
    partes = [meta["autor"], meta["titulo"], ", ".join(x for x in (meta["local"], meta["ano"]) if x)]
    return ". ".join(p for p in partes if p) + "."


def exemplo(meta, ocs):
    o = next((x for x in ocs if not x["em_nota"]), ocs[0])
    pag = f", p. {o['pagina']}" if o["pagina"] else ""
    return (f"{referencia(meta)} [ocorrência na obra; primeira atestação ainda não verificada]"
            f"<br><b>{meta['ano']}</b>: “{o['contexto_html']}” "
            f"(Extraído de: {meta['titulo']}, {meta['ano']}{pag})")


def escrever_csv(caminho, colunas, linhas):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=colunas, extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)


def gerar_ttl(provs, fonte_uri, hoje):
    L = ["# Esqueleto RDF de verbetes provisórios (gerado automaticamente).",
         "# ATENÇÃO: dicbio:entryStatus e dicbio:provisional são termos NOVOS: defina-os na ontologia.",
         "# AJUSTE o padrão de URI das entradas e a forma canônica (aqui, nó em branco) ao seu modelo.",
         "# dcterms:language omitido em todas as entradas (ausente = português).", "",
         "@prefix dicbio:  <https://dicbio.fflch.usp.br/ontology/> .",
         "@prefix dbres:   <https://dicbio.fflch.usp.br/recurso/> .",
         "@prefix dbsrc:   <https://dicbio.fflch.usp.br/fontes/> .",
         "@prefix ontolex: <http://www.w3.org/ns/lemon/ontolex#> .",
         "@prefix dcterms: <http://purl.org/dc/terms/> .",
         "@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .",
         "@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .", ""]
    for p in provs:
        uri = PADRAO_URI_ENTRADA.format(slug=slug(p["lemma"]), id=p["ID"])
        L += [f"dbres:{uri} a ontolex:LexicalEntry ;",
              f'    ontolex:canonicalForm [ a ontolex:Form ; ontolex:writtenRep "{esc_ttl(p["lemma"])}"@pt ] ;',
              "    dicbio:entryStatus dicbio:provisional ;",
              f"    dcterms:source dbsrc:{fonte_uri} ;",
              f'    dcterms:created "{hoje.isoformat()}"^^xsd:date ;',
              '    rdfs:comment "Verbete provisório gerado automaticamente; sem estudo lexicográfico."@pt .', ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tei")
    ap.add_argument("--verbetes", help="CSV de verbetes existentes")
    ap.add_argument("--definicoes", help="CSV de definições existentes")
    ap.add_argument("--lemmas-revisados", help="lemmas_revisao.csv com a coluna lemma_final preenchida")
    ap.add_argument("--tei-saida", help="grava cópia do TEI com @lemma confirmados (revisado/propagado)")
    ap.add_argument("--saida", default="saida_provisorios")
    ap.add_argument("--primeiro-id", type=int, help="ID do primeiro verbete novo (padrão: maior ID + 1)")
    ap.add_argument("--fonte-uri", help="nome local em dbsrc: da obra (padrão: <obra>_<ano>)")
    a = ap.parse_args()

    out = Path(a.saida)
    out.mkdir(parents=True, exist_ok=True)
    hoje = datetime.date.today()
    data_csv = f"{hoje.day:02d} {MESES[hoje.month - 1]} {hoje.year}"

    arvore, meta, ocs = extrair(a.tei)
    obra_id = detectar_obra(ocs)
    fonte_uri = a.fonte_uri or f"{obra_id}_{meta['ano']}".strip("_")
    resolver_lemmas(ocs, ler_revisados(a.lemmas_revisados) if a.lemmas_revisados else {})

    exist, maxid = carregar_existentes(a.verbetes, a.definicoes)
    exist_sa = {sem_acentos(k): v for k, v in exist.items()}
    for o in ocs:
        o["situacao"], o["id_verbete"] = classificar(o["lemma"], exist, exist_sa)

    # IDs para os lemas novos (ordem alfabética)
    grupos = defaultdict(list)
    for o in ocs:
        if o["situacao"] == "novo":
            grupos[o["lemma"]].append(o)
    prox = a.primeiro_id if a.primeiro_id else maxid + 1
    provs = []
    for lemma in sorted(grupos, key=chave):
        g = grupos[lemma]
        tipos = Counter(x["tipo"] for x in g if x["tipo"])
        prov = {"ID": prox, "Headword": lemma, "lemma": lemma, "FirstAttestationDate": "",
                "FirstAttestationExampleMD": exemplo(meta, g), "Etymology": "", "WClass": "",
                "Credits": "Verbete provisório gerado automaticamente",
                "DateOfCreation": data_csv, "DateOfUpdate": data_csv,
                "Status": "provisional", "TermType": "/".join(t for t, _ in tipos.most_common()),
                "Variants": " | ".join(sorted({x["forma"].lower() for x in g}))}
        for x in g:
            x["id_verbete"] = prox
        provs.append(prov)
        prox += 1

    # --- arquivos
    escrever_csv(out / "ocorrencias.csv",
                 ["obra_id", "xml_id", "forma", "tipo", "lemma", "origem", "situacao", "id_verbete",
                  "pagina", "secao", "em_nota", "contexto_html"],
                 [dict(o, obra_id=obra_id) for o in ocs])
    escrever_csv(out / "verbetes_provisorios.csv", COLUNAS_VERBETES + COLUNAS_EXTRA, provs)
    (out / "verbetes_provisorios.ttl").write_text(gerar_ttl(provs, fonte_uri, hoje), encoding="utf-8")

    por_forma = defaultdict(list)
    for o in ocs:
        if o["origem"] == "sugerido" or o["situacao"] == "possivel":
            por_forma[o["forma"].lower()].append(o)
    revisao = []
    for forma, g in sorted(por_forma.items(), key=lambda kv: chave(kv[0])):
        revisao.append({"forma": forma, "lemma_atual": g[0]["lemma"], "lemma_final": "",
                        "situacao": g[0]["situacao"], "id_existente_possivel": g[0]["id_verbete"]
                        if g[0]["situacao"] == "possivel" else "",
                        "n_ocorrencias": len(g), "tipo": g[0]["tipo"], "exemplo_xml_id": g[0]["xml_id"],
                        "contexto_html": g[0]["contexto_html"]})
    escrever_csv(out / "lemmas_revisao.csv",
                 ["forma", "lemma_atual", "lemma_final", "situacao", "id_existente_possivel",
                  "n_ocorrencias", "tipo", "exemplo_xml_id", "contexto_html"], revisao)

    if a.tei_saida:
        for o in ocs:
            if o["origem"] in ("revisado", "propagado") and o["_el"].get("lemma") is None:
                o["_el"].set("lemma", o["lemma"])
        arvore.write(a.tei_saida, encoding="utf-8", xml_declaration=True)

    # --- relatório
    por_lemma = defaultdict(list)
    for o in ocs:
        por_lemma[o["lemma"]].append(o)
    sit = Counter(g[0]["situacao"] for g in por_lemma.values())
    R = [f"Obra: {referencia(meta)}",
         f"Ocorrências de <term>: {len(ocs)} (sem xml:id: {sum(1 for o in ocs if not o['xml_id'])}; "
         f"em notas: {sum(1 for o in ocs if o['em_nota'])})",
         f"Lemas distintos: {len(por_lemma)}",
         "Origem do lema (ocorrências): " + ", ".join(f"{k}={v}" for k, v in
                                                       Counter(o["origem"] for o in ocs).items()),
         f"Cruzamento com o dicionário: existentes={sit['existente']}, "
         f"possíveis (diferem só por acento)={sit['possivel']}, novos={sit['novo']}",
         f"Verbetes provisórios gerados: {len(provs)} (IDs {provs[0]['ID']}–{provs[-1]['ID']})"
         if provs else "Verbetes provisórios gerados: 0",
         f"Formas na fila de revisão: {len(revisao)}", "", "Lemas mais frequentes:"]
    for lemma, g in sorted(por_lemma.items(), key=lambda kv: -len(kv[1]))[:15]:
        R.append(f"  {len(g):4d}  {lemma}  [{g[0]['situacao']}]")
    texto = "\n".join(R)
    (out / "relatorio.txt").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
