# verbetes/management/commands/generate_full_pdf.py

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings
from verbetes.models import Verbete
from weasyprint import HTML
import os

class Command(BaseCommand):
    help = 'Gera um único arquivo PDF com todos os verbetes do dicionário.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando a geração do PDF completo do dicionário...")

        # 1. Buscar todos os dados necessários do banco
        # Usamos prefetch_related para otimizar a busca das definições
        verbetes = Verbete.objects.all().prefetch_related('definicoes').order_by('termo')
        
        if not verbetes:
            self.stdout.write(self.style.WARNING("Nenhum verbete encontrado. PDF não gerado."))
            return

        self.stdout.write(f"Encontrados {verbetes.count()} verbetes para incluir no PDF.")

        # 2. Renderizar o template HTML
        context = {
            'todos_os_verbetes': verbetes
        }
        html_string = render_to_string('pagina_inicial/pdf_template.html', context)

        # 3. Definir o caminho de saída do PDF
        # O PDF será salvo na sua pasta MEDIA_ROOT
        output_filename = 'dicionario_completo.pdf'
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        
        # Garante que o diretório MEDIA_ROOT existe
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        self.stdout.write(f"Renderizando HTML e gerando PDF em {output_path}...")

        # 4. Usar WeasyPrint para converter o HTML em PDF e salvar no arquivo
        try:
            HTML(string=html_string).write_pdf(output_path)
            self.stdout.write(self.style.SUCCESS(f"PDF gerado com sucesso: {output_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ocorreu um erro ao gerar o PDF: {e}"))
            self.stderr.write(self.style.NOTICE("Verifique se as dependências do WeasyPrint (Pango, Cairo, etc.) estão instaladas corretamente."))