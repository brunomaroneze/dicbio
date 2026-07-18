# Protocolo de descrição dos termos:

## Informações gerais do termo:

- O termo que corresponde à entrada do verbete é indicado por "dbres:entry_XXXXX".

- O termo é colocado como "a ontolex:LexicalEntry".

- A propriedade "rdfs:seeAlso" pode ser usada para ligar ao verbete no Wiktionary.

- A propriedade "skos:exactMatch" pode ser usada para ligar ao verbete no Dbnary.

- "dcterms:created" indica a data de criação do verbete.

- "dcterms:creator" indica os autores do verbete.

- "lexinfo:partOfSpeech" indica a classe gramatical.

- "ontolex:canonicalForm" indica a forma (prefixada com "form_") canônica, e "ontolex:otherForm" indica as outras formas.

- "ontolex:sense" liga às acepções (no formato "entry_XXXX_sense1").

-------------------------------------------------
## Informações sobre as formas:

- Os recursos "dbres:form_XXXX" representam formas flexionadas e também formas gráficas encontradas no córpus.

- São indicados com a classe "a ontolex:Form" e precisam conter sempre a representação escrita "ontolex:writtenRep". Podem conter também "lexinfo:gender" (no caso dos adjetivos) e "lexinfo:number". Observação: no caso dos substantivos, "lexinfo:gender" fica atribuído à entrada, e não à forma.

- Se uma forma existe com acento e outra sem acento, a forma com acento recebe o nome "form_XXXX_accent".

--------------------------------------------------

## Informações sobre as acepções:

- As acepções são denominadas "dbres:entry_XXXXX_sense1" e entram na classe "a ontolex:LexicalSense"

- Precisam conter sempre a "skos:definition" (definição) e "lemonety:etymology" (lista das hipóteses etimológicas).

------------------------------------------------------------------------------------
## Informações sobre as hipóteses etimológicas:

- As hipóteses etimológicas são ligadas às acepções, e não às entradas.

- Uma acepção deve conter a propriedade "lemonety:etymology" seguida da lista das hipóteses etimológicas.

- O nome da hipótese etimológica é indicado por "dbres:etym_XXXXX_sense1"; se houver mais de uma, fica "dbres:etym_XXXXX_sense1_h1".

- A fonte da hipótese é indicada com "dcterms:source".

- Para indicar o processo geral, usa-se "dicbio:etymologicalProcess", e as opções são "dicbio:inherited" (herdadas), "dicbio:borrowed" (empréstimos), "dicbio:created" (neologismos morfológicos) e "dicbio:semanticDerivation" (neologismos semânticos). Novas possibilidades poderão ser criadas.

- A explicação discursiva da hipótese entra em "dicbio:etymologicalArgumentation".

- O nível de confiança da hipótese entra em "dicbio:confidenceLevel" e pode ser "dicbio:impossible", "dicbio:improbable", "dicbio:plausible", "dicbio:probable" e "dicbio:certain".

- No caso de palavras criadas, usa-se "dicbio:hasWordFormationRelation" para introduzir a explicação morfológica; esta é denominada "dbres:XXXX_derivation", se for um caso de derivação.

- No caso das palavras criadas por derivação, a derivação morfológica "dbres:XXXX_derivation" é indicada com "a morph:WordFormationRelation" e as propriedades "vartans:source" e "vartrans:target" indicam as relações entre primitivo e derivado, respectivamente. A propriedade "vartrans:category" indica se é derivação sufixal ("dicbio:Suffixation"), prefixal ("dicbio:Prefixation"), composição ("dicbio:Compounding") ou outra.

- No caso das palavras emprestadas ou herdadas, usa-se "dicbio:semanticEtymon" para relacionar a hipótese ao étimo.

- O étimo é denominado "dbres:etymon_XXXX" e é indicado como "a dicbio:SemanticEtymon".

- Ao étimo convém apresentar os elementos "dcterms:language" (a língua do étimo), "ontolex:writtenRep" (a forma escrita) e "skos:definition" (a definição do étimo). A propriedade "skos:exactMatch" pode ser usada para relacionar o étimo latino ao seu URI no projeto LiLa.

