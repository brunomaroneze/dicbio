# Ontologia Dicbio 1.0 / DicBio Ontology 1.0

**Ontologia do Dicionário Histórico de Termos da Biologia**

> **Status:** Rascunho — versão 1.0 em preparação  
> **Versão:** 1.0  
> **URI da ontologia:** https://dicbio.fflch.usp.br/ontology/  
> **URI da versão:** https://dicbio.fflch.usp.br/ontology/1.0/  
> **Idioma da documentação:** português / inglês

---

## 1. Introdução

### 1.1. Apresentação

O **Dicionário Histórico de Termos da Biologia** (DicBio) é um dicionário eletrônico dedicado à descrição histórico-etimológica dos termos da Biologia em língua portuguesa. O projeto reúne dados lexicais, linguísticos, etimológicos, histórico-documentais e semântico-conceituais provenientes de diferentes fontes, incluindo dicionários históricos e obras que integram seu corpus documental.

O projeto é desenvolvido por estudantes e pesquisadores da Universidade Federal da Grande Dourados (UFGD) e da Universidade Federal de Mato Grosso do Sul (UFMS).

Esta ontologia tem por finalidade fornecer um modelo semântico formal para a representação dos dados do dicionário em RDF, favorecendo sua publicação como Linked Open Data e sua interoperabilidade com outros conjuntos de dados e vocabulários da Web Semântica.

### 1.2. Motivação

De acordo com os princípios do Linked Open Data, os dados devem ser disponibilizados na Web de modo a explicitar suas relações com outros dados. A própria natureza relacional dos dados lexicais convida à sua representação como dados interligados (*Linked Data*), possibilitando a recuperação automatizada da rede de relações que se estabelece entre uma entrada lexical e suas formas, acepções, relações etimológicas, fontes, atestações e conceitos. Essa estrutura pode ser explorada tanto por pesquisadores quanto por aplicações computacionais, inclusive sistemas baseados em inteligência artificial. Para isso, faz-se necessário um modelo semântico que sistematize as diversas relações possíveis entre esses diferentes tipos de recursos. A Ontologia DicBio foi desenvolvida com essa finalidade.

### 1.3. Organização desta documentação

Esta documentação apresenta a estrutura e os princípios fundamentais da Ontologia DicBio 1.0. Seu objetivo é descrever as classes, propriedades, vocabulários controlados, relações com ontologias externas e principais decisões de modelagem que constituem a ontologia.

A documentação da ontologia deve ser distinguida do **DicBio — Guia de Modelagem dos Dados**, que apresenta instruções mais detalhadas para a criação e manutenção das instâncias dos dados. Enquanto esta documentação descreve o modelo semântico propriamente dito, o Guia de Modelagem orienta sua aplicação na construção dos dados do dicionário. A validação automática desses dados será realizada por meio de formas SHACL, descritas em documentação própria.

---

## 2. Objetivo e escopo

### 2.1. Objetivo

Esta ontologia visa representar as informações lexicográficas, linguístico-semânticas, histórico-documentais e etimológicas relacionadas aos termos descritos no Dicionário Histórico de Termos da Biologia, bem como as relações desses termos com suas fontes documentais e com as ocorrências identificadas no corpus do projeto.

### 2.2. Escopo

A Ontologia DicBio contempla a representação de:

- entradas lexicais e suas formas;
- acepções e definições;
- informações gramaticais e linguísticas associadas às entradas e formas;
- hipóteses etimológicas e seus argumentos;
- étimos entendidos como acepções lexicalmente identificáveis;
- processos etimológicos e tipos de formação de palavras;
- atestações históricas das formas e acepções;
- conceitos associados às acepções;
- fontes bibliográficas e documentais;
- autores e colaboradores relacionados aos recursos do dicionário;
- relações de proveniência e outras relações relevantes para a documentação dos dados;
- relações entre os recursos lexicais e as ocorrências identificadas no corpus documental do DicBio.

A ontologia reutiliza, sempre que possível, classes e propriedades de ontologias e vocabulários consolidados, especialmente OntoLex-Lemon, LemonEty, SKOS, Dublin Core Terms, PROV-O, ITS-RDF e NIF.

### 2.3. Fora do escopo

A Ontologia DicBio não pretende representar exaustivamente:

- o conhecimento biológico propriamente dito;
- uma taxonomia completa dos organismos;
- uma ontologia geral da língua portuguesa;
- uma teoria linguística ou etimológica completa;
- as regras editoriais e operacionais utilizadas pelos pesquisadores para produzir os verbetes;
- a estrutura interna das obras do corpus para além das informações necessárias à representação das fontes, atestações e relações documentais relevantes para o dicionário.

Essas informações podem ser representadas por outros modelos ou vocabulários e relacionadas aos dados do DicBio quando pertinente.

### 2.4. Público-alvo

O público-alvo imediato desta ontologia são os pesquisadores e estudantes que atuam na elaboração do Dicionário Histórico de Termos da Biologia.
Além disso, espera-se que esta ontologia seja útil particularmente para pesquisadores das áreas de Terminologia e Linguística, em especial a Linguística Histórica. Por fim, os dados descritos por esta ontologia poderão ser úteis a desenvolvedores e pesquisadores de Humanidades Digitais que pretendem consultar os dados do dicionário via SPARQL.

---

## 3. Status e versão

### 3.1. Status

