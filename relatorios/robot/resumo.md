# Testes da ontologia DicBio com o ROBOT

- Data: 2026-11-13 19:19
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

✗ Fora do perfil OWL 2 DL: 237 violações —

- **0** envolvem termos ou dados do DicBio (a examinar);
- 1 são conhecidas e aceitas por decisão de modelagem (ver abaixo);
- 0 se devem a vocabulários usados nos dados e não importados de propósito (esperadas; a existência desses termos é conferida na etapa f);
- 236 vêm só das ontologias importadas.

Violações aceitas:

- **xsd:gYear em dicbio:attestationDate** (1): xsd:gYear não faz parte do mapa de tipos de dados do OWL 2, mas é o tipo semanticamente correto para um ano de atestação e o esperado em dados abertos. O HermiT do `reason` ignora o tipo; a validade do valor é conferida pelo SHACL (`sh:datatype xsd:gYear`).

Violações só das importações, por tipo (as 8 mais frequentes):

- 155 × Use of undeclared annotation property
- 26 × Use of undeclared class
- 23 × Cannot pun between properties
- 11 × Use of undeclared object property
- 11 × Use of reserved vocabulary for class IRI
- 9 × Use of undeclared data property
- 1 × Use of reserved vocabulary for object property IRI

Lista completa: `perfil_owl2dl.txt`; só as do DicBio: `perfil_owl2dl_dicbio.txt`.

### b. Raciocínio com HermiT (`reason`)

✓ Consistente; nenhuma classe insatisfazível.

### d. Relatório de qualidade (`report`)

✓ Nenhum problema encontrado.

### e. Métricas (`measure`)

| métrica | valor |
|---|---|
| axiom_count | 222 |
| logical_axiom_count | 60 |
| class_count | 12 |
| individual_count | 18 |
| axiom_count_incl | 3765 |
| class_count_incl | 120 |
| expressivity | RRESTRH(D) |

Todas as métricas: `metricas.tsv` (sufixo `_incl` = com importações).

### f. Termos de vocabulários usados nos dados e não importados

Nenhum termo desses vocabulários nos arquivos testados.

## Cenário: dados

Arquivos: `data/dicbio-ontology.ttl`, `data/sources.ttl`, `data/authors.ttl`, `data/entries/adiposo.ttl`

### a. Perfil OWL 2 DL (`validate-profile`)

✗ Fora do perfil OWL 2 DL: 302 violações —

- **0** envolvem termos ou dados do DicBio (a examinar);
- 5 são conhecidas e aceitas por decisão de modelagem (ver abaixo);
- 61 se devem a vocabulários usados nos dados e não importados de propósito (esperadas; a existência desses termos é conferida na etapa f);
- 236 vêm só das ontologias importadas.

Violações aceitas:

- **xsd:gYear em dicbio:attestationDate** (5): xsd:gYear não faz parte do mapa de tipos de dados do OWL 2, mas é o tipo semanticamente correto para um ano de atestação e o esperado em dados abertos. O HermiT do `reason` ignora o tipo; a validade do valor é conferida pelo SHACL (`sh:datatype xsd:gYear`).

Esperadas, por vocabulário: `bibo:` 23, `foaf:` 25, `lexinfo:` 13.

Violações só das importações, por tipo (as 8 mais frequentes):

- 155 × Use of undeclared annotation property
- 26 × Use of undeclared class
- 23 × Cannot pun between properties
- 11 × Use of undeclared object property
- 11 × Use of reserved vocabulary for class IRI
- 9 × Use of undeclared data property
- 1 × Use of reserved vocabulary for object property IRI

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
| axiom_count | 463 |
| logical_axiom_count | 163 |
| class_count | 18 |
| individual_count | 82 |
| axiom_count_incl | 4006 |
| class_count_incl | 125 |
| expressivity | RRESTRHO(D) |

Todas as métricas: `metricas.tsv` (sufixo `_incl` = com importações).

### f. Termos de vocabulários usados nos dados e não importados

`lexinfo:` 9 termo(s) usado(s), 0 inexistente(s); `bibo:` 7 termo(s) usado(s), 0 inexistente(s); `foaf:` 5 termo(s) usado(s), 0 inexistente(s).

✓ Todos os termos usados existem nos vocabulários.

