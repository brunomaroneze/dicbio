"""Núcleo do sistema de conferência: extrai o texto visível de cada página do
TEI e aplica correções ao XML bruto sem nunca alterar as tags.

Só usa a biblioteca padrão.
"""
import html
import re
import unicodedata
import xml.etree.ElementTree as ET

# Elementos "transparentes": o texto deles faz parte do bloco em que estão.
# Todos os demais (exceto note e pb) delimitam blocos.
EM_LINHA = {
    "term", "s", "foreign", "w", "rs", "name", "title", "g", "sic", "corr",
    "hi", "ref", "pubPlace", "docDate", "docAuthor", "date", "gap", "lb",
    "emph", "persName", "placeName", "abbr", "expan", "choice", "c", "pc",
}
TOKEN = re.compile(r"<!--.*?-->|<\?.*?\?>|<!\[CDATA\[.*?\]\]>|<[^>]+>|[^<]+", re.S)
CARACTERE = re.compile(r"&[^;\s]+;|\s+|.", re.S)
NOME = re.compile(r"</?\s*([\w:.-]+)")


class ErroConferencia(Exception):
    pass


class Ch:
    """Um caractere visível e o(s) trecho(s) do XML bruto que o produzem."""
    __slots__ = ("c", "spans", "fixo", "tags")

    def __init__(self, c, spans, fixo=None, tags=()):
        self.c, self.spans, self.fixo, self.tags = c, spans, fixo, tags


class Segmento:
    def __init__(self, tipo, continua=False, nota=None):
        self.tipo, self.continua, self.nota, self.chs = tipo, continua, nota, []

    @property
    def texto(self):
        return "".join(x.c for x in self.chs)


class Pagina:
    def __init__(self, n, facs):
        self.n, self.facs, self.segs, self.id, self.notas = n, facs, [], "", 0


def atributo(tag, nome):
    m = re.search(r"\s" + nome + r"\s*=\s*(\"[^\"]*\"|'[^']*')", tag)
    return html.unescape(m.group(1)[1:-1]) if m else ""


def hash_texto(t):
    """FNV-1a de 32 bits (a mesma função existe no diff.js)."""
    h = 0x811C9DC5
    for b in t.encode("utf-8"):
        h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    return f"{h:08x}"


def paginas(xml):
    m = re.search(r"<text[\s>]", xml)
    if not m:
        raise ErroConferencia("o arquivo não tem elemento <text>")
    lista, pag = [], None
    pilha = []      # blocos e notas abertos
    linha = []      # elementos em linha abertos

    def nova_pagina(n, facs):
        nonlocal pag
        pag = Pagina(n, facs)
        lista.append(pag)
        for b in pilha:
            b["seg"] = None

    def segmento():
        b = pilha[-1]
        if b["seg"] is None:
            b["seg"] = Segmento(b["nome"], b["usado"], b.get("nota"))
            b["usado"] = True
            pag.segs.append(b["seg"])
        return b["seg"]

    for t in TOKEN.finditer(xml, m.start()):
        s = t.group()
        if s.startswith(("<!--", "<?")):
            continue
        if s.startswith("<![CDATA["):
            raise ErroConferencia("seções CDATA não são aceitas")
        if not s.startswith("<"):
            if not pilha or (pag is None and not s.strip()):
                continue
            if pag is None:
                nova_pagina("sem indicação", "")
            b = pilha[-1]
            tags = tuple(linha)
            for k in CARACTERE.finditer(s):
                g = k.group()
                span = (t.start() + k.start(), t.start() + k.end())
                if g.isspace():
                    seg = b["seg"]
                    if seg is None or not seg.chs:
                        continue
                    if seg.chs[-1].c == " ":
                        seg.chs[-1].spans.append(span)
                    else:
                        seg.chs.append(Ch(" ", [span], None, tags))
                else:
                    c = html.unescape(g) if g[0] == "&" else g
                    segmento().chs.append(Ch(c, [span], None, tags))
            continue
        nome = NOME.match(s).group(1)
        if nome == "pb":
            if not s.startswith("</"):
                nova_pagina(atributo(s, "n") or "?", atributo(s, "facs"))
            continue
        if s.startswith("</"):
            if nome in EM_LINHA:
                if linha and linha[-1] == nome:
                    linha.pop()
            elif pilha:
                b = pilha.pop()
                for c in b.get("marcas", ()):
                    c.spans[0] = (c.spans[0][0], t.end())
            continue
        vazio = s.endswith("/>")
        if nome in EM_LINHA:
            if not vazio:
                linha.append(nome)
            continue
        if nome == "titlePage" and atributo(s, "facs"):
            nova_pagina("folha de rosto", atributo(s, "facs"))
        novo = {"nome": nome, "seg": None, "usado": False}
        if nome == "note" and pilha and pag is not None and pilha[-1]["nome"] not in ("div", "body", "front", "back"):
            # A nota vira um bloco à parte; no lugar dela fica a marca ⟦1⟧.
            pag.notas += 1
            novo["nota"] = pag.notas
            seg = segmento()
            f = object()
            novo["marcas"] = [Ch(c, [(t.start(), t.end())], f) for c in f"⟦{pag.notas}⟧"]
            seg.chs.extend(novo["marcas"])
        elif pilha:
            pilha[-1]["seg"] = None
        if not vazio:
            pilha.append(novo)

    vistos = {}
    for i, p in enumerate(lista):
        for seg in p.segs:
            while seg.chs and seg.chs[-1].c == " ":
                seg.chs.pop()
        achados = re.findall(r"([\w.-]+)\.(?:jpe?g|jp2|png|tiff?)", p.facs, re.I)
        base = achados[-1] if achados else f"pagina_{i + 1:04d}"
        base = re.sub(r"[^A-Za-z0-9_-]", "-", base)
        vistos[base] = vistos.get(base, 0) + 1
        p.id = base if vistos[base] == 1 else f"{base}--{vistos[base]}"
    return lista