A versão 1.0 da Ontologia DicBio constitui a primeira versão estável da ontologia. Foi submetida a testes de consistência lógica com o reasoner HermiT, executado por meio do Protégé Desktop. A versão foi revisada quanto à definição das classes, propriedades, vocabulários controlados, domínios, *ranges*, reutilização de ontologias externas e documentação.

### 3.2. Identificação da versão

| Elemento | Valor |
|---|---|
| Versão | 1.0 |
| URI da ontologia | `https://dicbio.fflch.usp.br/ontology/` |
| URI da versão | `https://dicbio.fflch.usp.br/ontology/1.0/` |
| Data de emissão | <!-- preencher --> |
| Data da última modificação | <!-- preencher --> |

### 3.3. Política de versionamento

A Ontologia DicBio adota versionamento semântico em três níveis. Alterações que preservem a compatibilidade semântica e acrescentem classes, propriedades ou conceitos sem modificar o significado dos elementos existentes poderão resultar em versões secundárias (1.1, 1.2 etc.). Alterações que corrijam erros sem modificar a estrutura conceitual poderão resultar em versões de correção. Alterações incompatíveis com a versão anterior, especialmente aquelas que modifiquem o significado ou removam classes ou propriedades existentes, resultarão em uma nova versão principal (2.0, 3.0 etc.).

Cada versão estável da ontologia possui uma URI própria, de modo a preservar sua identificação e permitir a referência a versões históricas.

---

## 4. Namespace e URIs

### 4.1. Namespace principal

```text
https://dicbio.fflch.usp.br/ontology/
```

Prefixo:

```turtle
@prefix dicbio: <https://dicbio.fflch.usp.br/ontology/> .
```

### 4.2. URI da versão 1.0

```text
https://dicbio.fflch.usp.br/ontology/1.0/
```

### 4.3. Política de URIs

Os URIs das classes e propriedades da Ontologia DicBio são construídos a partir do namespace da ontologia:

`https://dicbio.fflch.usp.br/ontology/`

Os identificadores dos recursos são estáveis e não dependem da versão específica da ontologia. Assim, por exemplo, a classe `dicbio:Attestation` tem por URI:

`https://dicbio.fflch.usp.br/ontology/Attestation`

A versão específica da ontologia é identificada separadamente por meio de sua `owl:versionIRI`.

Os URIs das instâncias dos dados pertencem a namespaces distintos, como `dbres:`, `dbsrc:` e `dbauth:`. Essa separação permite distinguir claramente os termos do modelo ontológico dos recursos concretos descritos pelo dicionário.


### 4.4. Namespaces utilizados nos dados

O *namespace* `dicbio:` é empregado para as classes e propriedades gerais que foram criadas para descrever as informações do dicionário.
O *namespace* `dbres:` é empregado para as instâncias das entradas, formas, acepções, descrições etimológicas etc.
O *namespace* `dbsrc:` é empregado para as instâncias das fontes dos dados, sejam primárias (as próprias obras que integram o *corpus* e outras), sejam secundárias (em geral, os demais dicionários consultados).
O *namespace* `dbauth:` é empregado para os recursos que representam os colaboradores do dicionário (estudantes e pesquisadores que atuam ou atuaram no projeto).

| Prefixo | Namespace | Função |
|---|---|---|
| `dicbio:` | `https://dicbio.fflch.usp.br/ontology/` | Ontologia DicBio |
| `dbres:` | `https://dicbio.fflch.usp.br/recurso/` | Recursos do DicBio |
| `dbsrc:` | `https://dicbio.fflch.usp.br/fontes/` | Fontes e obras |
| `dbauth:` | `https://dicbio.fflch.usp.br/autores/` | Autores |

---

## 5. Licença

A Ontologia DicBio é disponibilizada sob a licença **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

A licença da ontologia não implica necessariamente a mesma licença para os dados, código-fonte, imagens, reproduções de obras ou demais recursos associados ao projeto. As condições de uso desses materiais são indicadas em sua documentação específica.

---

## 6. Autores(as)

### 6.1. Autor(es/as) e colaboradores(as)

Bruno Oliveira Maroneze - concepção, desenvolvimento e manutenção da Ontologia DicBio.

### 6.2. Atribuição

Ao reutilizar ou citar a Ontologia DicBio, recomenda-se atribuir a autoria a **Bruno Oliveira Maroneze** e indicar o projeto **Dicionário Histórico de Termos da Biologia** (DicBio), juntamente com a versão da ontologia utilizada.

Recomenda-se a seguinte referência:

MARONEZE, Bruno Oliveira. DicBio Ontology 1.0. Dicionário Histórico de Termos da Biologia. 2026. Disponível em: https://dicbio.fflch.usp.br/ontology/1.0/. Acesso em: [data].

Para citações em trabalhos acadêmicos, recomenda-se também citar a publicação ou documentação científica do projeto, quando disponível.

---

## 7. Ontologias e vocabulários reutilizados

A Ontologia DicBio reutiliza vocabulários e ontologias existentes sempre que apropriado, evitando a criação de conceitos já disponíveis em modelos consolidados.

### 7.1. Ontologias e vocabulários

| Prefixo | Ontologia / vocabulário | Namespace | Função na Ontologia DicBio |
|---|---|---|---|
| `ontolex:` | OntoLex-Lemon | `http://www.w3.org/ns/lemon/ontolex#` | Representação lexical |
| `lemonety:` | LemonEty | `http://lari-datasets.ilc.cnr.it/lemonEty#` | Representação etimológica |
| `morph:` | OntoLex-Morph | `http://www.w3.org/ns/lemon/morph#` | Relações de formação de palavras |
| `skos:` | SKOS | `http://www.w3.org/2004/02/skos/core#` | Vocabulários e conceitos |
| `dcterms:` | Dublin Core Terms | `http://purl.org/dc/terms/` | Metadados |
| `prov:` | PROV-O | `http://www.w3.org/ns/prov#` | Proveniência |
| `nif:` | NIF | `http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#` | Integração com o *corpus* |
| `itsrdf:` | ITS | `http://www.w3.org/2005/11/its/rdf#` | Anotação de sentido das ocorrências |


