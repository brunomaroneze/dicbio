library(shiny)
library(shinythemes)
library(tidyverse)
library(DT)
#library(data.table)
#library(collapsibleTree)
library(markdown)
library(stringr)
library(slickR) #Verificar se vai funcionar no servidor da USP


# Lê a base de dados do dicionário
data <- read.csv("./data/DadosDoDicionario.csv", encoding = "UTF-8")

# Lê o arquivo com as definições
definitions <-
  read.csv("./data/definitions.csv", encoding = "UTF-8")

# Lê o córpus etiquetado
TokTextDF <-
  read.csv("./data/DataframePrincipal.csv", encoding = "UTF-8")

# Cria uma função que retorna os contextos de uma palavra consultada, com a
# palavra negritada, e formata para mostrar; os parâmetros são a
# palavra-entrada e o número da acepção
Contextos <- function(InputConsulta, SenseNumber) {
  ContextosTexto <-
    as.list(TokTextDF$sentence[TokTextDF$Headword == InputConsulta &
                                 TokTextDF$sensenumber == SenseNumber])
  ContextosTextoFormatados <- NULL
  for (a in 1:length(ContextosTexto)) {
    ContextosTextoFormatados[a] <-
      paste0(a, " - ", ContextosTexto[a], "<br><br>")
    
  }
  ContextosTextoFormatados <- as.list(ContextosTextoFormatados)
  return(ContextosTextoFormatados)
}

# Acrescenta a coluna das variantes gráficas a partir do dataframe


for (n in 1:length(data$Headword)) {
  data$VariantSpellings[n] <- paste(sort(unique
                                         (TokTextDF$variants
                                           [tolower(TokTextDF$Headword) == tolower(data$Headword)[n]])),
                                    collapse = ", ")
  if (data$VariantSpellings[n] == data$Headword[n]) {
    data$VariantSpellings[n] <- NA
  }
}

# Cria uma lista com todas as variantes e lemas, a ser usada
# na versão futura para incluir a pesquisa com variantes
# listatotal <- sort(unique(c(TokTextDF$token,
#                             TokTextDF$orth,
#                             TokTextDF$Headword, data$Headword)))


