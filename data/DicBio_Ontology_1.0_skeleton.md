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

A ontologia reutiliza, sempre que possível, classes e propriedades de ontologias e vocabulários consolidados, especialmente OntoLex-Lemon, LemonEty, LexInfo, SKOS, Dublin Core Terms, PROV-O e NIF.

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

´https://dicbio.fflch.usp.br/ontology/´

Os identificadores dos recursos são estáveis e não dependem da versão específica da ontologia. Assim, por exemplo, a classe ´dicbio:Attestation´ tem por URI:

´https://dicbio.fflch.usp.br/ontology/Attestation´

A versão específica da ontologia é identificada separadamente por meio de sua ´owl:versionIRI´.

Os URIs das instâncias dos dados pertencem a namespaces distintos, como ´dbres:´, ´dbsrc:´ e ´dbauth:´. Essa separação permite distinguir claramente os termos do modelo ontológico dos recursos concretos descritos pelo dicionário.


### 4.4. Namespaces utilizados nos dados

O *namespace* `dicbio:` é empregado para as classes e propriedades gerais que foram criadas para descrever as informações do dicionário.
O *namespace* `dbres:` é empregado para as instâncias das entradas, formas, acepções, descrições etimológicas etc.
O *namespace* `dbsrc:` é empregado para as instâncias das fontes dos dados, sejam primárias (as próprias obras que integram o *corpus* e outras), sejam secundárias (em geral, os demais dicionários consultados).
O *namespace* `dbauth:` é empregado para os recursos que representam os colaboradores do dicionário (estudantes e pesquisadores que atuam ou atuaram no projeto).

| Prefixo | Namespace | Função |
|---|---|---|
| `dicbio:` | `https://dicbio.fflch.usp.br/ontology/` | Ontologia DicBio |
| `dbres:` | <!-- preencher --> | Recursos do DicBio |
| `dbsrc:` | <!-- preencher --> | Fontes e obras |
| `dbauth:` | <!-- preencher --> | Autores |

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

Além das ontologias reutilizadas diretamente na definição da Ontologia DicBio, os dados do DicBio utilizam outros vocabulários externos para representar informações específicas. Esses vocabulários não constituem dependências da ontologia e, por isso, não são necessariamente incluídos em ´owl:imports´.

| Prefixo | Ontologia / vocabulário | Namespace | Função nos dados do DicBio |
|---|---|---|---|
| `foaf:` | FOAF | `http://xmlns.com/foaf/0.1/` | Nomes e endereços web |
| `dcterms:` | Dublin Core Terms | `http://purl.org/dc/terms/` | Metadados das fontes |
| `lexinfo:` | LexInfo | `http://www.lexinfo.net/ontology/3.0/lexinfo#` | Propriedades gramaticais |
| `bibo:` | The Bibliographic Ontology | `http://purl.org/ontology/bibo/` | Informações sobre as fontes bibliográficas |
| `vartrans:` | Variation and Translation | `http://www.w3.org/ns/lemon/vartrans#` | Informações morfológicas |
| `morph:` | Ontolex-Morph | `http://www.w3.org/ns/lemon/morph#` | Informações morfológicas |
| `glotto:` | Glottolog | `https://glottolog.org/resource/languoid/id/` | Idiomas das fontes ou dos termos |
| `skos:` | SKOS | `http://www.w3.org/2004/02/skos/core#` | Definições e conceitos |
| `owl:` | Web Ontology Language | `https://www.w3.org/TR/owl-ref/` | owl:sameAs para remissões |
| `rdfs:` | RDF Schema | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` | rdfs:seeAlso para remissões |
| `nif:` | NIF | `http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#` | Informações relacionadas ao *corpus* |
| `lemonety:` | LemonEty | `http://lari-datasets.ilc.cnr.it/lemonEty#` | Informações etimológicas |


<!-- ### 7.3. Justificativa das reutilizações

Será que precisa deste item?

Explicar as principais decisões de reutilização. Mencionar o problema do LemonEty. -->

---

## 8. Princípios de modelagem

### 8.1. Reutilização de ontologias existentes

A Ontologia DicBio procura reutilizar ontologias e vocabulários existentes sempre que estes oferecem classes ou propriedades adequadas às entidades e relações que precisam ser representadas. Essa estratégia favorece a interoperabilidade e reduz a necessidade de criação de termos específicos do projeto.

