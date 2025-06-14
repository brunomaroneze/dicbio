// web/corpus_digital/static/corpus_digital/js/corpus_image_sync.js

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
    // Novas referências aos botões de navegação
    const prevPageBtn = document.getElementById('prev-page-btn');
    const nextPageBtn = document.getElementById('next-page-btn');

    // Só executa o resto se uma obra estiver carregada e os elementos essenciais existirem
    if (!obraAtualExiste || !textoContainer || !imgDisplay || !legendaDisplay) {
        // console.log("Obra não carregada ou elementos de sincronia de imagem não encontrados.");
        if (imgDisplay) imgDisplay.style.display = 'none'; // Esconde a imagem se não houver obra
        if (legendaDisplay) legendaDisplay.textContent = '';
        // Desabilita e esconde os botões se não houver obra para exibir
        if (prevPageBtn) { prevPageBtn.style.display = 'none'; prevPageBtn.disabled = true; }
        if (nextPageBtn) { nextPageBtn.style.display = 'none'; nextPageBtn.disabled = true; }
        return;
    } else {
        if (imgDisplay) imgDisplay.style.display = 'block';
        if (prevPageBtn) prevPageBtn.style.display = 'inline-block'; // Garante que estejam visíveis
        if (nextPageBtn) nextPageBtn.style.display = 'inline-block';
    }

    const marcadores = Array.from(textoContainer.querySelectorAll('.marcador-pagina')); // Converte para Array para usar .indexOf
    if (marcadores.length === 0) {
        // console.log("Nenhum marcador de página encontrado no texto.");
        legendaDisplay.textContent = 'Nenhum marcador de página nesta obra.';
        imgDisplay.src = '';
        imgDisplay.alt = 'Nenhum marcador de página';
        // Desabilita os botões se não houver marcadores
        if (prevPageBtn) prevPageBtn.disabled = true;
        if (nextPageBtn) nextPageBtn.disabled = true;
        return;
    }

    let activePageMarker = null; // Guarda o marcador DOM atualmente ativo
    let currentPageIndex = 0;   // Guarda o índice da página ativa na lista `marcadores`

    // Função para atualizar o estado dos botões de navegação
    function updateNavigationButtons() {
        if (prevPageBtn) prevPageBtn.disabled = currentPageIndex <= 0;
        if (nextPageBtn) nextPageBtn.disabled = currentPageIndex >= marcadores.length - 1;
    }

    // Função que atualiza a imagem e a legenda, e agora também o índice e os botões
    function updateImageAndCaption(marker) {
        if (marker) {
            const imageUrl = marker.dataset.facs;
            const pageNum = marker.dataset.paginaNumero;

            if (imageUrl) {
                if (imgDisplay.src !== imageUrl) {
                    imgDisplay.src = imageUrl;
                }
                imgDisplay.alt = `Imagem da página ${pageNum || 'desconhecida'}`;
            } else {
                imgDisplay.src = '';
                imgDisplay.alt = `Imagem não disponível para a página ${pageNum || 'desconhecida'}`;
            }
            legendaDisplay.textContent = `Página: ${pageNum || '?'}`;
            activePageMarker = marker; // Atualiza o marcador DOM ativo

            // Atualiza o índice da página atual e o estado dos botões
            currentPageIndex = marcadores.indexOf(activePageMarker);
            updateNavigationButtons();
        }
    }

    // Tenta definir uma imagem inicial (o primeiro marcador com 'data-facs')
    const primeiroMarcadorComImagem = marcadores.find(m => m.dataset.facs);
    if (primeiroMarcadorComImagem) {
        updateImageAndCaption(primeiroMarcadorComImagem);
    } else if (marcadores.length > 0) {
        updateImageAndCaption(marcadores[0]); // Pega o primeiro para a legenda, mesmo sem imagem
    }


    // IntersectionObserver para detectar qual marcador está visível
    const observerOptions = {
        root: textoContainer,
        rootMargin: "-30% 0px -70% 0px", // A área de "ativação"
        threshold: 0
    };
    
    const intersectionCallback = (entries) => {
        let bestCandidate = activePageMarker;
        let bestCandidateRect = activePageMarker ? activePageMarker.getBoundingClientRect() : null;
        let containerRect = textoContainer.getBoundingClientRect();

        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Tenta encontrar o marcador intersectando que está mais próximo do topo da "zona ativa"
                let currentEntryRect = entry.target.getBoundingClientRect();
                if (!bestCandidate || currentEntryRect.top < bestCandidateRect.top) {
                    bestCandidate = entry.target;
                    bestCandidateRect = currentEntryRect;
                }
            }
        });

        // Se o melhor candidato encontrado não é o que está ativo, atualiza
        if (bestCandidate && bestCandidate !== activePageMarker) {
            updateImageAndCaption(bestCandidate);
        }
    };

    const observer = new IntersectionObserver(intersectionCallback, observerOptions);
    marcadores.forEach(marcador => observer.observe(marcador));

    // Opcional: Adicionar clique nos marcadores para navegação e atualização
    marcadores.forEach(marcador => {
        marcador.addEventListener('click', (event) => {
            event.preventDefault();
            
            const containerRect = textoContainer.getBoundingClientRect();
            const markerRect = marcador.getBoundingClientRect();
            const scrollTopOffset = markerRect.top - containerRect.top + textoContainer.scrollTop;
            
            textoContainer.scrollTo({
                top: scrollTopOffset - (containerRect.height * 0.3), // Rola para o terço superior do container
                behavior: 'smooth'
            });

            updateImageAndCaption(marcador); // Garante que a imagem e botões são atualizados
        });
    });

    // --- Lógica dos Botões de Navegação Anterior/Próxima ---
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => {
            if (currentPageIndex > 0) {
                const prevMarker = marcadores[currentPageIndex - 1];
                // Rola para o marcador anterior
                textoContainer.scrollTo({
                    top: prevMarker.offsetTop - textoContainer.offsetTop - (textoContainer.offsetHeight * 0.3), // Rola para o terço superior
                    behavior: 'smooth'
                });
                updateImageAndCaption(prevMarker); // Atualiza imagem e estado dos botões
            }
        });
    }

    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', () => {
            if (currentPageIndex < marcadores.length - 1) {
                const nextMarker = marcadores[currentPageIndex + 1];
                // Rola para o próximo marcador
                textoContainer.scrollTo({
                    top: nextMarker.offsetTop - textoContainer.offsetTop - (textoContainer.offsetHeight * 0.3), // Rola para o terço superior
                    behavior: 'smooth'
                });
                updateImageAndCaption(nextMarker); // Atualiza imagem e estado dos botões
            }
        });
    }

    // Inicializa o estado dos botões ao carregar a página
    updateNavigationButtons(); 

});