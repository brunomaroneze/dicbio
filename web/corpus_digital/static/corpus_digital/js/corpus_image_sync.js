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
    const prevPageBtn = document.getElementById('prev-page-btn');
    const nextPageBtn = document.getElementById('next-page-btn');

    // Só executa o resto se uma obra estiver carregada e os elementos essenciais existirem
    if (!obraAtualExiste || !textoContainer || !imgDisplay || !legendaDisplay) {
        // console.log("Obra não carregada ou elementos de sincronia de imagem não encontrados.");
        if (imgDisplay) imgDisplay.style.display = 'none';
        if (legendaDisplay) legendaDisplay.textContent = '';
        if (prevPageBtn) { prevPageBtn.style.display = 'none'; prevPageBtn.disabled = true; }
        if (nextPageBtn) { nextPageBtn.style.display = 'none'; nextPageBtn.disabled = true; }
        return;
    } else {
        if (imgDisplay) imgDisplay.style.display = 'block';
        if (prevPageBtn) prevPageBtn.style.display = 'inline-block';
        if (nextPageBtn) nextPageBtn.style.display = 'inline-block';
    }

    const marcadores = Array.from(textoContainer.querySelectorAll('.marcador-pagina'));
    if (marcadores.length === 0) {
        // console.log("Nenhum marcador de página encontrado no texto.");
        legendaDisplay.textContent = 'Nenhum marcador de página nesta obra.';
        imgDisplay.src = '';
        imgDisplay.alt = 'Nenhum marcador de página';
        if (prevPageBtn) prevPageBtn.disabled = true;
        if (nextPageBtn) nextPageBtn.disabled = true;
        return;
    }

    let activePageMarker = null;
    let currentPageIndex = 0;

    function updateNavigationButtons() {
        if (prevPageBtn) prevPageBtn.disabled = currentPageIndex <= 0;
        if (nextPageBtn) nextPageBtn.disabled = currentPageIndex >= marcadores.length - 1;
    }

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
            activePageMarker = marker;

            currentPageIndex = marcadores.indexOf(activePageMarker);
            updateNavigationButtons();
        }
    }

    // Tenta definir uma imagem inicial (o primeiro marcador com 'data-facs')
    const primeiroMarcadorComImagem = marcadores.find(m => m.dataset.facs);
    if (primeiroMarcadorComImagem) {
        updateImageAndCaption(primeiroMarcadorComImagem);
    } else if (marcadores.length > 0) {
        updateImageAndCaption(marcadores[0]);
    }

    // --- NOVO BLOCO: Lógica para URLs com âncora (#pagina_N) ---
    const initialHash = window.location.hash;
    if (initialHash) {
        const targetId = initialHash.substring(1); // Remove o '#'
        const targetMarker = document.getElementById(targetId);

        // Verifica se o elemento encontrado é um dos nossos marcadores de página
        if (targetMarker && marcadores.includes(targetMarker)) {
            updateImageAndCaption(targetMarker);

            // Rola para o marcador para garantir que ele esteja bem visível,
            // mesmo que o navegador já tenha rolado para a âncora.
            // Um pequeno atraso pode ajudar a sincronizar com a rolagem padrão do navegador.
            setTimeout(() => {
                const containerRect = textoContainer.getBoundingClientRect();
                const markerRect = targetMarker.getBoundingClientRect();
                const scrollTarget = markerRect.top - containerRect.top + textoContainer.scrollTop - (containerRect.height * 0.3);
                
                textoContainer.scrollTo({
                    top: scrollTarget,
                    behavior: 'smooth'
                });
            }, 100); // Pequeno atraso de 100ms
        }
    }
    // --- FIM DO NOVO BLOCO ---


    // IntersectionObserver para detectar qual marcador está visível
    const observerOptions = {
        root: textoContainer,
        rootMargin: "-30% 0px -70% 0px",
        threshold: 0
    };
    
    const intersectionCallback = (entries) => {
        let bestCandidate = activePageMarker;
        let bestCandidateRect = activePageMarker ? activePageMarker.getBoundingClientRect() : null;
        let containerRect = textoContainer.getBoundingClientRect();

        entries.forEach(entry => {
            if (entry.isIntersecting) {
                let currentEntryRect = entry.target.getBoundingClientRect();
                // Prioriza o marcador que está mais próximo do topo da zona ativa
                if (!bestCandidate || currentEntryRect.top < bestCandidateRect.top) {
                    bestCandidate = entry.target;
                    bestCandidateRect = currentEntryRect;
                }
            }
        });

        if (bestCandidate && bestCandidate !== activePageMarker) {
            updateImageAndCaption(bestCandidate);
        }
    };

    const observer = new IntersectionObserver(intersectionCallback, observerOptions);
    marcadores.forEach(marcador => observer.observe(marcador));

    // Opcional: Adicionar clique nos marcadores para navegação e atualização
    marcadores.forEach(marador => {
        marcador.addEventListener('click', (event) => {
            event.preventDefault();
            
            const containerRect = textoContainer.getBoundingClientRect();
            const markerRect = marcador.getBoundingClientRect();
            const scrollTopOffset = markerRect.top - containerRect.top + textoContainer.scrollTop;
            
            textoContainer.scrollTo({
                top: scrollTopOffset - (containerRect.height * 0.3),
                behavior: 'smooth'
            });

            updateImageAndCaption(marcador);
        });
    });

    // Lógica dos Botões de Navegação Anterior/Próxima
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => {
            if (currentPageIndex > 0) {
                const prevMarker = marcadores[currentPageIndex - 1];
                textoContainer.scrollTo({
                    top: prevMarker.offsetTop - textoContainer.offsetTop - (textoContainer.offsetHeight * 0.3),
                    behavior: 'smooth'
                });
                updateImageAndCaption(prevMarker);
            }
        });
    }

    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', () => {
            if (currentPageIndex < marcadores.length - 1) {
                const nextMarker = marcadores[currentPageIndex + 1];
                textoContainer.scrollTo({
                    top: nextMarker.offsetTop - textoContainer.offsetTop - (textoContainer.offsetHeight * 0.3),
                    behavior: 'smooth'
                });
                updateImageAndCaption(nextMarker);
            }
        });
    }

    // Inicializa o estado dos botões ao carregar a página
    // (updateImageAndCaption já faz isso na inicialização ou via hash)
    // Mas chamar aqui garante que o estado inicial seja definido mesmo se não houver marcadores com facs
    updateNavigationButtons(); 

});