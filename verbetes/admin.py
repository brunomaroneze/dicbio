# web/verbetes/admin.py

from django.contrib import admin, messages
from django.core.management import call_command
from .models import Verbete, Definition, OcorrenciaCorpus
from django.utils.text import slugify

# --- DEFINIÇÃO DA ADMIN ACTION ---

@admin.action(description="PASSO B.1: Importar dados do Dicionário (Verbetes, Definições, Ocorrências)")
def acao_importar_dados_dicionario(modeladmin, request, queryset):
    management_command_name = 'import_dictionary_data'
    try:
        call_command(management_command_name)
        messages.success(request,
                         f"Comando '{management_command_name}' executado com sucesso. Verbetes, definições e ocorrências foram importados/atualizados.")
    except Exception as e:
        messages.error(request,
                       f"Ocorreu um erro ao executar '{management_command_name}': {e}")


# --- CONFIGURAÇÃO PARA INLINES ---

class DefinitionInline(admin.TabularInline):
    model = Definition
    extra = 1
    fields = ('sensenumber', 'definition') # Mostra apenas estes campos no inline
    ordering = ('sensenumber',)


# --- CONFIGURAÇÃO DO ADMIN PARA O MODELO VERBETE ---

@admin.register(Verbete)
class VerbeteAdmin(admin.ModelAdmin):
    inlines = [DefinitionInline]
    
    list_display = ('termo', 'slug', 'classe_gramatical', 'get_first_definition_preview', 'criado_em', 'atualizado_em')
    search_fields = ('termo', 'etimologia', 'autores')
    list_filter = ('classe_gramatical', 'criado_em', 'atualizado_em')
    prepopulated_fields = {'slug': ('termo',)}
    ordering = ('termo',) # Ordenar por termo por padrão
    
    actions = [acao_importar_dados_dicionario]

    fieldsets = (
        (None, {
            'fields': ('termo', 'slug', 'classe_gramatical', 'etimologia')
        }),
        ('Detalhes da Primeira Ocorrência', {
            'classes': ('collapse',), # Começa colapsado
            'fields': ('primeira_ocorrencia', 'data_ocorrencia', 'autores'),
        }),
        ('Datas de Controle', {
            'classes': ('collapse',),
            'fields': ('criado_em', 'atualizado_em'),
        }),
    )
    # readonly_fields = ('criado_em', 'atualizado_em') # Se forem preenchidos automaticamente

    def get_first_definition_preview(self, obj):
        first_def = obj.definicoes.order_by('sensenumber').first() # Usando related_name 'definicoes'
        if first_def:
            return first_def.definition[:75] + '...' if len(first_def.definition) > 75 else first_def.definition
        return "Nenhuma definição"
    get_first_definition_preview.short_description = 'Início da 1ª Definição'

    # O método save no modelo Verbete já cuida da criação do slug.
    # O save_model aqui é redundante se o modelo já faz isso.
    # def save_model(self, request, obj, form, change):
    #     if not obj.slug:
    #         obj.slug = slugify(obj.termo)
    #     super().save_model(request, obj, form, change)


# --- CONFIGURAÇÃO DO ADMIN PARA O MODELO DEFINITION ---

@admin.register(Definition)
class DefinitionAdmin(admin.ModelAdmin):
    list_display = ('get_verbete_termo', 'sensenumber', 'get_definition_preview')
    search_fields = ('definition', 'verbete__termo') # Busca no texto da definição e no termo do verbete
    list_filter = ('verbete__classe_gramatical',) # Exemplo: filtrar por classe gramatical do verbete pai
    autocomplete_fields = ['verbete'] # Essencial para associar a um Verbete
    ordering = ('verbete__termo', 'sensenumber')

    def get_verbete_termo(self, obj):
        return obj.verbete.termo
    get_verbete_termo.short_description = 'Verbete'
    get_verbete_termo.admin_order_field = 'verbete__termo'

    def get_definition_preview(self, obj):
        return obj.definition[:100] + '...' if len(obj.definition) > 100 else obj.definition
    get_definition_preview.short_description = 'Definição (início)'


# --- CONFIGURAÇÃO DO ADMIN PARA O MODELO OCORRENCIACORPUS ---

@admin.register(OcorrenciaCorpus)
class OcorrenciaCorpusAdmin(admin.ModelAdmin):
    list_display = ('token', 'get_verbete_termo_oc', 'titulo_obra', 'pagina_obra', 'data', 'gram')
    search_fields = ('token', 'verbete__termo', 'frase', 'autor', 'titulo_obra')
    list_filter = ('verbete__classe_gramatical', 'autor', 'titulo_obra', 'gram') # Filtros úteis
    autocomplete_fields = ['verbete', 'definicao'] # Para os ForeignKeys
    ordering = ('verbete__termo', 'titulo_obra', 'pagina_obra')
    # readonly_fields = ('frase',) # Se a frase for muito longa para editar diretamente

    fieldsets = (
        (None, {
            'fields': ('token', 'verbete', 'definicao', 'gram', 'orth')
        }),
        ('Contexto da Ocorrência', {
            'fields': ('frase',)
        }),
        ('Detalhes da Fonte', {
            'fields': ('autor', 'titulo_obra', 'slug_obra', 'pagina_obra', 'data'),
        }),
    )

    def get_verbete_termo_oc(self, obj): # Nome diferente para evitar conflito
        return obj.verbete.termo if obj.verbete else '-'
    get_verbete_termo_oc.short_description = 'Verbete Associado'
    get_verbete_termo_oc.admin_order_field = 'verbete__termo'