### 7.2. Vocabulários utilizados na representação dos dados

Além das ontologias reutilizadas diretamente na definição da Ontologia DicBio, os dados do DicBio utilizam outros vocabulários externos para representar informações específicas. Esses vocabulários não constituem dependências da ontologia e, por isso, não são necessariamente incluídos em `owl:imports`.

| Prefixo | Ontologia / vocabulário | Namespace | Função nos dados do DicBio |
|---|---|---|---|
| `foaf:` | FOAF | `http://xmlns.com/foaf/0.1/` | Nomes e endereços web |
| `dcterms:` | Dublin Core Terms | `http://purl.org/dc/terms/` | Metadados avulsos das instâncias |
| `lexinfo:` | LexInfo | `http://www.lexinfo.net/ontology/3.0/lexinfo#` | Propriedades gramaticais |
| `bibo:` | The Bibliographic Ontology | `http://purl.org/ontology/bibo/` | Informações bibliográficas |
| `vartrans:` | Variation and Translation | `http://www.w3.org/ns/lemon/vartrans#` | Informações morfológicas |
| `glotto:` | Glottolog | `https://glottolog.org/resource/languoid/id/` | Idiomas das fontes ou dos termos |
| `skos:` | SKOS | `http://www.w3.org/2004/02/skos/core#` | Anotação/mapeamento avulsos |
| `owl:` | Web Ontology Language | `https://www.w3.org/TR/owl-ref/` | owl:sameAs para remissões |
| `rdfs:` | RDF Schema | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` | rdfs:seeAlso para remissões |


<!-- ### 7.3. Justificativa das reutilizações

Será que precisa deste item?

Explicar as principais decisões de reutilização -->

---

## 8. Princípios de modelagem

### 8.1. Reutilização de ontologias existentes

A Ontologia DicBio procura reutilizar ontologias e vocabulários existentes sempre que estes oferecem classes ou propriedades adequadas às entidades e relações que precisam ser representadas. Essa estratégia favorece a interoperabilidade e reduz a necessidade de criação de termos específicos do projeto.

Entre os principais vocabulários reutilizados encontram-se OntoLex-Lemon, LemonEty, SKOS, Dublin Core Terms, PROV-O e NIF.

A reutilização não implica que todos os vocabulários empregados na representação dos dados sejam dependências formais da ontologia. A distinção entre ontologias importadas e vocabulários utilizados apenas nas instâncias é apresentada na seção 7.

### 8.2. Separação entre ontologia e dados

A Ontologia DicBio distingue o modelo conceitual utilizado para descrever os dados dos próprios recursos que constituem o dicionário. As classes e propriedades definidas ou reutilizadas pela ontologia pertencem ao namespace `dicbio:`, enquanto as instâncias concretas são identificadas por namespaces específicos, como `dbres:`, `dbsrc:` e `dbauth:`.

Essa separação permite que o modelo ontológico seja mantido e versionado independentemente dos dados, ao mesmo tempo em que possibilita que diferentes conjuntos de dados sejam descritos segundo o mesmo modelo.


### 8.3. Separação entre entrada lexical e acepção

Uma entrada lexical (`ontolex:LexicalEntry`) representa a unidade lexical que constitui o verbete e pode estar associada a uma ou mais formas (`ontolex:Form`) e a uma ou mais acepções (`ontolex:LexicalSense`). Cada acepção é representada como um recurso próprio e se relaciona à entrada lexical à qual pertence por meio da propriedade `ontolex:sense`.

Essa distinção permite representar adequadamente a polissemia: uma mesma entrada lexical pode apresentar diversas acepções, enquanto cada acepção pode receber informações semânticas, etimológicas e documentais próprias.

### 8.4. Representação das hipóteses etimológicas

Em relação ao modelo adotado por *LemonEty*, a Ontologia DicBio faz uma escolha de modelagem distinta. Optou-se aqui por descrever o étimo como um recurso da classe `dicbio:SemanticEtymon` (definida como uma subclasse de `ontolex:LexicalSense` e, portanto, distinta de `lemonety:Etymon`). Duas são as principais vantagens desta modelagem:
1. Isso permite descrever adequadamente os casos em que apenas uma das acepções de uma palavra foi transmitida a outra. Por exemplo, o português brasileiro *mouse* tem como étimo não a entrada inglesa *mouse* (com todas as suas acepções), mas apenas a acepção de "dispositivo informático";
2. Também é possível associar etimologicamente duas acepções da mesma entrada, indicando que a mudança semântica também tem natureza etimológica.

A classe `lemonety:Etymology` (reaproveitada da ontologia *LemonEty*) é entendida como a descrição de uma hipótese etimológica e, portanto, deve relacionar sempre uma acepção ao seu étimo, que, por sua vez, também é uma acepção.

Tem-se, por exemplo, o verbete para "aurícula", que é uma entrada lexical (`ontolex:LexicalEntry`) à qual correspondem três sentidos ou acepções (`ontolex:LexicalSense`):

`dbres:entry_auricula a ontolex:LexicalEntry ;
    ontolex:sense dbres:entry_auricula_sense1,
        dbres:entry_auricula_sense2,
        dbres:entry_auricula_sense3 .`

Cada uma dessas acepções é associada a uma definição (`skos:definition`) e a uma descrição etimológica (por meio de `lemonety:etymology`). A primeira acepção é assim definida e associada à sua descrição etimológica:

`dbres:entry_auricula_sense1 a ontolex:LexicalSense ;
   skos:definition "Cavidade superior dos ventrículos do coração."@pt ;
   lemonety:etymology dbres:etym_auricula_sense1 .`

A descrição etimológica (da classe `lemonety:Etymology`), por sua vez, indica (por meio da propriedade `dicbio:semanticEtymon`) qual é o étimo (que é necessariamente outra acepção, não outra entrada):

`dbres:etym_auricula_sense1 a lemonety:Etymology ;
    dicbio:semanticEtymon dbres:etymon_auricula_sense1 .`
    
Já o étimo (da classe `dicbio:SemanticEtymon`) apresenta uma definição (`skos:definition`):

`dbres:etymon_auricula_sense1 a dicbio:SemanticEtymon ;
   dcterms:language glotto:lati1261 ;
   skos:definition "Cavidade superior dos ventrículos do coração."@pt .`

Por fim, o étimo (que, lembre-se, é uma acepção) é associado à sua entrada correspondente, que também contém uma forma (`ontolex:canonicalForm`):

`dbres:auricula_lat a ontolex:LexicalEntry ;
    dcterms:language glotto:lati1261 ;
    ontolex:canonicalForm dbres:form_auricula_lat ;
    ontolex:sense dbres:etymon_auricula_sense1 .`


### 8.5. Representação das atestações

Uma **atestação** representa uma ocorrência documentada de uma forma lexical ou de uma acepção em uma fonte histórica. A atestação permite registrar informações sobre a ocorrência e relacioná-la à fonte que fornece a evidência documental.

As atestações são representadas pela classe `dicbio:Attestation` e podem ser associadas às acepções ou formas lexicais correspondentes. A fonte da atestação é indicada por meio de `dcterms:source`, permitindo distinguir a evidência documental de outras fontes utilizadas na elaboração do verbete. Por exemplo, a forma latina *auricula* (étimo da forma portuguesa "aurícula") é atestada numa obra de 1681 (a data é informada pela propriedade `dicbio:attestationDate`):

dbres:etymon_auricula_sense1 a dicbio:SemanticEtymon ;
    dcterms:language glotto:lati1261 ;
    dicbio:hasAttestation dbres:attestation_auricula_lat_sense1_blasius ;
    skos:definition "Cavidade superior dos ventrículos do coração."@pt .

`dbres:attestation_auricula_lat_sense1_blasius a dicbio:Attestation ;
    dicbio:attestationDate "1681"^^xsd:gYear ;
    dcterms:source dbsrc:source_blasius .`

Quando a atestação corresponde a uma ocorrência identificável no corpus digital do DicBio, ela pode também ser relacionada ao recurso correspondente no corpus. Por exemplo, a primeira acepção de "aurícula" tem uma atestação na obra de Vandelli, indicada pela propriedade `dicbio:hasAttestation`:

`dbres:entry_auricula_sense1 a ontolex:LexicalSense ;
    skos:definition "Cavidade superior dos ventrículos do coração."@pt ;
    lemonety:etymology dbres:etym_auricula_sense1 ;
    ontolex:reference dbres:concept_atrio ;
    dicbio:hasAttestation dbres:attestation_auricula_sense1_vandelli .`

A atestação em Vandelli é relacionada a uma ocorrência específica do corpus, por meio da propriedade `dicbio:attestedByOccurrence`:

`dbres:attestation_auricula_sense1_vandelli a dicbio:Attestation ;
    dicbio:attestationDate "1788"^^xsd:gYear ;
    dcterms:source dbsrc:work_diciovandelli ;
    dicbio:attestedByOccurrence dbres:t_vandelli_0012 .`

Por fim, a própria ocorrência do corpus é associada tanto à forma quanto à acepção, indicadas, respectivamente, pelas propriedades `dicbio:realizesForm` e `dicbio:realizesSense`:

`dbres:t_vandelli_0012 a nif:Word ;
    nif:anchorOf "auriculas"@pt ;
    nif:lemma "aurícula"@pt ;
    nif:referenceContext dbres:sn_vandelli_0015 ;
    dicbio:realizesForm dbres:form_auricula ;
    dicbio:realizesSense dbres:entry_auricula_sense1 .`

### 8.6. Vocabulários controlados

A Ontologia DicBio utiliza SKOS para representar conjuntos de valores controlados empregados na descrição dos dados. Esses conjuntos são organizados como `skos:ConceptScheme`, enquanto seus valores são representados como `skos:Concept`.

Na versão 1.0, são definidos vocabulários controlados para certeza etimológica, processo etimológico e tipo de formação de palavras. Os conceitos desses vocabulários recebem rótulos e definições em português e inglês.

A utilização de SKOS permite que esses vocabulários sejam tratados como conjuntos de conceitos identificáveis por URIs, sem exigir que se estabeleça entre eles uma hierarquia conceitual quando tal hierarquia não corresponde às necessidades de modelagem do DicBio.

### 8.7. Evidência e fontes

A representação dos dados do DicBio procura distinguir as informações afirmadas sobre os termos das fontes e evidências que sustentam essas informações. As fontes bibliográficas e documentais são representadas como recursos próprios e podem ser relacionadas às afirmações ou recursos correspondentes por meio de propriedades de proveniência e de citação bibliográfica.

Essa separação permite registrar, por exemplo, que uma determinada hipótese etimológica foi proposta ou registrada em determinada fonte, sem confundir a fonte com a própria hipótese representada no grafo.

A modelagem detalhada das diferentes categorias de fontes e das convenções utilizadas para sua identificação é apresentada no **Guia de Modelagem dos Dados DicBio**.

### 8.8. Vinculação com conceitos

<!-- Incluir aqui o uso de skos:Concept e ontolex:reference para relacionar um sentido ao seu conceito em outras ontologias como UBERON -->

### 8.9. Representação de textos com formatação

Os textos apresentados como literais, especialmente definições e descrições etimológicas, que podem ser relativamente longos, podem apresentar formatação simples em MarkDown, principalmente *itálicos* para representar estrangeirismos e latinismos.

---

## 9. Visão geral da ontologia

### 9.1. Visão conceitual

A Ontologia DicBio organiza-se em torno de cinco camadas articuladas. A camada *lexical*, baseada em OntoLex-Lemon, representa entradas, formas e acepções. A camada *etimológica*, baseada em LemonEty com adaptações próprias, descreve hipóteses etimológicas que relacionam uma acepção a seu étimo — este último modelado como outra acepção lexical (`dicbio:SemanticEtymon`), e não como uma entrada inteira. A camada *morfológica*, baseada em OntoLex-Morph e OntoLex-VarTrans, descreve a estrutura morfológica interna de uma hipótese etimológica quando pertinente. A camada de *evidência documental*, que combina classes próprias (`dicbio:Attestation`) com PROV-O e NIF, relaciona uma hipótese ou acepção a ocorrências específicas identificadas no corpus digital do projeto, distinguindo a forma e o sentido realizados por uma ocorrência textual da fonte que a atesta historicamente. Por fim, a camada *conceptual*, baseada em SKOS, correlaciona os conceitos com conceitos presentes em outras ontologias da área da Saúde, como UBERON.


### 9.2. Principais classes

* `dicbio:SemanticEtymon` — um sentido lexical que atua como étimo de outro sentido.
* `dicbio:EtymologicalProcess` — vocabulário controlado dos tipos de processo etimológico(herança, empréstimo, criação, derivação semântica).
* `dicbio:WordFormationType` — vocabulário controlado dos tipos de formação de palavras (sufixação, prefixação, composição).
* `dicbio:Attestation` — registro de uma atestação histórica, com data e fonte.

### 9.3. Principais propriedades

* Etimologia: `dicbio:semanticEtymon`, `dicbio:etymologicalProcess`, `dicbio:etymologicalArgumentation`, `dicbio:confidenceLevel`.
* Estrutura morfológica: `dicbio:hasWordFormationRelation`.
* Atestação e corpus: `dicbio:hasAttestation`, `dicbio:attestedByOccurrence`, `dicbio:realizesForm`, `dicbio:realizesSense`, `dicbio:attestationDate`.

### 9.4. Relação entre os principais componentes

<!-- Inserir diagrama da ontologia, se houver. -->

---

## 10. Classes

Esta seção apresenta as classes definidas pela Ontologia DicBio.

### 10.1. `dicbio:Attestation`

**URI:** `https://dicbio.fflch.usp.br/ontology/Attestation`

