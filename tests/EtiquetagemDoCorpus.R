library(tidyverse)
library(DT)
library(data.table)
#library(koRpus.lang.pt)
library(stringr)


# TokTextDF$token[TokTextDF$lttr==0] <- "" # Elimina o caractere BOM

## Scripts para anotação de POS usando o UDPipe
library(udpipe)

# m_port <- udpipe::udpipe_download_model(language = "portuguese-bosque") # faz download do modelo

m_port <- udpipe_load_model(file = "./tests/portuguese-bosque-ud-2.5-191206.udpipe") # carrega na memória

# Trocar por um script automático que lê o arquivo CorpusTextsMetadata.csv

# Lê os metadados do córpus
CorpusMetadata <- read.csv2("./data/CorpusTextsMetadata.csv",
                            encoding = "UTF-8")
colnames(CorpusMetadata) <- c("Filename", "Author", "Title",
                              "DateOfPublication")

# Cria uma função que retorna o dataframe de um arquivo txt

CriaDataframeDados <- function(NomeDoArquivo){
  
  CorpusText <- readLines(con = paste0("./data/", NomeDoArquivo),
                       encoding = "UTF-8")

  text_anndfCorpusText <- udpipe::udpipe_annotate(m_port, x = CorpusText) %>%
    as.data.frame() # Cria um dataframe no formato CONLLU com as anotações
  
  # Corrige a numeração da lista de sentenças
  text_anndfCorpusText$sentence_id[1] <- 1
  for(x in 2:length(text_anndfCorpusText$sentence_id)){
    if(text_anndfCorpusText$sentence[x] == text_anndfCorpusText$sentence[(x-1)]){
      text_anndfCorpusText$sentence_id[x] <- text_anndfCorpusText$sentence_id[(x-1)]
    } else {
      text_anndfCorpusText$sentence_id[x] <- text_anndfCorpusText$sentence_id[(x-1)] + 1
    }
  }
  
  text_anndfCorpusText$doc_id <- NomeDoArquivo
  
  return(text_anndfCorpusText)
}

# Junta todos num só
DataframeTotal <- lapply(CorpusMetadata$Filename,
                     CriaDataframeDados) %>% rbindlist()

# Elimina as colunas desnecessárias

DataframeTotal <- subset(DataframeTotal, upos!="PUNCT")
DataframeTotal$paragraph_id <- NULL
DataframeTotal$head_token_id <- NULL
DataframeTotal$dep_rel <- NULL
DataframeTotal$deps <- NULL
DataframeTotal$upos <- NULL
DataframeTotal$xpos <- NULL
DataframeTotal$feats <- NULL

# O arquivo de dados só precisa conter as palavras presentes no dicionário
# Assim, lematizamos o necessário e eliminamos o resto

# Lematização e correção ortográfica:
# Primeiro, copia a coluna token para orth e lemma
DataframeTotal$orth <- DataframeTotal$token
DataframeTotal$lemma <- DataframeTotal$orth

# Abre o arquivo de lemas
LematizacaoDataFrame <- read.csv("./data/OrtografiaLematizacao.csv",
                            encoding = "UTF-8")

# Atribui os lemas e as formas ortográficas para as respectivas colunas

for(i in 1:length(DataframeTotal$token)){
  if(DataframeTotal$token[i] %in% LematizacaoDataFrame$Token){

    DataframeTotal$orth[i] <- LematizacaoDataFrame$Ortografia[LematizacaoDataFrame$Token == DataframeTotal$token[i]]
    DataframeTotal$lemma[i] <- LematizacaoDataFrame$Lemma[LematizacaoDataFrame$Token == DataframeTotal$token[i]]
    DataframeTotal$misc[i] <- LematizacaoDataFrame$InflForm[LematizacaoDataFrame$Token == DataframeTotal$token[i]]

    } else

  if(DataframeTotal$token[i] %in% toupper(LematizacaoDataFrame$Token)){

    DataframeTotal$orth[i] <- toupper(LematizacaoDataFrame$Ortografia[toupper(LematizacaoDataFrame$Token) == DataframeTotal$token[i]])
    DataframeTotal$lemma[i] <- LematizacaoDataFrame$Lemma[toupper(LematizacaoDataFrame$Token) == DataframeTotal$token[i]]
    DataframeTotal$misc[i] <- LematizacaoDataFrame$InflForm[toupper(LematizacaoDataFrame$Token) == DataframeTotal$token[i]]
        
  } else
  
  if(DataframeTotal$token[i] %in% str_to_title(LematizacaoDataFrame$Token)){
    
    DataframeTotal$orth[i] <- str_to_title(LematizacaoDataFrame$Ortografia[str_to_title(LematizacaoDataFrame$Token) == DataframeTotal$token[i]])
    DataframeTotal$lemma[i] <- LematizacaoDataFrame$Lemma[str_to_title(LematizacaoDataFrame$Token) == DataframeTotal$token[i]]
    DataframeTotal$misc[i] <- LematizacaoDataFrame$InflForm[str_to_title(LematizacaoDataFrame$Token) == DataframeTotal$token[i]]
    
  }
}
  
