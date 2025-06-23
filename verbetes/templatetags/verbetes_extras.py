from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def formatar_autores(autores_str):
    """
    Formata uma string de autores (ex: "Nome Sobrenome; Nome Sobrenome")
    para o formato ABNT (ex: "SOBRENOME, Nome; SOBRENOME, Nome.").
    Aceita autores separados por ';' ou 'e' ou 'and'.
    """
    if not autores_str:
        return "Autor(es) não especificado(s)"

    # Divide a string de autores por ';' ou 'e' ou ' and '
    # O re.split permite dividir por múltiplos delimitadores
    partes_autores = re.split(r';| e | and ', autores_str, flags=re.IGNORECASE)
    
    autores_formatados = []
    for autor_completo in partes_autores:
        autor_completo = autor_completo.strip()
        if not autor_completo:
            continue

        partes_nome = autor_completo.split(' ')
        if len(partes_nome) > 1:
            sobrenome = partes_nome[-1].upper() # Última parte é o sobrenome
            nome_restante = " ".join(partes_nome[:-1]) # O restante é o nome
            autores_formatados.append(f"{sobrenome}, {nome_restante}")
        else:
            autores_formatados.append(autor_completo.upper()) # Se só tem um nome, capitaliza

    return "; ".join(autores_formatados)

@register.filter
def process_sentence_display(text_with_markup):
    """
    Substitui marcações intermediárias [[b]]...[[/b]] e [[cite_link:...]]...[[/cite_link]]
    por HTML <b> e <a>, respectivamente.
    Recebe o dicionário 'ocorrencia_obj' para construir a URL do corpus.
    """
    if not text_with_markup:
        return ""

    
    # 1. Substituir negrito: [[b]]token[[/b]] -> <b>token</b>
    final_text = re.sub(r'\[\[b\]\](.*?)\[\[/b\]\]', r'<b>\1</b>', text_with_markup)
    
    return mark_safe(final_text) # Marcar como seguro, pois injetamos HTML