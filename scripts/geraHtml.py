"""Código gerado pelo DeepSeek.
Gera um HTML para cada verbete."""

import csv
import random
import os
from datetime import datetime
from collections import defaultdict

def read_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def process_data(dados_csv, definitions_csv, termos_csv):
    # Organizar definições por headword
    definitions = defaultdict(list)
    for row in definitions_csv:
        definitions[row['Headword']].append(row)
    
    # Organizar termos extraídos por headword, sense number e gram
    termos = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for row in termos_csv:
        headword = row['Headword']
        sense_num = row['SenseNumber']
        gram = row['gram']
        autor = row['author_surname'].strip().upper() if row['author_surname'] else 'OUTRO'
        
        termos[headword][sense_num][gram].append({
            'token': row['token'],
            'gram': gram,
            'sentence': row['sentence'],
            'autor': autor
        })
    
    # Combinar tudo
    verbetes = []
    for row in dados_csv:
        headword = row['Headword']
        verbete = {
            'headword': headword,
            'first_attestation': row['FirstAttestationDate'],
            'first_attestation_example': row['FirstAttestationExampleMD'],
            'etymology': row['Etymology'],
            'wclass': row['WClass'],
            'credits': row['Credits'],
            'date_creation': row['DateOfCreation'],
            'date_update': row['DateOfUpdate'],
            'definitions': definitions.get(headword, []),
            'termos': termos.get(headword, {})
        }
        verbetes.append(verbete)
    
    return verbetes

def generate_html(verbete):
    # Processar autores para citação
    autores_citacao = []
    for autor in verbete['credits'].split(';'):
        partes = autor.strip().split()
        if len(partes) >= 2:
            sobrenome = partes[-1].upper()
            iniciais = ' '.join([f"{nome[0]}." for nome in partes[:-1]])
            autores_citacao.append(f"{sobrenome}, {iniciais}")
    autores_citacao = '; '.join(autores_citacao)
    
    # Data de acesso (hoje)
    data_acesso = datetime.now().strftime('%d %b %Y').lower()
    
    html = f"""<!DOCTYPE html>
<html>
    <head>
        <title>{verbete['headword']}</title>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <div class="verbete-header">
            <h1>{verbete['headword']}</h1>
            <p class="word-class">{verbete['wclass']}</p>
        </div>
        
        <div class="etymology-section">
            <h2>Discussão histórico-etimológica</h2>
            <p>{verbete['etymology']}</p>
        </div>
        
        <div class="definitions-section">
            <h2>Definição(ões)</h2>"""
    
    # Adicionar definições e exemplos
    for definicao in verbete['definitions']:
        sense_num = definicao['SenseNumber']
        html += f"""
            <div class="definition-block">
                <p class="definition">{sense_num}. {definicao['Definition']}</p>"""
        
        # Buscar exemplos para este sense number
        if str(sense_num) in verbete['termos']:
            termos_sense = verbete['termos'][str(sense_num)]
            
            # Para cada variação gramatical, pegar um exemplo
            exemplos_por_autor = defaultdict(list)
            for gram in termos_sense:
                exemplos = termos_sense[gram]
                # Agrupar por autor e selecionar um de cada
                exemplos_autor = defaultdict(list)
                for ex in exemplos:
                    exemplos_autor[ex['autor']].append(ex)
                
                # Selecionar um exemplo por autor (em ordem alfabética do autor)
                for autor in sorted(exemplos_autor.keys()):
                    if exemplos_autor[autor]:
                        ex_escolhido = random.choice(exemplos_autor[autor])
                        exemplos_por_autor[gram].append(ex_escolhido)
            
            # Ordenar as variações gramaticais
            ordens_gram = {
                'masculino singular': 0,
                'feminino singular': 1,
                'masculino plural': 2,
                'feminino plural': 3
            }
            gram_ordenadas = sorted(exemplos_por_autor.keys(), 
                                  key=lambda x: ordens_gram.get(x, 99))
            
            for gram in gram_ordenadas:
                for ex in exemplos_por_autor[gram]:
                    # Formatar a exibição da forma gramatical
                    form_display = ex['token']
                    if gram.strip():  # Só mostra gram se não for vazio
                        form_display += f" ({gram})"
                    
                    html += f"""
                <div class="example">
                    <p class="example-form">{form_display}</p>
                    <p class="example-text">{ex['sentence']}</p>
                </div>"""
        
        html += "\n            </div>"  # fecha definition-block
    
    html += """
        </div>"""  # fecha definitions-section
    
    # Adicionar rodapé
    html += f"""
        <div class="verbete-footer">
            <div class="credits">
                <p>Autor(es) do verbete: {verbete['credits']}</p>
                <p>Este verbete foi incluído em {verbete['date_creation']}"""
    
    if verbete['date_creation'] != verbete['date_update']:
        html += f" e atualizado em {verbete['date_update']}"
    
    html += f"""</p>
            </div>
            
            <div class="citation">
                <p>Como citar este verbete:</p>
                <p>{autores_citacao}. {verbete['headword'].capitalize()}. In: MARONEZE, Bruno (coord.) <b>Dicionário Histórico de Termos da Biologia</b>. 2022-2025. Disponível em: https://dicbio.fflch.usp.br/. Acesso em: {data_acesso}.</p>
            </div>
        </div>
    </body>
</html>"""
    
    return html

def main():
    # Criar pasta html se não existir
    if not os.path.exists('html'):
        os.makedirs('html')
    
    # Ler os arquivos CSV
    dados_csv = read_csv('data/DadosDoDicionario.csv')
    definitions_csv = read_csv('data/definitions.csv')
    termos_csv = read_csv('data/termos_extraidos.csv')
    
    # Processar os dados
    verbetes = process_data(dados_csv, definitions_csv, termos_csv)
    
    # Gerar HTML para cada verbete
    for verbete in verbetes:
        html = generate_html(verbete)
        filename = f"html/{verbete['headword']}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Arquivo gerado: {filename}")

if __name__ == '__main__':
    main()