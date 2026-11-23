"""Cria cópias reduzidas das imagens locais, para publicar em outro repositório.

  python revisao/preparar_imagens.py PASTA_DESTINO carvalhoaviso_imagens [outra_pasta ...]

Requer Pillow. Não altera os originais.
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

from gerar_site import RAIZ

LARGURA, QUALIDADE = 1400, 70

destino = Path(sys.argv[1])
for pasta in sys.argv[2:]:
    total = 0
    (destino / pasta).mkdir(parents=True, exist_ok=True)
    for arq in sorted((RAIZ / "corpus_digital" / "obras" / pasta).glob("*.jpg")):
        novo = destino / pasta / arq.name
        if not novo.exists():
            im = ImageOps.exif_transpose(Image.open(arq)).convert("RGB")
            if im.width > LARGURA:
                im = im.resize((LARGURA, round(im.height * LARGURA / im.width)), Image.LANCZOS)
            im.save(novo, quality=QUALIDADE, optimize=True, progressive=True)
        total += novo.stat().st_size
    print(f"{pasta}: {total / 1e6:.0f} MB")
