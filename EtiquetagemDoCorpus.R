#library(tidyverse)
#library(DT)
#library(data.table)
library(stringr)
library(XML)
library(xml2)
library(stylo)
library(jsonlite)
library(dplyr)
#library(sqldf)


# Ler os arquivos XML
xml_vandelli <- read_xml("data/diciovandelli.xml")
xml_santucci <- read_xml("data/anatomiasantucci.xml")
xml_brotero <- read_xml("data/compendio1brotero.xml")

# Definir o namespace do TEI
tei_ns <- c(tei = "http://www.tei-c.org/ns/1.0")

# Combinar os arquivos em um único corpus
corpus <- xml_new_root("corpus")
xml_add_child(corpus, xml_vandelli)
xml_add_child(corpus, xml_santucci)
xml_add_child(corpus, xml_brotero)

<<<<<<< HEAD
corpustotal <- paste("<corpus>", corpusVandelli, "\\n",
                     corpusSantucci, "\\n", corpusBrotero, "</corpus>")


# Lê a árvore XML do corpus total, extrai todos os termos e atributos
CorpusXML <- read_xml(corpustotal, encoding = "UTF-8", as_html = FALSE)
#corpusRoot <- xml_root(CorpusXML)

terms <- xml_find_all(CorpusXML, "//term")
tokenTerms <- xml_text(terms) %>% str_squish()  # Remove quebras de linha e espaços extras
=======
terms <- xml_find_all(corpus, "//tei:term", tei_ns)
tokenTerms <- xml_text(terms)
>>>>>>> TEI-XML
token_lemma <- xml_attr(terms, attr = "lemma")
token_orth <- xml_attr(terms, attr = "norm")
token_gram <- xml_attr(terms, attr = "msd")
token_senseNumber <- xml_attr(terms, attr = "senseNumber")

# Este loop é necessário para extrair todas as sentenças equivalentes
# No futuro, pretendo incluir aqui um código para negritar os termos
# em cada sentença

token_sentence <- NULL
author <- NULL
date <- NULL
currentPage <- NULL
previousPage <- NULL
pageNumber <- NULL
for(i in 1:length(terms)){
# Insere um caractere qualquer para depois ser transformado em <b></b>
  xml_text(terms[i]) <- paste0("[b]", xml_text(terms[i]), "[xb]")

# Extrai todas as sentenças e limpa as marcações
  token_sentence[i] <- as.character(xml_find_first(terms[i],
                                                   xpath = "string(./ancestor::*[1])"))
  token_sentence[i] <- delete.markup(token_sentence[i], markup.type = "xml")

# Substitui as marcas inseridas pelas marcas de negrito
  token_sentence[i] <- gsub("\\[b\\]", "<b>", token_sentence[i])
  token_sentence[i] <- gsub("\\[xb\\]", "</b>", token_sentence[i])

# Retorna à forma anterior (necessário para não afetar o negrito nos outros termos)
  xml_text(terms[i]) <- gsub("\\[b\\]", "", xml_text(terms[i]))
  xml_text(terms[i]) <- gsub("\\[xb\\]", "", xml_text(terms[i]))

#Insere autor e data - correção pelo DeepSeek
  author_full <- xml_text(xml_find_first(terms[i],
                                       xpath = ".//ancestor::tei:TEI//tei:author", tei_ns))
  date[i] <- xml_text(xml_find_first(terms[i],
                                       xpath = ".//ancestor::tei:TEI//tei:date", tei_ns))
  # Extrair apenas o sobrenome (tudo antes da vírgula)
  author[i] <- str_extract(author_full, "^[^,]+")
  
  # Verificar se há um <pb/> dentro do trecho de token_sentence
  pb_current <- xml_find_first(terms[i], ".//tei:pb", tei_ns)
  pb_preceding <- xml_find_first(terms[i], ".//preceding::tei:pb[1]", tei_ns)
  
  if (!is.na(pb_current)) {
    # Se houver um <pb/> no trecho, usar o anterior e o atual
    pageNumber[i] <- paste0(xml_attr(pb_preceding, "n"), "-", xml_attr(pb_current, "n"))
  } else {
    # Se não houver <pb/> no trecho, usar apenas o anterior
    pageNumber[i] <- xml_attr(pb_preceding, "n")
  }
  
  token_sentence[i] <- paste0(token_sentence[i], " (", author[i],
                              ", ", date[i], ", p. ", pageNumber[i], ")")
}
rm(pageNumber, currentPage, previousPage)

# Cria um dataframe único
DataFrameTotalXML <- data.frame(
  token = tokenTerms,
  Headword = token_lemma,
  orth = token_orth,
  gram = token_gram,
  SenseNumber = as.integer(token_senseNumber),
  sentence = token_sentence
)

# Este loop preenche as lacunas "por defeito"
# Se o lema está vazio, por defeito será igual ao token
# Se o campo de atualização ortográfica está vazio, por defeito será
# igual ao lema
# Se o número da acepção está vazio, por defeito será 1
for(x in 1:length(DataFrameTotalXML$Headword)){
  if(is.na(DataFrameTotalXML$Headword[x])){
    DataFrameTotalXML$Headword[x] <- DataFrameTotalXML$token[x]
  }
  if(is.na(DataFrameTotalXML$orth[x])){
    DataFrameTotalXML$orth[x] <- DataFrameTotalXML$Headword[x]
  }
  if(is.na(DataFrameTotalXML$SenseNumber[x])){
    DataFrameTotalXML$SenseNumber[x] <- 1
  }
}

