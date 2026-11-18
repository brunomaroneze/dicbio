"""
Etapa 1 da marcação TEI de uma obra do corpus: mapa de páginas.

Lê o TXT da obra, localiza os marcadores de página do tipo "(12)", "( 205 )", "(xiv)",
confere a sequência numérica, associa cada página à imagem digitalizada correspondente
e gera um CSV para revisão.

Situações possíveis no CSV:
  ok              marcador lido corretamente e coerente com os vizinhos
  corrigido       número lido incoerente, mas só há uma página possível naquela posição
  verificar       número lido incoerente e há mais de uma página possível
  conferido       marcador do TXT cuja página foi conferida manualmente na imagem (--ajustes)
  localizado      página sem marcador no TXT, cuja posição foi localizada na imagem (--ajustes):
                  o <pb/> entra no início de linha_txt ou, se preenchido, antes do trecho indicado
  sem_marcador    página que existe nas imagens, mas não tem marcador no TXT
  sem_numero      página sem número impresso (página de rosto, verso etc.)

Uso (exemplo para o Manual do Fazendeiro, de Imbert):
  python scripts/tei_mapa_paginas.py corpus_digital/obras/fazendeiroimbert.txt \
      --imagens fazendeiroimbert_imagens --prefixo b29341152_ \
      --inicio-corpo "MANUAL DO FAZENDEIRO." \
      --romanas 5-18 --desloc-romanas 4 \
      --arabicas 1-340 --desloc-arabicas 22 \
      --sem-numero 7:rosto 8:verso_rosto \
      --ajustes corpus_digital/obras/fazendeiroimbert_paginas_ajustes.csv
"""
import argparse
import csv
import re
import sys
from pathlib import Path

ROMANOS = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}


def romano_para_int(s):
    s = s.lower().replace("j", "i")  # grafia antiga: vij, xiij
    if not s or any(ch not in ROMANOS for ch in s):
        return None
    total = 0
    for a, b in zip(s, s[1:] + " "):
        v = ROMANOS[a]
        total += -v if b != " " and ROMANOS[b] > v else v
    return total


