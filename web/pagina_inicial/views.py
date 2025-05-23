from utilitarios.markdown_utils import render_markdown_from_file
from django.shortcuts import render
from pathlib import Path

def home(request):
    caminho_md = Path(__file__).resolve().parent.parent.parent / 'ProjectIntro.md'
    conteudo_html = render_markdown_from_file(caminho_md)

    return render(request, 'pagina_inicial/home.html', {
        'conteudo_md': conteudo_html
    })
