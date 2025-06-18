"""
Django settings for dicionario_web project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv # Importe as bibliotecas necessárias

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR aponta para a pasta 'web'
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CARREGAMENTO DAS VARIÁVEIS DE AMBIENTE ---
# Carrega as variáveis do arquivo .env localizado na BASE_DIR (web/.env)
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=dotenv_path)
# -----------------------------------------------


# --- CONFIGURAÇÕES DE SEGURANÇA E AMBIENTE ---
# SECURITY WARNING: keep the secret key used in production secret!
# A chave secreta agora é lida do arquivo .env
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# O valor de DEBUG (True/False) é controlado pelo .env
# O 'True' é um valor padrão caso a variável não seja encontrada
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')

# ALLOWED_HOSTS controla quais domínios podem servir o site.
# Lemos do .env, separando por vírgula se houver mais de um.
ALLOWED_HOSTS_STRING = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STRING.split(',') if host.strip()]
# -----------------------------------------------


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pagina_inicial',
    'verbetes',
    'documentacao',
    # 'diversos', # Este app foi consolidado, pode ser removido se não existir mais
    'corpus_digital',

    # Apps de terceiros que adicionamos
    'markdownify.apps.MarkdownifyConfig', # Vamos precisar para o futuro
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dicionario_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Mantém a pasta de templates compartilhada
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # Adicionando a biblioteca de templatetags customizadas
            'libraries': {
                'custom_filters': 'verbetes.templatetags.custom_filters',
                'doc_filters': 'documentacao.templatetags.doc_filters',
            }
        },
    },
]

WSGI_APPLICATION = 'dicionario_web.wsgi.application'


# --- CONFIGURAÇÃO DO BANCO DE DADOS (DINÂMICA) ---
DJANGO_ENV = os.environ.get('DJANGO_ENV', 'development') # Padrão para 'development'

if DJANGO_ENV == 'production':
    # Configuração para MariaDB/MySQL (para o servidor de produção)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_NAME'),
            'USER': os.environ.get('MYSQL_USER'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
            'HOST': os.environ.get('MYSQL_HOST'),
            'PORT': os.environ.get('MYSQL_PORT'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
        }
    }
else:
    # Configuração para SQLite (para desenvolvimento local)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3', # Ele criará este arquivo se não existir
        }
    }
# -----------------------------------------------------------------


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True # USE_L10N está obsoleto no Django 5, USE_TZ é o correto.


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
# Em produção, você também precisará desta configuração:
# STATIC_ROOT = BASE_DIR / 'staticfiles'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- MINHAS CONFIGURAÇÕES PERSONALIZADAS ---
# Caminho para a pasta raiz onde os arquivos XML do corpus estão armazenados
CORPUS_XML_ROOT = BASE_DIR / 'corpus_digital' / 'obras'

# --- Configuração de Cache ---
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-dicbio-cache', # Nome único para o cache
        'TIMEOUT': 86400, # 24 horas
    }
}

# --- Markdownify (para renderizar markdown em templates) ---
MARKDOWNIFY = {
   "default": {
      "STRIP": False,
      "WHITELIST_TAGS": [
          'a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
          'ul', 'ol', 'li', 'em', 'strong', 'blockquote',
          'code', 'pre', 'br',
      ]
   }
}
# ----------------------------------------------------