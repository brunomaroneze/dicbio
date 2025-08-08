# web/utilitarios/markdown_utils.py

import markdown
from pathlib import Path

def render_markdown_from_file(caminho_arquivo):
    caminho = Path(caminho_arquivo)
    with caminho.open(encoding='utf-8') as f:
        texto = f.read()
    return markdown.markdown(texto, extensions=['extra', 'smarty'])