# Preenche a coluna "variantes" com informações do token, Headword e gram

DataFrameTotalXML$variants <- ifelse(is.na(DataFrameTotalXML$gram)==FALSE,
                                     paste0(tolower(DataFrameTotalXML$token),
                                    " (", DataFrameTotalXML$gram, ")"
                                    #, " (", author, ", ", date, ")"
                                    ),
                                    paste0(tolower(DataFrameTotalXML$token)
                                    #       , " (", author, ", ", date, ")")
                                    # Tirar o comentário para incluir 
                                    # autor e data na variante
                                    )
)



# Abre os arquivos .csv do dicionário e cria um dataframe unindo-os

DadosDoDicionario <- read.csv("data/DadosDoDicionario.csv")
Definitions <- read.csv("data/definitions.csv")
Definitions$IDDef <- NULL #remove a coluna desnecessária

# Acrescenta a coluna das variantes gráficas a partir do dataframe total

for (n in 1:length(DadosDoDicionario$Headword)) {
  DadosDoDicionario$VariantSpellings[n] <- paste(sort(unique
                                         (DataFrameTotalXML$variants
                                           [tolower(DataFrameTotalXML$Headword)
                                             == tolower(DadosDoDicionario$Headword)[n]])),
                                    collapse = ", ")
  if (DadosDoDicionario$VariantSpellings[n] == DadosDoDicionario$Headword[n]) {
    DadosDoDicionario$VariantSpellings[n] <- NA
  }
}
# Reordena a coluna das variantes para depois da classe gramatical
DadosDoDicionario <- DadosDoDicionario[,c(1,2,3,4,5,6,10,7,8,9)]

# Atribui a cada definição do Definitions um vetor com as sentenças correspondentes
# 1. Cria uma coluna vazia no Definitions
#Definitions$Sentences <- NA

# 2. Atribui a cada célula Sentences uma lista de sentenças extraída do outro dataframe
# Este código a seguir foi sugerido pelo ChatGPT
Definitions <- Definitions %>%
  left_join(DataFrameTotalXML %>%
              group_by(Headword, SenseNumber) %>%
              summarise(Sentences = list(sentence), .groups = "drop"),
            by = c("Headword", "SenseNumber"))


# Salva o arquivo
write.csv(DataFrameTotalXML, file = "./data/DataframePrincipal.csv", fileEncoding = "UTF-8")
write.csv(DadosDoDicionario, file = "./data/DicionarioParaSite.csv", fileEncoding = "UTF-8")

# Junta os dados das definições no dataframe principal, reordena e salva em formato JSON
DadosDoDicionario$Definitions <- lapply(DadosDoDicionario$Headword,
                                        function(x) Definitions[Definitions$Headword == x, ])

DadosDoDicionario <- DadosDoDicionario[,c(1,2,3,4,5,6,7,11,8,9,10)]

write(jsonlite::toJSON(DadosDoDicionario), file = "data/DadosDoDicionario.json")


# Limpa a memória
rm(author, date, x, i, terms, corpus, token_gram, token_lemma, token_orth,
   token_senseNumber, token_sentence, tokenTerms, corpusVandelli,
   corpusSantucci, corpusBrotero, corpustotal, DataFrameTotalXML,
<<<<<<< HEAD
   m, n, consulta, DadosDoDicionario, Definitions)



#-------------------------------------------------------
# Este código abaixo tenta incluir a tag <s></s> em todas as sentenças
# do texto. Não funciona porque algumas das sentenças são aplicadas
# dentro de outras, como sentenças curtas ("L" por exemplo)

#Dataframeteste1 <- CriaDataframeDados("anatomiasantucci.xml")
#listasentencas <- unique(Dataframeteste1$sentence)

#for(c in 1:length(listasentencas)){
#  if(str_detect(listasentencas[c], regex("^\\<.+\\>$"))){
#    listasentencas[c] <- ""
#  } else if(listasentencas[c] == "<!"){
#    listasentencas[c] <- ""
#  }else if(str_detect(listasentencas[c], "DOCTYPE")){
#    listasentencas[c] <- ""
#  }else if(str_detect(listasentencas[c], regex("^\\<s>"))){
#    listasentencas[c] <- ""
#  }
#  listasentencas <- listasentencas[listasentencas != ""]
#}

#for(d in 1:length(listasentencas)){
#    listasentencas[d] <- str_replace(listasentencas[d], regex("^<.+>"), "")
  
#}

#for(e in 1:length(listasentencas)){
#  teste2 <- str_replace(teste2, listasentencas[e],
#                        paste0("<s>", listasentencas[e], "</s>"))
#}  

#arquivo <- file("arquivo.txt")
#writeLines(teste2, arquivo)
#-------------------------------------------------------
=======
   xml_brotero, xml_santucci, xml_vandelli, tei_ns, pb_current, pb_following, pb_preceding,
   author_full)
>>>>>>> TEI-XML