def int_para_romano(n):
    pares = [(100, "c"), (90, "xc"), (50, "l"), (40, "xl"), (10, "x"),
             (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, r in pares:
        while n >= v:
            out += r
            n -= v
    return out


MARCADOR = re.compile(r"^\s*\(\s*([0-9]+|[ivxlcj]+)\s*\)\s*(.*)$", re.IGNORECASE)


def intervalo(s):
    a, b = s.split("-")
    return int(a), int(b)


def ler_marcadores(linhas, linha_inicio_corpo, prim_arabica):
    """Devolve lista de dicts com os candidatos a marcador de página, em ordem."""
    marcs = []
    ultimo = {"romana": 0, "arabica": prim_arabica - 1}
    for i, linha in enumerate(linhas, start=1):
        m = MARCADOR.match(linha)
        if not m:
            continue
        bruto, resto = m.group(1), m.group(2).strip()
        serie = "romana" if i < linha_inicio_corpo else "arabica"
        valor = int(bruto) if bruto.isdigit() else romano_para_int(bruto)
        if valor is None:
            continue
        # Linha com texto após o número: pode ser nota de rodapé "(1) Texto...".
        # Só a aceitamos como marcador se o número estiver perto do esperado.
        if resto and serie == "arabica" and abs(valor - (ultimo[serie] + 1)) > 3:
            continue
        marcs.append({"linha": i, "bruto": linha.strip()[:20] if not resto else f"({bruto})",
                      "serie": serie, "lido": valor, "resto": resto})
        ultimo[serie] = valor
    return marcs


def atribuir(marcs, primeira, ultima):
    """Atribui a cada marcador a página que ele representa (dentro de uma série)."""
    n = len(marcs)
    # Âncoras: marcadores cujo valor é coerente com pelo menos um vizinho.
    for k, m in enumerate(marcs):
        ant = marcs[k - 1]["lido"] if k > 0 else primeira - 1
        prox = marcs[k + 1]["lido"] if k + 1 < n else ultima + 1
        m["ancora"] = primeira <= m["lido"] <= ultima and (m["lido"] == ant + 1 or m["lido"] == prox - 1)
    # Garante monotonia entre âncoras (descarta âncoras que voltam para trás).
    maior = primeira - 1
    for m in marcs:
        if m["ancora"]:
            if m["lido"] <= maior:
                m["ancora"] = False
            else:
                maior = m["lido"]
    # Resolve os trechos entre âncoras.
    k = 0
    while k < n:
        if marcs[k]["ancora"]:
            marcs[k]["pagina"] = marcs[k]["lido"]
            marcs[k]["situacao"] = "ok"
            marcs[k]["candidatas"] = ""
            k += 1
            continue
        j = k
        while j < n and not marcs[j]["ancora"]:
            j += 1
        lo = marcs[k - 1]["lido"] + 1 if k > 0 else primeira
        hi = marcs[j]["lido"] - 1 if j < n else ultima
        bloco = marcs[k:j]
        cands = list(range(lo, hi + 1))
        if len(cands) == len(bloco):
            for m, p in zip(bloco, cands):
                m["pagina"], m["candidatas"] = p, ""
                m["situacao"] = "ok" if m["lido"] == p else "corrigido"
        else:
            for m in bloco:
                m["pagina"] = None
                m["situacao"] = "verificar"
                m["candidatas"] = f"{lo}-{hi}" if lo != hi else str(lo)
        k = j


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("txt")
    ap.add_argument("--imagens", required=True, help="pasta das imagens, relativa ao XML")
    ap.add_argument("--prefixo", required=True)
    ap.add_argument("--ext", default=".jpg")
    ap.add_argument("--inicio-corpo", required=True, help="linha (texto exato) onde começa a numeração arábica")
    ap.add_argument("--romanas", type=intervalo, help="ex.: 5-18")
    ap.add_argument("--desloc-romanas", type=int, default=0, help="imagem = página romana + deslocamento")
    ap.add_argument("--arabicas", type=intervalo, required=True, help="ex.: 1-340")
    ap.add_argument("--desloc-arabicas", type=int, required=True, help="imagem = página + deslocamento")
    ap.add_argument("--sem-numero", nargs="*", default=[], help="imagem:descrição, ex.: 7:rosto")
    ap.add_argument("--ajustes", help="CSV com páginas conferidas nas imagens (serie,pagina,linha_txt,antes_de,observacao)")
    ap.add_argument("--saida", help="CSV de saída (padrão: <txt>_paginas.csv)")
    a = ap.parse_args()

    txt = Path(a.txt)
    linhas = txt.read_text(encoding="utf-8").splitlines()
    try:
        inicio = next(i for i, l in enumerate(linhas, 1) if l.strip() == a.inicio_corpo.strip())
    except StopIteration:
        sys.exit(f"Linha de início do corpo não encontrada: {a.inicio_corpo!r}")

    marcs = ler_marcadores(linhas, inicio, a.arabicas[0])
    series = {"romana": a.romanas, "arabica": a.arabicas}
    desloc = {"romana": a.desloc_romanas, "arabica": a.desloc_arabicas}

    ajustes = []
    if a.ajustes:
        with open(a.ajustes, encoding="utf-8-sig", newline="") as f:
            ajustes = list(csv.DictReader(f))

    linhas_csv = []
    for serie, faixa in series.items():
        if not faixa:
            continue
        ms = [m for m in marcs if m["serie"] == serie]
        atribuir(ms, *faixa)
        # Ajustes conferidos manualmente nas imagens.
        for aj in (x for x in ajustes if x["serie"] == serie):
            p = romano_para_int(aj["pagina"]) if serie == "romana" else int(aj["pagina"])
            linha_aj = int(aj["linha_txt"])
            for m in ms:  # a página não pode ficar atribuída a outro marcador
                if m["pagina"] == p and m["linha"] != linha_aj:
                    m["pagina"], m["situacao"] = None, "verificar"
            alvo = next((m for m in ms if m["linha"] == linha_aj and not aj["antes_de"]), None)
            if alvo:
                alvo.update(pagina=p, situacao="conferido", candidatas="", obs=aj["observacao"])
            else:
                linhas_csv.append((linha_aj, serie, {
                    "linha": linha_aj, "bruto": "", "lido": "", "pagina": p, "situacao": "localizado",
                    "candidatas": "", "resto": "", "antes_de": aj["antes_de"], "obs": aj["observacao"]}))
        cobertas = {m["pagina"] for m in ms if m["pagina"] is not None}
        cobertas |= {m["pagina"] for _, s, m in linhas_csv if s == serie}
        for m in ms:
            linhas_csv.append((m["linha"], serie, m))
        # Páginas sem marcador: posição aproximada = antes do próximo marcador conhecido.
        for p in range(faixa[0], faixa[1] + 1):
            if p in cobertas:
                continue
            prox = next((m["linha"] for m in ms if m["pagina"] and m["pagina"] > p), None)
            linhas_csv.append((prox or len(linhas), serie, {
                "linha": "", "bruto": "", "lido": "", "pagina": p, "situacao": "sem_marcador",
                "candidatas": "", "resto": "", "antes_de_linha": prox}))

    def nome_img(n):
        return f"{a.imagens}/{a.prefixo}{n:04d}{a.ext}"

    saida = []
    for _, serie, m in linhas_csv:
        p = m["pagina"]
        n_pb = (int_para_romano(p) if serie == "romana" else str(p)) if p else ""
        img = nome_img(p + desloc[serie]) if p else ""
        linha = m["linha"]
        if m["situacao"] == "localizado":
            # sem marcador no TXT: o <pb/> entra na própria linha (antes do trecho indicado)
            trecho = m["antes_de"] or linhas[linha - 1].strip()
        else:
            trecho = m["resto"] or next((l.strip() for l in linhas[linha:linha + 6] if l.strip()), "") if linha else ""
        obs = m.get("obs", "")
        if m["situacao"] == "sem_marcador":
            obs = f"inserir antes da linha {m['antes_de_linha']} (posição exata a localizar)" if m["antes_de_linha"] else ""
        elif m["situacao"] == "verificar":
            obs = f"páginas possíveis: {m['candidatas']}"
        saida.append({
            "linha_txt": linha, "marcador_txt": m["bruto"], "serie": serie,
            "pagina_lida": (int_para_romano(m["lido"]) if serie == "romana" and m["lido"] else m["lido"]),
            "pagina": n_pb, "imagem": img, "situacao": m["situacao"],
            "inicio_pagina_txt": trecho[:70], "observacao": obs,
            "_ordem": (linha if linha else (m.get("antes_de_linha") or len(linhas)) - 0.5, p or 0)})

    for item in a.sem_numero:
        n, desc = item.split(":", 1)
        saida.append({"linha_txt": "", "marcador_txt": "", "serie": "", "pagina_lida": "",
                      "pagina": "", "imagem": nome_img(int(n)), "situacao": "sem_numero",
                      "inicio_pagina_txt": "", "observacao": desc, "_ordem": (-1, int(n))})

    # Ordem do texto (posição no TXT), que é também a ordem das páginas.
    saida.sort(key=lambda r: r["_ordem"])
    imgs = [int(re.search(r"(\d+)\D*$", r["imagem"]).group(1)) for r in saida if r["imagem"]]
    if imgs != sorted(imgs) or len(imgs) != len(set(imgs)):
        print("AVISO: a sequência de imagens não é estritamente crescente na ordem do texto.")

    out = Path(a.saida) if a.saida else txt.with_name(txt.stem + "_paginas.csv")
    campos = ["imagem", "pagina", "situacao", "linha_txt", "marcador_txt", "pagina_lida",
              "serie", "inicio_pagina_txt", "observacao"]
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        w.writerows(saida)

    from collections import Counter
    c = Counter(r["situacao"] for r in saida)
    print(f"{out}: {len(saida)} linhas")
    for k, v in sorted(c.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
