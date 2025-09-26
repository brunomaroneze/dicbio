from django.shortcuts import render, get_object_or_404
from .models import Obra
import re


def home(request, slug=None):
    """
    View principal que exibe a lista de obras e o conteúdo de uma obra específica quando selecionada.

    Args:
        request: Objeto HttpRequest
        slug (str, optional): Slug da obra selecionada. Defaults to None.

    Returns:
        HttpResponse: Renderiza o template com o contexto
    """

    # Obtém a lista de obras, deferindo o campo pesado conteudo_html_processado para otimização
    # Ordena por ordem, autor e título para exibição consistente
    obras_list = Obra.objects.defer("conteudo_html_processado").order_by('ordem', 'autor', 'titulo')

    obra_selecionada = None  # Armazena a obra atualmente selecionada
    html_da_obra_para_exibir = None  # Conteúdo HTML processado para exibição

    # Se um slug foi fornecido na URL, significa que uma obra específica foi selecionada
    if slug:
        # Obtém a obra pelo slug ou retorna 404 se não existir
        obra_selecionada = get_object_or_404(Obra, slug=slug)

        # Verifica se a obra selecionada tem conteúdo HTML processado
        if obra_selecionada.conteudo_html_processado:
            # Faz uma cópia do conteúdo HTML para processamento
            conteudo_html = obra_selecionada.conteudo_html_processado

            # Processa os termos destacados se existirem na obra
            if hasattr(obra_selecionada, 'termos_extraidos') and obra_selecionada.termos_extraidos:
                termos_processados = set()  # Conjunto para evitar processar o mesmo token múltiplas vezes

                # Itera sobre cada termo extraído
                for termo in obra_selecionada.termos_extraidos:
                    token = termo.get('token', '').strip()  # Forma atual da palavra
                    orth = termo.get('orth', '').strip()  # Forma original da palavra

                    # Verifica se o termo deve ser processado:
                    # - Token e orth existem
                    # - São diferentes (case insensitive)
                    # - Ainda não foi processado
                    if token and orth and token.lower() != orth.lower() and token not in termos_processados:
                        # Expressão regular avançada para:
                        # 1. (?<!\w) - Não precede por caractere de palavra
                        # 2. (?<!\/) - Não precede por barra (evita caminhos de arquivo)
                        # 3. (?<!") - Não precede por aspas (evita atributos HTML)
                        # 4. (?<!') - Não precede por apóstrofo (evita atributos HTML)
                        # 5. (token) - A palavra a ser substituída
                        # 6. (?!\w) - Não seguida por caractere de palavra
                        # 7. (?!\/) - Não seguida por barra
                        # 8. (?!") - Não seguida por aspas
                        pattern = r'(?<!\w)(?<!\/)(?<!\")(?<!\')({})(?!\w)(?!\/)(?!\")'.format(re.escape(token))

                        # Cria a substituição com um span que terá o tooltip
                        replacement = (
                            f'<span class="termo-destaque" '  # Classe para estilização
                            f'data-bs-toggle="tooltip" '  # Ativa o tooltip do Bootstrap
                            f'data-bs-placement="top" '  # Posiciona o tooltip acima
                            f'title="{orth}">'  # Texto do tooltip (forma original)
                            f'\\1</span>'  # Mantém o texto original (token)
                        )

                        # Faz a substituição no conteúdo HTML
                        conteudo_html = re.sub(
                            pattern,
                            replacement,
                            conteudo_html,
                            flags=re.IGNORECASE  # Faz a busca case insensitive
                        )
                        termos_processados.add(token.lower())  # Marca o token como processado

                # Atribui o conteúdo processado para exibição
                html_da_obra_para_exibir = conteudo_html
            else:
                # Se não houver termos para processar, usa o conteúdo original
                html_da_obra_para_exibir = obra_selecionada.conteudo_html_processado
        else:
            # Mensagem de fallback se o conteúdo não estiver disponível
            html_da_obra_para_exibir = (
                "<p><em>O conteúdo desta obra ainda não foi processado ou não está disponível.</em></p>"
                "<p><em>Por favor, execute o comando de processamento ou verifique o arquivo XML original.</em></p>"
            )

    # Prepara o contexto para o template
    context = {
        'obras': obras_list,  # Lista de todas as obras para navegação
        'obra_atual': obra_selecionada,  # Obra atualmente selecionada (pode ser None)
        'conteudo_html': html_da_obra_para_exibir  # Conteúdo HTML para exibição
    }

    # Renderiza o template com o contexto
    return render(request, 'corpus_digital/home.html', context)