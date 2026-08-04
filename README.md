# Dicionário Histórico de Termos da Biologia

O *Dicionário Histórico de Termos da Biologia* é um projeto de Humanidades Digitais dedicado ao estudo histórico do léxico científico português a partir dos séculos XVII e XVIII.

## Objetivos
Os objetivos são:

- Documentar a história dos termos científicos;
- Construir um *corpus* histórico de textos científicos em língua portuguesa;
- Disponibilizar os dados em formatos reutilizáveis (XML e RDF).

O *Dicionário Histórico de Termos da Biologia* é consultável neste link:
https://dicbio.fflch.usp.br

## Principais recursos
No site do projeto, é possível:

- Consultar os verbetes;
- Consultar o *corpus* transcrito e as imagens das obras.

Este repositório contém:

- o código-fonte do dicionário (em Python e Django);
- os arquivos do *corpus* anotado em XML (padrão TEI);
- os dados do dicionário em RDF (OntoLex-Lemon).

Os dados são continuamente atualizados à medida que o dicionário também é atualizado.

## Tecnologias utilizadas

- Python
- Django
- Bootstrap
- TEI-XML
- RDF
- OntoLex-Lemon

## Como executar o site localmente

Para executar o site localmente, as seguintes etapas são necessárias:

1. Clonar o repositório (comando ```git clone https://github.com/brunomaroneze/dicbio```);
2. Criar um ambiente virtual (comando ```python -m venv venv```);
3. Instalar as dependências necessárias (comando ```pip install -r requirements.txt```);
4. Gerar a lista de contextos do *corpus* (comando ```python manage.py extract_corpus_terms --force-regen```);
5. Gerar os metadados das obras do *corpus* (comando ```python manage.py import_obra_metadata```);
6. Converter os arquivos XML do *corpus* para HTML (comando ```python manage.py processar_obras_tei --force```);
7. Extrair os dados dos verbetes dos arquivos CSV (comando ```python manage.py import_dictionary_data```);
8. Popular o banco de dados (comando ```python manage.py migrate```);
9. Rodar o servidor local (comando ```python manage.py runserver```).

## Documentação

A documentação mais detalhada pode ser acessada em https://dicbio.fflch.usp.br/documentacao/.

## Financiamento

O projeto contou com financiamento do CNPq (2023-2024) e atualmente conta com o financiamento da FUNDECT.

## Licença

Tanto os códigos-fonte quanto os demais arquivos são disponíveis gratuitamente
sob a Licença
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by/4.0/),
que permite o compartilhamento e o uso livres, desde que citada a fonte.
