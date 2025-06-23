import pandas as pd
from verbetes.models import Verbete, Definition

CAMINHO_CSV = 'data/definitions.csv'

# Lê o CSV com os campos headword, sensenumber, definition
df = pd.read_csv(CAMINHO_CSV)

erros = []

for _, row in df.iterrows():
    headword = str(row['Headword']).strip()
    sensenumber = int(row['SenseNumber'])
    definicao_texto = str(row['Definition']).strip()

    try:
        verbete = Verbete.objects.get(termo=headword)
        Definition.objects.create(
            verbete=verbete,
            sensenumber=sensenumber,
            definition=definicao_texto
        )
        print(f"✔️ {headword} ({sensenumber})")
    except Verbete.DoesNotExist:
        erros.append(headword)
        print(f"❌ Verbete não encontrado: {headword}")