def normaliza_insercao(t):
    t = re.sub(r"\s+", " ", unicodedata.normalize("NFC", t))
    if "⟦" in t or "⟧" in t:
        raise ErroConferencia("as marcas de nota ⟦ ⟧ não podem ser alteradas")
    if any(unicodedata.category(c) in ("Cc", "Cf", "Cs", "Cn") for c in t):
        raise ErroConferencia("a correção contém caracteres de controle ou invisíveis")
    return t


def escapa(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _troca(seg, ini, apaga, insere):
    """Traduz uma alteração do texto visível em trocas (ini, fim, texto) no bruto."""
    chs = seg.chs
    while apaga and insere and apaga[0] == insere[0]:
        ini, apaga, insere = ini + 1, apaga[1:], insere[1:]
    while apaga and insere and apaga[-1] == insere[-1]:
        apaga, insere = apaga[:-1], insere[:-1]
    alvo = chs[ini:ini + len(apaga)]
    if any(c.fixo for c in alvo):
        raise ErroConferencia("as marcas de nota ⟦ ⟧ não podem ser alteradas")
    novo = escapa(insere)
    if alvo:
        spans = [sp for c in alvo for sp in c.spans]
        trocas = [(spans[0][0], spans[0][1], novo)]
        trocas += [(a, b, "") for a, b in spans[1:]]
        return trocas, {t for c in alvo for t in c.tags}
    if not insere:
        return [], set()
    ant = chs[ini - 1] if ini else None
    prox = chs[ini] if ini < len(chs) else None
    if ant and prox and ant.fixo and ant.fixo is prox.fixo:
        raise ErroConferencia("as marcas de nota ⟦ ⟧ não podem ser alteradas")
    # Prefere ficar colado à palavra anterior; senão, entra antes da seguinte.
    usa_ant = prox is None or (ant and ant.c != " " and (
        (insere[0] != " " and not ant.fixo) or prox.fixo))
    usa = ant if usa_ant else prox
    pos = usa.spans[-1][1] if usa_ant else usa.spans[0][0]
    return [(pos, pos, novo)], set(usa.tags)


def _tags(xml):
    return [t for t in TOKEN.findall(xml) if t.startswith("<")]


def aplica(xml, edicoes):
    """edicoes: {id_pagina: [{"i": índice, "h": hash, "ops": [[ini, apaga, insere]]}]}

    Devolve (xml_novo, relatório). Lança ErroConferencia se algo não bater.
    """
    lista = paginas(xml)
    por_id = {p.id: p for p in lista}
    trocas, relatorio, esperado = [], [], {}
    for pid, eds in edicoes.items():
        p = por_id.get(pid)
        if p is None:
            raise ErroConferencia("uma das páginas enviadas não existe mais no XML")
        for ed in eds:
            i, h = ed["i"], ed["h"]
            if not (0 <= i < len(p.segs) and hash_texto(p.segs[i].texto) == h):
                cand = [k for k, s in enumerate(p.segs) if hash_texto(s.texto) == h]
                if len(cand) != 1:
                    raise ErroConferencia(
                        f"o texto da página {p.n} mudou depois que foi aberto "
                        "para conferência; recarregue a página e refaça a correção")
                i = cand[0]
            seg = p.segs[i]
            if id(seg) in esperado:
                raise ErroConferencia("o mesmo trecho foi enviado duas vezes")
            velho, novo, cursor = seg.texto, [], 0
            for ini, apaga, insere in ed["ops"]:
                if ini < cursor or ini > len(velho) or velho[ini:ini + len(apaga)] != apaga:
                    raise ErroConferencia(f"correção inconsistente na página {p.n}")
                insere = normaliza_insercao(insere)
                tr, tags = _troca(seg, ini, apaga, insere)
                trocas += tr
                novo += [velho[cursor:ini], insere]
                cursor = ini + len(apaga)
                relatorio.append({
                    "n": p.n, "tipo": seg.tipo, "tags": sorted(tags),
                    "antes": velho[max(0, ini - 25):ini], "apaga": apaga,
                    "insere": insere, "depois": velho[cursor:cursor + 25]})
            novo.append(velho[cursor:])
            esperado[id(seg)] = "".join(novo)
    res = xml
    for a, b, t in sorted(trocas, key=lambda x: (x[0], x[1]), reverse=True):
        res = res[:a] + t + res[b:]

    # Conferências de segurança: mesmas tags, XML bem formado, texto esperado.
    if _tags(res) != _tags(xml):
        raise ErroConferencia("a correção alteraria as tags do XML")
    ET.fromstring(res.encode("utf-8"))

    def norma(t):
        return " ".join(t.split())
    quer = [[x for x in (norma(esperado.get(id(s), s.texto)) for s in p.segs) if x] for p in lista]
    tem = [[norma(s.texto) for s in p.segs] for p in paginas(res)]
    if quer != tem:
        raise ErroConferencia("o resultado não corresponde ao texto corrigido")
    return res, relatorio