**Rótulo:** Attestation / Atestação

**Definição:** Registro de datação histórica de uma acepção, baseado em uma fonte específica.

**Superclasse(s):** `prov:Entity`

**Uso:** Relaciona-se a uma acepção via `dicbio:hasAttestation` e, quando identificável no corpus, a uma ocorrência específica via `dicbio:attestedByOccurrence` (ver §8.5).

### 10.2. `dicbio:EtymologicalProcess`

**URI:** `https://dicbio.fflch.usp.br/ontology/EtymologicalProcess`

**Rótulo:** Etymological Process / Processo Etimológico

**Definição:** Conceito que representa um tipo de processo etimológico envolvido na origem de uma unidade lexical.

**Superclasse(s):** `skos:Concept`

**Uso:** Valores possíveis de `dicbio:etymologicalProcess`, atribuído a uma hipótese etimológica (`lemonety:Etymology`). Instâncias: `dicbio:inherited`, `borrowed`, `created`, `semanticDerivation` (ver §12.2).

### 10.3. `dicbio:SemanticEtymon`

**URI:** `https://dicbio.fflch.usp.br/ontology/SemanticEtymon`

**Rótulo:** Semantic Etymon / Étimo Semântico

**Definição:** Um Sentido Lexical que atua como origem semântica numa relação etimológica com outro Sentido Lexical.

