# web/corpus_digital/admin.py
from django.contrib import admin
from .models import Obra

@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'slug', 'ordem', 'caminho_arquivo')
    search_fields = ('titulo', 'autor')
    list_filter = ('autor',)
    prepopulated_fields = {'slug': ('titulo', 'autor')} # Gera slug de título e autor
    # Se você adicionou 'conteudo_html_processado' e o marcou como editable=False no models.py,
    # ele não aparecerá no formulário de edição por padrão, o que é bom.
    # Se você quiser vê-lo (read-only), adicione em readonly_fields:
    # readonly_fields = ('conteudo_html_processado',)