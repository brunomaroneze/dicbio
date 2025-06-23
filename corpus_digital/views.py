from django.shortcuts import render, get_object_or_404
from .models import Obra
# Não precisamos mais de: lxml, Path, slugify, reverse (para a conversão de HTML)
# Também não precisamos das funções converter_tei_para_html e substituir_tags_inadequadas aqui.

def home(request, slug=None):
    # Usar defer para não carregar o HTML pesado de todas as obras na listagem lateral
    # Apenas o HTML da obra_atual será carregado completamente quando ela for selecionada.
    obras_list = Obra.objects.defer("conteudo_html_processado").order_by('ordem', 'autor', 'titulo')
    obra_selecionada = None
    html_da_obra_para_exibir = None # Novo nome para clareza

    if slug:
        # Quando uma obra específica é selecionada, aí sim carregamos todos os seus campos
        # get_object_or_404 lida com o caso de não encontrar a obra
        obra_selecionada = get_object_or_404(Obra, slug=slug)

        if obra_selecionada.conteudo_html_processado:
            html_da_obra_para_exibir = obra_selecionada.conteudo_html_processado
        else:
            # Mensagem caso o HTML não tenha sido processado ou esteja vazio
            # Você pode querer uma mensagem mais específica ou até mesmo tentar processar aqui (menos ideal)
            html_da_obra_para_exibir = (
                "<p><em>O conteúdo desta obra ainda não foi processado ou não está disponível.</em></p>"
                "<p><em>Por favor, execute o comando de processamento ou verifique o arquivo XML original.</em></p>"
            )
            # Se você quiser ser mais robusto, poderia verificar se o arquivo XML original existe
            # e dar uma mensagem diferente caso o XML também não exista.
            # Mas, idealmente, o comando de processamento já teria tratado isso.

    context = {
        'obras': obras_list,                     # Lista de obras para a navegação lateral
        'obra_atual': obra_selecionada,          # A obra que está sendo visualizada (pode ser None)
        'conteudo_html': html_da_obra_para_exibir # O HTML da obra atual para ser renderizado
    }

    return render(request, 'corpus_digital/home.html', context)
