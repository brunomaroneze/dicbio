"""Gera o site de conferência em revisao/_site.

  python revisao/gerar_site.py                   (como no GitHub: imagens da internet)
  python revisao/gerar_site.py --local           (imagens das pastas locais)
  python revisao/gerar_site.py --local --todas   (inclui obras com "ativa": false)
"""
import json
import shutil
import sys
from pathlib import Path

from nucleo import hash_texto, paginas

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent


def le(caminho):
    """Lê sem converter os fins de linha, para o XML ser regravado igual."""
    with open(caminho, encoding="utf-8", newline="") as f:
        return f.read()


def main():
    local, todas = "--local" in sys.argv, "--todas" in sys.argv
    cfg = json.loads(le(AQUI / "config.json"))
    base = f"/{cfg['pasta_obras']}/" if local else cfg["base_imagens"]
    saida = AQUI / "_site"
    if saida.exists():
        shutil.rmtree(saida)
    shutil.copytree(AQUI / "site", saida)
    (saida / "dados").mkdir()
    indice = []
    for obra in cfg["obras"]:
        arq = RAIZ / cfg["pasta_obras"] / f"{obra['id']}.xml"
        if not (obra["ativa"] or todas):
            continue
        if not arq.exists():
            print("AVISO: não existe", arq)
            continue
        lista = []
        for p in paginas(le(arq)):
            f = p.facs
            img = f if not f or f.startswith(("http://", "https://")) else base + f
            conf = AQUI / "conferidas" / obra["id"] / f"{p.id}.json"
            lista.append({
                "id": p.id, "n": p.n, "img": img,
                "conferida": json.loads(le(conf))["revisor"] if conf.exists() else "",
                "segs": [{"t": s.texto, "h": hash_texto(s.texto), "tipo": s.tipo,
                          "cont": s.continua, "nota": s.nota} for s in p.segs]})
        (saida / "dados" / f"{obra['id']}.json").write_text(
            json.dumps(lista, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        indice.append({"id": obra["id"], "titulo": obra["titulo"]})
        print(obra["id"], len(lista), "páginas")
    (saida / "dados" / "indice.json").write_text(
        json.dumps({"repositorio": cfg["repositorio"], "obras": indice}, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
