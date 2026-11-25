from django.shortcuts import render, get_object_or_404
from django.conf import settings
from pathlib import Path
from .models import Obra
# Não precisamos mais de: lxml, Path, slugify, reverse (para a conversão de HTML)
# Também não precisamos das funções converter_tei_para_html e substituir_tags_inadequadas aqui.

def home(request, slug=None):
    # Listagem lateral das obras.
    obras_list = Obra.objects.order_by('ordem', 'autor', 'titulo')
    obra_selecionada = None
    html_da_obra_para_exibir = None # Novo nome para clareza

    if slug:
        # Quando uma obra específica é selecionada, aí sim carregamos todos os seus campos
        # get_object_or_404 lida com o caso de não encontrar a obra
        obra_selecionada = get_object_or_404(Obra, slug=slug)

        corpus_html_root = Path(
            getattr(settings, 'CORPUS_HTML_ROOT', settings.BASE_DIR / 'corpus_digital' / 'obras_html')
        )
        caminho_html = corpus_html_root / f"{obra_selecionada.slug}.html"

        if caminho_html.exists():
            html_da_obra_para_exibir = caminho_html.read_text(encoding='utf-8')
        else:
            html_da_obra_para_exibir = (
                "<p><em>O HTML desta obra não foi encontrado no diretório de arquivos processados.</em></p>"
                "<p><em>Execute o processamento com saída em arquivo para gerar o conteúdo desta obra.</em></p>"
            )

    context = {
        'obras': obras_list,                     # Lista de obras para a navegação lateral
        'obra_atual': obra_selecionada,          # A obra que está sendo visualizada (pode ser None)
        'conteudo_html': html_da_obra_para_exibir # O HTML da obra atual para ser renderizado
    }

    return render(request, 'corpus_digital/home.html', context)
