# verbetes/management/commands/generate_word_temporality.py

import csv
import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
from django.core.management.base import BaseCommand
from django.conf import settings
from corpus_digital.models import Obra

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class Command(BaseCommand):
    help = 'Gera um CSV com palavras (tokens ou lemas) de texto em português, título da obra e data de publicação, desconsiderando stopwords e trechos em latim.'

    def _extract_text_and_lemmas_from_element(self, element, tokens_and_lemmas):
        """
        Função recursiva para extrair texto e lemas de elementos BeautifulSoup.
        Prioriza data-lemma de tags <a> e depois o texto de outros nós.
        IGNORA o conteúdo de elementos com o atributo lang="la".
        """
        tags_to_ignore_content_completely = ['script', 'style']
        
        # Se o elemento atual for marcado como latim, não processar ele nem seus filhos.
        if element.name and element.get('lang') == 'la':
            # self.stdout.write(self.style.NOTICE(f"  Ignorando conteúdo do elemento <{element.name}> com lang='la'."))
            return 

        if element.name in tags_to_ignore_content_completely:
            return

        # tags_to_skip_direct_text foi removido porque a lógica de ignorar lang="la" é mais prioritária.
        # Se um span for lang="la", será ignorado. Se não for, seu texto será processado.

        for child in element.children:
            if isinstance(child, NavigableString):
                # Verifica se o pai direto do texto não é lang="la"
                # (embora a verificação no início da função já deva pegar o elemento pai)
                parent_lang = child.parent.get('lang') if child.parent and child.parent.name else None
                if parent_lang == 'la':
                    continue # Ignora este texto se o pai direto for latim

                text_content = child.strip()
                if text_content:
                    # Se o pai for um 'a' com data-lemma E NÃO for latim, já foi tratado.
                    # Este texto é de outros elementos.
                    parent_is_lemma_link = (child.parent.name == 'a' and child.parent.has_attr('data-lemma'))
                    if not parent_is_lemma_link: # Processa texto comum
                         tokens_and_lemmas.append({'text': text_content, 'lemma': None, 'is_term': False})
            
            elif child.name == 'a' and child.has_attr('data-lemma'):
                # Verifica se o próprio link <a> não está marcado como latim
                if child.get('lang') == 'la':
                    # self.stdout.write(self.style.NOTICE(f"  Ignorando link de termo <{child.name}> com lang='la': {child.get_text(strip=True)}"))
                    continue # Ignora este link de termo se ele estiver marcado como latim

                lemma = child.get('data-lemma')
                token_text = child.get_text(strip=True)
                if lemma:
                    tokens_and_lemmas.append({'text': token_text, 'lemma': lemma, 'is_term': True})
                elif token_text: 
                    tokens_and_lemmas.append({'text': token_text, 'lemma': None, 'is_term': False})
            
            elif child.name: 
                # Chamada recursiva para outros elementos filhos
                # A verificação de lang="la" no início da função cuidará de sub-árvores em latim.
                self._extract_text_and_lemmas_from_element(child, tokens_and_lemmas)


    def handle(self, *args, **options):
        # ... (o início do handle com stopwords, regex, etc., permanece o mesmo) ...
        self.stdout.write(self.style.SUCCESS('Iniciando a geração do CSV de temporalidade de palavras...'))

        try:
            portuguese_stopwords = set(stopwords.words('portuguese'))
        except LookupError:
            self.stderr.write(self.style.ERROR("Recursos NLTK (stopwords) não encontrados. Execute nltk.download('stopwords')."))
            return
        
        # Sua lista de custom_stopwords
        custom_stopwords = {
            'q', 'qs', 'huma', 'hum', 'deste', 'desta', 'neste', 'nesta', 
            'naõ', 'dos', 'das', 'pello', 'pella', 'se', 'ser', 'haver',
            'ter', 'athe', 'delle', 'he', 'saõ', 'porque', 'taõ', 'tres',
            'duas', 'fig', 'todos', 'muitos', 'cada', 'tal', 'assim',
            'quasi', 'dous', 'algumas', 'alguns', 'sobre', 'bem',
            'quatro', 'outro', 'outros', 'muito', 'mais', 'tudo', 'pois',
            'meya', 'algum', 'ha', 'quaes', 'si', 'elle', 'cinco',
            'sempre', 'toda', 'destas', 'qualquer', 'humas', 'foy',
            'taes', 'so', 'elles', 'tão', 'porèm', 'ella', 'taõbem',
            'della', 'delles', 'todas', 'tanto', 'antes', 'alguma',
            'estaõ', 'sendo', 'todo'
            # ADICIONE MAIS AQUI CONFORME NECESSÁRIO
        }
        all_stopwords = portuguese_stopwords.union(custom_stopwords)
        
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
            
            extracted_words_info = []
            body_content = soup.body if soup.body else soup 
            if body_content:
                self._extract_text_and_lemmas_from_element(body_content, extracted_words_info)

            if not extracted_words_info:
                self.stdout.write(self.style.NOTICE(f'  Nenhum texto/termo em português significativo extraído para: {obra.titulo}'))
                continue

            # O resto do loop para processar extracted_words_info e gerar o CSV permanece o mesmo
            for word_info in extracted_words_info:
                text_to_tokenize = word_info['lemma'] if word_info['is_term'] and word_info['lemma'] else word_info['text']
                
                if word_info['is_term'] and word_info['lemma']:
                    tokens = [word_info['lemma'].lower()]
                else:
                    try:
                        tokens = word_tokenize(text_to_tokenize.lower(), language='portuguese')
                    except LookupError:
                        self.stderr.write(self.style.ERROR("Recursos NLTK (punkt) não encontrados. Execute nltk.download('punkt')."))
                        return # Aborta se o punkt não estiver disponível
                
                for token in tokens:
                    cleaned_token = punct_re.sub('', token)
                    if cleaned_token and len(cleaned_token) > 1 and cleaned_token not in all_stopwords:
                        data_for_csv.append({
                            'palavra_analisada': cleaned_token,
                            'token_original': word_info['text'] if not word_info['is_term'] else token,
                            'titulo_obra': obra.titulo,
                            'data_publicacao': obra.data_referencia or 'N/A',
                            'slug_obra': obra.slug,
                            'eh_termo_dicionario': word_info['is_term']
                        })
        
        if not data_for_csv:
            self.stdout.write(self.style.WARNING('Nenhuma palavra (em português) processada para o CSV.'))
            return

        output_dir = settings.BASE_DIR / 'data'
        output_dir.mkdir(parents=True, exist_ok=True)
        # Sugiro um novo nome para o arquivo CSV para refletir que o latim foi ignorado
        csv_file_path = output_dir / 'temporalidade_palavras_pt_apenas.csv' 

        try:
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['palavra_analisada', 'token_original', 'titulo_obra', 'data_publicacao', 'slug_obra', 'eh_termo_dicionario']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data_for_csv)
            self.stdout.write(self.style.SUCCESS(f'CSV (ignorando latim) gerado com sucesso em: {csv_file_path}'))
        except IOError:
            self.stderr.write(self.style.ERROR(f'Não foi possível escrever o arquivo CSV em: {csv_file_path}'))