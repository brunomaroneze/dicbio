# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 17:09:07 2024

@author: bmaro
"""

import json

# Caminhos dos arquivos
json1_path = 'JSONs/DadosDoDicionario.json'
json2_path = 'JSONs/definitions.json'
output_path = 'JSONs/resultado.json'


def mesclar_jsons(json1_path, json2_path, output_path):
    try:
        # Ler os dois arquivos
        with open(json1_path, 'r', encoding='utf-8') as f1:
            dados_dicionario = json.load(f1)

        with open(json2_path, 'r', encoding='utf-8') as f2:
            definitions = json.load(f2)

        # Criar um dicionário para acesso rápido às definições por 'Headword'
        definitions_dict = {item['Headword']: item for item in definitions}

        # Mesclar os dados
        for entrada in dados_dicionario:
            headword = entrada.get('Headword')
            if headword in definitions_dict:
                entrada['DefinitionData'] = definitions_dict[headword]  # Adicionar a definição correspondente
            else:
                entrada['DefinitionData'] = None  # Nenhuma definição correspondente encontrada

        # Salvar o resultado em um novo arquivo
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dados_dicionario, f, ensure_ascii=False, indent=4)

        print(f"Arquivo mesclado criado com sucesso: {output_path}")
    except Exception as e:
        print(f"Erro ao mesclar os arquivos: {e}")


# Executar a função
mesclar_jsons(json1_path, json2_path, output_path)