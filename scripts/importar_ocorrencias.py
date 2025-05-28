import pandas as pd
from verbetes.models import Verbete, Definition, OcorrenciaCorpus

CAMINHO_CSV = 'data/termos_extraidos.csv'

df = pd.read_csv(CAMINHO_CSV)

erros = []

for _, row in df.iterrows():
    headword = str(row['Headword']).strip()
    sense_number = int(row['SenseNumber'])

    try:
        verbete = Verbete.objects.get(termo=headword)
    except Verbete.DoesNotExist:
        print(f"❌ Verbete não encontrado: {headword}")
        continue

    try:
        definicao = Definition.objects.get(verbete=verbete, sensenumber=sense_number)
    except Definition.DoesNotExist:
        definicao = None  # segue sem vínculo com definição

    ocorrencia = OcorrenciaCorpus.objects.create(
        verbete=verbete,
        definicao=definicao,
        token=row['token'],
        orth=row.get('orth', ''),
        gram=row.get('gram', ''),
        frase=row['sentence'],
        autor=row.get('author_surname', ''),
        data=row.get('date', '')
    )

    print(f"✔️ Ocorrência salva para: {verbete.termo} ({sense_number})")
