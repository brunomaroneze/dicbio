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

    return "; ".join(autores_formatados)

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

# verbetes/templatetags/citation_filters.py

@register.filter
def format_citation(ocorrencia):
    """
    Formata as informações de citação de uma OcorrenciaCorpus em uma única string.
    Ordem: Autor, Título da Obra, Data, Página.
    """
    parts = []

    # 1. Autor
    if ocorrencia.autor and ocorrencia.autor.strip() and ocorrencia.autor.strip().lower() != 'n/a':
        parts.append(ocorrencia.autor.capitalize()) 

    # 2. Título da Obra
    if ocorrencia.titulo_obra and ocorrencia.titulo_obra.strip():
        parts.append(ocorrencia.titulo_obra)

    # 3. Data
    if ocorrencia.data and ocorrencia.data.strip() and ocorrencia.data.strip().lower() != 's.d.':
        parts.append(ocorrencia.data)

    # 4. Página
    # Usamos ocorrencia.pagina_obra como campo único
    if ocorrencia.pagina_obra and ocorrencia.pagina_obra.strip():
        display_pagina_obra = ocorrencia.pagina_obra.replace("_", " ") 
        parts.append(f"p. {display_pagina_obra}")

    citation_string = ", ".join(parts)
    
    if not citation_string:
        return "informações da obra não disponíveis"
    
    return citation_string

@register.filter
def replace_chars(value, arg):
    """
    Substitui todas as ocorrências de uma substring por outra.
    Uso: {{ value|replace_chars:"old_string,new_string" }}
    """
    if not isinstance(value, str) or not isinstance(arg, str):
        return value # Retorna o valor original se não for string ou argumento inválido

    try:
        old_string, new_string = arg.split(',', 1) # Divide o argumento em duas partes
    except ValueError:
        return value # Se o argumento não estiver no formato "a,b", retorna o valor original

    return value.replace(old_string, new_string)