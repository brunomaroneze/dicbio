# Ontologia Dicbio 1.0 / DicBio Ontology 1.0

**Dicionário Histórico de Termos da Biologia**

> **Status:** Rascunho — versão 1.0 em preparação  
> **Versão:** 1.0  
> **URI da ontologia:** https://dicbio.fflch.usp.br/ontology/  
> **URI da versão:** https://dicbio.fflch.usp.br/ontology/1.0/  
> **Idioma da documentação:** português / inglês

---

## 1. Introdução

### 1.1. Apresentação

O **Dicionário Histórico de Termos da Biologia** (DicBio) é um dicionário eletrônico que visa reunir informações histórico-etimológicas sobre os termos da Biologia em língua portuguesa. É desenvolvido por estudantes e pesquisadores da Universidade Federal da Grande Dourados (UFGD) e da Universidade Federal de Mato Grosso do Sul (UFMS), com financiamento do CNPq e da FUNDECT.

Esta ontologia tem por finalidade modelar os dados do dicionário, disponibilizados no formato RDF, segundo os princípios do Linked Open Data.

### 1.2. Motivação

De acordo com os princípios do Linked Open Data, os dados devem estar disponíveis na Web de modo a explicitarem as suas relações com outros dados. A própria natureza relacional dos dados lexicais convida o(a) pesquisador(a) a procurá-los representar na forma de dados interligados (Linked Data), possibilitando assim a recuperação automatizada da vasta rede de remissões de uma determinada palavra. Essa recuperação automatizada pode ser usada para enriquecer diversos sistemas, como LLMs. Para isso, faz-se necessário elaborar uma ontologia que sistematize as diversas relações possíveis entre a entrada lexical e as informações linguísticas (classe gramatical, estrutura morfológica), etimológicas (étimo, datação) e conceituais, bem como as relações entre a entrada e as ocorrências de suas formas no *corpus*.

### 1.3. Organização desta documentação

<!-- Explicar a diferença entre esta documentação da ontologia e o futuro Guia de Modelagem dos Dados DicBio. -->

---

## 2. Objetivo e escopo

### 2.1. Objetivo

<!-- Definir o que a DicBio Ontology pretende representar. -->

### 2.2. Escopo

<!-- Delimitar os tipos de entidades e relações abrangidos pela ontologia. -->

### 2.3. Fora do escopo

<!-- Registrar explicitamente aspectos que não são objeto da ontologia. -->

### 2.4. Público-alvo

<!-- Indicar os principais usuários: pesquisadores, estudantes, desenvolvedores, editores de dados etc. -->

---

## 3. Status e versão

### 3.1. Status

<!-- Informar o status da versão 1.0 e a data de publicação. -->

### 3.2. Identificação da versão

| Elemento | Valor |
|---|---|
| Versão | 1.0 |
| URI da ontologia | `https://dicbio.fflch.usp.br/ontology/` |
| URI da versão | `https://dicbio.fflch.usp.br/ontology/1.0/` |
| Data de emissão | <!-- preencher --> |
| Data da última modificação | <!-- preencher --> |

### 3.3. Política de versionamento

<!-- Explicar como serão tratadas versões futuras (1.1, 1.2, 2.0 etc.). -->

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

<!-- Explicar a política de identificação das classes, propriedades e demais recursos da ontologia. -->

### 4.4. Namespaces utilizados nos dados

<!-- Distinguir o namespace da ontologia (dicbio:) dos namespaces utilizados para instâncias e recursos do projeto, como dbres:, dbsrc: e dbauth:. -->

| Prefixo | Namespace | Função |
|---|---|---|
| `dicbio:` | `https://dicbio.fflch.usp.br/ontology/` | Ontologia DicBio |
| `dbres:` | <!-- preencher --> | Recursos do DicBio |
| `dbsrc:` | <!-- preencher --> | Fontes e obras |
| `dbauth:` | <!-- preencher --> | Autores |

---

## 5. Licença

<!-- Informar a licença da ontologia e, se necessário, distinguir a licença da ontologia das licenças dos dados, código e documentação. -->

---

## 6. Autores

### 6.1. Autor(es)

<!-- Informar os autores da ontologia. -->

### 6.2. Contribuidores

<!-- Informar contribuidores, quando aplicável. -->

### 6.3. Atribuição

<!-- Informar como a ontologia deve ser citada. -->

---

## 7. Ontologias e vocabulários reutilizados

A Ontologia DicBio reutiliza vocabulários e ontologias existentes sempre que apropriado, evitando a criação de conceitos já disponíveis em modelos consolidados.

