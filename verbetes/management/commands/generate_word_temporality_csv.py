import csv
import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString # Importar NavigableString
from django.core.management.base import BaseCommand
from django.conf import settings
from corpus_digital.models import Obra

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
# import string # string não estava sendo usado diretamente

class Command(BaseCommand):
    help = 'Gera um CSV com palavras (tokens ou lemas), título da obra e data de publicação, desconsiderando stopwords.'

    def _extract_text_and_lemmas_from_element(self, element, tokens_and_lemmas):
        """
        Função recursiva para extrair texto e lemas de elementos BeautifulSoup.
        Prioriza data-lemma de tags <a> e depois o texto de outros nós.
        """
        # Excluir conteúdo de tags específicas e seus descendentes
        tags_to_ignore_content = ['script', 'style']
        # Excluir texto direto de certas tags, mas processar seus filhos (se não forem de ignore_content)
        tags_to_skip_direct_text = ['span'] # Ex: marcadores de página

        if element.name in tags_to_ignore_content:
            return # Ignora completamente o conteúdo dessas tags

        for child in element.children:
            if isinstance(child, NavigableString):
                if child.parent.name not in tags_to_skip_direct_text:
                    text_content = child.strip()
                    if text_content:
                        # Se o pai for um 'a' com data-lemma, já foi tratado.
                        # Este texto é de outros elementos.
                        if not (child.parent.name == 'a' and child.parent.has_attr('data-lemma')):
                             tokens_and_lemmas.append({'text': text_content, 'lemma': None, 'is_term': False})
            
            elif child.name == 'a' and child.has_attr('data-lemma'):
                lemma = child.get('data-lemma')
                token_text = child.get_text(strip=True) # Texto visível do link
                if lemma:
                    tokens_and_lemmas.append({'text': token_text, 'lemma': lemma, 'is_term': True})
                elif token_text: # Caso não tenha data-lemma mas seja um link
                    tokens_and_lemmas.append({'text': token_text, 'lemma': None, 'is_term': False})
                # Não processar mais os filhos de <a> se já pegamos o lema/texto
            
            elif child.name: # Se for outra tag
                self._extract_text_and_lemmas_from_element(child, tokens_and_lemmas)


    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando a geração do CSV de temporalidade de palavras...'))

        try:
            portuguese_stopwords = set(stopwords.words('portuguese'))
        except LookupError:
            self.stderr.write(self.style.ERROR("Recursos NLTK (stopwords) não encontrados. Execute nltk.download('stopwords')."))
            return
        
        custom_stopwords = {
            'q', 'qs', 'huma', 'hum', 'deste', 'desta', 'neste', 'nesta', 
            'nao', 'dos', 'das', 'pello', 'pella', 'se', 'ser', 'haver', 'ter' # Adicionei verbos comuns como exemplo
        }
        all_stopwords = portuguese_stopwords.union(custom_stopwords)
        
        # Regex para limpar tokens: remove pontuação nas bordas e se for só número/espaço
        punct_re = re.compile(r'^\W+|\W+$|^[\d\s]+$')
        
        data_for_csv = []
        obras = Obra.objects.filter(conteudo_html_processado__isnull=False).exclude(conteudo_html_processado='')

        if not obras.exists():
            self.stdout.write(self.style.WARNING('Nenhuma obra com HTML processado encontrada.'))
            return

        for obra in obras:
            self.stdout.write(f'Processando obra: {obra.titulo} ({obra.data_referencia or "Sem Data"})')
            
            html_content = obra.conteudo_html_processado
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Lista para armazenar {'text': texto_original, 'lemma': lema_se_termo, 'is_term': True/False}
            extracted_words_info = []
            
            # Encontrar o elemento body ou o root do conteúdo principal se não houver body
            body_content = soup.body if soup.body else soup 
            if body_content:
                self._extract_text_and_lemmas_from_element(body_content, extracted_words_info)

            if not extracted_words_info:
                self.stdout.write(self.style.NOTICE(f'  Nenhum texto/termo significativo extraído para: {obra.titulo}'))
                continue

            # Agora, processar a lista `extracted_words_info`
            for word_info in extracted_words_info:
                text_to_tokenize = word_info['lemma'] if word_info['is_term'] and word_info['lemma'] else word_info['text']
                
                # Os lemas de termos já devem estar "limpos", mas o texto comum precisa de tokenização
                if word_info['is_term'] and word_info['lemma']:
                    # Se for um termo e tivermos o lema, usamos o lema diretamente
                    # (assumindo que o lema já é uma "palavra" única e normalizada)
                    tokens = [word_info['lemma'].lower()]
                else:
                    # Se não for termo ou não tiver lema, tokenizamos o texto
                    try:
                        tokens = word_tokenize(text_to_tokenize.lower(), language='portuguese')
                    except LookupError:
                        self.stderr.write(self.style.ERROR("Recursos NLTK (punkt) não encontrados. Execute nltk.download('punkt')."))
                        return
                
                for token in tokens:
                    cleaned_token = punct_re.sub('', token)
                    if cleaned_token and len(cleaned_token) > 1 and cleaned_token not in all_stopwords:
                        data_for_csv.append({
                            'palavra_analisada': cleaned_token, # Esta é a palavra que vai para o CSV (lema ou token limpo)
                            'token_original': word_info['text'] if not word_info['is_term'] else token, # Para referência
                            'titulo_obra': obra.titulo,
                            'data_publicacao': obra.data_referencia or 'N/A',
                            'slug_obra': obra.slug,
                            'eh_termo_dicionario': word_info['is_term']
                        })
        
        if not data_for_csv:
            self.stdout.write(self.style.WARNING('Nenhuma palavra processada para o CSV.'))
            return

        output_dir = settings.BASE_DIR / 'data'
        output_dir.mkdir(parents=True, exist_ok=True)
        csv_file_path = output_dir / 'temporalidade_palavras_com_lemas.csv'

        try:
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['palavra_analisada', 'token_original', 'titulo_obra', 'data_publicacao', 'slug_obra', 'eh_termo_dicionario']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data_for_csv)
            self.stdout.write(self.style.SUCCESS(f'CSV gerado com sucesso em: {csv_file_path}'))
        except IOError:
            self.stderr.write(self.style.ERROR(f'Não foi possível escrever o arquivo CSV em: {csv_file_path}'))