"""Grava nos verbetes as datas preenchidas na planilha de atestações.

Lê relatorios/datas_atestacoes.csv (gerada por scripts/datas_atestacoes.py e
preenchida à mão) e, para cada linha com "ano" numérico:

  - acrescenta  dicbio:attestationDate "AAAA"^^xsd:gYear  à atestação
    (anos a.C. negativos: -160 → "-0160");
  - tira o comentário "# REVISAR: falta dicbio:attestationDate ..." e, nas
    fontes em texto livre, o trecho "e acrescentar dicbio:attestationDate";
  - copia a "nota" da planilha como comentário logo abaixo da atestação:
      # NOTA (datas): ...     — informação
      # REVISAR (datas): ...  — quando a nota pede uma ação ("é preciso",
                                "falta", "verificar", "rever"...)
    As notas ficam como comentário (não como tripla) para a revisão
    posterior decidir o que vira dado (nova atestação, étimo grego etc.).
  - se a fonte é uma obra primária com data própria em sources.ttl e o ano
    da planilha é outro, acrescenta um "# REVISAR" apontando a diferença:
    a data de uma atestação deve ser a da fonte citada.

Linhas com "ano" não numérico (ex.: "sem data") são ignoradas e listadas.

As edições são feitas no texto (comentários e formatação preservados) e
conferidas com rdflib: o grafo novo tem de ser o antigo mais as datas.

Uso:
    python scripts/gravar_datas.py            # mostra o que faria
    python scripts/gravar_datas.py --aplicar  # grava
"""

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, XSD

sys.path.insert(0, str(Path(__file__).resolve().parent))
from migrar_verbetes import fim_da_declaracao  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "data" / "entries"
SOURCES = ROOT / "data" / "sources.ttl"
PLANILHA = ROOT / "relatorios" / "datas_atestacoes.csv"

DICBIO = Namespace("https://dicbio.fflch.usp.br/ontology/")
DCT = Namespace("http://purl.org/dc/terms/")
BIBO = Namespace("http://purl.org/ontology/bibo/")
DBRES = "https://dicbio.fflch.usp.br/recurso/"

ACAO = re.compile(r"\b(é preciso|precisa|precisamos|falta|verificar|rever|revisto|tem que|será preciso|"
                  r"podemos colocar|inserir|incluir|descrever|registrar|encontrar)\b", re.I)


def gyear(ano):
    return f"-{abs(ano):04d}" if ano < 0 else f"{ano:04d}"