**Superclasse(s):** `ontolex:LexicalSense`

**Uso:** Valor do range de `dicbio:semanticEtymon`. Permite representar transmissão semântica parcial entre acepções (ver exemplo em §8.4).

### 10.4. `dicbio:WordFormationType`

**URI:** `https://dicbio.fflch.usp.br/ontology/WordFormationType`

**Rótulo:** Word Formation Type / Tipo de Formação de Palavras

**Definição:** Conceito que representa um tipo de processo de formação de palavras.

**Superclasse(s):** `skos:Concept`

**Uso:** Vocabulário inicial e extensível (§12.3), usado como valor de `vartrans:category` nas instâncias de `morph:WordFormationRelation` ligadas por `dicbio:hasWordFormationRelation`.

### 10.5. Classes reutilizadas

<!-- Apresentar, quando útil, as classes externas mais importantes utilizadas pela ontologia, como ontolex:LexicalEntry, ontolex:LexicalSense e ontolex:Form. -->

---

## 11. Propriedades

Esta seção apresenta as propriedades definidas pela Ontologia DicBio.

Para cada propriedade, registrar, quando aplicável:

- URI;
- rótulo em português;
- rótulo em inglês;
- definição em português;
- definição em inglês;
- domínio;
- range;
- superpropriedade;
- propriedades relacionadas;
- observações de uso;
- exemplo.

