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
- **pb** - Elemento vazio que indica quebra de página da obra; o número da página que se inicia a partir desta marca é indicado no atributo *n*;



## Critérios lexicográficos
Descrevem-se aqui os critérios adotados na seleção das entradas e na elaboração dos verbetes.

### Nomenclatura
Prevê-se que o **Dicionário** conterá a totalidade dos termos presentes no córpus analisado, ou seja, todos os substantivos, adjetivos e verbos (inclusive os formados por mais de uma palavra) que designam conceitos científicos relacionados às ciências biológicas e que ocorram nos textos que compõem o córpus. Por ser uma obra de natureza histórica, considera-se como referência a ciência da época dos textos analisados; ou seja, uma unidade lexical é considerada um termo se ela designava um conceito científico no período de circulação da obra, independentemente de esse conceito ser aceito ou não pela ciência do século XXI.

Como a totalidade dos termos é um objetivo ideal, a ser atingido no longo prazo, optou-se por disponibilizar os verbetes à medida que são incluídos (cf. "Política de disponibilização dos dados").

### Informações presentes nos verbetes
Cada entrada do dicionário contém:

a) Classe gramatical;
b) Definições;
c) Contextos de ocorrência;
d) Formas variantes gráficas;
e) Informações histórico-etimológicas.

No caso dos termos polissêmicos, as definições estão numeradas e os contextos de ocorrência estão agrupados juntamente com a definição correspondente.

O campo das variantes gráficas inclui as formas variantes do termo encontradas no córpus.

O campo das informações histórico-etimológicas traz uma discussão a respeito da etimologia do termo, com hipóteses a respeito de sua origem, as primeiras atestações na língua portuguesa, eventuais mudanças de significado pelas quais o termo passou ao longo da história e outras informações que os autores julguem relevantes para uma maior compreensão do termo.

### Bibliografia consultada

- HOUAISS, Antônio; VILLAR, Mauro de Salles. **Grande Dicionário Houaiss da Língua Portuguesa**. Disponível em: [https://houaiss.uol.com.br/](https://houaiss.uol.com.br/).
- GRÉCO, Gérard (dir.) **Gaffiot 2016**. Disponível em: [https://gaffiot.fr/](https://gaffiot.fr/). Baseado em: GAFFIOT, Félix. **Dictionnaire Latin-Français**. Paris: Hachette, 1934.
- LIDDELL, Henry George; SCOTT, Robert; JONES, Henry Stuart (eds.). **Greek-English Lexicon**. 9. ed. Oxford: Clarendon Press, 1940. Disponível em: [http://stephanus.tlg.uci.edu/lsj/#eid=1](http://stephanus.tlg.uci.edu/lsj/#eid=1).
- MEYER-LÜBKE, Wilhelm (org). **Romanisches Etymologisches Wörterbuch**. Heidelberg: Carl Winter's Universitätsbuchhandlung, 1911. Disponível em: [https://archive.org/details/romanischesetymo00meyeuoft] (https://archive.org/details/romanischesetymo00meyeuoft).
- OXFORD Latin Dictionary. Oxford: Clarendon Press, 1968.


## Estrutura computacional
O **Dicionário** apresenta uma interface computacional escrita em linguagem R e que funciona por meio da biblioteca *R Shiny*, que permite a criação de código HTML a partir da interação com o usuário. Dessa forma, a com a seleção de uma entrada da lista à esquerda por parte do usuário, apresentam-se os dados referentes à entrada na parte direita da tela.

Os dados que "alimentam" essa interface, bem como o código-fonte em linguagem R, estão disponíveis para *download* no repositório *GitHub* (cf. "Política de disponibilização dos dados").

## Política de disponibilização dos dados
O **Dicionário** encontra-se em permanente atualização. Para dar mais agilidade à divulgação, optou-se por disponibilizar os verbetes à medida que vão sendo elaborados.

Em cada verbete, registram-se a data da inserção e a data da última atualização. Para facilitar aos pesquisadores que desejam referir-se aos dados, inclui-se também uma proposta de como citar o verbete.

Os dados e o código-fonte encontram-se disponíveis para *download* no repositório *GitHub* [neste *link*](https://github.com/brunomaroneze/dicbio).


## Agradecimentos
A compilação do córpus foi (e ainda é) possível graças à colaboração de estudantes de graduação da Universidade Federal da Grande Dourados, alguns dos quais receberam bolsas de Iniciação Científica da PROPP-UFGD e do CNPq.

O projeto atualmente conta com o valiosíssimo financiamento do CNPq por meio do Edital Pró-Humanidades 2022, sob a forma de bolsas de Iniciação Científica e de Apoio Técnico.

A redação dos primeiros verbetes e a criação da parte computacional do dicionário foram possíveis graças ao estágio de pós-doutoramento desenvolvido pelo coordenador do projeto junto à Universidade de Coimbra (Portugal), sob a supervisão da Profa. Dra. **Graça Rio-Torto**.

A hospedagem do dicionário no servidor da FFLCH-USP foi possível graças à importante parceria com o **NEHiLP** e ao valioso auxílio do técnico **Thiago Gomes Veríssimo**.

Agradecemos a **Ligeia Lugli** (University of London) pelas valiosas orientações a respeito de como implementar um dicionário eletrônico online.

Agradecemos a **Gisele Cristina da Conceição** (Universidade do Porto) pelas valiosas sugestões e opiniões.


## Contato
Para comentários, críticas, perguntas e sugestões, contate [brunomaroneze@ufgd.edu.br](brunomaroneze@ufgd.edu.br)
