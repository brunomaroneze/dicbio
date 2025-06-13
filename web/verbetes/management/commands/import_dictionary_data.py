import pandas as pd
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from verbetes.models import Verbete, Definition, OcorrenciaCorpus

class Command(BaseCommand):
    help = 'Importa/Atualiza dados de Verbetes, Definições e Ocorrências a partir de CSVs.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Apaga TODOS os dados de Verbetes, Definições e Ocorrências antes da importação.',
        )
        parser.add_argument(
            '--skip-verbetes',
            action='store_true',
            help='Pula a importação/atualização de verbetes.',
        )
        parser.add_argument(
            '--skip-definitions',
            action='store_true',
            help='Pula a importação/atualização de definições.',
        )
        parser.add_argument(
            '--skip-ocorrencias',
            action='store_true',
            help='Pula a importação/atualização de ocorrências.',
        )

    def handle(self, *args, **options):
        clear_all = options['clear_all']
        skip_verbetes = options['skip_verbetes']
        skip_definitions = options['skip_definitions']
        skip_ocorrencias = options['skip_ocorrencias']

        data_dir = settings.BASE_DIR / "data"

        # --- Limpeza de Dados (se --clear-all for usado) ---
        if clear_all:
            self.stdout.write(self.style.WARNING('Apagando todos os dados de Ocorrências, Definições e Verbetes...'))
            OcorrenciaCorpus.objects.all().delete()
            Definition.objects.all().delete()
            Verbete.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Dados antigos apagados.'))

        # --- Parte 1: Importar/Atualizar Verbetes ---
        if not skip_verbetes:
            self.stdout.write(self.style.HTTP_INFO('Iniciando importação/atualização de Verbetes...'))
            csv_path = data_dir / 'DadosDoDicionario.csv'
            if not csv_path.exists():
                raise CommandError(f"Arquivo CSV não encontrado: {csv_path}")

            df = pd.read_csv(csv_path)
            
            def parse_date(date_str):
                if pd.isna(date_str) or not isinstance(date_str, str):
                    return None
                try:
                    return datetime.strptime(date_str.strip(), '%d %b %Y').date()
                except Exception:
                    return None

            for index, row in df.iterrows():
                try:
                    termo = str(row['Headword']).strip()
                    
                    # update_or_create: encontra pelo 'termo' ou cria um novo
                    # Ele também cuida da geração do slug se 'blank=True' e 'prepopulated_fields'
                    # não for usado para slug, ou se o save() method gerar.
                    # No seu modelo Verbete, o slug é gerado no save()
                    verbete, criado = Verbete.objects.update_or_create(
                        termo=termo,
                        defaults={
                            'classe_gramatical': row.get('WClass', '').strip(),
                            'etimologia': row.get('Etymology', '').strip(),
                            'primeira_ocorrencia': row.get('FirstAttestationExampleMD', '').strip(),
                            'data_ocorrencia': row.get('FirstAttestationDate', '').strip(),
                            'autores': row.get('Credits', '').strip(),
                            'criado_em': parse_date(row.get('DateOfCreation')),
                            'atualizado_em': parse_date(row.get('DateOfUpdate')),
                        }
                    )
                    if criado:
                        self.stdout.write(self.style.SUCCESS(f"✔️ Criado Verbete: {termo}"))
                    else:
                        self.stdout.write(self.style.NOTICE(f"🔁 Atualizado Verbete: {termo}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Erro ao processar linha {index} para Verbete {row.get("Headword")}: {e}'))
            self.stdout.write(self.style.SUCCESS('Importação de Verbetes concluída.'))
        else:
            self.stdout.write(self.style.NOTICE('Importação de Verbetes pulada (--skip-verbetes).'))

        # --- Parte 2: Importar/Atualizar Definições ---
        if not skip_definitions:
            self.stdout.write(self.style.HTTP_INFO('Iniciando importação/atualização de Definições...'))
            csv_path = data_dir / 'definitions.csv'
            if not csv_path.exists():
                raise CommandError(f"Arquivo CSV não encontrado: {csv_path}")

            df = pd.read_csv(csv_path)

            for index, row in df.iterrows():
                headword = str(row['Headword']).strip()
                sensenumber = int(row['SenseNumber'])
                definicao_texto = str(row['Definition']).strip()

                try:
                    verbete = Verbete.objects.get(termo=headword)
                    
                    # update_or_create: encontra pela combinação verbete e sensenumber
                    # ou cria uma nova definição se não existir
                    definition, criado = Definition.objects.update_or_create(
                        verbete=verbete,
                        sensenumber=sensenumber,
                        defaults={'definition': definicao_texto}
                    )
                    if criado:
                        self.stdout.write(self.style.SUCCESS(f"✔️ Criado Definição: {headword} ({sensenumber})"))
                    else:
                        self.stdout.write(self.style.NOTICE(f"🔁 Atualizado Definição: {headword} ({sensenumber})"))
                except Verbete.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"❌ Verbete não encontrado para Definição na linha {index}: {headword}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Erro ao processar linha {index} para Definição {row.get("Headword")}: {e}'))
            self.stdout.write(self.style.SUCCESS('Importação de Definições concluída.'))
        else:
            self.stdout.write(self.style.NOTICE('Importação de Definições pulada (--skip-definitions).'))

        # --- Parte 3: Importar Ocorrências ---
        if not skip_ocorrencias:
            self.stdout.write(self.style.HTTP_INFO('Iniciando importação de Ocorrências...'))
            csv_path = data_dir / 'termos_extraidos.csv'
            if not csv_path.exists():
                raise CommandError(f"Arquivo CSV não encontrado: {csv_path}. Certifique-se de ter rodado import_corpus_data primeiro.")

            df = pd.read_csv(csv_path)

            # Para Ocorrências, o padrão comum em full refresh é apagar tudo e recriar,
            # pois identificar uma única ocorrência por chaves de negócio é difícil.
            # Se você precisar de atualização em vez de recriação, precisará de uma chave única.
            self.stdout.write(self.style.WARNING('Apagando ocorrências antigas antes de importar novas...'))
            OcorrenciaCorpus.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Ocorrências antigas apagadas.'))

            for index, row in df.iterrows():
                try:
                    headword = str(row['Headword']).strip()
                    sense_number = int(row['SenseNumber'])

                    verbete = Verbete.objects.get(termo=headword)
                    
                    definicao = None
                    try:
                        # Tenta encontrar a definição vinculada, mas não é obrigatória
                        definicao = Definition.objects.get(verbete=verbete, sensenumber=sense_number)
                    except Definition.DoesNotExist:
                        self.stdout.write(self.style.NOTICE(f"  Definição {sense_number} para {headword} não encontrada. Ocorrência será vinculada sem definição específica."))
                    
                    OcorrenciaCorpus.objects.create(
                        verbete=verbete,
                        definicao=definicao,
                        token=row['token'],
                        orth=row.get('orth', ''),
                        gram=row.get('gram', ''),
                        frase=row['sentence'],
                        autor=row.get('author_surname', ''),
                        data=row.get('date', ''),
                        titulo_obra=row.get('title', ''),
                        slug_obra=row.get('slug_obra', ''),
                    )
                    self.stdout.write(self.style.SUCCESS(f"✔️ Salvo Ocorrência: {verbete.termo} ({sense_number}) na linha {index}"))
                except Verbete.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"❌ Verbete não encontrado para Ocorrência na linha {index}: {row.get('Headword')}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Erro ao processar linha {index} para Ocorrência: {e}'))
            self.stdout.write(self.style.SUCCESS('Importação de Ocorrências concluída.'))
        else:
            self.stdout.write(self.style.NOTICE('Importação de Ocorrências pulada (--skip-ocorrencias).'))

        self.stdout.write(self.style.SUCCESS('Comando import_dictionary_data concluído.'))