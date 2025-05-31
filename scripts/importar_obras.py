from lxml import etree
from pathlib import Path
from corpus_digital.models import Obra
from django.utils.text import slugify
import re

# Caminho da pasta onde estão os arquivos TEI
base_path = Path('web/corpus_digital/obras')
xml_files = list(base_path.glob('*.xml'))

ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

# Função para extrair título e autor de um arquivo TEI
def extrair_titulo_autor(xml_path):
    tree = etree.parse(str(xml_path))
    bibl = tree.find('.//tei:teiHeader//tei:sourceDesc//tei:bibl', namespaces=ns)
    if bibl is not None:
        title = bibl.findtext('tei:title', default='(Sem título)', namespaces=ns)
        author = bibl.findtext('tei:author', default='(Sem autor)', namespaces=ns)
        # Remove quebras de linha e espaços indesejados
        title = re.sub(r'\s+', ' ', title).strip()
        author = re.sub(r'\s+', ' ', author).strip()
        return title, author
    return '(Sem título)', '(Sem autor)'

# Laço principal: processa os arquivos e insere no banco de dados
for xml_file in xml_files:
    titulo, autor = extrair_titulo_autor(xml_file)
    slug = slugify(xml_file.stem)
    caminho_arquivo = f"obras/{xml_file.name}"

    # Verifica se já existe uma obra com este slug
    if Obra.objects.filter(slug=slug).exists():
        print(f"[IGNORADO] Já existe: {titulo} ({slug})")
        continue

    # Cria e salva a obra no banco de dados
    nova_obra = Obra(
        titulo=titulo,
        autor=autor,
        slug=slug,
        caminho_arquivo=caminho_arquivo
    )
    nova_obra.save()
    print(f"[IMPORTADO] {titulo} ({slug})")