### 7.1. Ontologias e vocabulários

| Prefixo | Ontologia / vocabulário | Namespace | Função na DicBio Ontology |
|---|---|---|---|
| `ontolex:` | OntoLex-Lemon | `http://www.w3.org/ns/lemon/ontolex#` | Representação lexical |
| `lemonety:` | LemonEty | `http://lari-datasets.ilc.cnr.it/lemonEty#` | Representação etimológica |
| `morph:` | OntoLex-Morph | `http://www.w3.org/ns/lemon/morph#` | Relações de formação de palavras |
| `vartrans:` | OntoLex-VarTrans | `http://www.w3.org/ns/lemon/vartrans#` | Relações entre formas/entradas |
| `lexinfo:` | LexInfo | `http://www.lexinfo.net/ontology/2.0/lexinfo#` | Informação linguística |
| `skos:` | SKOS | `http://www.w3.org/2004/02/skos/core#` | Vocabulários e conceitos |
| `dcterms:` | Dublin Core Terms | `http://purl.org/dc/terms/` | Metadados |
| `prov:` | PROV-O | `http://www.w3.org/ns/prov#` | Proveniência |
| `nif:` | NIF | `http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#` | <!-- preencher --> |

<!-- Confirmar a lista definitiva e distinguir ontologias efetivamente importadas daquelas utilizadas apenas nos dados. -->

### 7.2. Justificativa das reutilizações

<!-- Explicar as principais decisões de reutilização. -->

---

## 8. Princípios de modelagem

### 8.1. Reutilização de ontologias existentes

<!-- Explicar a preferência por OntoLex-Lemon, SKOS etc. -->

### 8.2. Separação entre ontologia e dados

<!-- Explicar a distinção entre classes/propriedades da ontologia e instâncias dos dados DicBio. -->

### 8.3. Separação entre entrada lexical e acepção

<!-- Explicar, em termos conceituais, a distinção entre LexicalEntry e LexicalSense. -->

### 8.4. Representação das hipóteses etimológicas

<!-- Explicar a opção por associar hipóteses etimológicas às acepções. -->

### 8.5. Representação das atestações

<!-- Explicar o papel das atestações e sua relação com as acepções. -->

### 8.6. Vocabulários controlados

<!-- Explicar o uso de SKOS para os vocabulários controlados do DicBio. -->

### 8.7. Evidência e fontes

<!-- Explicar os princípios gerais para representação de fontes e evidências históricas. -->

> **Nota:** As regras operacionais detalhadas para a criação das instâncias serão apresentadas no **DicBio — Guia de Modelagem dos Dados**.

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

### 10.2. `dicbio:EtymologicalArgument`

**URI:** `https://dicbio.fflch.usp.br/ontology/EtymologicalArgument`

**Rótulo:** <!-- preencher -->

**Definição:** <!-- preencher -->

**Superclasse(s):** <!-- preencher -->

**Uso:** <!-- preencher -->

### 10.3. `dicbio:EtymologicalProcess`

**URI:** `https://dicbio.fflch.usp.br/ontology/EtymologicalProcess`

**Rótulo:** <!-- preencher -->

**Definição:** <!-- preencher -->

**Superclasse(s):** <!-- preencher -->

**Uso:** <!-- preencher -->

### 10.4. `dicbio:SemanticEtymon`

**URI:** `https://dicbio.fflch.usp.br/ontology/SemanticEtymon`

**Rótulo:** <!-- preencher -->

**Definição:** <!-- preencher -->

**Superclasse(s):** <!-- preencher -->

**Uso:** <!-- preencher -->

### 10.5. `dicbio:WordFormationType`

**URI:** `https://dicbio.fflch.usp.br/ontology/WordFormationType`

**Rótulo:** <!-- preencher -->

**Definição:** <!-- preencher -->

**Superclasse(s):** <!-- preencher -->

**Uso:** <!-- preencher -->

### 10.6. Classes reutilizadas

<!-- Apresentar, quando útil, as classes externas mais importantes utilizadas pela ontologia, como ontolex:LexicalEntry, ontolex:LexicalSense e ontolex:Form. -->

---

## 11. Propriedades

Esta seção apresenta as propriedades definidas pela DicBio Ontology.

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

<!-- Registrar aspectos do domínio que a ontologia não pretende representar completamente. -->

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
| 0.1 | <!-- preencher --> | Início do desenvolvimento |
| 0.4 | <!-- preencher --> | Versão de desenvolvimento anterior à 1.0 |
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