Entre os principais vocabulários reutilizados encontram-se OntoLex-Lemon, LemonEty, LexInfo, SKOS, Dublin Core Terms, PROV-O e NIF.

A reutilização não implica que todos os vocabulários empregados na representação dos dados sejam dependências formais da ontologia. A distinção entre ontologias importadas e vocabulários utilizados apenas nas instâncias é apresentada na seção 7.

### 8.2. Separação entre ontologia e dados

A Ontologia DicBio distingue o modelo conceitual utilizado para descrever os dados dos próprios recursos que constituem o dicionário. As classes e propriedades definidas ou reutilizadas pela ontologia pertencem ao namespace ´dicbio:´, enquanto as instâncias concretas são identificadas por namespaces específicos, como ´dbres:´, ´dbsrc:´ e ´dbauth:´.

Essa separação permite que o modelo ontológico seja mantido e versionado independentemente dos dados, ao mesmo tempo em que possibilita que diferentes conjuntos de dados sejam descritos segundo o mesmo modelo.


### 8.3. Separação entre entrada lexical e acepção

Uma entrada lexical (´ontolex:LexicalEntry´) representa a unidade lexical que constitui o verbete e pode estar associada a uma ou mais formas (´ontolex:Form´) e a uma ou mais acepções (´ontolex:LexicalSense´). Cada acepção é representada como um recurso próprio e se relaciona à entrada lexical à qual pertence por meio da propriedade ´ontolex:sense´.

Essa distinção permite representar adequadamente a polissemia: uma mesma entrada lexical pode apresentar diversas acepções, enquanto cada acepção pode receber informações semânticas, etimológicas e documentais próprias.

### 8.4. Representação das hipóteses etimológicas

Em relação ao modelo adotado por *LemonEty*, a Ontologia DicBio faz uma escolha de modelagem distinta. Optou-se aqui por descrever o étimo como um recurso da classe ´dicbio:SemanticEtymon´ (definida como uma subclasse de `ontolex:LexicalSense` e, portanto, distinta de `lemonety:Etymon`). Duas são as principais vantagens desta modelagem:
1. Isso permite descrever adequadamente os casos em que apenas uma das acepções de uma palavra foi transmitida a outra. Por exemplo, o português brasileiro *mouse* tem como étimo não a entrada inglesa *mouse* (com todas as suas acepções), mas apenas a acepção de "dispositivo informático";
2. Também é possível associar etimologicamente duas acepções da mesma entrada, indicando que a mudança semântica também tem natureza etimológica.

A classe `lemonety:Etymology` (reaproveitada da ontologia *LemonEty*) é entendida como a descrição de uma hipótese etimológica e, portanto, deve relacionar sempre uma acepção ao seu étimo, que, por sua vez, também é uma acepção.

<!-- Acrescentar um exemplo -->

### 8.5. Representação das atestações

Uma **atestação** representa uma ocorrência documentada de uma forma lexical ou de uma acepção em uma fonte histórica. A atestação permite registrar informações sobre a ocorrência e relacioná-la à fonte que fornece a evidência documental.

As atestações são representadas pela classe ´dicbio:Attestation´ e podem ser associadas às acepções ou formas lexicais correspondentes. A fonte da atestação é indicada por meio de ´dcterms:source´, permitindo distinguir a evidência documental de outras fontes utilizadas na elaboração do verbete.

Quando a atestação corresponde a uma ocorrência identificável no corpus digital do DicBio, ela pode também ser relacionada ao recurso correspondente no corpus por meio das propriedades apropriadas.

<!-- Incluir as propriedades que relacionam a atestação ao corpus. -->

### 8.6. Vocabulários controlados

A Ontologia DicBio utiliza SKOS para representar conjuntos de valores controlados empregados na descrição dos dados. Esses conjuntos são organizados como ´skos:ConceptScheme´, enquanto seus valores são representados como ´skos:Concept´.

Na versão 1.0, são definidos vocabulários controlados para certeza etimológica, processo etimológico e tipo de formação de palavras. Os conceitos desses vocabulários recebem rótulos e definições em português e inglês.

A utilização de SKOS permite que esses vocabulários sejam tratados como conjuntos de conceitos identificáveis por URIs, sem exigir que se estabeleça entre eles uma hierarquia conceitual quando tal hierarquia não corresponde às necessidades de modelagem do DicBio.