- A língua do étimo é apresentada com o prefixo "glotto:" e o código da língua no projeto Glottolog. O código da língua latina é "glotto:lati1261".

- Um étimo pode ter outro étimo, formando cadeias etimológicas.

--------------------------------------------------
## Informações sobre as atestações:
# REVER
- A informação sobre a atestação será preferencialmente ligada a uma acepção, e não a uma entrada. É um recurso de nome "dbres:attestation_TERMO_FONTE" e é atribuída à classe "a dicbio:Attestation".

- A propriedade "dicbio:attestationDate" indica o ano da atestação e a propriedade "dcterms:source" indica a fonte da datação.

- (Ainda a ser considerado: vamos indicar atestações de étimos?) A atestação pode ser da acepção do verbete principal, ou da acepção do étimo.

- A fonte pode ser primária (ou seja, uma obra do próprio córpus do projeto) ou secundária (em geral, outro dicionário).

- Será feito um algoritmo que extrai automaticamente do córpus as informações sobre as atestações das fontes primárias.

---------------------------------------------------
## Informações sobre o nível conceitual:

- Uma acepção pode ser vinculada ao URI de um conceito por meio de "ontolex:reference".

- Pode-se ligar diretamente ao URI do conceito (extraído preferencialmente da ontologia Uberon ou outra ontologia de anatomia), mas, para fins de estudo histórico posterior, é adequado criar um recurso para o conceito.

- O recurso para o conceito terá a forma "dbres:concept_XXXX" e precisa conter, pelo menos, "skos:definition" e "skos:exactMatch" (este último ligado ao URI do conceito).

- Os casos de substituição de termo (como "aurícula" para "átrio") e de mais de uma denominação para o mesmo conceito (como "uropígio" e "sobrecu") serão modelados usando a atribuição dos sentidos ao mesmo conceito.


---------------------------------------------------
## Informações sobre autores e fontes:
- Os autores são indicados com "dbauth:nome_da_pessoa" e contêm "foaf:name" com  nome por escrito, "dcterms:identifier" com o Orcid e "rdfs:seeAlso" com o link do Lattes.

- As fontes são indicadas com "dbsrc:source_nome_da_fonte". Se for livro, é atribuído à classe "a bibo:Book" e contém "dcterms:title", "dcterms:creator", "dcterms:issued", "owl:sameAs" (com o URI do Wikidata) e, opcionalmente, "foaf:page" com o link.

- Os livros do córpus são indicados como se fossem fontes, exceto que se usa "dbsrc:work_nome_da_fonte" em vez de "source".

-------------------------------------------------
## Regras de identificação de URIs:

- entry_XXXX → entrada lexical (ontolex:LexicalEntry)

- form_XXXX → forma (ontolex:Form)

- etym_XXXX_sense1 → hipótese etimológica (lemonety:Etymology)

- etymon_XXXX → étimo (lemonety:Etymon)

- attestation_XXXX → atestação (dicbio:Attestation)

- XXXX_derivation → regra de derivação (morph:WordFormationRelation)

----------------------------------------------------
## Recomendações gerais:

- Todas as afirmações históricas devem vir acompanhadas da fonte "dcterms:source".

- Se alguma informação das previstas no protocolo não for conhecida, deixar em branco e avisar isso nos "issues" do GitHub.
-----------------------------------------------------

## O que falta:
- Falta um protocolo para associar os sentidos aos URIs dos conceitos (quando eles representam conceitos)
- Da mesma forma, precisamos associar nomes científicos de animais e plantas aos respectivos URIs
- Podemos pensar também em associar cada verbete a outras descrições em artigos científicos
- Falta escrever um script que identifica os elementos <term> do córpus e insere automaticamente as informações sobre as atestações
- As atestações ligadas ao córpus precisam ser relacionadas por meio do atributo @xml:id ou @ref no XML. Assim, cada verbete terá as suas atestações relacionadas. Além disso, cada forma encontrada no córpus tem uma acepção. Precisamos descobrir um jeito de relacionar forma, acepção e atestação.
