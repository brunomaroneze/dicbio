"""Atribui xml:id (pb_OBRA_0001...) aos elementos <pb> que ainda não o têm.

  python scripts/numerar_paginas.py

Os identificadores existentes nunca mudam; uma página incluída depois recebe o
próximo número livre. Só as tags <pb> são alteradas (o resto do arquivo fica igual).
Nas páginas com ana="#PaginacaoErronea" sem nReal, o script avisa.
"""
import re
from pathlib import Path

OBRAS = {
    "anatomiasantucci": "santucci",
    "carvalhoaviso": "carvalho",
    "compendio1brotero": "brotero1",
    "compendio2brotero": "brotero2",
    "diciovandelli": "vandelli",
    "fazendeiroimbert": "imbert",
    "novaesfebreamarela": "novaes",
    "observSemmedo": "semmedo",
}
PASTA = Path(__file__).resolve().parent.parent / "corpus_digital" / "obras"
PB_OU_COMENTARIO = re.compile(r"<!--.*?-->|<pb(?=[\s/>])[^>]*>", re.S)

for arquivo, obra in OBRAS.items():
    caminho = PASTA / f"{arquivo}.xml"
    with open(caminho, encoding="utf-8", newline="") as f:
        xml = f.read()
    usados = [int(n) for n in re.findall(rf'xml:id="pb_{obra}_(\d+)"', xml)]
    proximo = max(usados, default=0)
    novos = 0

    def numera(m):
        global proximo, novos
        tag = m.group()
        if tag.startswith("<!--"):
            return tag
        if "#PaginacaoErronea" in tag and "nReal=" not in tag:
            print(f"  {arquivo}: falta nReal em", re.sub(r"\s+", " ", tag)[:60])
        if "xml:id=" in tag:
            return tag
        proximo += 1
        novos += 1
        return f'<pb xml:id="pb_{obra}_{proximo:04d}"' + tag[3:]

    xml = PB_OU_COMENTARIO.sub(numera, xml)
    if novos:
        with open(caminho, "w", encoding="utf-8", newline="") as f:
            f.write(xml)
    print(f"{arquivo}: {novos} páginas numeradas")
