# verbetes/management/commands/generate_full_pdf.py

import os
import markdown
from pathlib import Path
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings
from verbetes.models import Verbete
from weasyprint import HTML
from django.db.models.functions import Lower
import logging

# Configura o log para mostrar erros do WeasyPrint no terminal
logger = logging.getLogger('weasyprint')
logger.addHandler(logging.StreamHandler())

# Função auxiliar para converter defaultdict recursivamente para dict
def convert_defaultdict_to_dict_recursive(d):
    if isinstance(d, defaultdict):
        return {k: convert_defaultdict_to_dict_recursive(v) for k, v in d.items()}
    return d

class Command(BaseCommand):
    help = 'Gera um único arquivo PDF com capa, textos de apoio e verbetes.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando a geração do PDF completo...")

        # --- 1. COLETA DOS TEXTOS DE APOIO (MARKDOWN) ---
        # Defina aqui o caminho base onde estão suas pastas de .md
        # Ajuste 'documentacao' para o nome real da sua pasta de arquivos md
        base_path = Path(settings.BASE_DIR) / 'documentacao' / 'textos'
        
        textos_apoio = []

        def processar_arquivo_md(caminho, categoria):
            if not caminho.exists():
                return None
            with open(caminho, encoding='utf-8') as f:
                raw_content = f.read()
                md = markdown.Markdown(extensions=['extra', 'smarty', 'meta'])
                html_content = md.convert(raw_content)
                
                # --- DEBUG DE IMAGENS ---
                import re
                # Procurar todos os src="/static/..."
                imgs = re.findall(r'src="/static/([^"]+)"', html_content)
                
                for img_path in imgs:
                    # Tente construir o caminho usando STATICFILES_DIRS ou BASE_DIR
                    # Se o seu projeto segue o padrão, a imagem física está em:
                    caminho_absoluto_img = settings.BASE_DIR / 'documentacao' / 'static' / img_path
                    
                    print(f"\n[DEBUG] Tentando localizar imagem:")
                    print(f"   - URL no Markdown: /static/{img_path}")
                    print(f"   - Caminho no Disco: {caminho_absoluto_img}")
                    
                    if caminho_absoluto_img.exists():
                        print(f"   - [OK] Arquivo encontrado no disco!")
                        # Para o WeasyPrint, o prefixo file:// é o mais seguro para caminhos absolutos
                        caminho_final = caminho_absoluto_img.as_uri() # Transforma em file:///C:/...
                        html_content = html_content.replace(f'src="/static/{img_path}"', f'src="{caminho_final}"')
                    else:
                        print(f"   - [ERRO] Arquivo NÃO encontrado no disco!")
                # ------------------------

                titulo = md.Meta.get('title', [caminho.stem.replace('_', ' ').title()])[0]
                return {
                    'titulo': titulo,
                    'conteudo_html': html_content,
                    'slug': caminho.stem,
                    'categoria': categoria
                }

        # 1. Prefácio (Geralmente fica na raiz de /textos/)
        path_prefacio = base_path / 'prefacio.md'
        prefacio_data = processar_arquivo_md(path_prefacio, 'Prefácio')
        if prefacio_data:
            textos_apoio.append(prefacio_data)

        # 2. Técnicos (Verifique se a pasta tem acento no nome real do Windows/Linux)
        # Se a pasta tiver acento, use 'técnicos'. Se não tiver, use 'tecnicos'.
        tecnicos_path = base_path / 'tecnicos' # ou 'técnicos'
        if tecnicos_path.exists():
            for path in sorted(tecnicos_path.glob('*.md')):
                text_data = processar_arquivo_md(path, 'Texto Técnico')
                if text_data:
                    textos_apoio.append(text_data)

        # 3. Curiosidades
        curiosidades_path = base_path / 'curiosidades'
        if curiosidades_path.exists():
            for path in sorted(curiosidades_path.glob('*.md')):
                text_data = processar_arquivo_md(path, 'Curiosidade')
                if text_data:
                    textos_apoio.append(text_data)

        # --- 2. COLETA E PROCESSAMENTO DOS VERBETES ---
        all_verbetes = Verbete.objects.all().prefetch_related(
            'definicoes',                  
            'definicoes__ocorrencias',     
        ).order_by(Lower('termo')) 

        processed_verbetes_for_pdf = []
        for verbete in all_verbetes:
            verbete_data = {
                'termo': verbete.termo,
                'slug': verbete.slug,
                'classe_gramatical': verbete.classe_gramatical,
                'etimologia': verbete.etimologia,
                'definicoes': [] 
            }

            for definicao in verbete.definicoes.all():
                def_data = {
                    'sensenumber': definicao.sensenumber,
                    'definition': definicao.definition,
                    'exemplos_agrupados': defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
                }
                
                for oco in definicao.ocorrencias.all():
                    token = oco.token or 'N/A'
                    gram = oco.gram or '' 
                    autor = oco.autor or 'N/A'
                    def_data['exemplos_agrupados'][token][gram][autor].append(oco)
                
                def_data['exemplos_agrupados'] = convert_defaultdict_to_dict_recursive(def_data['exemplos_agrupados'])
                verbete_data['definicoes'].append(def_data)
            
            processed_verbetes_for_pdf.append(verbete_data)

        # --- 3. RENDERIZAÇÃO ---
        context = {
            'textos_apoio': textos_apoio,
            'todos_os_verbetes': processed_verbetes_for_pdf,
            'organizador_nome': "Bruno Maroneze",
        }
        
        html_string = render_to_string('pagina_inicial/pdf_template.html', context)

        output_path = os.path.join(settings.MEDIA_ROOT, 'dicionario_completo.pdf')
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        self.stdout.write("Gerando PDF com WeasyPrint...")
        try:
            # base_url permite que o WeasyPrint encontre imagens ou CSS estáticos
            HTML(string=html_string, base_url=settings.BASE_DIR).write_pdf(output_path)
            self.stdout.write(self.style.SUCCESS(f"Sucesso! PDF gerado em: {output_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro: {e}"))