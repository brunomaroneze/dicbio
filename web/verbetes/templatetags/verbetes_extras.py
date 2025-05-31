from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def formatar_autores(autores_str):
    autores = [a.strip() for a in autores_str.split(';')]
    nomes_formatados = []
    for autor in autores:
        partes = autor.strip().split()
        if len(partes) >= 2:
            sobrenome = partes[-1].upper()
            nome_restante = ' '.join(partes[:-1])
            nomes_formatados.append(f"{sobrenome}, {nome_restante}")
        else:
            nomes_formatados.append(autor)
    return '; '.join(nomes_formatados)