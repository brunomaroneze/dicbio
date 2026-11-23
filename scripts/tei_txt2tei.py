"""
Etapa 2 da marcação TEI de uma obra do corpus: conversão TXT -> TEI (estrutura).

Usa o TXT da obra e o mapa de páginas gerado por tei_mapa_paginas.py e produz um XML
preliminar com <pb/>, <div>, <head>, <p>, <list>/<item>, <note> e <table>.
Os pontos duvidosos recebem comentários <!-- REVISAR: ... -->.
Não altera a transcrição, exceto:
  - junta palavras partidas por hífen de fim de linha ("cen- sura" -> "censura");
    com clíticos mantém o hífen ("deve- se" -> "deve-se");
  - remove as assinaturas tipográficas de pé de página ("3", "3**"), que o schema não prevê;
  - remove os marcadores de página "(n)" (substituídos por <pb/>) e as chamadas de nota "(1)"
    (substituídas pela própria <note>).
Não atribui xml:id (isso é feito depois da conferência).

Uso (Manual do Fazendeiro, de Imbert):
  python scripts/tei_txt2tei.py corpus_digital/obras/fazendeiroimbert.txt \
      --mapa corpus_digital/obras/fazendeiroimbert_paginas.csv \
      --sem-numero-linhas 7:1 8:12 \
      --rosto 1-12 --rosto-xml corpus_digital/obras/fazendeiroimbert_rosto.xml \
      --front-divs 16:dedication 40:introduction --assinaturas 35 \
      --inicio-corpo 79 --tabelas 3221-3595 \
      --back "3619:index:toc" "3705:subscribers:subscribers" \
      --saida corpus_digital/obras/fazendeiroimbert.xml
"""
import argparse
import csv
import re
import sys
from collections import Counter
from html import escape
from pathlib import Path

# ----------------------------------------------------------------- padrões de linha
RE_MARCADOR = re.compile(r"^\s*\(\s*([0-9]+|[ivxlcj]+)\s*\)\s*(.*)$", re.I)
RE_ASSINATURA = re.compile(r"^\s*\d{1,2}\s*\*{0,2}\s*$")
RE_CAPITULO = re.compile(r"^\s*CAP[IÍ]TULO\s+([IVXLC]+|PRIMEIRO)\b\.*\s*(.*)$")
RE_SECCAO = re.compile(r"^\s*SECC?Ç?[AÃ][OÕÓ]?\s+([IVXLC]+|[A-ZÁÉÍÓÚ]+)\s*[.,]?\s*(.*)$")
RE_ESPECIE = re.compile(r"^\s*(PRIMEIRA|SEGUNDA|TERCEIRA|QUARTA|QUINTA|SEXTA|SETIMA|OITAVA)\s+ESPECIE\b")
RE_NOTA = re.compile(r"^\s*\((\d)\)\s*(\S.*)$")
RE_TIT_RECEITA = re.compile(r"^\s*\d+\s*[ºª°]\.?(\s+.*)?$")
RE_DOSE = re.compile(r"(…|\.\s?\.|\b\d+[\d/½¼⅛ ]*\s*(grãos?|onças?|oitavas?|libras?|gotas|canadas?|oit)\b\.?\s*$)")
TERMINAL = tuple(".!?:;»”\"'")
CLITICOS = {"se", "lhe", "lhes", "o", "a", "os", "as", "me", "te", "nos", "vos", "lo", "la", "los",
            "las", "ha", "hia", "hão", "hei", "hemos", "ia"}

ORDINAIS = {"PRIMEIRO": 1, "PRIMEIRA": 1}
ROM = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def romano(s):
    s = s.upper()
    if s in ORDINAIS:
        return ORDINAIS[s]
    if any(c not in ROM for c in s):
        return None
    t = 0
    for a, b in zip(s, s[1:] + " "):
        t += -ROM[a] if b != " " and ROM[b] > ROM[a] else ROM[a]
    return t


def eh_caixa_alta(t):
    letras = [c for c in t if c.isalpha()]
    return len(letras) >= 3 and not any(c.islower() for c in letras)


