# verbetes/management/commands/generate_full_pdf.py

import os
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings
from verbetes.models import Verbete, Definition, OcorrenciaCorpus 
from weasyprint import HTML
from django.db.models.functions import Lower

# Função auxiliar para converter defaultdict recursivamente para dict
def convert_defaultdict_to_dict_recursive(d):
    if isinstance(d, defaultdict):
        return {k: convert_defaultdict_to_dict_recursive(v) for k, v in d.items()}
    return d

class Command(BaseCommand):
    help = 'Gera um único arquivo PDF com todos os verbetes do dicionário.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando a geração do PDF completo do dicionário...")

        all_verbetes = Verbete.objects.all().prefetch_related(
            'definicoes',                  
            'definicoes__ocorrencias',     
        ).order_by(Lower('termo')) 
        
        if not all_verbetes:
            self.stdout.write(self.style.WARNING("Nenhum verbete encontrado. PDF não gerado."))
            return

        self.stdout.write(f"Encontrados {all_verbetes.count()} verbetes para incluir no PDF.")

        processed_verbetes_for_pdf = []

        for verbete in all_verbetes:
            verbete_data = {
                'termo': verbete.termo,
                'slug': verbete.slug,
                'classe_gramatical': verbete.classe_gramatical,
                'etimologia': verbete.etimologia,
                'autores': verbete.autores,
                'criado_em': verbete.criado_em,
                'atualizado_em': verbete.atualizado_em,
                'definicoes': [] 
            }

            for definicao in verbete.definicoes.all():
                definicao_data = {
                    'sensenumber': definicao.sensenumber,
                    'definition': definicao.definition,
                    'exemplos_agrupados': defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
                }

                raw_ocorrencias_for_def = list(definicao.ocorrencias.all())
                
                for ocorrencia in raw_ocorrencias_for_def:
                    token_val = ocorrencia.token or 'N/A'
                    gram_val = ocorrencia.gram or '' 
                    autor_val = ocorrencia.autor or 'N/A'
                    
                    definicao_data['exemplos_agrupados'][token_val][gram_val][autor_val].append(ocorrencia)
                
                # --- NOVA LINHA CHAVE AQUI ---
                # Converter a estrutura defaultdict para dicts normais antes de adicionar
                definicao_data['exemplos_agrupados'] = convert_defaultdict_to_dict_recursive(definicao_data['exemplos_agrupados'])
                # --- FIM DA NOVA LINHA ---

                verbete_data['definicoes'].append(definicao_data)
            processed_verbetes_for_pdf.append(verbete_data)

        context = {
            'todos_os_verbetes': processed_verbetes_for_pdf
        }
        html_string = render_to_string('pagina_inicial/pdf_template.html', context)

        output_filename = 'dicionario_completo.pdf'
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        self.stdout.write(f"Renderizando HTML e gerando PDF em {output_path}...")

        try:
            HTML(string=html_string, base_url=settings.BASE_DIR).write_pdf(output_path)
            self.stdout.write(self.style.SUCCESS(f"PDF gerado com sucesso: {output_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ocorreu um erro ao gerar o PDF: {e}"))
            self.stderr.write(self.style.NOTICE("Verifique se as dependências do WeasyPrint (Pango, Cairo, etc.) estão instaladas corretamente."))