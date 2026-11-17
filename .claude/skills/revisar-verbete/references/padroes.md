# Padrões de modelagem para a revisão dos verbetes

Guia de decisão e modelos em Turtle. As regras valem nesta ordem de
autoridade: `data/dicbio-shacl-shapes.ttl` (o que o validador exige) →
`data/protocolo.md` (convenções do projeto) → este guia (como decidir os
casos de julgamento). O verbete `data/entries/adiposo.ttl` foi revisado à
mão e serve de modelo completo.

## Sumário
1. Processo etimológico
2. Grau de certeza
3. Fonte da hipótese
4. Definição e classe do étimo
5. Mais de uma hipótese
6. Palavra criada (derivação, composição)
7. Cadeia etimológica (étimo do étimo)
8. Segunda atestação e mudança de sentido
9. Fontes novas em sources.ttl
10. Os casos especiais do modelo antigo
11. Comentários e marcas

---

## 1. Processo etimológico (`dicbio:etymologicalProcess`)

Leia a argumentação e decida o que ela afirma sobre a ORIGEM da acepção
portuguesa:

| A argumentação diz… | Processo |
|---|---|
| o étimo é latim/grego (clássico ou científico), "latinismo", "palavra erudita", "empréstimo", "do francês" | `dicbio:borrowed` |
| evolução popular desde o latim vulgar, mudanças fonéticas regulares ("herdada", "forma popular") | `dicbio:inherited` |
| formada em português: sufixo, prefixo, parassíntese, composição, "formação vernácula", particípio de verbo português | `dicbio:created` |
| sentido novo de uma palavra portuguesa que já existia (metáfora, especialização), étimo = outra acepção portuguesa | `dicbio:semanticDerivation` |
| "origem obscura", "não se sabe", sem análise ainda | `dicbio:pendingResearch` |
| entrada de étimo, palavra primitiva fora da proposta do dicionário | `dicbio:outOfScope` |

Quase todos os termos científicos do córpus são empréstimos eruditos do
latim (`borrowed`), mesmo quando o latim é antigo: o que conta é que a
palavra entrou por via culta, não por evolução popular. Use `inherited` só
quando o texto falar de evolução popular.

O SHACL confere a coerência: `borrowed` e `inherited` exigem
`dicbio:semanticEtymon`; `borrowed` exige étimo em OUTRA língua;
`semanticDerivation` exige étimo na MESMA língua; `created` exige
`dicbio:hasWordFormationRelation`. `pendingResearch` e `outOfScope` pedem
`dicbio:confidenceLevel dicbio:notApplicable` e dispensam fonte.

## 2. Grau de certeza (`dicbio:confidenceLevel`)

Pelo modo como a argumentação afirma a hipótese:

| Marcas no texto | Grau |
|---|---|
| "certamente", "sem dúvida", "evidentemente", étimo direto e bem documentado nos dicionários | `dicbio:certain` |
| afirmação direta ("O étimo é o latim X") com apoio de dicionário ou atestação | `dicbio:probable` |
| "pode ser", "talvez", "possivelmente", "parece", "é razoável supor" | `dicbio:plausible` |
| o texto apresenta a hipótese para rejeitá-la ou a considera fraca | `dicbio:improbable` |
| o texto a refuta | `dicbio:impossible` |

Na dúvida entre dois graus, escolha o mais cauteloso e explique no
comentário `# REVISAR (skill)`.

## 3. Fonte da hipótese (`dcterms:source` na hipótese)

A fonte é QUEM propõe a hipótese, não onde o étimo está atestado:

- A argumentação atribui a hipótese a um dicionário ("segundo o Houaiss",
  "o Houaiss afirma") → a fonte desse dicionário (`dbsrc:source_houaiss`).
- A hipótese é do próprio projeto (argumentação própria, "nossa pesquisa",
  contra o Houaiss etc.) → `dbsrc:dicbio_project`, e acrescente
  `dcterms:creator` com os autores do verbete (como em
  `etym_adiposo_sense1_h2`).
