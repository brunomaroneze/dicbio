# verbetes/templatetags/verbetes_extras.py

from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()

#====================================================================
# Filtro: get_item (do seu arquivo original)
#====================================================================
@register.filter
def get_item(dictionary, key):
    """Permite acessar itens de dicionário com chaves variáveis no template."""
    return dictionary.get(key)

#====================================================================
# Filtro: formatar_autores (do seu arquivo original)
#====================================================================
@register.filter
def formatar_autores(autores_str):
    """
    Formata uma string de autores (ex: "Nome Sobrenome; Nome Sobrenome")
    para o formato ABNT (ex: "SOBRENOME, Nome; SOBRENOME, Nome.").
    Aceita autores separados por ';' ou 'e' ou 'and'.
    """
    if not autores_str:
        return "Autor(es) não especificado(s)"

    partes_autores = re.split(r';| e | and ', str(autores_str), flags=re.IGNORECASE)
    
    autores_formatados = []
    for autor_completo in partes_autores:
        autor_completo = autor_completo.strip()
        if not autor_completo:
            continue

        partes_nome = autor_completo.split(' ')
        if len(partes_nome) > 1:
            sobrenome = partes_nome[-1].upper()
            nome_restante = " ".join(partes_nome[:-1])
            autores_formatados.append(f"{sobrenome}, {nome_restante}")
        else:
            autores_formatados.append(autor_completo.upper())

    return "; ".join(autores_formatados) + "."

#====================================================================
# Filtro: process_sentence_display (VERSÃO ATUALIZADA E CORRETA)
#====================================================================
# Pré-compila a regex para melhor performance
highlight_pattern = re.compile(r'\[\[b\]\](.*?)\[\[/b\]\]', re.DOTALL)

def replacement_func_bold(match):
    """Função de substituição para a regex de negrito."""
    content = match.group(1)
    # Mantém o conteúdo interno exatamente como está (com quebras de linha, etc.)
    return f'<b>{content}</b>'

@register.filter(name='process_sentence_display')
def process_sentence_display(sentence_text):
    """
    Usa expressões regulares para converter a marcação [[b]]...[[/b]] 
    para <b>...</b>, lidando corretamente com quebras de linha.
    """
    if not sentence_text:
        return ""
    
    # Aplica a substituição usando a regex
    processed_text = highlight_pattern.sub(replacement_func_bold, sentence_text)
    
    return mark_safe(processed_text)
#====================================================================