ui <- fluidPage(
  tags$body(HTML("<body data-spy = 'scroll' data-target = '.navbar' 
    data-offset = '20'>")),
  includeCSS("www/styles.css"),
  navbarPage(
    id = "Dict",
    title = div(img(src="logo.png", height="40px", width="40px"), 
               HTML("Dicionário Histórico de Termos da Biologia")),

    windowTitle = "Dicionário Histórico de Termos da Biologia",
    collapsible = TRUE,
    inverse = FALSE,
    theme = shinytheme("readable"),
    tabPanel(
      id = "Home",
      "Home",
      fluid = TRUE,
      fluidRow(
        column(
          width = 4,
          offset = 1,
          htmlOutput("ProjectIntro")
        ),
        column(
          width = 6,
          offset = 1,

# Estas duas linhas seguintes são da versão antiga, caso o slideshow
# não funcione no servidor da USP
#          img(src = "VandelliTabXV.png", height = "500px"),
#          HTML("Tabela XV - Vandelli - <i>Diccionario de Termos Technicos de Historia Natural</i> (1788)"),
          
# Esta linha faz o slideshow, mas talveznão seja compatível com o servidor da USP
          slickROutput("slickr", height ="auto", width = "auto"),
          ##
          tags$br(),
          HTML(
           # "<a href=\"https://creativecommons.org/licenses/by-nc-sa/4.0/\"><img src=\"creativecommons.png\" height=\"31px\"></a>",
            "<p>Apoio:</p>",
            "<a href=\"https://www.gov.br/cnpq/pt-br\"><img src=\"cnpq.png\" height=\"40px\"></a>",
            "<a href=\"https://portal.ufgd.edu.br\"><img src=\"ufgd.png\" height=\"70px\"></a>"
          ),
          tags$br(),
          HTML(
            "<p style='font-size:10px'>O <b>Dicionário Histórico de Termos da Biologia</b>
                               está licenciado sob a <a href=\"https://creativecommons.org/licenses/by-nc-sa/4.0/\">Licença Creative Commons Attribution-NonCommercial-ShareAlike 4.0
                               International</a></p>"
          ),
          HTML(
            "<p style='font-size:10px'>The <b>Historical Dictionary of Biology Terms</b>
                               is licenced under a <a href=\"https://creativecommons.org/licenses/by-nc-sa/4.0/\">Creative Commons Attribution-NonCommercial-ShareAlike 4.0
                               International Licence</a></p>"
          )
        )
      )
    ),
    
    tabPanel(
      id = "Portuguese Search",
      "Consulta",
      fluid = TRUE,
      
      sidebarLayout(
        sidebarPanel(
          width = 3,
          #                                                 selectInput(inputId = "headword",
          #                                                           label = "Digite a entrada",
          #                                                           choices = listatotal,
          #                                                           selected = NULL,
          #                                                           multiple = FALSE,
          #                                                           selectize = TRUE),
          
          selectInput(
            inputId = "headword",
            list(label = "Selecione uma entrada "),
            choices = c(sort(as.character(data$Headword))),
#            selected = "angulado",
            multiple = FALSE,
            size = 10,
            selectize = FALSE
          ),
        ),
        mainPanel(width = 9,
                  fluidRow(
                    column(
                      7,
                      htmlOutput("Entry"),
                      tags$hr(),
                      #htmlOutput("Definition"),
                      #tags$hr(),
                      htmlOutput("Etymo"),
                      tags$hr(),
                      htmlOutput("FirstAttestation"),
                      tags$hr(),
                      htmlOutput("HowToCite"),
                      tags$br()
                    ),
                    column(
                      5
                      ,
                      HTML("<b>Definição(ões):</b><br>")
                      ,
                      htmlOutput("Definition"),
                    )
                  ))
        
      )
    ),

    tabPanel(
      id = "Documentation",
      "Documentação",
      fluid = TRUE,
      fluidRow(
        column(
          width = 5,
          offset = 1,
          htmlOutput("ProjectDocumentation"),
        ),
        column(
          width = 5,
          offset = 1,
          tags$nav(
            class = "navbar",
            tags$ul(
              class = "nav nav-pills nav-stacked",
              tags$li(
                class = "nav-item",
                tags$a(class = "nav-link", href = "#prefacio", "Prefácio")),
              tags$li(
                class = "nav-item",
                tags$a(class = "nav-link", href = "#objetivos", "Objetivos")),
              tags$li(
                class = "nav-item",
                tags$a(class = "nav-link", href = "#corpus", "Córpus")),
              tags$li(
                class = "nav-item",
                tags$a(class = "nav-link", href = "#critlex", "Critérios Lexicográficos")),
              tags$li(
                class = "nav-item",
                tags$a(class = "nav-link", href = "#publicacoes", "Publicações")),
              tags$li(
                class = "nav-item",
                tags$a(class = "nav-link", href = "#equipe", "Equipe")),
              tags$li(
                class = "nav-item",
                tags$a(class = "nav-link", href = "#agradecimentos", "Agradecimentos")),
              tags$li(
                class = "nav-item",
                tags$a(class = "nav-link", href = "#contato", "Contato")),
            ))

        )
      )),
# nova seção
tabPanel(
  id = "Curiosities",
  "Curiosidades",
  fluid = TRUE,
  fluidRow(
    column(
      width = 5,
      offset = 1,
      htmlOutput("Curiosities"),
    ),
              column(
          width = 5,
          offset = 1,
          tags$nav(
            class = "navbar",
            tags$ul(
              class = "nav nav-pills nav-stacked",
              tags$li(
                class = "nav-item",
                tags$a(class = "nav-link", href = "#bioSantucci", "Biografia de Santucci")),
              tags$li(
                class = "nav-item",
                tags$a(class = "nav-link", href = "#BroteroBananeira", "Brotero e a Bananeira")),
            ))

        )
    )))
# ------------------

    
  )
)



server <- function(input, output, session) {
  # Descobri que não precisa desse updateSelectizeInput porque o input não vai ficar mudando
  #  updateSelectizeInput(session, "headword", choices=c(sort(as.character(data$Headword))),
  #                       selected="angulado")
  
  
  EntryData <- reactive({
    # O if é para localizar as entradas quando a palavra digitada for variante
    
    if (input$headword %in% data$Headword) {
      EntryData <- as.list(data[data$Headword == input$headword, ])
      EntryData
      
    } else if (input$headword %in% TokTextDF$token) {
      RealHeadword <- TokTextDF$Headword[TokTextDF$token
                                      == input$headword]
      EntryData <- as.list(data[data$Headword == RealHeadword, ])
      EntryData
      
    } else if (input$headword %in% TokTextDF$orth) {
      RealHeadword <- TokTextDF$Headword[TokTextDF$orth
                                      == input$headword]
      EntryData <- as.list(data[data$Headword == RealHeadword, ])
      EntryData
      
    }
  })
  
  
  output$ProjectIntro <- renderText({
    includeMarkdown("ProjectIntro.Rmd")
  })
  
  output$ProjectDocumentation <- renderText({
    includeMarkdown("Documentation.Rmd")
  })
  
  output$Curiosities <- renderText({
    includeMarkdown("Curiosities.Rmd")
  })
  
  
  #rd 09.02.2022
  output$slickr <- renderSlickR({
    imgs <- list.files("./www/slideshow", pattern=".jpg", full.names = TRUE)
    slick <- slickR(imgs)
    slick + settings(autoplay = TRUE, autoplaySpeed = 3000)
  })
  
  
  output$Entry <- renderText({
    paste0(
      "<font size='+2'><b>",
      EntryData()$Headword,
      "</font></b><br>"
      ,
      EntryData()$WClass
    )
    
    
  })
  
  output$Definition <- renderText({
    Definition <- NULL
    for (c in 1:sum(definitions$Headword == EntryData()$Headword)) {
      Definicao <-
        definitions$Definition[definitions$Headword == EntryData()$Headword][c]
      Definition[c] <- paste0(
        c,
        ". ",
        Definicao,
        "<div style='height: 30vh; overflow-y: auto;
                              font-size:.7em;'>",
        paste(Contextos(EntryData()$Headword, c), collapse = ""),
        "</div><br>"
      )
    }
    
    Definition
    
  })
  
  
  output$Etymo <- renderText({
    paste("<b>Discussão histórico-etimológica:</b>",
          EntryData()$Etymology)
  })
  
  
  output$FirstAttestation <- renderText({
    FirstAttestationDate <- EntryData()$FirstAttestationDate
    FirstAttestationExampleMD <-
      EntryData()$FirstAttestationExampleMD
    
    VariantSpellings <- EntryData()$VariantSpellings
    if (!is.na(VariantSpellings)) {
      paste0(
        "<b>Variantes e formas flexionadas: </b>",
        VariantSpellings, "<hr>",
        "<font color='steelblue'>",
        EntryData()$Headword,
        "</font> é atestado em <b>",
        FirstAttestationDate,
        "</b>: ",
        FirstAttestationExampleMD
      )
    } else{
      paste0(
        "<font color='steelblue'>",
        EntryData()$Headword,
        "</font> é atestado em <b>",
        FirstAttestationDate,
        "</b>: ",
        FirstAttestationExampleMD
      )
      
    }
  })
  
  output$HowToCite <- renderText({
    EntryAuthors <- EntryData()$Credits
    
    if (str_detect(EntryAuthors, ";")) {
      EntryAuthorsSplit <- strsplit(EntryAuthors, "; ")
      EntryAuthor1 <- EntryAuthorsSplit[[1]][1]
      EntryAuthor2 <- EntryAuthorsSplit[[1]][2]
      Author1LastName <- toupper(word(EntryAuthor1,-1))
      Author1FirstName <- word(EntryAuthor1, 1,-2)
      Author2LastName <- toupper(word(EntryAuthor2,-1))
      Author2FirstName <- word(EntryAuthor2, 1,-2)
      AuthorInReference <-
        paste0(
          Author1LastName,
          ", ",
          Author1FirstName,
          "; ",
          Author2LastName,
          ", ",
          Author2FirstName
        )
      
    } else {
      AuthorLastName <- toupper(word(EntryAuthors,-1))
      AuthorFirstName <- word(EntryAuthors, 1,-2)
      AuthorInReference <-
        paste0(AuthorLastName, ", ", AuthorFirstName)
    }
    
    DateOfCreation <- EntryData()$DateOfCreation
    DateOfUpdate <- EntryData()$DateOfUpdate
    
    if (DateOfCreation == DateOfUpdate) {
      paste0(
        "<p style='font-size: .7em;'><br>Autores(as) do verbete: ",
        EntryAuthors,
        "</p><br><p style='font-size: .7em;'>Este verbete foi incluído em ",
        DateOfCreation,
        "</p><br><p style='font-size: .7em;'><b>Como citar este verbete:</b><br>",
        AuthorInReference,
        ". ",
        str_to_title(EntryData()$Headword),
        ". In: MARONEZE, Bruno (coord.)
           <b>Dicionário Histórico de Termos da Biologia</b>. 2022. Disponível em:
           https://dicbio.fflch.usp.br/.
           Acesso em: ",
        format(Sys.Date(), "%d %b. %Y"),
        ".</p><hr>"
      )
      
    } else {
      paste0(
        "<p style='font-size: .7em;'><br>Autores(as) do verbete: ",
        EntryAuthors,
        "</p><br><p style='font-size: .7em;'>Este verbete foi incluído em ",
        DateOfCreation,
        " e atualizado em ",
        DateOfUpdate,
        "</p><br>",
        "<p style='font-size: .7em;'><b>Como citar este verbete:</b><br>",
        AuthorInReference,
        ". ",
        str_to_title(EntryData()$Headword),
        ". In: MARONEZE, Bruno (coord.)
           <b>Dicionário Histórico de Termos da Biologia</b>. 2022. Disponível em:
           https://dicbio.fflch.usp.br/.
           Acesso em: ",
        format(Sys.Date(), "%d %b. %Y"),
        ".</p><hr>"
      )
    }
  })
  
  
  #  output$NumDeContextos <- renderText({
  
  #  Criar trecho para incluir variantes gráficas
  
  # if(existe variante gráfica){
  
  #     paste0("O termo <b>", input$headword, "</b> também é grafado ", "Y...", "(ver contextos abaixo)")
  
  # } else {
  
  # entra o outro "if" dos contextos que já existe aí embaixo
  
  # }
  
  
  
  #  })
  
  
  
}

shinyApp(ui = ui, server = server)
