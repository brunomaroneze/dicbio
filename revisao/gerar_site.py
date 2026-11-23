"""Gera o site de conferência em revisao/_site.

  python revisao/gerar_site.py --local           (imagens das pastas locais)
  python revisao/gerar_site.py --local --todas   (inclui obras com "ativa": false)
  python revisao/gerar_site.py --saida PASTA --imagens PASTA   (como na VPS)

Com --imagens, as páginas cujo facs é um endereço da internet usam a cópia
OBRA_imagens/IDPAGINA.jpg, se existir (ver baixar_imagens.py).
"""
import argparse
import json
import shutil
from pathlib import Path

from nucleo import hash_texto, paginas

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent


def le(caminho):
    """Lê sem converter os fins de linha, para o XML ser regravado igual."""
    with open(caminho, encoding="utf-8", newline="") as f:
        return f.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--saida", type=Path, default=AQUI / "_site")
    ap.add_argument("--imagens", type=Path)
    arg = ap.parse_args()
    cfg = json.loads(le(AQUI / "config.json"))
    base = f"/{cfg['pasta_obras']}/" if arg.local else cfg["base_imagens"]
    # Gera ao lado e só troca no fim: se algo falhar, o site anterior continua no ar.
    final = arg.saida.resolve()
    saida = final.with_name(final.name + ".novo")
    if saida.exists():
        shutil.rmtree(saida)
    shutil.copytree(AQUI / "site", saida)
    (saida / "dados").mkdir()
    indice = []
    for obra in cfg["obras"]:
        arq = RAIZ / cfg["pasta_obras"] / f"{obra['id']}.xml"
        if not (obra["ativa"] or arg.todas):
            continue
        if not arq.exists():
            print("AVISO: não existe", arq)
            continue
        lista = []
        for p in paginas(le(arq)):
            f = p.facs
            remota = f.startswith(("http://", "https://"))
            img = f if not f or remota else base + f
            copia = f"{obra['id']}_imagens/{p.id}.jpg"
            if remota and arg.imagens and (arg.imagens / copia).exists():
                img = base + copia
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
    if final.exists():
        shutil.rmtree(final)
    saida.rename(final)


if __name__ == "__main__":
    main()
