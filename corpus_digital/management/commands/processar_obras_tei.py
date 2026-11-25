from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from corpus_digital.models import Obra
from corpus_digital.tei_html import converter
from verbetes.models import Verbete


class Command(BaseCommand):
    help = 'Converte os arquivos TEI-XML das obras para HTML e salva em arquivos.'

    def add_arguments(self, parser):
        parser.add_argument('--slug', type=str, help='Processa apenas uma obra.')
        parser.add_argument('--force', action='store_true', help='Força reprocessamento.')

    def handle(self, *args, **options):
        slug_especifico = options['slug']
        forcar = options['force']

        corpus_xml_root = Path(getattr(settings, 'CORPUS_XML_ROOT', settings.BASE_DIR / 'corpus_digital' / 'obras'))
        corpus_html_root = Path(getattr(settings, 'CORPUS_HTML_ROOT', settings.BASE_DIR / 'corpus_digital' / 'obras_html'))
        corpus_html_root.mkdir(parents=True, exist_ok=True)

        obras = Obra.objects.all()
        if slug_especifico:
            obras = obras.filter(slug=slug_especifico)

        if not obras.exists():
            self.stdout.write(self.style.WARNING('Nenhuma obra para processar.'))
            return

        slugs_verbetes = set(Verbete.objects.values_list('slug', flat=True))
        if not slugs_verbetes:
            raise CommandError('Não há verbetes no banco. Execute antes import_dictionary_data.')

        falhas = []
        for obra in obras:
            connection.close_if_unusable_or_obsolete()
            self.stdout.write(f'Processando: {obra.titulo}')

            html_ja_em_arquivo = (corpus_html_root / f'{obra.slug}.html').exists()
            ja_processada = html_ja_em_arquivo

            if ja_processada and not forcar:
                self.stdout.write(self.style.NOTICE(f'  Ignorando {obra.titulo}.'))
                continue

            caminho_relativo = Path(obra.caminho_arquivo)
            if caminho_relativo.parts and caminho_relativo.parts[0] == 'obras':
                caminho_relativo = Path(*caminho_relativo.parts[1:])

            caminho_xml = corpus_xml_root / caminho_relativo

            if not caminho_xml.exists():
                falhas.append(obra.slug)
                self.stderr.write(self.style.ERROR(f'  Arquivo não encontrado: {caminho_xml}'))
                continue

            try:
                html_content = converter(caminho_xml, slugs_verbetes)

                caminho_html = corpus_html_root / f'{obra.slug}.html'
                caminho_html.write_text(html_content, encoding='utf-8')

                self.stdout.write(self.style.SUCCESS(f'  Sucesso!'))

            except Exception as e:
                falhas.append(obra.slug)
                self.stderr.write(self.style.ERROR(f'  Erro em {obra.titulo}: {e}'))

        if falhas:
            raise CommandError('Obras com erro: ' + ', '.join(falhas))
        self.stdout.write(self.style.SUCCESS('Concluído.'))
