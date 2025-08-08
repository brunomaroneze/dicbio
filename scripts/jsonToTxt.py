"""
Este código transforma o arquivo DadosDoDicionario.json para um arquivo TXT
que contém apenas o campo etimologia, para alimentar um LLM.
"""
import json

# Carrega o arquivo JSON
with open('DadosDoDicionario.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# Abre o arquivo de saída em modo de escrita
with open('dicionario_formatado.txt', 'w', encoding='utf-8') as txt_file:
    for entry in data:
        headword = entry.get("Headword", "")
        etymology = entry.get("Etymology", "")

        # Escreve os campos no arquivo TXT
        txt_file.write(f"{headword}\n")
        txt_file.write(f"Etimologia: {etymology}\n")
        txt_file.write("--------------------------------\n")

print("Arquivo TXT criado com sucesso!")