### 8.7. Evidência e fontes

A representação dos dados do DicBio procura distinguir as informações afirmadas sobre os termos das fontes e evidências que sustentam essas informações. As fontes bibliográficas e documentais são representadas como recursos próprios e podem ser relacionadas às afirmações ou recursos correspondentes por meio de propriedades de proveniência e de citação bibliográfica.

Essa separação permite registrar, por exemplo, que uma determinada hipótese etimológica foi proposta ou registrada em determinada fonte, sem confundir a fonte com a própria hipótese representada no grafo.

A modelagem detalhada das diferentes categorias de fontes e das convenções utilizadas para sua identificação é apresentada no **Guia de Modelagem dos Dados DicBio**.


---

## 9. Visão geral da ontologia

### 9.1. Visão conceitual

<!-- Inserir uma descrição geral da estrutura da ontologia. -->

### 9.2. Principais classes

<!-- Apresentar resumidamente as classes próprias da DicBio Ontology. -->

### 9.3. Principais propriedades

<!-- Apresentar resumidamente as propriedades próprias da DicBio Ontology. -->

### 9.4. Relação entre os principais componentes

<!-- Inserir diagrama da ontologia, se houver. -->

### 9.5. Módulos conceituais

<!-- Se pertinente, organizar a ontologia em módulos: léxico, etimologia, morfologia, atestação, conceitos etc. -->

---

## 10. Classes

Esta seção apresenta as classes definidas pela DicBio Ontology.

### 10.1. `dicbio:Attestation`

**URI:** `https://dicbio.fflch.usp.br/ontology/Attestation`

**Rótulo:** <!-- preencher -->

**Definição:** <!-- preencher -->

**Superclasse(s):** <!-- preencher -->

**Uso:** <!-- preencher -->

### 10.2. `dicbio:EtymologicalProcess`

**URI:** `https://dicbio.fflch.usp.br/ontology/EtymologicalProcess`

**Rótulo:** <!-- preencher -->

**Definição:** <!-- preencher -->

**Superclasse(s):** <!-- preencher -->

**Uso:** <!-- preencher -->

### 10.3. `dicbio:SemanticEtymon`

**URI:** `https://dicbio.fflch.usp.br/ontology/SemanticEtymon`

**Rótulo:** <!-- preencher -->

**Definição:** <!-- preencher -->

**Superclasse(s):** <!-- preencher -->

**Uso:** <!-- preencher -->

### 10.4. `dicbio:WordFormationType`

**URI:** `https://dicbio.fflch.usp.br/ontology/WordFormationType`

**Rótulo:** <!-- preencher -->

**Definição:** <!-- preencher -->

**Superclasse(s):** <!-- preencher -->

**Uso:** <!-- preencher -->

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

<!-- Listar propriedades como dicbio:etymologicalProcess, dicbio:etymologicalArgumentation, dicbio:confidenceLevel etc. -->
### 11.1.1 `dicbio:etymologicalArgumentation`

**URI:** `https://dicbio.fflch.usp.br/ontology/etymologicalArgumentation`

**Rótulo:** <!-- preencher -->

**Definição:** <!-- preencher -->

**Superclasse(s):** <!-- preencher -->

**Uso:** <!-- preencher -->



### 11.2. Propriedades de formação de palavras

<!-- Listar propriedades relacionadas à formação de palavras. -->

### 11.3. Propriedades de atestação

<!-- Listar propriedades relacionadas às atestações. -->

### 11.4. Outras propriedades

<!-- Demais propriedades próprias da ontologia. -->

### 11.5. Propriedades reutilizadas

<!-- Apresentar as propriedades externas mais importantes utilizadas pela ontologia. -->

---

## 12. Vocabulários controlados

### 12.1. `dicbio:EtymologicalCertaintyScheme`

<!-- Descrever o esquema de certeza etimológica. -->

| Conceito | URI | Rótulo | Definição |
|---|---|---|---|
| `dicbio:impossible` | <!-- URI --> | <!-- PT / EN --> | <!-- preencher --> |
| `dicbio:improbable` | <!-- URI --> | <!-- PT / EN --> | <!-- preencher --> |
| `dicbio:plausible` | <!-- URI --> | <!-- PT / EN --> | <!-- preencher --> |
| `dicbio:probable` | <!-- URI --> | <!-- PT / EN --> | <!-- preencher --> |
| `dicbio:certain` | <!-- URI --> | <!-- PT / EN --> | <!-- preencher --> |