def eh_item(t):
    return len(t) < 160 and bool(RE_DOSE.search(t))


log = Counter()
hifens = []


def desfaz_hifens(t):
    def rep(m):
        a, b = m.group(1), m.group(2)
        if b.lower() in CLITICOS and a.lower() not in ("del", "nel", "pel", "d", "n"):
            log["hifen_clitico"] += 1
            hifens.append(f"{a}- {b} -> {a}-{b}")
            return f"{a}-{b}"
        log["hifen_juntado"] += 1
        hifens.append(f"{a}- {b} -> {a}{b}")
        return f"{a}{b}"
    return re.sub(r"([A-Za-zÀ-ÿ]+)- ([a-zà-ÿ]+)", rep, t)


# ----------------------------------------------------------------- estrutura de saída
class No:
    def __init__(self, tag, attrs=None, texto=None, filhos=None, comentario=None, bruto=None):
        self.tag, self.attrs, self.bruto = tag, attrs or {}, bruto
        self.texto = texto  # lista de pedaços: str ou ('pb', attrs) ou ('note', [str])
        self.filhos = filhos if filhos is not None else []
        self.comentario = comentario


def fmt_attrs(a):
    return "".join(f' {k}="{escape(str(v), quote=True)}"' for k, v in a.items() if v not in (None, ""))


def fmt_inline(pedacos):
    out = []
    for p in pedacos:
        if isinstance(p, str):
            out.append(escape(p, quote=False))
        elif p[0] == "pb":
            out.append(f"<pb{fmt_attrs(p[1])}/>")
        elif p[0] == "note":
            corpo = "".join(fmt_inline([x]) for x in p[1])
            out.append(f'<note><p>{corpo}</p></note>')
    s = "".join(out)
    return re.sub(r"\s+", " ", s).strip()


def serializa(no, nivel, linhas):
    ind = "\t" * nivel
    if no.bruto is not None:  # fragmento XML pronto (ex.: página de rosto marcada à mão)
        linhas.extend(ind + l for l in no.bruto.rstrip().splitlines())
        return
    if no.comentario:
        linhas.append(f"{ind}<!-- {no.comentario} -->")
    if no.tag is None:
        return
    if no.texto is not None:
        linhas.append(f"{ind}<{no.tag}{fmt_attrs(no.attrs)}>{fmt_inline(no.texto)}</{no.tag}>")
    elif not no.filhos:
        linhas.append(f"{ind}<{no.tag}{fmt_attrs(no.attrs)}/>")
    else:
        linhas.append(f"{ind}<{no.tag}{fmt_attrs(no.attrs)}>")
        for f in no.filhos:
            serializa(f, nivel + 1, linhas)
        linhas.append(f"{ind}</{no.tag}>")


