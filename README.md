# Dicionário Histórico de Termos da Biologia

## Visão geral

O *Dicionário Histórico de Termos da Biologia* é um projeto de Humanidades Digitais dedicado ao estudo histórico do léxico científico português a partir dos séculos XVII e XVIII. O projeto reúne um dicionário histórico, um *corpus* digital anotado em TEI-XML e uma representação lexical em RDF seguindo o modelo OntoLex-Lemon.

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

## Arquitetura

O *corpus*, transcrito usando ferramentas computacionais (em especial o Transkribus) e revisão humana, está anotado com marcações do padrão TEI-XML. Um script em Python (comando ```python manage.py processar_obras_tei```) converte os textos para HTML (para serem exibidos no site). Outro script (comando ```python manage.py extract_corpus_terms```) extrai todos os elementos ```<term>``` do *corpus* e gera um arquivo CSV (```termos_extraidos.csv```) contendo um contexto (em geral, frase ou parágrafo) para cada termo.

As informações dos verbetes (definições, explicações etimológicas, classe gramatical etc.) estão nos arquivos ```DadosDoDicionario.csv``` e ```definitions.csv```, atualizados manualmente. Atualmente, estão sendo feitos testes para disponibilizar esses dados em formato RDF, de modo que LLMs possam redigir os verbetes de forma semiautomática. Esses dados em RDF (Turtle) estão na pasta ```entries```.

Os arquivos CSV são transformados num banco de dados administrado por scripts da biblioteca Django (Python), biblioteca essa que também é empregada no *front-end*.

## Estrutura do repositório

Este repositório contém diversas subpastas com todos os códigos necessários para rodar o site do projeto.

Algumas subpastas de interesse são:
- ```corpus_digital/obras```: contém os arquivos TEI-XML das obras que integram o *corpus*;
- ```data```: contém os arquivos CSV e Turtle com os dados dos verbetes;
- ```documentacao```: contém os textos da seção "Documentação" em formato MarkDown;
- ```scripts```: contém scripts diversos para manipular os dados.

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

## Como citar


## Licença

Tanto os códigos-fonte quanto os demais arquivos são disponíveis gratuitamente
sob a Licença
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by/4.0/),
que permite o compartilhamento e o uso livres, desde que citada a fonte.
