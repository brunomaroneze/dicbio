"""Migra verbetes do modelo antigo para o modelo atual (protocolo.md / SHACL v2.14).

Faz só as mudanças ESTRUTURAIS, que não exigem julgamento. O que exige
julgamento (processo etimológico, grau de certeza, fonte da hipótese,
definição do étimo, criação de fontes em sources.ttl) fica marcado com
"# REVISAR:" ou aparece como erro no SHACL, para a revisão posterior.

Migrações:

  M0. Étimo com o MESMO IRI da 1ª acepção portuguesa (lema latino igual ao
      português sem acento: botanica, glandula, placenta...). No grafo as
      duas acepções se fundem. O bloco do étimo é renomeado para
      entry_<lema>_lat_senseN e o dicbio:semanticEtymon é atualizado; a M1
      então o trata como os demais.

  M1. Étimo no modelo antigo — uma acepção solta, sem entrada, com
      ontolex:writtenRep, dcterms:language (IRI do Glottolog) e
      dcterms:source:

          dbres:entry_caulis_sense1 a ontolex:LexicalSense ;
              dcterms:language glotto:lati1261 ;
              dcterms:source dbsrc:source_old ;
              ontolex:writtenRep "caulis" .

      vira entrada + forma + acepção + atestação:

          dbres:entry_caulis       (LexicalEntry: língua, classe, criador)
          dbres:form_caulis        (Form: writtenRep com etiqueta de língua)
          dbres:entry_caulis_sense1 (LexicalSense, ligada à atestação)
          dbres:attestation_caulis_sense1_old (Attestation com a fonte)

      Só se aplica quando dcterms:language é um IRI do Glottolog. Os casos
      com língua em texto livre ("formação vernácula", "português",
      "obscuro"...) não são tocados: precisam de revisão manual.

  M2. Entrada principal sem dcterms:language, com formas em @pt:
      acrescenta dcterms:language glotto:port1283.

  M3. Formas com rdfs:label "plural", "feminino singular" etc.: troca o
      rótulo por lexinfo:number (e lexinfo:gender, só se a entrada não for
      substantivo — nos substantivos o gênero fica na entrada).

  M4. skos:exactMatch em ontolex:LexicalEntry: troca por
      dicbio:externalEntry (SHACL v2.14).

As edições são feitas no TEXTO do arquivo (preservando comentários, ordem e
formatação) e conferidas com rdflib: o grafo resultante precisa ser
exatamente o grafo original menos as triplas removidas mais as acrescentadas.

Uso:
    python scripts/migrar_verbetes.py caule calice        # mostra o diff
    python scripts/migrar_verbetes.py --todos             # diff de todos
    python scripts/migrar_verbetes.py caule --aplicar     # grava
"""

import argparse
import datetime as dt
import difflib
import re
import sys
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "data" / "entries"
SOURCES = ROOT / "data" / "sources.ttl"

ONTOLEX = Namespace("http://www.w3.org/ns/lemon/ontolex#")
LEXINFO = Namespace("http://www.lexinfo.net/ontology/3.0/lexinfo#")
LEMONETY = Namespace("http://lari-datasets.ilc.cnr.it/lemonEty#")
DICBIO = Namespace("https://dicbio.fflch.usp.br/ontology/")
DCT = Namespace("http://purl.org/dc/terms/")
GLOTTO = "https://glottolog.org/resource/languoid/id/"
DBRES = "https://dicbio.fflch.usp.br/recurso/"
DBSRC = "https://dicbio.fflch.usp.br/fontes/"

# glottocode -> (etiqueta de língua do writtenRep, sufixo para desambiguar nomes)
LINGUAS = {
    "lati1261": ("la", "lat"),
    "gree1276": ("grc", "grc"),
    "port1283": ("pt", "pt"),
}

# rótulo antigo da forma -> (gênero, número)
ROTULOS_FORMA = {
    "plural": (None, "plural"),
    "singular": (None, "singular"),
    "feminino plural": ("feminine", "plural"),
    "feminino singular": ("feminine", "singular"),
    "masculino plural": ("masculine", "plural"),
    "masculino singular": ("masculine", "singular"),
    "adjetivo plural": (None, "plural"),
    "adjetivo singular": (None, "singular"),
}

HOJE = dt.date.today().isoformat()


