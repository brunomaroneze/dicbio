# web/corpus_digital/admin.py

from django.contrib import admin, messages
from django.core.management import call_command
from .models import Obra

# --- DEFINIÇÃO DAS ADMIN ACTIONS ---

@admin.action(description="PASSO A.1: Extrair termos do Corpus (gera termos_extraidos.csv)")
def acao_extrair_termos_corpus(modeladmin, request, queryset):
    try:
        call_command('extract_corpus_terms')
        messages.success(request,
                         "Comando 'extract_corpus_terms' executado. 'web/data/termos_extraidos.csv' gerado/atualizado.")
    except Exception as e:
        messages.error(request, f"Erro em 'extract_corpus_terms': {e}")

@admin.action(description="PASSO A.2: Importar/Atualizar metadados das Obras (XML para BD)")
def acao_importar_metadados_obras(modeladmin, request, queryset):
    try:
        call_command('import_obra_metadata')
        messages.success(request,
                         "Comando 'import_obra_metadata' executado. Metadados das obras no BD atualizados.")
    except Exception as e:
        messages.error(request, f"Erro em 'import_obra_metadata': {e}")

@admin.action(description="PASSO A.3: Processar Obras TEI para HTML (força reprocessamento)")
def acao_processar_obras_tei_para_html(modeladmin, request, queryset):
    management_command_name = 'processar_obras_tei'
    selected_objects_count = queryset.count()

    try:
        if selected_objects_count > 0:
            processed_count = 0
            error_count = 0
            # Processa apenas as obras selecionadas
            for obra_obj in queryset:
                try:
                    call_command(management_command_name, slug=obra_obj.slug, force=True)
                    processed_count += 1
                except Exception as e_item:
                    messages.error(request, f"Erro ao processar '{obra_obj.titulo}' (slug: {obra_obj.slug}): {e_item}")
                    error_count +=1
            
            if processed_count > 0:
                 messages.success(request, f"{processed_count} obra(s) selecionada(s) foram reprocessadas (HTML atualizado).")
            if error_count > 0:
                messages.warning(request, f"Houve erro ao tentar reprocessar {error_count} obra(s) selecionada(s). Verifique o console do servidor.")
            # Não faz nada se nenhuma obra foi selecionada e a ação foi chamada em um queryset vazio,
            # para evitar processar todas acidentalmente quando o usuário esperava operar na seleção.
            # Se o usuário não selecionar nada e quiser processar todas, ele pode executar o comando `processar_obras_tei --force`
            # manualmente, ou podemos adicionar uma ação separada "Processar TODAS as obras TEI para HTML".

        else: # Nenhuma obra selecionada na lista do admin
            # Decide-se não fazer nada para evitar processamento em massa acidental.
            # Se quiser processar todas quando nada é selecionado, descomente a linha abaixo
            # e ajuste a mensagem de feedback.
            # call_command(management_command_name, force=True)
            # messages.success(request, f"Nenhuma obra selecionada. Comando '{management_command_name} --force' executado para TODAS as obras.")
            messages.info(request, "Nenhuma obra foi selecionada. Para processar obras específicas, selecione-as na lista. Para processar todas, use o comando no terminal ou crie uma ação específica para 'processar todas'.")

    except Exception as e: # Erro geral, menos provável com o try/except interno
        messages.error(request, f"Erro geral ao executar '{management_command_name}': {e}")


# --- CONFIGURAÇÃO DO ADMIN PARA O MODELO OBRA ---
@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'slug', 'ordem', 'caminho_arquivo', 'html_processado_status')
    search_fields = ('titulo', 'autor', 'slug')
    list_filter = ('autor',)
    ordering = ('ordem', 'titulo')
    prepopulated_fields = {'slug': ('titulo',)}
    
    actions = [
        acao_extrair_termos_corpus,
        acao_importar_metadados_obras,
        acao_processar_obras_tei_para_html,
    ]

    def html_processado_status(self, obj):
        return bool(obj.conteudo_html_processado) # Mais direto para booleano
    html_processado_status.short_description = "HTML Processado?"
    html_processado_status.boolean = True