### 11.1. Propriedades de etimologia

### 11.1.1 `dicbio:etymologicalArgumentation`

**URI:** `https://dicbio.fflch.usp.br/ontology/etymologicalArgumentation`

**Rótulo:** etymological argumentation / argumentação etimológica

**Definição:** Fornece a argumentação discursiva que apoia ou explica a hipótese etimológica.

**Domínio:** `lemonety:Etymology`

**Range:** `rdf:langString`

**Superpropriedade:** nenhuma (propriedade própria, sem equivalente direto reutilizado)

**Uso:** O texto pode conter formatação leve em Markdown (por exemplo, *itálico* para estrangeirismos e latinismos), convertida em HTML apenas no momento da publicação — mantendo o dado independente de qualquer decisão de apresentação.

### 11.1.2 `dicbio:semanticEtymon`

**URI:** 

**Rótulo:** 

**Definição:** 

**Domínio:** 

**Range:** 

**Superpropriedade:** 

**Uso:** 


### 11.1.3 `dicbio:confidenceLevel`

**URI:** 

**Rótulo:** 

**Definição:** 

**Domínio:** 

**Range:** 

**Superpropriedade:** 

**Uso:** 

### 11.2. Propriedades de formação de palavras

### 11.2.1 `dicbio:hasWordFormationRelation`

**URI:** 

**Rótulo:** 

**Definição:** 

**Domínio:** 

**Range:** 

**Superpropriedade:** 

**Uso:** 

<!-- Listar propriedades relacionadas à formação de palavras. -->

### 11.3. Propriedades de atestação

### 11.3.1 `dicbio:attestedByOccurrence`

**URI:** 

**Rótulo:** 

**Definição:** 

**Domínio:** 

**Range:** 

**Superpropriedade:** 

**Uso:** 

### 11.3.2 `dicbio:hasAttestation`

**URI:** 

**Rótulo:** 

**Definição:** 

**Domínio:** 

**Range:** 

**Superpropriedade:** 

**Uso:** 

### 11.3.3 `dicbio:attestationDate`

**URI:** 

**Rótulo:** 

**Definição:** 

**Domínio:** 

**Range:** 

**Superpropriedade:** 

**Uso:** 

### 11.3.4 `dicbio:realizesForm`

**URI:** 

**Rótulo:** 

**Definição:** 

**Domínio:** 

**Range:** 

**Superpropriedade:** 

**Uso:** 

### 11.3.5 `dicbio:realizesSense`

**URI:** 

**Rótulo:** 

**Definição:** 

**Domínio:** 

**Range:** 

**Superpropriedade:** 

**Uso:** 

<!-- Listar propriedades relacionadas às atestações. -->

### 11.4. Outras propriedades

<!-- Demais propriedades próprias da ontologia. -->

### 11.5. Propriedades reutilizadas

<!-- Apresentar as propriedades externas mais importantes utilizadas pela ontologia. -->

---

## 12. Vocabulários controlados

### 12.1. `dicbio:EtymologicalCertaintyScheme`

| Conceito | URI | Rótulo | Definição |
|---|---|---|---|
| `dicbio:impossible` | <!-- URI --> | Impossível / Impossible | A hipótese contradiz evidências linguísticas ou históricas estabelecidas. |
| `dicbio:improbable` | <!-- URI --> | Improvável / Improbable | A hipótese carece de evidências suficientes ou entra em contradição com o conhecimento atual. |
| `dicbio:plausible` | <!-- URI --> | Plausível / Plausible | A hipótese é concebível mas pouco apoiada por evidências. |
| `dicbio:probable` | <!-- URI --> | Provável / Probable | A hipótese é apoiada por evidências relevantes e é consistente com o conhecimento atual. |
| `dicbio:certain` | <!-- URI --> | Certa / Certain | A hipótese é fortemente apoiada por evidências convergentes e é totalmente consistente com o conhecimento científico atual. |

### 12.2. `dicbio:EtymologicalProcessScheme`

| Conceito | URI | Rótulo | Definição |
|---|---|---|---|
| `dicbio:inherited` | <!-- URI --> | Herdado / Inherited | Unidade lexical herdada de um estágio anterior da mesma língua ou da sua língua-mãe. |
| `dicbio:borrowed` | <!-- URI --> | Emprestado / Borrowed | Unidade lexical emprestada de outra língua. |
| `dicbio:created` | <!-- URI --> | Criado / Created | Unidade lexical criada dentro da língua (derivação, composição etc.). |
| `dicbio:semanticDerivation` | <!-- URI --> | Derivado de outro sentido / Derived from another sense | Unidade lexical derivada de outro sentido lexical na mesma língua. |

### 12.3. `dicbio:WordFormationTypeScheme`

