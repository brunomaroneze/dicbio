# web/verbetes/admin.py
from django.contrib import admin
from .models import Verbete, Definition, OcorrenciaCorpus # Importe todos os seus modelos

# --- Configuração para Definir Definições diretamente no Verbete Admin ---
class DefinitionInline(admin.TabularInline): # Ou admin.StackedInline para layout diferente
    model = Definition
    extra = 1 # Quantas linhas vazias para novas definições exibir por padrão
    # Você pode personalizar campos aqui, se quiser:
    # fields = ['sensenumber', 'definition']
    # raw_id_fields = ('verbete',) # se 'verbete' fosse um campo selecionável

# --- Configuração para Definir Ocorrências diretamente no Verbete Admin ---
class OcorrenciaCorpusInline(admin.TabularInline):
    model = OcorrenciaCorpus
    extra = 0 # Não exibir linhas vazias por padrão, mas pode adicionar
    # Você pode personalizar os campos aqui, se quiser
    # fields = ['token', 'frase', 'autor', 'titulo_obra', 'definicao']
    # raw_id_fields = ('verbete', 'definicao',) # se quiser selectbox para verbete/definicao


# --- Registro do Modelo Verbete com as Inlines ---
@admin.register(Verbete) # Uma forma mais elegante de registrar o modelo
class VerbeteAdmin(admin.ModelAdmin):
    list_display = ('termo', 'classe_gramatical', 'slug', 'criado_em', 'atualizado_em')
    search_fields = ('termo', 'etimologia', 'autores') # Campos para pesquisa
    list_filter = ('classe_gramatical', 'criado_em') # Filtros na barra lateral
    prepopulated_fields = {'slug': ('termo',)} # Gera o slug automaticamente a partir do termo
    inlines = [DefinitionInline, OcorrenciaCorpusInline] # Inclui as Definições e Ocorrências

    # Para que o slug seja gerado automaticamente mesmo ao salvar via admin
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = obj.termo # O prepopulated_fields já ajuda, mas isso é uma salvaguarda
        super().save_model(request, obj, form, change)

# --- Registro dos Modelos restantes (se não forem inlines de outros) ---
# Se Definition e OcorrenciaCorpus são apenas inlines, não precisam ser registrados diretamente,
# mas se quiser vê-los e gerenciá-los como modelos separados no admin, você pode.
# admin.site.register(Definition) # Geralmente não necessário se for apenas um inline
# admin.site.register(OcorrenciaCorpus) # Geralmente não necessário se for apenas um inline