"""Copia, já reduzidas, as imagens de uma obra cujo facs aponta para a internet.

  python3 revisao/baixar_imagens.py OBRA PASTA_DESTINO [MÁXIMO]

Pode ser interrompido e repetido: pula o que já existe. Requer Pillow.
"""
import io
import json
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

from gerar_site import AQUI, RAIZ, le
from nucleo import paginas

LARGURA, QUALIDADE = 1400, 70
# O certificado deste site é inválido; a verificação é dispensada só para ele.
SEM_CERTIFICADO = {"digitalis-dsp.uc.pt"}

obra, destino = sys.argv[1], Path(sys.argv[2])
maximo = int(sys.argv[3]) if len(sys.argv) > 3 else None
cfg = json.loads(le(AQUI / "config.json"))
if obra not in {o["id"] for o in cfg["obras"]}:
    sys.exit(f"Obra desconhecida: {obra}")
pasta = destino / f"{obra}_imagens"
pasta.mkdir(parents=True, exist_ok=True)
feitas, erros = 0, []
for p in paginas(le(RAIZ / cfg["pasta_obras"] / f"{obra}.xml")):
    novo = pasta / f"{p.id}.jpg"
    if not p.facs.startswith(("http://", "https://")) or novo.exists():
        continue
    if maximo is not None and feitas + len(erros) >= maximo:
        break
    try:
        ctx = ssl.create_default_context()
        if urllib.parse.urlsplit(p.facs).hostname in SEM_CERTIFICADO:
            ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
        with urllib.request.urlopen(p.facs, timeout=90, context=ctx) as r:
            im = Image.open(io.BytesIO(r.read())).convert("RGB")
        if im.width > LARGURA:
            im = im.resize((LARGURA, round(im.height * LARGURA / im.width)), Image.LANCZOS)
        tmp = novo.with_suffix(".parte")
        im.save(tmp, "JPEG", quality=QUALIDADE, optimize=True, progressive=True)
        tmp.replace(novo)
        feitas += 1
        print(p.n, novo.name, flush=True)
    except Exception as e:
        erros.append(p.n)
        print("ERRO", p.n, e, flush=True)
    time.sleep(1)
print(f"{feitas} imagens copiadas; {len(erros)} erros {erros if erros else ''}")
