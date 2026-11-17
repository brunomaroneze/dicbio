---
name: revisar-verbete
description: Revisa e completa verbetes do DicBio (data/entries/*.ttl) para o modelo RDF atual — transforma a argumentação etimológica em texto em dados (processo, grau de certeza, fonte da hipótese, definição do étimo, cadeias etimológicas, atestações, fontes em sources.ttl), resolve os comentários "# REVISAR"/"# NOTA" e valida com o SHACL. Use sempre que a pessoa pedir para revisar, converter, completar ou corrigir verbetes do dicionário, rodar o próximo lote da revisão, tratar os erros do SHACL de hipóteses etimológicas, ou continuar a "conversão para RDF" dos verbetes, mesmo que não cite a skill.
---

# Revisar verbetes do DicBio

Os verbetes foram migrados do modelo antigo por script
(`scripts/migrar_verbetes.py`, `scripts/gravar_datas.py`). O que sobrou é o
que exige leitura e julgamento: a argumentação etimológica está em texto e
precisa virar dado; étimos não têm definição; fontes estão em texto livre;
as notas da planilha de datas pedem atestações e cadeias novas. Esta skill
faz esse trabalho em lotes, deixando cada decisão marcada para a pessoa
conferir no diff. Quem confere é especialista em etimologia e redigiu os
verbetes: o objetivo é poupar o trabalho mecânico, não substituir esse juízo. Por isso cada escolha vem
com o motivo, e o que o texto não sustenta fica marcado, não inventado.

## Arquivos de referência

- `data/protocolo.md` — convenções do projeto (nomes, propriedades).
- `data/dicbio-shacl-shapes.ttl` — o que o validador exige.
- `data/entries/adiposo.ttl` — verbete revisado à mão: o modelo completo.
- `references/padroes.md` (nesta skill) — como decidir processo, grau,
  fonte, definição, cadeias, atestações, fontes novas e os casos especiais,
  com modelos em Turtle. Leia antes do primeiro verbete do lote.
- `data/sources.ttl` — fontes; `data/authors.ttl` — colaboradores.

O script de apoio fica em `.claude/skills/revisar-verbete/scripts/revisao.py`
e roda da raiz do projeto (abaixo, `R=` esse caminho).

## Fluxo de um lote

1. **Escolher o lote.** Se a pessoa não nomeou verbetes:
   `python $R proximos 10` lista os próximos pendentes (em ordem alfabética).
2. **Para cada verbete:**
   1. `python $R contexto <verbete>` — mostra os comentários REVISAR/NOTA com
      número de linha, cada hipótese com a argumentação na íntegra, as fontes
      que já existem, o L&S dos étimos latinos (cabeçalho com classe e gênero,
      acepções com os autores mais antigos) e os erros do SHACL.
   2. Leia o arquivo inteiro do verbete. Leia a argumentação com atenção:
      é dela que saem o processo, o grau, a fonte e a definição do étimo.
   3. Decida e edite seguindo `references/padroes.md`. Antes de criar
      qualquer IRI novo, `python $R nome-livre <nome> …` (os nomes são únicos
      no projeto inteiro, não só no arquivo).
   4. Se precisar de fonte nova, crie-a em `data/sources.ttl` (padrões §9),
      procurando autor/obra no Wikidata pela web.
   5. `python $R validar <verbete>` até não sobrar erro que você possa
      resolver com o que o texto dá. Rode também
      `python scripts/validate_graph.py data/sources.ttl` se mexeu nas fontes.
   6. `python $R marcar <verbete> revisado-skill "<pendências em poucas palavras>"`.
3. **Resumo do lote para a pessoa** (formato abaixo). Não faça commit: a
   pessoa confere o diff (`git diff data/`) e faz o commit ela mesma.

## O que preencher e o que só marcar

Preencha (sempre com `# REVISAR (skill): <motivo>` na linha):
- `dicbio:etymologicalProcess`, `dicbio:confidenceLevel` e `dcterms:source`
  de cada hipótese, a partir da argumentação;
- `skos:definition` das acepções de étimo, a partir da glosa da argumentação
  ou do L&S;
- classe e gênero do étimo conferidos no L&S;
- divisão em hipóteses `_h1`/`_h2` quando o texto apresenta origens rivais;
- entrada do primitivo e `WordFormationRelation` para palavras criadas;
- cadeia etimológica, segunda atestação ou acepção de sentido científico,
  quando a argumentação ou a nota trazem os dados (forma, sentido, fonte);
- fontes novas em sources.ttl para as fontes em texto livre.

Só marque, sem inventar:
- qualquer dado que o texto não dá (data, forma grega, Q-id do Wikidata,
  atestação científica "ainda a ser encontrada");
- decisões editoriais que mudam a interpretação do verbete (ex.: a nota diz
  "precisamos colocar hipóteses alternativas" sem dizer quais).

A argumentação (`dicbio:etymologicalArgumentation`) é texto de quem redigiu
o verbete: não reescreva. Se dividir hipóteses, distribua os trechos sem alterá-los.

## Cuidados com o Turtle

- Edite cirurgicamente (Edit), preservando a ordem, os comentários e as
  quebras de linha dos arquivos (CRLF). Não reescreva o arquivo inteiro.
- `#` comenta até o fim da linha: um comentário antes do `;` ou do `.`
  quebra a sintaxe. Ponha-o depois do terminador ou em linha própria.
- Literais em português com `@pt`; formas com a etiqueta da língua da
  entrada (`@pt`, `@la`, `@grc`); datas `"AAAA"^^xsd:gYear` (a.C. negativo:
  `"-0160"`); `dcterms:created` de entrada nova = data de hoje.
- Se o arquivo usar um prefixo novo (`vartrans:`, `morph:`, `owl:`), declare
  o `@prefix` no topo.
- Depois de editar, o `validar` também prova que o arquivo continua legível.

## Resumo do lote

Termine com uma tabela curta e uma lista das decisões que mais merecem
conferência:

```markdown
| Verbete | Processo / grau | Fonte da hipótese | Criado | Erros SHACL restantes |
|---|---|---|---|---|
| caule | borrowed / probable | dicbio_project | definição de caulis | 0 |
| ciliado | created? / plausible | dicbio_project | — | 1 (fonte sem autor) |

**Para conferir com atenção**
- ciliado: a nota diz que é "muito provavelmente palavra criada"; classifiquei
  como created com base em cilio + -ado, mas o texto não detalha.
- …
```

Diga também quantos verbetes faltam (`python $R resumo`).
