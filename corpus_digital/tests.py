import csv
import io
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import SimpleTestCase, override_settings


class ExtrairTermosTests(SimpleTestCase):
    def test_normaliza_headword_sem_alterar_token_ou_sentenca(self):
        with TemporaryDirectory() as diretorio:
            raiz = Path(diretorio)
            corpus = raiz / 'corpus'
            corpus.mkdir()
            (corpus / 'obra.xml').write_text(
                '<TEI xmlns="http://www.tei-c.org/ns/1.0">'
                '<teiHeader><fileDesc><sourceDesc><bibl>'
                '<author>Autor</author><title>Obra</title><date>1871</date>'
                '</bibl></sourceDesc></fileDesc></teiHeader>'
                '<text><body><p><term>icterice\n\tgrave</term> e '
                '<term lemma="febre de Sião">febre de Sian</term>.</p></body></text>'
                '</TEI>',
                encoding='utf-8',
            )
            with override_settings(BASE_DIR=raiz, CORPUS_XML_ROOT=corpus):
                call_command('extract_corpus_terms', stdout=io.StringIO(), stderr=io.StringIO())
            with (raiz / 'data' / 'termos_extraidos.csv').open(
                encoding='utf-8', newline=''
            ) as arquivo:
                linhas = list(csv.DictReader(arquivo))

        self.assertEqual(linhas[0]['token'], 'icterice\n\tgrave')
        self.assertEqual(linhas[0]['Headword'], 'icterice grave')
        self.assertIn('[[b]]icterice\n\tgrave[[/b]]', linhas[0]['sentence'])
        self.assertEqual(linhas[1]['Headword'], 'febre de Sião')
