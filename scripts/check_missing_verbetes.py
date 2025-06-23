# scripts/check_missing_verbetes.py

import pandas as pd
from pathlib import Path
import os
import sys
import django

# --- Configuração do Caminho do Projeto ---
# Calcula o caminho para o diretório raiz do seu projeto (a pasta 'web')
# e o adiciona ao caminho de busca de módulos do Python.
# Este script está em 'web/scripts/check_missing_verbetes.py'
# project_root = Path(__file__).resolve().parent.parent aponta para 'web/'
project_root = Path(__file__).resolve().parent.parent 
sys.path.append(str(project_root)) # Adiciona 'web/' ao sys.path

# --- Configuração do Ambiente Django ---
# Você precisa configurar o ambiente Django para que o script possa acessar seus modelos.
# Altere 'dicionario_web.settings' para o caminho do seu arquivo settings.py
# Ex: 'seu_projeto.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dicionario_web.settings')
django.setup()

# --- Importação dos Modelos Django ---
from verbetes.models import Verbete

# --- Caminho do CSV de Ocorrências ---
# Ajuste conforme a localização real do seu arquivo termos_extraidos.csv
# Ele deve estar na pasta 'data' dentro da raiz do projeto (web/)
TERMOS_EXTRAIDOS_CSV_PATH = Path('web/data/termos_extraidos.csv')

def check_missing_verbetes():
    if not TERMOS_EXTRAIDOS_CSV_PATH.exists():
        print(f"Erro: Arquivo CSV não encontrado em '{TERMOS_EXTRAIDOS_CSV_PATH}'")
        return

    print(f"Lendo o arquivo CSV: {TERMOS_EXTRAIDOS_CSV_PATH}")
    df = pd.read_csv(TERMOS_EXTRAIDOS_CSV_PATH)

    missing_verbetes = []
    
    # Dicionário para armazenar os termos de verbetes existentes, para consultas rápidas
    # Carregamos todos os termos do banco de dados uma vez para evitar N consultas ao DB no loop
    existing_verbetes_terms = set(Verbete.objects.values_list('termo', flat=True))

    print(f"Verificando {len(df)} ocorrências no CSV...")
    for index, row in df.iterrows():
        headword_csv = str(row['Headword']).strip() # O termo que deveria ser um Verbete
        
        # Opcional: Para depuração, se quiser ver cada termo verificado
        # print(f"Verificando linha {index+2}: Headword='{headword_csv}'") # +2 para contar header e 0-index

        if headword_csv not in existing_verbetes_terms:
            # A linha +2 é para compensar o header (1) e o índice baseado em 0 do Pandas
            missing_verbetes.append({
                'linha_csv': index + 2,
                'headword_csv': headword_csv,
                'contexto_exemplo': row.get('sentence', '')[:100] + '...' # Pega os primeiros 100 chars da sentença
            })

    if missing_verbetes:
        print("\n--- ERROS ENCONTRADOS: Verbetes não encontrados para as seguintes ocorrências ---")
        for error in missing_verbetes:
            print(f"  Linha CSV: {error['linha_csv']}")
            print(f"  Headword no CSV: '{error['headword_csv']}'")
            print(f"  Contexto (início da sentença): '{error['contexto_exemplo']}'")
            print("-" * 30)
    else:
        print("\n🎉 Nenhuma ocorrência encontrada com verbete faltante! O CSV está alinhado com os Verbetes existentes.")

if __name__ == "__main__":
    check_missing_verbetes()