| Conceito | URI | Rótulo | Definição |
|---|---|---|---|
| `dicbio:Suffixation` | <!-- URI --> | Sufixação / Suffixation | Adição de sufixo para criar palavra com significado/função diferente. |
| `dicbio:Prefixation` | <!-- URI --> | Prefixação / Prefixation | Adição de prefixo para criar palavra com significado/função diferente. |
| `dicbio:Compounding` | <!-- URI --> | Composição / Compounding | Combinação de duas ou mais palavras/elementos para criar palavra com significado/função diferente. |

### 12.4. Extensibilidade dos vocabulários

<!-- Explicar como novos conceitos dos vocabulários controlados poderão ser acrescentados em versões futuras. -->

---

## 13. Exemplos

### 13.1. Exemplo mínimo de uma entrada lexical

```turtle
dbres:entry_adiposo a ontolex:LexicalEntry ;
    rdfs:seeAlso <https://pt.wiktionary.org/wiki/adiposo> ;
    skos:exactMatch <http://kaiko.getalp.org/dbnary/por/adiposo> ;
    dcterms:created "2024-05-04"^^xsd:date ;
    dcterms:creator dbauth:bruno_maroneze,
        dbauth:fabiani_goncalves ;
    lexinfo:partOfSpeech lexinfo:adjective ;
    ontolex:canonicalForm dbres:form_adiposo ;
    ontolex:otherForm dbres:form_adiposa,
        dbres:form_adiposas,
        dbres:form_adiposos ;
    ontolex:sense dbres:entry_adiposo_sense1 .
```

### 13.2. Exemplo de uma forma

```turtle
dbres:form_adiposo a ontolex:Form ;
    ontolex:writtenRep "adiposo"@pt ;
    lexinfo:number lexinfo:singular ;
    lexinfo:gender lexinfo:masculine .

dbres:form_adiposa a ontolex:Form ;
    ontolex:writtenRep "adiposa"@pt ;
    lexinfo:number lexinfo:singular ;
    lexinfo:gender lexinfo:feminine .
```

### 13.3. Exemplo de uma acepção

```turtle
dbres:entry_adiposo_sense1 a ontolex:LexicalSense ;
    skos:definition "Que contém gordura."@pt ;
    lemonety:etymology dbres:etym_adiposo_sense1_h1 .
```
```turtle
dbres:entry_auricula_sense1 a ontolex:LexicalSense ;
    skos:definition "Cavidade superior dos ventrículos do coração."@pt ;
    lemonety:etymology dbres:etym_auricula_sense1 ;
    ontolex:reference dbres:concept_atrio ;
    dicbio:hasAttestation dbres:attestation_auricula_sense1_vandelli .

dbres:entry_auricula_sense2 a ontolex:LexicalSense ;
    skos:definition "Orelha."@pt ;
    lemonety:etymology dbres:etym_auricula_sense2 ;
    ontolex:reference dbres:concept_orelha ;
    dicbio:hasAttestation dbres:attestation_auricula_sense2_vandelli .
```

### 13.4. Exemplo de uma hipótese etimológica

```turtle
dbres:etym_adiposo_sense1_h1 a lemonety:Etymology ;
    dcterms:creator dbauth:bruno_maroneze,
        dbauth:fabiani_goncalves ;
    dcterms:source dbsrc:dicbio_project ;
    dicbio:etymologicalProcess dicbio:borrowed ;
    dicbio:semanticEtymon dbres:etymon_adiposus ;
    dicbio:etymologicalArgumentation """A forma latina *adiposus*, ainda que não esteja registrada nos dicionários de latim da Antiguidade, pode ser encontrada em textos em latim científico, como, por exemplo, na expressão “panniculus adiposus”, presente na “Acta Physico-Medica” de 1730 (https://www.google.com.br/books/edition/Acta_physico_medica_Academiae_caesareae/bYy3qY5Fgn8C). Dessa forma, o étimo da forma portuguesa pode ser o latim científico, e não uma formação vernacular, como propõe o dicionário Houaiss."""@pt ;
    dicbio:confidenceLevel dicbio:probable .
```

### 13.5. Exemplo de um étimo

```turtle
dbres:etymon_adiposus a dicbio:SemanticEtymon ;
    dicbio:hasAttestation dbres:attestation_adiposus ;
    skos:definition "Que contém gordura."@pt .
```

### 13.6. Exemplo de uma relação de formação de palavras

```turtle
dbres:adiposo_derivation a morph:WordFormationRelation ;
    vartrans:source dbres:entry_adipe ;
    vartrans:target dbres:entry_adiposo ;
    vartrans:category dicbio:Suffixation .
```

### 13.7. Exemplo de uma atestação

```turtle
dbres:attestation_adiposo a dicbio:Attestation ;
    dcterms:source dbsrc:work_anatomiasantucci ;
    dicbio:attestationDate "1739"^^xsd:gYear .
```

### 13.8. Exemplo envolvendo um conceito

```turtle
dbres:concept_atrio a skos:Concept ;
    skos:definition "Cavidade superior do coração."@pt ;
    skos:exactMatch <http://purl.obolibrary.org/obo/UBERON_0002081> .
```

### 13.9. Exemplo completo

<!-- Inserir aqui um exemplo real e suficientemente completo de um verbete DicBio. -->

---

## 14. Alinhamentos com outras ontologias

### 14.1. OntoLex-Lemon

<!-- Explicar o alinhamento com ontolex:LexicalEntry, ontolex:Form, ontolex:LexicalSense etc. -->

### 14.2. LemonEty