def ler_planilha(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def gravar_arquivo(arq, linhas, fontes, aplicar):
    bruto = arq.read_bytes().decode("utf-8")
    crlf = "\r\n" in bruto
    texto = bruto.replace("\r\n", "\n")
    g = Graph().parse(data=texto, format="turtle")
    esperado = set(g)
    log, problemas = [], []
    edicoes = []

    for l in linhas:
        nome = l["atestacao"].split(":", 1)[1]
        iri = URIRef(DBRES + nome)
        ano = int(l["ano"].strip())
        if g.value(iri, DICBIO.attestationDate) is not None:
            problemas.append(f"{nome}: já tem attestationDate — ignorada")
            continue
        achados = list(re.finditer(r"^dbres:" + re.escape(nome) + r"(?=\s)", texto, re.M))
        if len(achados) != 1:
            problemas.append(f"{nome}: bloco não localizado ({len(achados)} ocorrências)")
            continue
        ini = achados[0].start()
        fim = fim_da_declaracao(texto, ini)  # logo após o '.'
        antes = texto[ini:fim - 1].rstrip()
        ultima = antes.rsplit("\n", 1)[-1]
        if re.search(r'#[^"<>]*$', ultima):
            problemas.append(f"{nome}: a última linha da declaração termina em comentário — edite à mão")
            continue
        novo = antes + f' ;\n    dicbio:attestationDate "{gyear(ano)}"^^xsd:gYear .'

        # comentários que seguem a declaração
        m = re.compile(r"(?:\n[ \t]*#[^\n]*)*").match(texto, fim)
        coment = texto[fim:m.end()]
        coment = re.sub(r"\n[ \t]*# REVISAR: falta dicbio:attestationDate[^\n]*", "", coment)
        coment = coment.replace("(dbsrc:source_... ou dbsrc:work_...) e acrescentar dicbio:attestationDate",
                                "(dbsrc:source_... ou dbsrc:work_...)")

        extras = []
        nota = " ".join(l.get("nota", "").split())
        if nota:
            rotulo = "REVISAR (datas)" if ACAO.search(nota) else "NOTA (datas)"
            extras.append(f"    # {rotulo}: {nota}")
        fonte = g.value(iri, DCT.source)
        if isinstance(fonte, URIRef) and (fonte, RDF.type, BIBO.ReferenceSource) not in fontes:
            issued = fontes.value(fonte, DCT.issued)
            if issued is not None and int(str(issued)[:5].rstrip("-") or 0) != ano:
                pm = g.namespace_manager.normalizeUri(fonte)
                extras.append(f"    # REVISAR (datas): o ano {ano} não é o da fonte {pm} ({issued}); "
                              "se a data vem de outra obra, a atestação precisa de outra fonte (ou crie uma segunda atestação)")
                problemas.append(f"{nome}: ano {ano} ≠ data da fonte {pm} ({issued}) — marcado com REVISAR")
        bloco_novo = novo + "".join("\n" + e for e in extras) + coment
        edicoes.append((ini, m.end(), bloco_novo))
        esperado.add((iri, DICBIO.attestationDate, Literal(gyear(ano), datatype=XSD.gYear)))
        log.append(f"{nome}: {gyear(ano)}" + (" + nota" if nota else ""))

    if not edicoes:
        return log, problemas, False
    for a, b, novo in sorted(edicoes, reverse=True):
        texto = texto[:a] + novo + texto[b:]
    if not re.search(r"^@prefix xsd:", texto, re.M):
        texto = "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n" + texto
    obtido = set(Graph().parse(data=texto, format="turtle"))
    if obtido != esperado:
        raise AssertionError(f"{arq.name}: grafo resultante difere do esperado "
                             f"({len(esperado - obtido)} faltando, {len(obtido - esperado)} sobrando)")
    if aplicar:
        arq.write_bytes((texto.replace("\n", "\r\n") if crlf else texto).encode("utf-8"))
    return log, problemas, True


def main():
    ap = argparse.ArgumentParser(description="Grava as datas da planilha nos verbetes.")
    ap.add_argument("--planilha", type=Path, default=PLANILHA)
    ap.add_argument("--aplicar", action="store_true", help="grava (sem isso, só mostra)")
    args = ap.parse_args()

    fontes = Graph().parse(SOURCES)
    por_arquivo = defaultdict(list)
    ignoradas = []
    for l in ler_planilha(args.planilha):
        if re.fullmatch(r"-?\d{1,4}", l["ano"].strip()) and l["ano"].strip() not in ("0", "-0"):
            por_arquivo[l["arquivo"]].append(l)
        else:
            ignoradas.append(f"{l['atestacao']}: ano {l['ano']!r}")

    total, alterados, todos_problemas = 0, 0, []
    for nome_arq, linhas in sorted(por_arquivo.items()):
        log, problemas, mudou = gravar_arquivo(ENTRIES / nome_arq, linhas, fontes, args.aplicar)
        total += len(log)
        alterados += mudou
        todos_problemas += [f"{nome_arq}: {p}" for p in problemas]
        print(f"{nome_arq}: " + "; ".join(log))
    print(f"\n{total} data(s) em {alterados} arquivo(s) {'gravada(s)' if args.aplicar else '(simulação)'}.")
    if ignoradas:
        print("\nLinhas ignoradas (ano não numérico):")
        for i in ignoradas:
            print(f"  {i}")
    if todos_problemas:
        print("\nAvisos:")
        for p in todos_problemas:
            print(f"  {p}")


if __name__ == "__main__":
    main()
