import csv
import io
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import TestCase, override_settings

from verbetes.models import Definition, OcorrenciaCorpus, Verbete


class ImportarOcorrenciasTests(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.base_dir = Path(self.temp_dir.name)
        (self.base_dir / 'data').mkdir()

    def importar(self, headwords):
        csv_path = self.base_dir / 'data' / 'termos_extraidos.csv'
        with csv_path.open('w', encoding='utf-8', newline='') as arquivo:
            writer = csv.DictWriter(
                arquivo,
                fieldnames=['Headword', 'SenseNumber', 'token', 'sentence'],
            )
            writer.writeheader()
            for headword in headwords:
                writer.writerow({
                    'Headword': headword,
                    'SenseNumber': 1,
                    'token': headword,
                    'sentence': 'Exemplo',
                })
        saida, erros = io.StringIO(), io.StringIO()
        with override_settings(BASE_DIR=self.base_dir):
            call_command(
                'import_dictionary_data',
                skip_verbetes=True,
                skip_definitions=True,
                stdout=saida,
                stderr=erros,
                no_color=True,
            )
        return erros.getvalue()

    def test_importa_espacos_normalizados_e_capitalizacao_identica(self):
        for termo in ('febre de Sião', 'icterice grave', 'centeio espigado'):
            verbete = Verbete.objects.create(termo=termo)
            Definition.objects.create(verbete=verbete, sensenumber=1, definition='Exemplo')

        erros = self.importar(['febre de Sião', 'icterice\n\tgrave', 'centeio\n\t espigado'])

        self.assertEqual(erros, '')
        self.assertEqual(OcorrenciaCorpus.objects.count(), 3)
        self.assertEqual(
            set(OcorrenciaCorpus.objects.values_list('verbete__termo', flat=True)),
            {'febre de Sião', 'icterice grave', 'centeio espigado'},
        )
        self.assertEqual(OcorrenciaCorpus.objects.filter(definicao__isnull=False).count(), 3)

    def test_exige_capitalizacao_exata(self):
        Verbete.objects.create(termo='Febre', slug='febre-maiuscula')
        Verbete.objects.create(termo='febre', slug='febre-minuscula')

        erros = self.importar(['Febre', 'FEBRE', 'inexistente'])

        self.assertEqual(OcorrenciaCorpus.objects.count(), 1)
        self.assertEqual(OcorrenciaCorpus.objects.get().verbete.termo, 'Febre')
        self.assertIn('Verbete não encontrado', erros)
        self.assertIn('FEBRE', erros)
        self.assertIn('inexistente', erros)