A Ontologia DicBio reutiliza `lemonety:Etymology` para representar hipóteses etimológicas, bem como a propriedade `lemonety:etymology` para relacionar a hipótese à entrada lexical cuja etimologia ela descreve. Entretanto, devido à opção de modelar o étimo como uma acepção, e não como uma entrada lexical, a classe `lemonety:Etymon` não é reutilizada, sendo substituída por `dicbio:SemanticEtymon`.

As demais classes e propriedades de *LemonEty* também não foram reutilizadas, devido à opção por um formato próprio de modelagem.
	
### 14.3. SKOS

<!-- Explicar a relação entre os conceitos e vocabulários controlados DicBio e SKOS. -->

### 14.4. LexInfo

<!-- Explicar o uso de LexInfo para categorias e propriedades linguísticas. -->

### 14.5. Outros alinhamentos

<!-- Registrar outros alinhamentos relevantes. -->

### 14.6. Tabela de alinhamentos

| DicBio | Ontologia externa | Elemento externo | Tipo de relação |
|---|---|---|---|
| `dicbio:SemanticEtymon` | OntoLex-Lemon | `ontolex:LexicalSense` | `rdfs:subClassOf` |
| `dicbio:EtymologicalProcess` | SKOS | `skos:Concept` | `rdfs:subClassOf` |
| `dicbio:WordFormationType` | SKOS | `skos:Concept` | `rdfs:subClassOf` |
| `dicbio:Attestation` | PROV-O | `prov:Entity` | `rdfs:subClassOf` |
| `dicbio:realizesSense` | ITS-RDF | `itsrdf:taIdentRef` | `rdfs:subPropertyOf` |
---

## 15. Inferências e raciocínio

A Ontologia DicBio 1.0 foi submetida a testes de consistência lógica utilizando o reasoner HermiT no Protégé Desktop. O reasoner classificou a ontologia sem apresentar erros de consistência.

Entre as inferências esperadas encontra-se a classificação das instâncias de `dicbio:EtymologicalProcess` e `dicbio:WordFormationType` como instâncias de `skos:Concept`.

### 15.1. Perfil de raciocínio

<!-- Registrar as características OWL relevantes e o reasoner utilizado nos testes. -->

### 15.2. Inferências esperadas

<!-- Documentar inferências que decorrem dos axiomas da ontologia. -->

Exemplo:

```turtle
dicbio:EtymologicalProcess
    rdfs:subClassOf skos:Concept .
```

Consequentemente, uma instância de `dicbio:EtymologicalProcess` também é inferida como instância de `skos:Concept`.

### 15.3. Domínio e range

<!-- Explicar as principais inferências decorrentes de rdfs:domain e rdfs:range. -->

### 15.4. Testes com reasoner

<!-- Registrar os testes realizados com HermiT ou outro reasoner. -->

### 15.5. Limites do raciocínio

<!-- Distinguir inferências lógicas de validação de dados. Explicar que a validação estrutural dos dados será realizada por SHACL. -->

---

## 16. Limitações

### 16.1. Limitações conceituais

A versão 1.0 não pretende constituir uma representação exaustiva de todos os fenômenos lexicais, etimológicos e histórico-documentais relacionados à terminologia biológica. Ela estabelece um modelo suficientemente geral para a representação dos dados atualmente contemplados pelo projeto, podendo ser ampliada em versões futuras.

Algumas necessidades de modelagem que surgirem com a expansão do *corpus*, a inclusão de novos tipos de dados ou a incorporação de novos casos lexicográficos poderão exigir extensões ou revisões da ontologia. Tais alterações serão avaliadas em versões posteriores, preservando-se, sempre que possível, a compatibilidade com as versões anteriores.

### 16.2. Limitações de interoperabilidade

<!-- Registrar limitações decorrentes de dependências externas ou diferenças entre modelos. -->

### 16.3. Limitações dos vocabulários reutilizados

<!-- Registrar eventuais limitações relevantes de OntoLex-Lemon, LemonEty, LexInfo etc. -->

### 16.4. Questões em desenvolvimento

A integração completa com NIF requer a definição de uma estratégia consistente para representação dos offsets de termos, sentenças e parágrafos no corpus. Essa questão será aprofundada durante o desenvolvimento da camada de integração com o corpus.

<!-- Registrar questões que permanecerão em desenvolvimento sem transformá-las em regras da versão 1.0. -->

---

## 17. Histórico de versões

| Versão | Data | Descrição |
|---|---|---|
| desenvolvimento | 2025-2026 | Desenvolvimento e revisão da ontologia |
| 1.0 | <!-- preencher --> | Primeira versão estável |

### 17.1. Política para versões futuras

<!-- Explicar o que caracteriza uma versão de correção, uma versão compatível (1.x) e uma versão com mudanças incompatíveis (2.x). -->

---

## Referências

<!-- Incluir aqui as referências bibliográficas e documentais das ontologias e vocabulários reutilizados, além das referências metodológicas relevantes. -->

### Ontologias e vocabulários

- OntoLex-Lemon: <!-- referência -->
- LemonEty: <!-- referência -->
- SKOS: <!-- referência -->
- LexInfo: <!-- referência -->
- PROV-O: <!-- referência -->
- NIF: <!-- referência -->

### Documentação e especificações

<!-- Outras referências. -->

---

## Documentos relacionados

- **DicBio — Guia de Modelagem dos Dados:** <!-- link futuro -->
- **DicBio — Protocolo de descrição dos termos:** <!-- link, se mantido -->
- **DicBio — SHACL Shapes:** <!-- link futuro -->
- **DicBio Ontology — arquivo Turtle:** <!-- link futuro -->