### 12.2. `dicbio:EtymologicalProcessScheme`

<!-- Descrever o esquema de processos etimológicos. -->

| Conceito | URI | Rótulo | Definição |
|---|---|---|---|
| `dicbio:inherited` | <!-- URI --> | <!-- PT / EN --> | <!-- preencher --> |
| `dicbio:borrowed` | <!-- URI --> | <!-- PT / EN --> | <!-- preencher --> |
| `dicbio:created` | <!-- URI --> | <!-- PT / EN --> | <!-- preencher --> |
| `dicbio:semanticDerivation` | <!-- URI --> | <!-- PT / EN --> | <!-- preencher --> |

### 12.3. `dicbio:WordFormationTypeScheme`

<!-- Descrever o esquema de tipos de formação de palavras. -->

| Conceito | URI | Rótulo | Definição |
|---|---|---|---|
| `dicbio:Suffixation` | <!-- URI --> | <!-- PT / EN --> | <!-- preencher --> |
| `dicbio:Prefixation` | <!-- URI --> | <!-- PT / EN --> | <!-- preencher --> |
| `dicbio:Compounding` | <!-- URI --> | <!-- PT / EN --> | <!-- preencher --> |

### 12.4. Extensibilidade dos vocabulários

<!-- Explicar como novos conceitos dos vocabulários controlados poderão ser acrescentados em versões futuras. -->

---

## 13. Exemplos
<!-- 
13.1. Exemplo básico: entrada e formas
13.2. Exemplo de polissemia
13.3. Exemplo de hipótese etimológica
13.4. Exemplo de étimo semântico
13.5. Exemplo de atestação
13.6. Exemplo de formação de palavra
13.7. Exemplo completo: um verbete real
-->
### 13.1. Exemplo mínimo de uma entrada lexical

```turtle
# inserir exemplo
```

### 13.2. Exemplo de uma forma

```turtle
# inserir exemplo
```

### 13.3. Exemplo de uma acepção

```turtle
# inserir exemplo
```

### 13.4. Exemplo de uma hipótese etimológica

```turtle
# inserir exemplo
```

### 13.5. Exemplo de um étimo

```turtle
# inserir exemplo
```

### 13.6. Exemplo de uma relação de formação de palavras

```turtle
# inserir exemplo
```

### 13.7. Exemplo de uma atestação

```turtle
# inserir exemplo
```

### 13.8. Exemplo envolvendo um conceito

```turtle
# inserir exemplo
```

### 13.9. Exemplo completo

<!-- Inserir aqui um exemplo real e suficientemente completo de um verbete DicBio. -->

---

## 14. Alinhamentos com outras ontologias

### 14.1. OntoLex-Lemon

<!-- Explicar o alinhamento com ontolex:LexicalEntry, ontolex:Form, ontolex:LexicalSense etc. -->

### 14.2. LemonEty

<!-- Explicar o uso de LemonEty para a representação das relações etimológicas. -->

### 14.3. SKOS

<!-- Explicar a relação entre os conceitos e vocabulários controlados DicBio e SKOS. -->

### 14.4. LexInfo

<!-- Explicar o uso de LexInfo para categorias e propriedades linguísticas. -->

### 14.5. Outros alinhamentos

<!-- Registrar outros alinhamentos relevantes. -->

### 14.6. Tabela de alinhamentos

| DicBio | Ontologia externa | Elemento externo | Tipo de relação |
|---|---|---|---|
| <!-- preencher --> | <!-- preencher --> | <!-- preencher --> | <!-- preencher --> |

---

## 15. Inferências e raciocínio

A Ontologia DicBio 1.0 foi submetida a testes de consistência lógica utilizando o reasoner HermiT no Protégé Desktop. O reasoner classificou a ontologia sem apresentar erros de consistência.

Entre as inferências esperadas encontra-se a classificação dos conceitos dos vocabulários controlados como instâncias de ´skos:Concept´, em decorrência da relação de subclasse estabelecida entre ´dicbio:EtymologicalProcess´, ´dicbio:WordFormationType´ e ´skos:Concept´.

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

### 16.4. Questões não resolvidas

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