# ----------------------------------------------------------------------------
# Localização de blocos (declarações Turtle) no texto
# ----------------------------------------------------------------------------
def fim_da_declaracao(texto, inicio):
    """Índice logo após o '.' que encerra a declaração que começa em `inicio`.

    Percorre o texto ignorando strings ("...", '...', \"\"\"...\"\"\"), IRIs
    <...> e comentários.
    """
    i, n = inicio, len(texto)
    while i < n:
        c = texto[i]
        if texto.startswith('"""', i) or texto.startswith("'''", i):
            q = texto[i:i + 3]
            j = texto.find(q, i + 3)
            if j < 0:
                raise ValueError("string longa sem fechamento")
            i = j + 3
            continue
        if c in "\"'":
            j = i + 1
            while j < n and texto[j] != c:
                j += 2 if texto[j] == "\\" else 1
            i = j + 1
            continue
        if c == "<":
            i = texto.index(">", i) + 1
            continue
        if c == "#":
            j = texto.find("\n", i)
            i = n if j < 0 else j
            continue
        if c == "." and (i + 1 == n or texto[i + 1].isspace()):
            return i + 1
        i += 1
    raise ValueError("declaração sem '.' final")


def achar_bloco(texto, sujeito, g):
    """(início, fim) da declaração cujo sujeito é `sujeito` (no começo de linha)."""
    candidatos = [re.escape(f"<{sujeito}>")]
    try:
        pref = g.namespace_manager.normalizeUri(sujeito)
        if not pref.startswith("<"):
            # o rdflib não escapa ( ) ao compactar; o arquivo pode escapar
            candidatos.append(re.escape(pref))
            candidatos.append(re.escape(pref).replace(r"\(", r"\\\(").replace(r"\)", r"\\\)"))
    except Exception:
        pass
    padrao = re.compile(r"^(?:" + "|".join(candidatos) + r")(?=\s)", re.M)
    achados = list(padrao.finditer(texto))
    if len(achados) != 1:
        return None
    ini = achados[0].start()
    return ini, fim_da_declaracao(texto, ini)


def bloco_com_linha_seguinte(texto, ini, fim):
    """Estende o fim para engolir a quebra de linha e uma linha em branco."""
    m = re.compile(r"[ \t]*\n(?:[ \t]*\n)?").match(texto, fim)
    return (ini, m.end()) if m else (ini, fim)


# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
def local(iri):
    return str(iri)[len(DBRES):] if str(iri).startswith(DBRES) else None


def turtle_literal(lit):
    s = str(lit).replace("\\", "\\\\").replace('"', '\\"')
    if "\n" in s:
        s = s.replace("\n", "\\n")
    return f'"{s}"'


def nome_valido(nome):
    return re.fullmatch(r"[A-Za-z0-9_\-À-ÿ]+", nome) is not None


def carregar_nomes_existentes():
    """Todos os IRIs dbres: já usados como sujeito em qualquer verbete."""
    usados = defaultdict(set)
    for f in ENTRIES.glob("*.ttl"):
        g = Graph()
        try:
            g.parse(f)
        except Exception:
            continue
        for s in set(g.subjects()):
            if isinstance(s, URIRef) and str(s).startswith(DBRES):
                usados[str(s)].add(f.name)
    return usados


# ----------------------------------------------------------------------------
# M0: colisão de nome entre o étimo e a acepção portuguesa
# ----------------------------------------------------------------------------
def blocos_do_sujeito(texto, nome):
    """Todas as declarações (ini, fim) cujo sujeito é dbres:<nome>."""
    padrao = re.compile(r"^dbres:" + re.escape(nome) + r"(?=\s)", re.M)
    return [(m.start(), fim_da_declaracao(texto, m.start())) for m in padrao.finditer(texto)]