# ----------------------------------------------------------------- conversão
class Conversor:
    def __init__(self, raiz):
        self.pilha = [raiz]          # pilha de containers (div/body/front/back)
        self.ultimo = None           # último bloco textual (p/head/item) para continuação
        self.pb_pend = []            # <pb/> aguardando o próximo bloco
        self.div_vazia = False       # div recém-aberta, só com head(s)
        self.lista = None            # lista aberta

    @property
    def topo(self):
        return self.pilha[-1]

    def nivel_div(self, nivel):
        """Fecha divs até restar 'nivel' divs abertas na pilha."""
        while sum(1 for n in self.pilha if n.tag == "div") > nivel:
            self.pilha.pop()

    def solta_pbs(self):
        for attrs in self.pb_pend:
            self.topo.filhos.append(No("pb", attrs))
        self.pb_pend = []

    def abre_div(self, nivel, tipo, n=None):
        self.nivel_div(nivel - 1)
        self.fecha_lista()
        self.solta_pbs()
        d = No("div", {"type": tipo, "n": n})
        self.topo.filhos.append(d)
        self.pilha.append(d)
        self.div_vazia, self.ultimo = True, None
        return d

    def head(self, texto, tipo=None):
        self.solta_pbs()
        h = No("head", {"type": tipo}, texto=[texto])
        self.topo.filhos.append(h)
        self.ultimo = h

    def fecha_lista(self):
        self.lista = None

    def bloco(self, tag, texto, comentario=None):
        self.fecha_lista()
        self.solta_pbs()
        b = No(tag, texto=[texto], comentario=comentario)
        self.topo.filhos.append(b)
        self.ultimo = b
        self.div_vazia = False
        return b

    def item(self, texto, cabeca=None):
        if self.lista is None:
            self.solta_pbs()
            self.lista = No("list", {"type": "receita"})
            if cabeca:
                self.lista.filhos.append(No("head", texto=[cabeca]))
            self.topo.filhos.append(self.lista)
        else:
            for attrs in self.pb_pend:
                self.lista.filhos.append(No("pb", attrs))
            self.pb_pend = []
        it = No("item", texto=[texto])
        self.lista.filhos.append(it)
        self.ultimo = it
        self.div_vazia = False

    def continua(self, texto):
        """Acrescenta texto ao último bloco, com os <pb/> pendentes no ponto de junção."""
        u = self.ultimo
        sep = " "
        # palavra partida com hífen no fim da linha/página: junta e põe o <pb/> antes da palavra inteira
        k = next((j for j in range(len(u.texto) - 1, -1, -1) if isinstance(u.texto[j], str)), None)
        if k is not None and texto[:1].islower():
            m = re.search(r"([A-Za-zÀ-ÿ]+)-\s*$", u.texto[k])
            if m:
                u.texto[k] = u.texto[k][:m.start()]
                texto = m.group(1) + texto
                sep = "" if not self.pb_pend else " "
                if not self.pb_pend:
                    texto = texto  # junção simples, sem espaço
                log["palavra_partida_juntada"] += 1
                hifens.append(f"{m.group(1)}-|{texto.split()[0]} (quebra de linha/página)")
        if self.pb_pend:
            if u.texto and isinstance(u.texto[-1], str) and u.texto[-1].endswith(" ") is False and sep == " ":
                u.texto.append(" ")
            for attrs in self.pb_pend:
                u.texto.append(("pb", attrs))
            self.pb_pend = []
            u.texto.append(texto)
        else:
            u.texto.append(sep + texto)

    def nota(self, num, texto):
        """Insere a nota no ponto da chamada '(num)' mais recente."""
        chamada = f"({num})"
        for bloco in reversed(self._blocos_recentes()):
            for i in range(len(bloco.texto) - 1, -1, -1):
                pedaco = bloco.texto[i]
                if isinstance(pedaco, str) and chamada in pedaco:
                    antes, _, depois = pedaco.rpartition(chamada)
                    bloco.texto[i:i + 1] = [antes.rstrip(), ("note", [texto]), depois]
                    log["nota_no_lugar"] += 1
                    return
        log["nota_sem_chamada"] += 1
        self.bloco("note", texto, comentario=f"REVISAR: chamada ({num}) desta nota não encontrada")

    def _blocos_recentes(self, limite=60):
        out = []

        def visita(no):
            if no.texto is not None:
                out.append(no)
            for f in no.filhos:
                visita(f)
        visita(self.pilha[0])
        return out[-limite:]


