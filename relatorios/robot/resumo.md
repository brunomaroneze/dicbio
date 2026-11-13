# Testes da ontologia DicBio com o ROBOT

- Data: 2026-11-13 18:51
- ROBOT version 1.9.11; reasoner HermiT (embutido no ROBOT)
- Importações resolvidas por cópias locais (`ferramentas/robot/imports/`)

## Resultado geral

| cenário | perfil OWL 2 DL | consistência | relatório (sem ERROR) | termos lexinfo/bibo/foaf |
|---|---|---|---|---|
| ontologia | ✗ | ✓ | ✓ | ✓ |
| dados | ✗ | ✓ | ✓ | ✓ |

## Cenário: ontologia

Arquivos: `data/dicbio-ontology.ttl`

### a. Perfil OWL 2 DL (`validate-profile`)

✗ Fora do perfil OWL 2 DL: 961 violações —

- **8** envolvem termos ou dados do DicBio (a examinar);
- 0 se devem a vocabulários usados nos dados e não importados de propósito (esperadas; a existência desses termos é conferida na etapa f);
- 953 vêm só das ontologias importadas.

Violações que envolvem o DicBio (exceto as esperadas), por tipo:

- 3 × Use of undeclared annotation property
- 2 × Use of undeclared datatype
- 1 × Use of undeclared data property
- 1 × Cannot pun between properties
- 1 × Use of defined datatype in datatype restriction

Termos usados pelo DicBio e não declarados em nenhuma ontologia importada (o reasoner os trata como anotações ou os ignora):

- propriedade de anotação: `dc:date`, `dcterms:creator`, `dcterms:issued`
- propriedade de dado: `dcterms:modified`
- tipo de dado: `xsd:date`, `xsd:gYear`

Violações só das importações, por tipo (as 8 mais frequentes):

- 382 × Use of undeclared annotation property
- 171 × Cannot pun between properties
- 142 × Use of undeclared data property
- 99 × Use of defined datatype in datatype restriction
- 99 × Use of undeclared datatype
- 35 × Use of undeclared class
- 12 × Use of reserved vocabulary for class IRI
- 11 × Use of undeclared object property

Lista completa: `perfil_owl2dl.txt`; só as do DicBio: `perfil_owl2dl_dicbio.txt`.

### b. Raciocínio com HermiT (`reason`)

✓ Consistente; nenhuma classe insatisfazível.

### d. Relatório de qualidade (`report`)

✓ Nenhum problema encontrado.

### e. Métricas (`measure`)

| métrica | valor |
|---|---|
| axiom_count | 854 |
| logical_axiom_count | 203 |
| class_count | 36 |
| individual_count | 118 |
| axiom_count_incl | 4397 |
| class_count_incl | 143 |
| expressivity | RRESTRH(D) |

Todas as métricas: `metricas.tsv` (sufixo `_incl` = com importações).

### f. Termos de vocabulários usados nos dados e não importados

Nenhum termo desses vocabulários nos arquivos testados.

## Cenário: dados

Arquivos: `data/dicbio-ontology.ttl`, `data/sources.ttl`, `data/authors.ttl`, `data/entries/adiposo.ttl`

### a. Perfil OWL 2 DL (`validate-profile`)

✗ Fora do perfil OWL 2 DL: 1139 violações —

- **126** envolvem termos ou dados do DicBio (a examinar);
- 61 se devem a vocabulários usados nos dados e não importados de propósito (esperadas; a existência desses termos é conferida na etapa f);
- 952 vêm só das ontologias importadas.

Esperadas, por vocabulário: `bibo:` 23, `foaf:` 25, `lexinfo:` 13.

Violações que envolvem o DicBio (exceto as esperadas), por tipo:

- 73 × Use of undeclared annotation property
- 33 × Cannot pun between properties
- 8 × Use of undeclared datatype
- 7 × Use of defined datatype in datatype restriction
- 5 × Use of undeclared data property

Termos usados pelo DicBio e não declarados em nenhuma ontologia importada (o reasoner os trata como anotações ou os ignora):

- propriedade de anotação: `dc:date`, `dcterms:accrualPeriodicity`, `dcterms:creator`, `dcterms:description`, `dcterms:hasFormat`, `dcterms:identifier`, `dcterms:isPartOf`, `dcterms:issued`, `dcterms:language`, `dcterms:publisher`, `dcterms:source`, `dcterms:title`
- propriedade de dado: `dcterms:created`, `dcterms:modified`
- tipo de dado: `xsd:date`, `xsd:gYear`

Violações só das importações, por tipo (as 8 mais frequentes):

- 381 × Use of undeclared annotation property
- 171 × Cannot pun between properties
- 142 × Use of undeclared data property
- 99 × Use of defined datatype in datatype restriction
- 99 × Use of undeclared datatype
- 35 × Use of undeclared class
- 12 × Use of reserved vocabulary for class IRI
- 11 × Use of undeclared object property

Lista completa: `perfil_owl2dl.txt`; só as do DicBio: `perfil_owl2dl_dicbio.txt`.

### b. Raciocínio com HermiT (`reason`)

✓ Consistente; nenhuma classe insatisfazível.

### c. Tipos inferidos pelo HermiT para os recursos dos dados

10 tipos novos em 9 recursos. Confira se cada inferência faz sentido — um tipo inesperado costuma indicar propriedade usada com o sujeito ou o objeto errado.

| classe inferida | recursos |
|---|---|
| `semiotics:Expression` | 3 |
| `semiotics:Meaning` | 3 |
| `prov:Entity` | 2 |
| `vartrans:LexicalRelation` | 1 |
| `vartrans:LexicoSemanticRelation` | 1 |

Lista por recurso: `tipos_inferidos.tsv`.

### d. Relatório de qualidade (`report`)

✓ Nenhum problema encontrado.

### e. Métricas (`measure`)

| métrica | valor |
|---|---|
| axiom_count | 1095 |
| logical_axiom_count | 310 |
| class_count | 42 |
| individual_count | 182 |
| axiom_count_incl | 4638 |
| class_count_incl | 148 |
| expressivity | RRESTRHO(D) |

Todas as métricas: `metricas.tsv` (sufixo `_incl` = com importações).

### f. Termos de vocabulários usados nos dados e não importados

`lexinfo:` 9 termo(s) usado(s), 0 inexistente(s); `bibo:` 7 termo(s) usado(s), 0 inexistente(s); `foaf:` 5 termo(s) usado(s), 0 inexistente(s).

✓ Todos os termos usados existem nos vocabulários.

