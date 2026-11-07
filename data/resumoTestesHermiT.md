# Resumo dos testes com HermiT

## Texto sugerido para a descrição da ontologia

Em 7 de novembro de 2026, a ontologia DicBio e uma amostra de seus dados foram
submetidas a testes de consistência e de inferência com o reasoner HermiT (versão 1.3.8),
executado por meio do Owlready2. As execuções incluíram as importações
carregadas da ontologia e não apontaram inconsistências nos conjuntos testados.
Em dados sintéticos, seis inferências de domínio e contradomínio das
propriedades `semanticEtymon`, `formalEtymon` e `hasAttestation` foram
confirmadas. Na amostra de dados, quatro consultas não encontraram os padrões
de tipos e relações indesejados selecionados.

Esses resultados se limitam aos arquivos, axiomas e casos examinados: a
materialização de relações inferidas entre indivíduos foi desativada devido a
um erro interno do HermiT nessa etapa. As consultas negativas verificam a
ausência dos padrões no grafo consultado, não a negação lógica das afirmações.

## Observação sobre o teste de antera

No conjunto adicional de seis expectativas relativas a *antera*, cinco foram
atendidas. A expectativa AN-001 não foi confirmada pela consulta a um triplo de
tipo direto: embora OntoLex declare `LexicalEntry` como subclasse de
`semiotics:Expression`, esse tipo indireto não foi materializado no grafo
consultado. O resultado não demonstra, por si só, uma inconsistência.