# Troca grupos de caracteres na coluna orth
#DataframeTotal$orth <- str_replace(DataframeTotal$orth, "nn", "n")
#DataframeTotal$orth <- str_replace(DataframeTotal$orth, "aõ", "ão")
#DataframeTotal$orth <- str_replace(DataframeTotal$orth, "oens", "ões")
#DataframeTotal$orth <- str_replace(DataframeTotal$orth, "mm", "m")
#DataframeTotal$orth <- str_replace(DataframeTotal$orth, "ll", "l")
#DataframeTotal$orth <- str_replace(DataframeTotal$orth, "mm", "m")
#DataframeTotal$orth <- str_replace(DataframeTotal$orth, "ff", "f")
#DataframeTotal$orth <- str_replace(DataframeTotal$orth, "FF", "F")
#DataframeTotal$orth <- str_replace(DataframeTotal$orth, "th", "t")
#DataframeTotal$orth <- str_replace(DataframeTotal$orth, "ph", "f")
#DataframeTotal$orth <- str_replace(DataframeTotal$orth, "cco", "co")


# Junta a expressão "jardim botânico"
# Funcionou com o txt_recode_ngram(), desde que eu preveja todas as formas variantes
# das três colunas token, orth, lemma
# O algoritmo embaixo funciona também, mas baseado só no lema

DataframeTotal$token <- txt_recode_ngram(DataframeTotal$token,
                                         c("jardim botânico", "jardim botanico", "jardins botanicos",
                                           "JARDINS BOTANICOS", "JARDIM BOTANICO",
                                           "Jardim Botanico", "Jardins Botanicos"), 2, sep = " ")
DataframeTotal$orth <- txt_recode_ngram(DataframeTotal$orth,
                                        c("jardim botânico", "jardins botânicos",
                                          "JARDINS BOTÂNICOS", "JARDIM BOTÂNICO",
                                          "Jardim Botânico", "Jardins Botânicos"), 2, sep = " ")
DataframeTotal$lemma <- txt_recode_ngram(DataframeTotal$lemma,
                                         "jardim botânico", 2, sep = " ")

# Junta a expressão "jardim botânico". Dá para adaptar esse código para uma função
# que junta quaisquer duas palavras

#DataframeTotal <- subset(DataframeTotal, lemma != "") # Elimina tudo o que não tiver lema
# Por alguma razão, a nova versão do R
# exige que primeiro se faça isso antes de rodar
# o loop for embaixo
#for(n in 1:length(DataframeTotal$doc_id)){
#  if(DataframeTotal$lemma[n] == "jardim" &&
#    DataframeTotal$lemma[n+1] == "botânico"){
#    DataframeTotal$lemma[n] <- paste(DataframeTotal$lemma[n], DataframeTotal$lemma[n+1], sep = " ")
#    DataframeTotal$token[n] <- paste(DataframeTotal$token[n], DataframeTotal$token[n+1], sep = " ")
#    DataframeTotal$orth[n] <- paste(DataframeTotal$orth[n], DataframeTotal$orth[n+1], sep = " ")
#    DataframeTotal$lemma[n+1] <- ""
#  }
#}

# Função para lematizar
lematizar <- function(lema, wclass){
  
  for(n in 1:length(DataframeTotal$orth)){
    
    if(tolower(DataframeTotal$orth[n]) == tolower(lema)){ # O primeiro "if" lematiza palavras idênticas
      DataframeTotal$lemma[n] <- tolower(lema)
      
    } else
      
      if(tolower(DataframeTotal$orth[n]) == str_c(tolower(lema),"s")){ # O segundo "if" lematiza plurais
        
        DataframeTotal$lemma[n] <- tolower(lema)
        
      } else
        
        if(tolower(DataframeTotal$orth[n]) == str_c(str_sub(lema, end = -2L), "a") # Este lematiza adjetivos femininos
           & wclass == "adj") 
          
        {
          
          DataframeTotal$lemma[n] <- tolower(lema)
          
        } else
          
          if(tolower(DataframeTotal$orth[n]) == str_c(str_sub(lema, end = -2L), "as") # Este lematiza adjetivos femininos plurais
             & wclass == "adj") 
            
          {
            
            DataframeTotal$lemma[n] <- tolower(lema)
            
          } else
            
            if(str_detect(lema, "ão\\b")
               & tolower(DataframeTotal$orth[n]) == str_c(str_sub(lema, end = -3L), "ões") # Este lematiza substantivos em -ão
               & wclass == "subst") 
              
            {
              
              DataframeTotal$lemma[n] <- tolower(lema)
              
            } else
              
              if(str_detect(lema, "m\\b")
                 & tolower(DataframeTotal$orth[n]) == str_c(str_sub(lema, end = -2L), "ns") # Este lematiza substantivos em -m
                 & wclass == "subst") 
                
              {
                
                DataframeTotal$lemma[n] <- tolower(lema)
                
              } else
                
                if(str_detect(lema, "l\\b")
                   & tolower(DataframeTotal$orth[n]) == str_c(str_sub(lema, end = -2L), "is") # Este lematiza adjetivos em -l
                   & wclass == "adj") 
                  
                {
                  
                  DataframeTotal$lemma[n] <- tolower(lema)
                  
                } else
                  
                  if(str_detect(lema, "r\\b")
                     & tolower(DataframeTotal$orth[n]) == str_c(lema, "es")) # Este lematiza subst e adj em -r 
                  {
                    DataframeTotal$lemma[n] <- tolower(lema)
                  }
  }
  return(DataframeTotal)
}



