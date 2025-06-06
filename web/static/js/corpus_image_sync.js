// static/js/corpus_image_sync.js
document.addEventListener('DOMContentLoaded', function () {
    const djangoVarsElement = document.getElementById('django-vars');
    if (!djangoVarsElement) {
        // console.warn("Elemento django-vars não encontrado.");
        return;
    }
    const djangoData = JSON.parse(djangoVarsElement.textContent);
    const obraAtualExiste = djangoData.obraAtualExiste;

    const textoContainer = document.getElementById('texto-obra-container');
    const imgDisplay = document.getElementById('imagem-pagina-ativa');
    const legendaDisplay = document.getElementById('legenda-pagina-ativa');

    // Só executa o resto se uma obra estiver carregada e os elementos existirem
    if (!obraAtualExiste || !textoContainer || !imgDisplay || !legendaDisplay) {
        // console.log("Obra não carregada ou elementos de sincronia de imagem não encontrados.");
        if (imgDisplay) imgDisplay.style.display = 'none'; // Esconde a imagem se não houver obra
        if (legendaDisplay) legendaDisplay.textContent = '';
        return;
    } else {
        if (imgDisplay) imgDisplay.style.display = 'block';
    }

    const marcadores = textoContainer.querySelectorAll('.marcador-pagina');
    if (marcadores.length === 0) {
        // console.log("Nenhum marcador de página encontrado no texto.");
        legendaDisplay.textContent = 'Nenhum marcador de página nesta obra.';
        imgDisplay.src = ''; // Limpa imagem se não houver marcadores
        imgDisplay.alt = 'Nenhum marcador de página';
        return;
    }

    let activePageMarker = null; // Guarda o marcador atualmente ativo

    function updateImageAndCaption(marker) {
        if (marker) {
            const imageUrl = marker.dataset.facs;
            const pageNum = marker.dataset.paginaNumero;

            if (imageUrl) {
                if (imgDisplay.src !== imageUrl) { // Atualiza só se a URL mudou
                    imgDisplay.src = imageUrl;
                }
                imgDisplay.alt = `Imagem da página ${pageNum || 'desconhecida'}`;
            } else {
                imgDisplay.src = ''; // Ou um placeholder para "imagem não disponível"
                imgDisplay.alt = `Imagem não disponível para a página ${pageNum || 'desconhecida'}`;
            }
            legendaDisplay.textContent = `Página: ${pageNum || '?'}`;
            activePageMarker = marker; // Atualiza o marcador ativo
        }
    }

    // Tenta definir uma imagem inicial (o primeiro marcador com 'data-facs')
    const primeiroMarcadorComImagem = Array.from(marcadores).find(m => m.dataset.facs);
    if (primeiroMarcadorComImagem) {
        updateImageAndCaption(primeiroMarcadorComImagem);
    } else if (marcadores.length > 0) {
        // Se há marcadores, mas nenhum tem imagem, pega o primeiro para a legenda
        updateImageAndCaption(marcadores[0]);
    }


    // IntersectionObserver para detectar qual marcador está visível
    const observerOptions = {
        root: textoContainer, // A área de scroll que observamos
        rootMargin: "-30% 0px -70% 0px", // Tenta ativar quando o marcador está no terço superior da área visível do textoContainer
        threshold: 0 // Qualquer parte visível do marcador dispara
    };
    
    // Guarda o último marcador que entrou na "zona ativa"
    let candidateMarker = activePageMarker; 

    const intersectionCallback = (entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Se um novo marcador entra na zona ativa e é diferente do atual
                if (entry.target !== activePageMarker) { 
                    candidateMarker = entry.target; // Atualiza o candidato
                    updateImageAndCaption(candidateMarker);
                }
            }
        });
    };

    const observer = new IntersectionObserver(intersectionCallback, observerOptions);
    marcadores.forEach(marcador => observer.observe(marcador));

    // Opcional: Adicionar clique nos marcadores para navegação e atualização
    marcadores.forEach(marcador => {
        marcador.addEventListener('click', (event) => {
            event.preventDefault(); // Previne comportamento padrão se o marcador for um link
            
            // Rolar o marcador para uma posição visível (ex: topo do container)
            const containerRect = textoContainer.getBoundingClientRect();
            const markerRect = marcador.getBoundingClientRect();
            // Calcula a posição do topo do marcador relativa ao topo do container de scroll
            const scrollTopOffset = markerRect.top - containerRect.top + textoContainer.scrollTop;
            
            textoContainer.scrollTo({
                top: scrollTopOffset - 20, // -20 para dar uma pequena margem acima
                behavior: 'smooth'
            });

            updateImageAndCaption(marcador);
        });
    });

});