- O dicionário de latim citado só para ATESTAR o étimo ("atestado desde a
  Antiguidade segundo o OLD") não é fonte da hipótese: isso é atestação do
  étimo (já modelada em `dicbio:Attestation`).

Exemplo (caule): "O étimo é o latim *caulis*, atestado desde a Antiguidade
(segundo o OLD)… palavra erudita, adaptada como latinismo" → a hipótese é
do projeto (`dbsrc:dicbio_project`); o OLD é a fonte da atestação.

## 4. Definição e classe do étimo

- `skos:definition` da acepção do étimo: use a glosa que a própria
  argumentação dá ("que significa 'tronco, talo das plantas, couve'"), em
  português, com `@pt`. Escolha a acepção que se relaciona com o sentido
  português. Se a argumentação não traz glosa, traduza a glosa pertinente do
  L&S (saída do `contexto`) e diga no `# REVISAR (skill)` de onde veio.
- `lexinfo:partOfSpeech`: confirme pelo cabeçalho do L&S (`is, m.` →
  substantivo masculino; `a, um` → adjetivo; verbo com `āre`, `ēre`…).
  Particípios usados como adjetivo (*connivens*, *elongatus*) ficam como
  `lexinfo:adjective`, com a explicação na nota. Se confirmar, apague o
  `# REVISAR: classe copiada da entrada principal`; se não, corrija.
- Gênero do substantivo latino/grego: `lexinfo:gender` na ENTRADA do étimo
  (masculine, feminine ou neuter), conforme o L&S.
- Criadores copiados da entrada principal: é a convenção (quem redige o
  verbete cria a entrada do étimo). Mantenha e apague o `# REVISAR`.

## 5. Mais de uma hipótese

Quando a argumentação defende hipóteses diferentes (ex.: o Houaiss propõe
derivação vernácula e o projeto propõe latim científico), separe-as como em
adiposo: `etym_X_sense1_h1`, `etym_X_sense1_h2`, cada uma com seu processo,
fonte, grau e o trecho da argumentação que lhe cabe. Renomear exige trocar a
referência em `lemonety:etymology` da acepção. Só separe quando o texto
realmente apresenta duas origens; uma hipótese com ressalvas continua uma.

## 6. Palavra criada (`dicbio:created`)

```turtle
dbres:etym_enovelado_sense1 a lemonety:Etymology ;
    dcterms:source dbsrc:source_houaiss ;
    dicbio:etymologicalProcess dicbio:created ;
    dicbio:hasWordFormationRelation dbres:enovelado_derivation ;
    dicbio:etymologicalArgumentation "…"@pt ;
    dicbio:confidenceLevel dicbio:probable .

dbres:enovelado_derivation a morph:WordFormationRelation ;
    vartrans:source dbres:entry_enovelar ;      # primitivo
    vartrans:target dbres:entry_enovelado ;     # derivado
    vartrans:category dicbio:Suffixation .      # Prefixation, Compounding…

dbres:entry_enovelar a ontolex:LexicalEntry ;   # o primitivo, se não existir
    dcterms:language glotto:port1283 ;
    dcterms:created "AAAA-MM-DD"^^xsd:date ;
    dcterms:creator dbauth:… ;
    lexinfo:partOfSpeech lexinfo:verb ;
    ontolex:canonicalForm dbres:form_enovelar ;
    ontolex:sense dbres:entry_enovelar_sense1 .

dbres:form_enovelar a ontolex:Form ;
    ontolex:writtenRep "enovelar"@pt .

dbres:entry_enovelar_sense1 a ontolex:LexicalSense ;
    skos:definition "…"@pt ;
    lemonety:etymology dbres:etym_enovelar_sense1 .

dbres:etym_enovelar_sense1 a lemonety:Etymology ;
    dicbio:etymologicalProcess dicbio:outOfScope ;
    dicbio:confidenceLevel dicbio:notApplicable .
```

O primitivo é acepção portuguesa e por isso precisa de hipótese; como fica
fora da proposta, usa `outOfScope` (como `entry_adipe` em adiposo). Antes
de criar `entry_<primitivo>`, rode `nome-livre`: se o primitivo já é verbete
do dicionário, aponte para a entrada existente em vez de criar outra.
Parassíntese (en- + novelo + -ado): use a categoria mais próxima e explique
no comentário; a ontologia aceita categorias novas, mas o SHACL avisa.

## 7. Cadeia etimológica (étimo do étimo)

Quando a argumentação ou a nota informam o étimo grego (ou outro) do étimo
latino, com dados suficientes (forma, sentido, fonte e, de preferência, data):

```turtle
dbres:entry_botanica_lat_sense1 a ontolex:LexicalSense ;
    skos:definition "Ciência dos vegetais."@pt ;
    dicbio:hasAttestation dbres:attestation_botanica_lat_sense1_… ;
    lemonety:etymology dbres:etym_botanica_lat .

dbres:etym_botanica_lat a lemonety:Etymology ;          # sem _sense1 (cadeia)
    dcterms:source dbsrc:source_LSJ ;
    dicbio:etymologicalProcess dicbio:borrowed ;
    dicbio:semanticEtymon dbres:entry_botanikos_sense1 ;
    dicbio:etymologicalArgumentation "…"@pt ;
    dicbio:confidenceLevel dicbio:probable .

dbres:entry_botanikos a ontolex:LexicalEntry ;          # nome transliterado, ASCII
    dcterms:created "AAAA-MM-DD"^^xsd:date ;
    dcterms:creator dbauth:… ;
    dcterms:language glotto:gree1276 ;
    lexinfo:partOfSpeech lexinfo:adjective ;
    ontolex:canonicalForm dbres:form_botanikos ;
    ontolex:sense dbres:entry_botanikos_sense1 .

dbres:form_botanikos a ontolex:Form ;
    ontolex:writtenRep "βοτανικός"@grc .

dbres:entry_botanikos_sense1 a ontolex:LexicalSense ;
    skos:definition "Relativo às ervas."@pt ;
    dicbio:hasAttestation dbres:attestation_botanikos_sense1_lsj .

dbres:attestation_botanikos_sense1_lsj a dicbio:Attestation ;
    dcterms:source dbsrc:source_LSJ ;
    dicbio:attestationDate "0100"^^xsd:gYear ;
    skos:note "Plutarco, Quaestiones convivales (c. 100 d.C.)."@pt .
```

Se faltar dado (a nota só diz "é preciso descrever o étimo grego"), não
invente: deixe o `# REVISAR (datas)` existente.

## 8. Segunda atestação e mudança de sentido

Notas como "a atestação antiga é X, mas o sentido científico é de 1788"
pedem duas atestações na acepção do étimo, cada uma com sua fonte e data:

- a da Antiguidade, com a fonte do dicionário (Gaffiot/OLD) e o ano do
  autor citado, e `skos:note` com o autor/obra;
- a do latim científico, com a obra primária (Vandelli, Lineu…) e o ano dela.

Isso resolve os `# REVISAR (datas): o ano … não é o da fonte …`: a data
antiga passa para a nova atestação com a fonte certa, e a atestação com
Vandelli fica com 1788. A nota de cada atestação vira `skos:note` (texto
curto e informativo, para o leitor) e o comentário sai.

Quando a nota diz que o SENTIDO antigo é diferente do científico, e o texto
dá os dois sentidos, a regra do projeto é uma acepção por sentido: crie
`entry_X_sense2` para o sentido científico (com a atestação científica) e
aponte o `dicbio:semanticEtymon` da hipótese portuguesa para a acepção que é
de fato o étimo. Se o texto não dá os dois sentidos, só marque.

## 9. Fontes novas em sources.ttl

Para trocar uma fonte em texto livre por um IRI:

1. Verifique se a obra já existe em sources.ttl (lista do `contexto`).
2. Se não, crie-a no fim de sources.ttl, num bloco com comentário de título:

```turtle
# Lineu, Systema Naturae (1748)
dbsrc:source_linnaeus_systema_naturae_1748 a bibo:Book ;
    dcterms:title "Systema Naturae" ;
    dcterms:creator <https://www.wikidata.org/entity/Q1043> ;   # Lineu
    dcterms:issued "1748"^^xsd:gYear ;
    owl:sameAs <https://www.wikidata.org/entity/Q…> ;           # se a edição/obra tiver item
    foaf:page <https://www.google.com.br/books/edition/…> .
```

- Nome: `source_<autor>_<obra curta>_<ano>`, minúsculas, ASCII, `_`.
  Confira com `nome-livre`.
- Wikidata: procure na web o autor (e a obra, se houver item). Use a forma
  `https://www.wikidata.org/entity/Q…`, que é a usada no projeto. Se não
  achar o autor com segurança, deixe `# REVISAR (skill): autor não
  localizado no Wikidata` e NÃO invente um Q-id: um identificador errado é
  pior que um ausente. Sem autor nem editor o SHACL acusa erro; aceite o
  erro e registre no resumo.
- `foaf:page`: o link do Google Livros que estava no texto livre.
- Dicionários: `a bibo:Book, bibo:ReferenceSource`.
- Na atestação, troque o literal pelo IRI e renomeie a atestação para
  `attestation_<lema>_sense<N>_<slug da fonte>` (atualize o
  `dicbio:hasAttestation`). Rode `python scripts/validate_graph.py
  data/sources.ttl` depois de mexer em sources.ttl.

Fontes em texto livre que são só um nome de dicionário ("Dicionário
Houaiss", "OLD/LSJ", "Gaffiot/OLD") → use as fontes existentes; com duas
obras, crie duas atestações.

## 10. Os casos especiais do modelo antigo

São acepções falsas, criadas porque o modelo antigo exigia um étimo mesmo
quando não havia. Têm `dcterms:language` em texto livre:

| língua no texto | o que fazer |
|---|---|
| "formação vernácula" (`entry_en-_+_novelo_+_-ado_sense1` etc.) | apague a acepção falsa; a hipótese vira `created` com `hasWordFormationRelation` (seção 6), primitivo tirado do `writtenRep` antigo ("en- + novelo + -ado"); a fonte antiga ("nossa pesquisa") vira `dbsrc:dicbio_project` |
| "português" (`entry_bulbo_(1)_sense1` etc.) | é derivação semântica ou composição dentro do português: leia a argumentação e use `semanticDerivation` (étimo = acepção portuguesa existente ou nova) ou `created` |
| "obscuro" | `pendingResearch`, `notApplicable`; a argumentação fica; apague a acepção falsa |
| "não se aplica" (jardim botânico) | leia a argumentação: decalque/tradução de expressão estrangeira → `borrowed` com o étimo na outra língua (ex.: latim *hortus botanicus*), grau conforme o texto |
| "latim medieval" | entrada latina (`glotto:lati1261`), com `skos:note` ou comentário dizendo que é latim medieval |

IRIs com `+`, `(`, `)` ou espaços não devem sobreviver: os nomes novos seguem
as regras de nome do protocolo.

## 11. Comentários e marcas

- Toda decisão de julgamento recebe um comentário curto na linha:
  `# REVISAR (skill): <por que esta escolha>`. É o que a pessoa vai conferir
  no diff; um comentário vago ("verificar") não ajuda, diga o motivo
  ("'O étimo é o latim X' afirmado sem ressalva → probable").
- Ao resolver uma pendência marcada (`# REVISAR: falta skos:definition`,
  `# REVISAR (datas): é preciso descrever o étimo grego`…), apague o
  comentário antigo; o `# REVISAR (skill)` novo o substitui.
- `# NOTA (datas)` que for só informação: converta em `skos:note` da
  atestação, quando for útil ao leitor, ou mantenha como comentário.
- Comentário nunca vai dentro de string, e um `#` antes do `;` ou do `.`
  comenta o resto da linha: ponha o comentário DEPOIS do `;`/`.` ou em
  linha própria.