# Elimina tudo o que não for relevante para o dicionário

DadosdoDicionario <- read.csv("./data/DadosDoDicionario.csv", encoding = "UTF-8")
#colnames(DadosdoDicionario) <- c("ID", "Headword", "FirstAttestationDate",
#                                 "FirstAttestationExampleMD", "VariantSpellings", "Etymology",
#                                 "WClass", "Credits")

DataframeTotal <- subset(DataframeTotal, lemma %in% DadosdoDicionario$Headword)

# Insere os metadados nas sentenças
for(i in 1:length(DataframeTotal$sentence)){
  DataframeTotal$sentence[i] <- paste0(DataframeTotal$sentence[i], " (",
                                       CorpusMetadata$Author[CorpusMetadata$Filename == DataframeTotal$doc_id[i]],
                                       ", ", 
                                       CorpusMetadata$DateOfPublication[CorpusMetadata$Filename == DataframeTotal$doc_id[i]],
                                       ")")
}


# Desambiguações
DataframeTotal$sensenumber <- "1"

# "gema"
DataframeTotal$sensenumber[DataframeTotal$lemma=="gema" & 
                             DataframeTotal$sentence=="d. branco. b. gema. (VANDELLI, Domingos, 1788)"] <- "2"

# "bulbo"
DataframeTotal$sensenumber[DataframeTotal$token=="bulbo"
                           & DataframeTotal$doc_id=="AnatomiadeSantucci.txt"] <- "2"

# "disco"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="Quando o meio, ou disco da folha se approxima, ou se une ao mesmo caule. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="Quando as mesmas folhas lançaõ no disco inferior raizes como em algumas Algas. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="Por margem da folha entendem-se todos os lados exteriores, naõ fallando do disco. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="Sendo a margem cartilaginea, differente da substancia do disco, ou da superficie, Sedum. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="As veias da folha se contrahem de tal sorte, que comprimindo o disco, este sobresahe; isto he, eleva-se mais, que os mesmos lados da folha. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="Sobresahindo de entre as rugas para parte do disco, ou da superficies da folha, de figura conica pela parte superior, e concava pela inferior. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="A folha, que tem varias excavaçoens, ou o disco entre as veias está abaixado. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="Folha revestida e tuberculos algum tanto duros, espalhados pelo seu disco ou superficie. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="Havendo sedas de disco, ou na superficie da folha, que sejaõ algum tanto duras, rijas, asperas, e quebradiças. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="Estando o disco cheio de espinhos rijos, e picantes. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="A margem ou lado mais restricto obriga o disco da folha a ser concavo. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="Sendo o disco superior da folha mais elevado, ou convexo. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="O disco da folha sobe, e desce para a margem formando assim varios angulos, e muitas pregas. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="Subindo, e descendo o disco da folha convexamente até a margem. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="O disco da folha forma varias dobras obtusas, e alternadas. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="Folha monstruosa, pois he quando a margem da folha sahe maior do que o disco admitte, de maneira que a margem he as ondas. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="A folha he mais funda no disco, que nos lados. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="A superficie interior ou disco da folha elevada longitudinalmente á mesma maneira de quilha. (VANDELLI, Domingos, 1788)"] <- "2"
DataframeTotal$sensenumber[DataframeTotal$lemma=="disco" & 
                             DataframeTotal$sentence=="Tendo dous angulos longitudinaes, prominentes, oppostos, e o disco mais convexo. (VANDELLI, Domingos, 1788)"] <- "2"

# Script para incluir negrito nas sentenças

for(i in 1:length(DataframeTotal$sentence)){
  
  DataframeTotal$sentence[i]<- sub(DataframeTotal$token[i],
                                   paste0("<b>",
                                          DataframeTotal$token[i], 
                                          "</b>"),
                                   DataframeTotal$sentence[i])
}