def m0_separar_colisoes(texto, prefixos, publicID, usados, arquivo):
    """Separa étimos que ganharam o mesmo IRI da 1ª acepção portuguesa.

    Ex.: botanica.ttl declara dbres:entry_botanica_sense1 duas vezes — uma
    como acepção de "botânica", outra como o étimo latino "Botanica" (com
    writtenRep/language/source). No grafo as duas se fundem. O bloco do
    étimo é renomeado para entry_<lema>_<sufixo>_senseN, e o
    dicbio:semanticEtymon das hipóteses passa a apontar para o novo nome.
    Depois disso, a M1 trata o étimo normalmente.
    """
    log = []
    g = Graph()
    g.parse(data=texto, format="turtle", publicID=publicID)
    com_entrada = set(g.objects(None, ONTOLEX.sense))
    for s in sorted(com_entrada):
        nome = local(s)
        if not nome or g.value(s, DCT.language) is None or not isinstance(g.value(s, DCT.language), URIRef):
            continue
        m = re.fullmatch(r"entry_(.+)_sense(\d+)", nome)
        code = str(g.value(s, DCT.language))[len(GLOTTO):]
        if not m or code not in LINGUAS:
            continue
        blocos = blocos_do_sujeito(texto, nome)
        if len(blocos) != 2:
            continue
        etimo = [b for b in blocos if re.search(r"\b(ontolex:writtenRep|dcterms:language)\b", texto[b[0]:b[1]])]
        if len(etimo) != 1:
            continue
        ini, fim = etimo[0]
        sufixo = LINGUAS[code][1]
        novo_nome = f"entry_{m.group(1)}_{sufixo}_sense{m.group(2)}"
        if DBRES + novo_nome in usados or (URIRef(DBRES + novo_nome), None, None) in g:
            raise ValueError(f"M0: nome {novo_nome} já existe")
        bloco_etimo = texto[ini:fim]
        resto = texto[:ini] + texto[fim:]
        # hipóteses que apontam para o étimo
        padrao_ref = re.compile(r"(dicbio:semanticEtymon\s+)dbres:" + re.escape(nome) + r"(?=[\s;.,])")
        antes, n1 = padrao_ref.subn(r"\1dbres:" + novo_nome, texto[:ini])
        depois, n2 = padrao_ref.subn(r"\1dbres:" + novo_nome, texto[fim:])
        n_refs = n1 + n2
        if n_refs == 0:
            continue
        novo_texto = antes + "dbres:" + novo_nome + bloco_etimo[len("dbres:" + nome):] + depois

        # conferência: grafo novo == resto (com semanticEtymon renomeado) + étimo renomeado
        g_resto = Graph().parse(data=resto, format="turtle", publicID=publicID)
        g_etimo = Graph().parse(data=prefixos + bloco_etimo, format="turtle", publicID=publicID)
        assert set(g_resto) | set(g_etimo) == set(g), "M0: separação de blocos não reproduz o grafo"
        novo_iri = URIRef(DBRES + novo_nome)
        esperado = {(a, p, novo_iri if (p == DICBIO.semanticEtymon and o == s) else o) for a, p, o in g_resto}
        esperado |= {(novo_iri, p, o) for _, p, o in g_etimo}
        obtido = set(Graph().parse(data=novo_texto, format="turtle", publicID=publicID))
        if obtido != esperado:
            raise AssertionError(f"M0: grafo inesperado ao renomear {nome}")
        texto = novo_texto
        g = Graph().parse(data=texto, format="turtle", publicID=publicID)
        usados[DBRES + novo_nome].add(arquivo.name)
        log.append(f"M0 {nome}: étimo com o mesmo IRI da acepção portuguesa → renomeado para {novo_nome} "
                   f"({n_refs} semanticEtymon atualizado(s))")
    return texto, log


