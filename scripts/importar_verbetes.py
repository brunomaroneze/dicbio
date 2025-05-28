import pandas as pd
from verbetes.models import Verbete
from datetime import datetime

# Caminho do CSV (ajuste conforme a localização real)
CAMINHO_CSV = 'data/DadosDoDicionario.csv'

# Lê o CSV com Pandas
df = pd.read_csv(CAMINHO_CSV)

# Função para converter '25 Jan 2024' em datetime.date
def parse_data(data_str):
    if pd.isna(data_str) or not isinstance(data_str, str):
        return None
    try:
        return datetime.strptime(data_str.strip(), '%d %b %Y').date()
    except Exception as e:
        print(f'Erro ao converter data: "{data_str}" — {e}')
        return None

for _, row in df.iterrows():
    termo = str(row['Headword']).strip()

    verbete, criado = Verbete.objects.get_or_create(termo=termo)
    verbete.classe_gramatical = row.get('WClass', '').strip()
    verbete.etimologia = row.get('Etymology', '').strip()
    verbete.primeira_ocorrencia = row.get('FirstAttestationExampleMD', '').strip()
    verbete.data_ocorrencia = row.get('FirstAttestationDate', '').strip()
    verbete.autores = row.get('Credits', '').strip()

    verbete.criado_em = parse_data(row.get('DateOfCreation'))
    verbete.atualizado_em = parse_data(row.get('DateOfUpdate'))

    verbete.save()

    if criado:
        print(f"✔️ Criado: {termo}")
    else:
        print(f"🔁 Atualizado: {termo}")
