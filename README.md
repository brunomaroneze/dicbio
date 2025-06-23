# Dicionário Histórico de Termos da Biologia

O *Dicionário Histórico de Termos da Biologia* é consultável neste link:
https://dicbio.fflch.usp.br

Este repositório contém o código-fonte desse dicionário (em Python e Django) e os arquivos .CSV que o alimentam.

Também contém os arquivos .XML que compõem o córpus e os scripts que extraem
as informações dessas obras.

Os dados são continuamente atualizados à medida que o dicionário também é
atualizado.

Tanto os códigos-fonte quanto os demais arquivos são disponíveis gratuitamente
sob a Licença
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/),
que permite o compartilhamento e o uso livre (exceto para usos comerciais),
desde que citada a fonte.

## Procedimentos mínimos para ambiente de desenvolvimento

Dependências Debian:

    sudo apt-get install pkg-config python3-dev default-libmysqlclient-dev build-essential

Opção se for usar virtualenv:

    python3 -m venv venv
    source venv/bin/activate
    ./venv/bin/pip3 install -r requirements.txt

Gerando uma secret key:

    python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

Configurando variáveis de ambiente (secret key gerada anteriormente e mysql):

    cp .env.sample .env

Rodando migrations e subindo server:

    python manage.py migrate
    python manage.py runserver