# ----------------------------------------------------------------------------
# Migração de um arquivo
# ----------------------------------------------------------------------------
class Migracao:
    def __init__(self, arquivo, usados, fontes_conhecidas):
        self.arquivo = arquivo
        bruto = arquivo.read_bytes().decode("utf-8")
        self.crlf = "\r\n" in bruto
        self.original = bruto.replace("\r\n", "\n")  # texto do arquivo, para o diff
        self.prefixos = "".join(l + "\n" for l in self.original.splitlines() if l.startswith("@prefix"))
        publicID = str(arquivo.resolve().as_uri())
        # M0 roda antes e já se confere sozinha; as demais partem do texto dela
        self.texto, log_m0 = m0_separar_colisoes(self.original, self.prefixos, publicID, usados, arquivo)
        self.g = Graph()
        self.g.parse(data=self.texto, format="turtle", publicID=publicID)
        self.usados = usados
        self.fontes = fontes_conhecidas
        self.remover = set()  # triplas removidas
        self.acrescentar = Graph()  # triplas novas
        self.edicoes = []  # (ini, fim, novo_texto)
        self.log = list(log_m0)  # o que foi feito
        self.pendencias = []  # o que fica para revisão

    # --- registro de edições -------------------------------------------------
    def editar(self, ini, fim, novo, triplas_removidas, texto_novo_para_parse):
        for a, b, _ in self.edicoes:
            if not (fim <= a or ini >= b):
                raise ValueError("edições sobrepostas")
        self.edicoes.append((ini, fim, novo))
        self.remover |= set(triplas_removidas)
        if texto_novo_para_parse:
            self.acrescentar.parse(data=self.prefixos + texto_novo_para_parse, format="turtle")

    def nome_livre(self, base, sufixo):
        iri = DBRES + base
        if iri not in self.usados and not (URIRef(iri), None, None) in self.g:
            return base
        alt = f"{base}_{sufixo}"
        if DBRES + alt in self.usados or (URIRef(DBRES + alt), None, None) in self.g:
            raise ValueError(f"nomes {base} e {alt} já existem")
        return alt

    def entrada_dona(self, acepcao_etimo):
        """Entrada do verbete cuja hipótese aponta para este étimo."""
        for h in self.g.subjects(DICBIO.semanticEtymon, acepcao_etimo):
            for sentido in self.g.subjects(LEMONETY.etymology, h):
                for e in self.g.subjects(ONTOLEX.sense, sentido):
                    return e
        return None

    # --- M1 -------------------------------------------------------------------
    def m1_etimos(self):
        g = self.g
        com_entrada = set(g.objects(None, ONTOLEX.sense))
        for s in sorted(set(g.subjects(RDF.type, ONTOLEX.LexicalSense))):
            if s in com_entrada:
                continue
            nome_s = local(s)
            lingua = g.value(s, DCT.language)
            wrs = list(g.objects(s, ONTOLEX.writtenRep))
            if not wrs and lingua is None:
                continue  # não é o padrão antigo
            if not (isinstance(lingua, URIRef) and str(lingua).startswith(GLOTTO)):
                self.pendencias.append(
                    f"{nome_s}: língua em texto livre ({lingua!r}) — caso especial, revisão manual"
                )
                continue
            code = str(lingua)[len(GLOTTO):]
            if code not in LINGUAS or len(wrs) != 1:
                self.pendencias.append(f"{nome_s}: língua {code} ou writtenRep inesperados — revisão manual")
                continue
            m = re.fullmatch(r"entry_(.+)_sense(\d+)", nome_s or "")
            if not m or not nome_valido(m.group(1)):
                self.pendencias.append(f"{nome_s}: nome fora da convenção entry_X_senseN — revisão manual")
                continue
            lema, tag, sufixo = m.group(1), *LINGUAS[code]
            predicados_previstos = {RDF.type, DCT.language, DCT.source, ONTOLEX.writtenRep,
                                    SKOS.definition, SKOS.exactMatch}
            extras = set(g.predicates(s)) - predicados_previstos
            if extras:
                self.pendencias.append(f"{nome_s}: propriedades inesperadas {extras} — revisão manual")
                continue
            bloco = achar_bloco(self.texto, s, g)
            if not bloco:
                self.pendencias.append(f"{nome_s}: bloco não localizado no texto — revisão manual")
                continue

            dona = self.entrada_dona(s)
            n_entrada = self.nome_livre(f"entry_{lema}", sufixo)
            n_forma = self.nome_livre(f"form_{lema}", sufixo)
            criadores = sorted(g.objects(dona, DCT.creator)) if dona else []
            classe = g.value(dona, LEXINFO.partOfSpeech) if dona else None
            definicoes = list(g.objects(s, SKOS.definition))
            externos = list(g.objects(s, SKOS.exactMatch))
            fontes = list(g.objects(s, DCT.source))
            escrita = str(wrs[0])

            pm = g.namespace_manager.normalizeUri
            L = [f"dbres:{n_entrada} a ontolex:LexicalEntry ;",
                 f'    dcterms:created "{HOJE}"^^xsd:date ;']
            if criadores:
                L.append("    dcterms:creator " + ",\n        ".join(pm(c) for c in criadores) + " ;"
                         + "  # REVISAR: criadores copiados da entrada principal")
            else:
                L.append("    # REVISAR: falta dcterms:creator")
            L.append(f"    dcterms:language glotto:{code} ;")
            if classe is not None:
                L.append(f"    lexinfo:partOfSpeech {pm(classe)} ;  # REVISAR: classe copiada da entrada principal")
            else:
                L.append("    # REVISAR: falta lexinfo:partOfSpeech")
            for ext in externos:
                L.append(f"    dicbio:externalEntry <{ext}> ;")
            L.append(f"    ontolex:canonicalForm dbres:{n_forma} ;")
            L.append(f"    ontolex:sense {pm(s)} .")
            L.append("")
            L.append(f"dbres:{n_forma} a ontolex:Form ;")
            L.append(f"    ontolex:writtenRep {turtle_literal(escrita)}@{tag} .")
            L.append("")

            nomes_atest = []
            atest_txt = []
            for fonte in fontes:
                if isinstance(fonte, URIRef) and str(fonte).startswith(DBSRC):
                    slug = re.sub(r"^(source|work)_", "", str(fonte)[len(DBSRC):])
                    n_at = self.nome_livre(f"attestation_{lema}_sense{m.group(2)}_{slug}", sufixo)
                    corpo = [f"dbres:{n_at} a dicbio:Attestation ;",
                             f"    dcterms:source {pm(fonte)} .",
                             "    # REVISAR: falta dicbio:attestationDate (recuperar a data na fonte)"]
                    if fonte not in self.fontes:
                        corpo.append(f"    # REVISAR: {pm(fonte)} não existe em sources.ttl")
                else:
                    n_at = self.nome_livre(f"attestation_{lema}_sense{m.group(2)}", sufixo)
                    corpo = [f"dbres:{n_at} a dicbio:Attestation ;",
                             f"    dcterms:source {turtle_literal(fonte)} .",
                             "    # REVISAR: fonte em texto livre (modelo antigo) — criar a fonte em sources.ttl",
                             "    #          (dbsrc:source_... ou dbsrc:work_...) e acrescentar dicbio:attestationDate"]
                nomes_atest.append(n_at)
                atest_txt += corpo + [""]

            props = ["a ontolex:LexicalSense"]
            for d in definicoes:
                lang = f"@{d.language}" if d.language else ""
                props.append(f"skos:definition {turtle_literal(d)}{lang}")
            if nomes_atest:
                props.append("dicbio:hasAttestation " + ",\n        ".join(f"dbres:{a}" for a in nomes_atest))
            L.append(f"{pm(s)} " + " ;\n    ".join(props) + " .")
            if not definicoes:
                L.append("    # REVISAR: falta skos:definition (sentido do étimo; ver a argumentação)")
            L.append("")
            L += atest_txt
            novo = "\n".join(L).rstrip("\n") + "\n\n"

            ini, fim = bloco_com_linha_seguinte(self.texto, *bloco)
            removidas = list(g.triples((s, None, None)))
            # a acepção mantém o tipo e a definição; elas são re-declaradas no bloco novo
            self.editar(ini, fim, novo, removidas, novo)
            self.usados[DBRES + n_entrada].add(self.arquivo.name)
            self.usados[DBRES + n_forma].add(self.arquivo.name)
            for a in nomes_atest:
                self.usados[DBRES + a].add(self.arquivo.name)
            self.log.append(
                f"M1 {nome_s}: criadas {n_entrada}, {n_forma}"
                + (f", {', '.join(nomes_atest)}" if nomes_atest else "")
            )

    # --- M2 -------------------------------------------------------------------
    def m2_lingua_entrada(self):
        g = self.g
        for e in sorted(set(g.subjects(RDF.type, ONTOLEX.LexicalEntry))):
            if g.value(e, DCT.language) is not None:
                continue
            formas = list(g.objects(e, ONTOLEX.canonicalForm)) + list(g.objects(e, ONTOLEX.otherForm))
            tags = {w.language for f in formas for w in g.objects(f, ONTOLEX.writtenRep)}
            if tags != {"pt"}:
                self.pendencias.append(f"{local(e)}: sem dcterms:language e formas com etiquetas {tags} — revisão manual")
                continue
            bloco = achar_bloco(self.texto, e, g)
            if not bloco:
                self.pendencias.append(f"{local(e)}: bloco não localizado (M2)")
                continue
            ini, _ = bloco
            fim_linha = self.texto.index("\n", ini) + 1
            linha = self.texto[ini:fim_linha]
            if not linha.rstrip().endswith(";"):
                self.pendencias.append(f"{local(e)}: primeira linha da entrada não termina em ';' (M2)")
                continue
            novo = linha + "    dcterms:language glotto:port1283 ;\n"
            trecho = f"<{e}> dcterms:language glotto:port1283 ."
            self.editar(ini, fim_linha, novo, [], trecho)
            self.log.append(f"M2 {local(e)}: acrescentado dcterms:language glotto:port1283")

    # --- M3 -------------------------------------------------------------------
    def m3_rotulos_formas(self):
        g = self.g
        dona_da_forma = {}
        for e in g.subjects(RDF.type, ONTOLEX.LexicalEntry):
            for f in list(g.objects(e, ONTOLEX.canonicalForm)) + list(g.objects(e, ONTOLEX.otherForm)):
                dona_da_forma[f] = e
        for f in sorted(set(g.subjects(RDF.type, ONTOLEX.Form))):
            rotulos = list(g.objects(f, RDFS.label))
            if not rotulos:
                continue
            if len(rotulos) != 1 or str(rotulos[0]) not in ROTULOS_FORMA:
                self.pendencias.append(f"{local(f)}: rdfs:label {[str(r) for r in rotulos]} não reconhecido — revisão manual")
                continue
            genero, numero = ROTULOS_FORMA[str(rotulos[0])]
            e = dona_da_forma.get(f)
            substantivo = e is not None and g.value(e, LEXINFO.partOfSpeech) == LEXINFO.noun
            if substantivo:
                genero = None  # nos substantivos, o gênero fica na entrada
            atuais_n = set(g.objects(f, LEXINFO.number))
            atuais_g = set(g.objects(f, LEXINFO.gender))
            if (atuais_n and atuais_n != {LEXINFO[numero]}) or (genero and atuais_g and atuais_g != {LEXINFO[genero]}):
                self.pendencias.append(f"{local(f)}: rótulo '{rotulos[0]}' conflita com lexinfo já presente — revisão manual")
                continue
            bloco = achar_bloco(self.texto, f, g)
            if not bloco:
                self.pendencias.append(f"{local(f)}: bloco não localizado (M3)")
                continue
            ini, fim = bloco
            trecho = self.texto[ini:fim]
            m = re.search(r'^([ \t]+)rdfs:label\s+"[^"\n]*"@pt\s*([;.])[ \t]*$', trecho, re.M)
            if not m:
                self.pendencias.append(f"{local(f)}: linha do rdfs:label em formato inesperado (M3)")
                continue
            novos = []
            if not atuais_n:
                novos.append(f"lexinfo:number lexinfo:{numero}")
            if genero and not atuais_g:
                novos.append(f"lexinfo:gender lexinfo:{genero}")
            fim_char = m.group(2)
            if novos:
                linhas = [f"{m.group(1)}{p} ;" for p in novos]
                linhas[-1] = linhas[-1][:-1] + fim_char
                subst = "\n".join(linhas)
            else:
                subst = None
            a, b = ini + m.start(), ini + m.end()
            if subst is None:
                if fim_char == ";":
                    b = ini + m.end() + 1  # remove a linha inteira
                    subst = ""
                else:
                    self.pendencias.append(f"{local(f)}: rótulo é a última propriedade e não há o que pôr no lugar (M3)")
                    continue
            novas_triplas = "".join(f"<{f}> {p} .\n" for p in novos)
            self.editar(a, b, subst, [(f, RDFS.label, rotulos[0])], novas_triplas)
            self.log.append(f"M3 {local(f)}: rótulo '{rotulos[0]}' → {', '.join(novos) or '(já havia lexinfo)'}")

    # --- M4 -------------------------------------------------------------------
    def m4_exactmatch_entrada(self):
        g = self.g
        for e in sorted(set(g.subjects(RDF.type, ONTOLEX.LexicalEntry))):
            alvos = list(g.objects(e, SKOS.exactMatch))
            if not alvos:
                continue
            bloco = achar_bloco(self.texto, e, g)
            if not bloco:
                self.pendencias.append(f"{local(e)}: bloco não localizado (M4)")
                continue
            ini, fim = bloco
            trecho = self.texto[ini:fim]
            ocorr = list(re.finditer(r"\bskos:exactMatch\b", trecho))
            if len(ocorr) != 1:
                self.pendencias.append(f"{local(e)}: skos:exactMatch em formato inesperado (M4)")
                continue
            a = ini + ocorr[0].start()
            b = ini + ocorr[0].end()
            novas = "".join(f"<{e}> dicbio:externalEntry <{x}> .\n" for x in alvos)
            self.editar(a, b, "dicbio:externalEntry", [(e, SKOS.exactMatch, x) for x in alvos], novas)
            self.log.append(f"M4 {local(e)}: skos:exactMatch → dicbio:externalEntry")

    # --- aplicação e conferência ----------------------------------------------
    def resultado(self):
        texto = self.texto
        for ini, fim, novo in sorted(self.edicoes, reverse=True):
            texto = texto[:ini] + novo + texto[fim:]
        return texto

    def conferir(self, novo_texto):
        novo = Graph()
        novo.parse(data=novo_texto, format="turtle", publicID=str(self.arquivo.resolve().as_uri()))
        esperado = set(self.g) - self.remover | set(self.acrescentar)
        obtido = set(novo)
        if esperado != obtido:
            faltam = esperado - obtido
            sobram = obtido - esperado
            raise AssertionError(
                f"grafo resultante difere do esperado: {len(faltam)} faltando, {len(sobram)} sobrando\n"
                + "\n".join(f"  - {t}" for t in list(faltam)[:5])
                + "\n" + "\n".join(f"  + {t}" for t in list(sobram)[:5])
            )

    def rodar(self):
        self.m1_etimos()
        self.m2_lingua_entrada()
        self.m3_rotulos_formas()
        self.m4_exactmatch_entrada()
        novo = self.resultado()
        if self.edicoes:
            self.conferir(novo)
        return novo


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Migra verbetes para o modelo atual.")
    ap.add_argument("verbetes", nargs="*", help="nomes dos verbetes (sem .ttl)")
    ap.add_argument("--todos", action="store_true", help="todos os verbetes de data/entries")
    ap.add_argument("--aplicar", action="store_true", help="grava as mudanças (sem isso, só mostra o diff)")
    ap.add_argument("--sem-diff", action="store_true", help="não mostra o diff, só o resumo")
    args = ap.parse_args()

    if args.todos:
        arquivos = sorted(ENTRIES.glob("*.ttl"))
    else:
        arquivos = [ENTRIES / (v if v.endswith(".ttl") else v + ".ttl") for v in args.verbetes]
    if not arquivos:
        ap.error("indique verbetes ou --todos")

    usados = carregar_nomes_existentes()
    fontes = Graph()
    fontes.parse(SOURCES)
    fontes_conhecidas = set(fontes.subjects())

    total_mod = 0
    for arq in arquivos:
        if not arq.exists():
            print(f"!! {arq.name}: não encontrado")
            continue
        try:
            mig = Migracao(arq, usados, fontes_conhecidas)
            novo = mig.rodar()
        except Exception as e:
            print(f"!! {arq.name}: ERRO — {e}\n")
            continue
        print(f"=== {arq.name}: {len(mig.log)} mudança(s), {len(mig.pendencias)} pendência(s)")
        for l in mig.log:
            print(f"   {l}")
        for p in mig.pendencias:
            print(f"   PENDENTE {p}")
        if novo != mig.original:
            total_mod += 1
            if not args.sem_diff:
                diff = difflib.unified_diff(
                    mig.original.splitlines(keepends=True), novo.splitlines(keepends=True),
                    fromfile=f"a/{arq.name}", tofile=f"b/{arq.name}",
                )
                sys.stdout.writelines(diff)
            if args.aplicar:
                saida = novo.replace("\n", "\r\n") if mig.crlf else novo
                arq.write_bytes(saida.encode("utf-8"))
        print()
    print(f"{total_mod} arquivo(s) {'alterado(s)' if args.aplicar else 'a alterar'} de {len(arquivos)}.")


if __name__ == "__main__":
    main()