def termina_frase(no):
    ult = next((p for p in reversed(no.texto) if isinstance(p, str) and p.strip()), "")
    return ult.rstrip().endswith(TERMINAL)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("txt")
    ap.add_argument("--mapa", required=True)
    ap.add_argument("--sem-numero-linhas", nargs="*", default=[], help="imagem:linha do TXT antes da qual entra o <pb/>")
    ap.add_argument("--rosto", help="intervalo de linhas da página de rosto (titlePage), ex.: 1-12")
    ap.add_argument("--rosto-xml", help="fragmento XML que substitui a página de rosto (linhas de --rosto)")
    ap.add_argument("--assinaturas", nargs="*", type=int, default=[], help="linhas que são assinaturas (closer/signed)")
    ap.add_argument("--front-divs", nargs="*", default=[], help="linha:tipo de cada div do front (a linha é o head)")
    ap.add_argument("--inicio-corpo", type=int, required=True, help="linha onde começa o <body>")
    ap.add_argument("--tabelas", nargs="*", default=[], help="intervalos de linhas que são tabelas desestruturadas")
    ap.add_argument("--back", nargs="*", default=[], help="linha:tipo_div:tipo_lista de cada lista do <back>")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()

    linhas = Path(a.txt).read_text(encoding="utf-8").splitlines()

    # --- eventos de página por linha
    pbs_antes = {}    # linha -> [(attrs, trecho_ou_None)]
    linhas_marcador = set()
    with open(a.mapa, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            facs = r["imagem"]
            attrs = {"n": r["pagina"], "facs": facs}
            if r["situacao"] in ("ok", "corrigido", "conferido"):
                ln = int(r["linha_txt"])
                linhas_marcador.add(ln)
                pbs_antes.setdefault(ln, []).append((attrs, None))
            elif r["situacao"] == "localizado":
                ln = int(r["linha_txt"])
                obs = r["observacao"]
                trecho = r["inicio_pagina_txt"] if "quebra no meio" in obs else None
                pbs_antes.setdefault(ln, []).append((attrs, trecho))
            elif r["situacao"] == "sem_numero":
                n_img = int(re.search(r"(\d+)\.\w+$", facs).group(1))
                ln = next(int(x.split(":")[1]) for x in a.sem_numero_linhas if int(x.split(":")[0]) == n_img)
                pbs_antes.setdefault(ln, []).append(({"facs": facs}, None))
            else:
                sys.exit(f"Mapa com situação pendente: {r}")

    tabelas = []
    for t in a.tabelas:
        i, j = map(int, t.split("-"))
        tabelas.append((i, j))
    rosto = tuple(map(int, a.rosto.split("-"))) if a.rosto else None
    assinaturas = set(a.assinaturas)
    front_divs = {int(x.split(":")[0]): x.split(":")[1] for x in a.front_divs}
    backs = {int(x.split(":")[0]): x.split(":")[1:] for x in a.back}
    inicio_back = min(backs) if backs else len(linhas) + 1

    text = No("text")
    front, body, back = No("front"), No("body"), No("back")
    text.filhos = [front, body] + ([back] if backs else [])
    cv = Conversor(front)
    tabela_atual = None
    lista_back = None
    proximo_titulo = None   # 'capitulo' | 'secao' | 'especie' : a próxima linha é título

    def proxima_linha_texto(i):
        for j in range(i + 1, min(i + 8, len(linhas) + 1)):
            t = linhas[j - 1].strip()
            if t and j not in linhas_marcador and not RE_ASSINATURA.match(t):
                return t
        return ""

    for i, bruta in enumerate(linhas, start=1):
        # mudança de região
        if i == a.inicio_corpo:
            cv.nivel_div(0)
            cv.pilha = [body]
            cv.ultimo = None
        if i == inicio_back:
            cv.nivel_div(0)
            cv.pilha = [back]
            cv.ultimo = None

        t = bruta.strip()
        eventos = pbs_antes.get(i, [])
        trecho_pb = None
        for attrs, trecho in eventos:
            if trecho:
                trecho_pb = (attrs, trecho)
            else:
                cv.pb_pend.append(attrs)
        if i in linhas_marcador:
            m = RE_MARCADOR.match(t)
            t = m.group(2).strip() if m else ""
        if not t:
            continue
        if RE_ASSINATURA.match(t):
            log["assinatura_removida"] += 1
            continue
        t = desfaz_hifens(t)

        # página de rosto: fragmento marcado à mão (--rosto-xml) ou rascunho em titlePart
        if rosto and rosto[0] <= i <= rosto[1] and a.rosto_xml:
            cv.pb_pend = []  # os <pb/> da página de rosto já estão no fragmento
            if i == rosto[0]:
                front.filhos.append(No(None, bruto=Path(a.rosto_xml).read_text(encoding="utf-8")))
            continue
        if rosto and rosto[0] <= i <= rosto[1]:
            if i == rosto[0]:
                cv.solta_pbs()
                tp = No("titlePage", comentario="REVISAR: página de rosto — distribuir em docTitle/titlePart, byline, epigraph, docImprint")
                front.filhos.append(tp)
                cv.pilha = [front, tp]
            cv.solta_pbs()
            cv.topo.filhos.append(No("titlePart", texto=[t]))
            if i == rosto[1]:
                cv.pilha = [front]
            continue

        # tabelas desestruturadas pelo OCR
        tab = next(((x, y) for x, y in tabelas if x <= i <= y), None)
        if tab:
            if tabela_atual is None or tabela_atual[0] != tab:
                cv.fecha_lista()
                cv.solta_pbs()
                tb = No("table", comentario="REVISAR: tabela desestruturada pelo OCR — reconstruir linhas e colunas pelas imagens")
                cv.topo.filhos.append(tb)
                tabela_atual = (tab, tb)
                cv.div_vazia, cv.ultimo = False, None
            for attrs in cv.pb_pend:
                tabela_atual[1].filhos.append(No("pb", attrs))
            cv.pb_pend = []
            tabela_atual[1].filhos.append(No("row", filhos=[No("cell", texto=[t])]))
            log["linha_tabela"] += 1
            continue

        # back: listas
        if i in backs:
            tipo_div, tipo_lista = backs[i]
            cv.abre_div(1, tipo_div)
            cv.head(t)
            lista_back = No("list", {"type": tipo_lista})
            cv.topo.filhos.append(lista_back)
            continue
        if i >= inicio_back:
            for attrs in cv.pb_pend:
                lista_back.filhos.append(No("pb", attrs))
            cv.pb_pend = []
            if t.startswith("FIM DO INDICE"):
                cv.bloco("p", t)
                continue
            nova_entrada = tipo_lista != "toc" or re.match(
                r"^(CAP|GAP|Sec|SEC|DEDICAT|INTRODU|QUADRO|ADVERT|PLANO|LISTA|Quadro)", t)
            if nova_entrada or not lista_back.filhos:
                it = No("item", texto=[t])
                lista_back.filhos.append(it)
            else:
                it = next(x for x in reversed(lista_back.filhos) if x.tag == "item")
                it.texto.append(" " + t)
            continue

        # assinatura (closer/signed)
        if i in assinaturas:
            cv.fecha_lista()
            cv.solta_pbs()
            cv.topo.filhos.append(No("closer", filhos=[No("signed", texto=[t])]))
            cv.ultimo = None
            continue

        # front: divs nomeadas
        if i in front_divs:
            cv.abre_div(1, front_divs[i])
            cv.head(t)
            continue

        # quebra de página no meio da linha (página sem marcador no TXT)
        if trecho_pb:
            attrs, trecho = trecho_pb
            pos = t.find(trecho)
            if pos > 0:
                antes, depois = t[:pos].rstrip(), t[pos:]
                processa(cv, antes, i, proxima_linha_texto, a)
                cv.pb_pend.append(attrs)
                cv.continua(depois)
                continue
            cv.pb_pend.append(attrs)
            log["pb_trecho_nao_achado"] += 1

        proximo_titulo = processa(cv, t, i, proxima_linha_texto, a, proximo_titulo)

    cv.solta_pbs()

    # --- saída
    saida = ["<?xml version='1.0' encoding='UTF-8'?>",
             '<?xml-model href="tei_dhtb.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>',
             '<TEI xmlns="http://www.tei-c.org/ns/1.0">',
             "\t<!-- REVISAR: substituir pelo teiHeader definitivo -->",
             "\t<teiHeader>", "\t\t<fileDesc>",
             "\t\t\t<titleStmt><title>Manual do Fazendeiro (Imbert, 1834)</title></titleStmt>",
             "\t\t\t<publicationStmt><p>Em preparação.</p></publicationStmt>",
             "\t\t\t<sourceDesc><p>Em preparação.</p></sourceDesc>",
             "\t\t</fileDesc>", "\t</teiHeader>"]
    serializa(text, 1, saida)
    saida.append("</TEI>")
    Path(a.saida).write_text("\n".join(saida) + "\n", encoding="utf-8")

    Path(a.saida).with_suffix(".hifens.txt").write_text("\n".join(hifens) + "\n", encoding="utf-8")
    print(f"{a.saida} gerado.")
    for k, v in sorted(log.items()):
        print(f"  {k}: {v}")


def processa(cv, t, i, proxima, a, proximo_titulo=None):
    """Classifica uma linha de texto e a insere na estrutura. Devolve o estado de 'próximo título'."""
    # título de capítulo/secção na linha seguinte ao rótulo
    if proximo_titulo and not (RE_CAPITULO.match(t) or RE_SECCAO.match(t)):
        cv.head(t)
        log[f"titulo_{proximo_titulo}"] += 1
        return None

    m = RE_CAPITULO.match(t)
    if m:
        cv.abre_div(1, "chapter", romano(m.group(1)))
        cv.head(t)
        log["capitulo"] += 1
        return "capitulo" if not m.group(2) or re.fullmatch(r"\(\d\)\.?", m.group(2)) else None
    m = RE_SECCAO.match(t)
    if m:
        cv.abre_div(max(nivel_base_cap(cv), 1) + 1, "section", romano(m.group(1)))
        cv.head(t)
        log["secao"] += 1
        return None if m.group(2) else "secao"
    if RE_ESPECIE.match(t):
        cv.abre_div(nivel_base(cv) + 1, "subsection")
        cv.head(t)
        log["especie"] += 1
        return "especie"

    m = RE_NOTA.match(t)
    if m:
        cv.nota(m.group(1), m.group(2))
        return None

    prox = proxima(i)
    # título de receita seguido de itens
    if (RE_TIT_RECEITA.match(t) or (eh_caixa_alta(t) and len(t) < 120)) and eh_item(prox) and not eh_item(t):
        cv.fecha_lista()
        cv.solta_pbs()
        cv._cabeca_pendente = t
        log["cabeca_receita"] += 1
        return None
    if eh_item(t):
        cab = getattr(cv, "_cabeca_pendente", None)
        cv._cabeca_pendente = None
        cv.item(t, cab)
        log["item"] += 1
        return None
    cv._cabeca_pendente = None

    if eh_caixa_alta(t) and len(t) < 250 and t != "FIM":
        if cv.div_vazia and cv.ultimo is not None and cv.ultimo.tag == "head":
            cv.head(t)
        elif nivel_atual(cv) == 0 and cv.topo.tag == "body" and not any(f.tag == "div" for f in cv.topo.filhos):
            cv.head(t)  # título geral no início do <body>
        else:
            cv.abre_div(nivel_base(cv) + 1, "subsection")
            cv.head(t)
        log["subtitulo_caixa_alta"] += 1
        return None

    # parágrafo, possivelmente continuação do anterior
    u = cv.ultimo
    if u is not None and u.tag in ("p", "item"):
        comeca_min = t[:1].islower() or t[:1] in ",;.)"
        if comeca_min:
            cv.continua(t)
            log["juncao_paragrafo" if not termina_frase(u) else "juncao_minuscula_apos_pontuacao"] += 1
            return None
        if u.tag == "p" and not termina_frase(u):
            cv.bloco("p", t, comentario="REVISAR: o parágrafo anterior termina sem pontuação — talvez seja o mesmo parágrafo")
            log["revisar_juncao"] += 1
            return None
    cv.bloco("p", t)
    log["paragrafo"] += 1
    return None


def nivel_base(cv):
    """Profundidade da div estrutural (capítulo/secção) mais interna."""
    prof = 0
    for k, n in enumerate([x for x in cv.pilha if x.tag == "div"], start=1):
        if n.attrs.get("type") in ("chapter", "section") or cv.pilha[0].tag == "front":
            prof = k
    return prof


def nivel_base_cap(cv):
    divs = [x for x in cv.pilha if x.tag == "div"]
    return next((k for k, n in enumerate(divs, 1) if n.attrs.get("type") == "chapter"), 0)


def nivel_atual(cv):
    return sum(1 for n in cv.pilha if n.tag == "div")


if __name__ == "__main__":
    main()
