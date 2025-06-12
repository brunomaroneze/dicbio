# Córpus
O **Dicionário Histórico de Termos da Biologia** é inteiramente baseado num córpus formado por textos científicos publicados em língua portuguesa. Esse córpus (assim como o próprio dicionário) está em contínua atualização (cf. "Política de disponibilização dos dados") e disponível integralmente (no repositório *GitHub*), por ser constituído apenas por textos em domínio público.

Optou-se por, inicialmente, incluir no córpus apenas textos do século XVIII (por ser este um momento histórico altamente significativo no desenvolvimento da Ciência, especialmente em língua portuguesa); posteriormente, pretende-se incluir outros períodos históricos (tanto anteriores quanto posteriores).

Os textos que compõem o córpus (cf. "Textos que compõem o córpus", abaixo) estão disponibilizados em formato .xml (cf. "Política de disponibilização dos dados"), com as etiquetas descritas abaixo; o *script* que extrai as informações dos textos (cf. "Estrutura computacional") também disponível no repositório *GitHub*.

### Textos que compõem o córpus:
Os textos que integram o córpus podem ser encontrados nos *links* abaixo. O córpus transcrito em formato .xml está disponível no repositório *GitHub* (cf. "Política de disponibilização dos dados").

- BROTERO, Félix de Avelar. [**Compendio de Botanica**](https://digitalis-dsp.uc.pt/botanica/UCFCTBt-B-78-1-15_2/UCFCTBt-B-78-1-15_2_item1/index.html). Vol. 1. Paris: Vende-se em Lisboa, em caza de Paulo Martin, Mercador de Livros, 1788.

- SANTUCCI, Bernardo. [**Anatomia do corpo humano**](https://books.google.com.br/books/about/Anatomia_do_corpo_humano.html?id=D83JL7ybBeUC&redir_esc=y). Lisboa: na Officina de Antonio Pedrozo Galram, 1739.

- VANDELLI, Domingos. [**Diccionario dos termos technicos de Historia Natural**](https://purl.pt/13958). Coimbra: na Real Officina da Universidade, 1788.

### Formatação do córpus
Os textos que compõem o córpus estão sendo etiquetados com o emprego de etiquetas XML (também chamados de "elementos XML") que seguem o padrão [Text Encoding Initiative](https://tei-c.org/)). Os arquivos com a extensão .xml, bem como o arquivo RELAX-NG (*tei_dhtb.rng*) que contém as instruções para o emprego das etiquetas, estão disponíveis no repositório *GitHub* (cf. "Política de disponibilização dos dados").

Dentro do elemento **TeiHeader** de cada arquivo estão descritos os critérios de transcrição e de uso dos elementos TEI-XML. Os principais elementos empregados são os seguintes:

- **text** - Contém toda a parte textual de cada obra transcrita; é dividido em **front** (que contém a página de rosto e outros elementos pré-textuais), **body** (que contém o texto propriamente dito) e **back** (que contém índices e outros elementos pós-textuais);

- **div** - Indica subdivisões no texto, como partes, capítulos e subcapítulos;

- **p** - Delimita parágrafos;

- **s** - Delimita sentenças;

- **entry** - Delimita verbetes de dicionários (no caso das obras que são ou contêm dicionários, como a obra de Vandelli ou o segundo volume do *Compendio de Botanica* de Brotero). Dentro de cada verbete, o elemento **form** marca a palavra-entrada e o elemento **sense** indica o equivalente ou a explicação;

- **term** - Etiqueta que marca os termos que integram a nomenclatura do dicionário; pode vir acompanhada dos atributos *lemma* (lema), *norm* (forma ortográfica atualizada), *msd* (descrição morfossintática, como "plural" ou "feminino") e *senseNumber* (número da acepção);

- **w** - Etiqueta empregada para o registro de informações (inseridas como atributos) sobre palavras diversas do texto, mas que não são termos e não constam da nomenclatura do dicionário;

- **note** - Elemento que delimita notas de rodapé ou de margem de página;

- **foreign** - Indica que a palavra ou o trecho delimitado está numa língua diferente da portuguesa; o atributo *xml:lang* indica que língua é essa;

- **pb** - Elemento vazio que indica quebra de página da obra; o número da página que se inicia a partir desta marca é indicado no atributo *n*.
