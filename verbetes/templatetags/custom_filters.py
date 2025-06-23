# web/verbetes/templatetags/custom_filters.py

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='process_sentence_display')
def process_sentence_display(sentence_text):
    """
    Converte a marcação [[b]]token[[/b]] para <b>token</b>.
    """
    if not sentence_text:
        return ""
    processed_text = sentence_text.replace("[[b]]", "<b>").replace("[[/b]]", "</b>")
    return mark_safe(processed_text)