# Correção do negrito
DataframeTotal$sentence[DataframeTotal$sentence=="d. He a parte, que sustenta, une a anthera (131), ou he o pè da anthera, pelo qual esta se une á planta; ás vezes faltaõ totalmente os filamentos, ou saõ taõ pequenos, que apenas apparecem, e entaõ contaõ-se as <b>antheras</b>. (VANDELLI, Domingos, 1788)"
                        & DataframeTotal$token_id==22] <-
  "d. He a parte, que sustenta, une a anthera (131), ou he o pè da <b>anthera</b>, pelo qual esta se une á planta; ás vezes faltaõ totalmente os filamentos, ou saõ taõ pequenos, que apenas apparecem, e entaõ contaõ-se as antheras. (VANDELLI, Domingos, 1788)"

DataframeTotal$sentence[DataframeTotal$sentence=="Duas antheras em hum só filamento; Mercurialis; tres antheras em hum só filamento, Fumaria; cinco em tres <b>filamentos</b> (VANDELLI, Domingos, 1788)"
                        & DataframeTotal$token_id==11] <-
  "Duas antheras em hum só filamento; Mercurialis; tres <b>antheras</b> em hum só filamento, Fumaria; cinco em tres filamentos (VANDELLI, Domingos, 1788)"

DataframeTotal$sentence[DataframeTotal$sentence=="Duas antheras em hum só filamento; Mercurialis; tres antheras em hum só filamento, Fumaria; cinco em tres <b>filamentos</b> (VANDELLI, Domingos, 1788)"
                        & DataframeTotal$token_id==15] <-
  "Duas antheras em hum só filamento; Mercurialis; tres antheras em hum só <b>filamento</b>, Fumaria; cinco em tres filamentos (VANDELLI, Domingos, 1788)"

DataframeTotal$sentence[DataframeTotal$sentence=="Abertura da <b>anthera</b> pela qual sahe, ou se lança o pollen da sua cavidade, ou loculo, a qual está em hum lado da anthera no Leucojum; em muitas plantas tem as antheras esta abertura no apice Solanum; outras desde a (VANDELLI, Domingos, 1788)"
                        & DataframeTotal$token_id==31] <-
  "Abertura da anthera pela qual sahe, ou se lança o pollen da sua cavidade, ou loculo, a qual está em hum lado da <b>anthera</b> no Leucojum; em muitas plantas tem as antheras esta abertura no apice Solanum; outras desde a (VANDELLI, Domingos, 1788)"

write.csv(DataframeTotal, file = "./data/DataframePrincipal.csv", fileEncoding = "UTF-8")

rm(i, lematizar, CriaDataframeDados, CorpusMetadata, DadosdoDicionario, DataframeTotal, LematizacaoDataFrame)


# Testes para o algoritmo que extrai dados do XML

library(XML)
library(xml2)
library(stylo)

CorpusTesteXML <- read_xml("tests/diciovandelli.xml", encoding = "UTF-8")
#corpusRoot <- xml_root(CorpusTesteXML)
terms <- xml_find_all(CorpusTesteXML, "//term")
tokenTerms <- xml_text(terms)
token_lemma <- xml_attr(terms, attr = "lemma")
token_orth <- xml_attr(terms, attr = "orth")
token_gram <- xml_attr(terms, attr = "msd")
token_senseNumber <- xml_attr(terms, attr = "senseNumber")

token_sentence <- NULL
author <- NULL
date <- NULL
for(i in 1:length(terms)){
  token_sentence[i] <- as.character(xml_find_first(terms[i],
                                                 xpath = "./ancestor::s"))
  token_sentence[i] <- delete.markup(token_sentence[i], markup.type = "xml")
  
  author[i] <- as.character(xml_find_first(terms[i],
                                           xpath = "string(/text/@author)"))
  date[i] <- as.character(xml_find_first(terms[i],
                                         xpath = "string(/text/@date)"))
  
  token_sentence[i] <- paste0(token_sentence[i], " (", author[i],
                              ", ", date[i], ")")
}

DataFrameTesteXML <- data.frame(
  token = tokenTerms,
  lemma = token_lemma,
  orth = token_orth,
  gram = token_gram,
  sensenumber = token_senseNumber,
  sentence = token_sentence
)

for(x in 1:length(DataFrameTesteXML$lemma)){
  if(is.na(DataFrameTesteXML$lemma[x])){
    DataFrameTesteXML$lemma[x] <- DataFrameTesteXML$token[x]
  }
  if(is.na(DataFrameTesteXML$orth[x])){
    DataFrameTesteXML$orth[x] <- DataFrameTesteXML$token[x]
  }
  if(is.na(DataFrameTesteXML$sensenumber[x])){
    DataFrameTesteXML$sensenumber[x] <- "1"
  }
}