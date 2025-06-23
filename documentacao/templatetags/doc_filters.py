# web/documentacao/templatetags/doc_filters.py

from django import template

register = template.Library()

@register.filter(name='formatar_autores')
def formatar_autores(autores_str):
    """
    Formata uma string de autores 'SOBRENOME, Nome; SOBRENOME, Nome'
    para o formato ABNT 'SOBRENOME, Nome; SOBRENOME, Nome.'
    """
    if not isinstance(autores_str, str):
        return ""
    
    autores = [autor.strip() for autor in autores_str.split(';') if autor.strip()]
    if not autores:
        return ""
    
    # Retorna a string unida por '; ' e com um ponto final.
    return "; ".join(autores) + "."