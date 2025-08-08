# calculate_word_frequencies.py

import pandas as pd
from pathlib import Path

# --- Configuração ---
# Ajuste estes caminhos conforme necessário
# Assumindo que o projeto tem uma pasta 'data' na raiz
# PROJECT_ROOT = Path(__file__).resolve().parent # Se o script estiver na raiz do projeto
# Se o script estiver em uma subpasta 'scripts', use:
PROJECT_ROOT = Path(__file__).resolve().parent.parent 

DATA_DIR = PROJECT_ROOT / 'data'
INPUT_CSV_NAME = 'temporalidade_palavras_pt_apenas.csv' # O CSV gerado pelo script anterior
OUTPUT_CSV_NAME = 'frequencia_palavras_total.csv'
OUTPUT_CSV_BY_DATE_NAME = 'frequencia_palavras_por_data.csv'

def main():
    print(f"Iniciando cálculo de frequência de palavras...")

    input_csv_path = DATA_DIR / INPUT_CSV_NAME
    output_csv_path_total = DATA_DIR / OUTPUT_CSV_NAME
    output_csv_path_by_date = DATA_DIR / OUTPUT_CSV_BY_DATE_NAME

    if not input_csv_path.exists():
        print(f"ERRO: Arquivo de entrada não encontrado: {input_csv_path}")
        print("Certifique-se de que o script 'generate_word_temporality_csv.py' (ou o comando Django) foi executado primeiro.")
        return

    try:
        # Ler o CSV gerado anteriormente
        df = pd.read_csv(input_csv_path)
        print(f"Lidas {len(df)} linhas do arquivo {input_csv_path}")
    except Exception as e:
        print(f"ERRO ao ler o arquivo CSV: {e}")
        return

    # Verificar se a coluna 'palavra_analisada' existe
    if 'palavra_analisada' not in df.columns:
        print("ERRO: A coluna 'palavra_analisada' não foi encontrada no CSV de entrada.")
        print(f"Colunas encontradas: {df.columns.tolist()}")
        return

    # --- 1. Calcular Frequência Total das Palavras ---
    print("\nCalculando frequência total das palavras...")
    # value_counts() já conta e ordena por padrão (do maior para o menor)
    word_frequencies_total = df['palavra_analisada'].value_counts().reset_index()
    word_frequencies_total.columns = ['palavra', 'frequencia_total']
    
    try:
        word_frequencies_total.to_csv(output_csv_path_total, index=False, encoding='utf-8')
        print(f"CSV com frequência total salvo em: {output_csv_path_total}")
    except Exception as e:
        print(f"ERRO ao salvar CSV de frequência total: {e}")


    # --- 2. Calcular Frequência das Palavras Agrupadas por Data de Publicação ---
    print("\nCalculando frequência das palavras por data de publicação...")
    if 'data_publicacao' in df.columns:
        # Agrupa por 'data_publicacao' e 'palavra_analisada', conta as ocorrências, e desempilha
        # O size().reset_index(name='frequencia') cria um DataFrame com as contagens
        word_frequencies_by_date = df.groupby(['data_publicacao', 'palavra_analisada']).size().reset_index(name='frequencia')
        
        # Ordenar para melhor visualização (opcional, mas útil)
        # Ordena primeiro por data, depois por frequência (decrescente) dentro de cada data
        word_frequencies_by_date = word_frequencies_by_date.sort_values(
            by=['data_publicacao', 'frequencia'], 
            ascending=[True, False]
        )
        
        try:
            word_frequencies_by_date.to_csv(output_csv_path_by_date, index=False, encoding='utf-8')
            print(f"CSV com frequência por data salvo em: {output_csv_path_by_date}")
        except Exception as e:
            print(f"ERRO ao salvar CSV de frequência por data: {e}")
    else:
        print("AVISO: Coluna 'data_publicacao' não encontrada. Não foi possível calcular frequência por data.")

    print("\nProcesso concluído.")

if __name__ == '__main__':
    main()