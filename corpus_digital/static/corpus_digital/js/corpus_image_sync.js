// corpus_digital/static/corpus_digital/js/corpus_image_sync.js

document.addEventListener('DOMContentLoaded', function () {
    const djangoVarsElement = document.getElementById('django-vars');
    if (!djangoVarsElement) return;

    const djangoData = JSON.parse(djangoVarsElement.textContent);
    const obraAtualExiste = djangoData.obraAtualExiste;

    const textoContainer = document.getElementById('texto-obra-container');
    const imgDisplay = document.getElementById('imagem-pagina-ativa');
    const legendaDisplay = document.getElementById('legenda-pagina-ativa');
    const prevPageBtn = document.getElementById('prev-page-btn');
    const nextPageBtn = document.getElementById('next-page-btn');

    // Se não houver obra ou os elementos essenciais não existirem, encerra.
    if (!obraAtualExiste || !textoContainer || !imgDisplay || !legendaDisplay) {
        if (imgDisplay) imgDisplay.style.display = 'none';
        if (legendaDisplay) legendaDisplay.textContent = '';
        if (prevPageBtn) { prevPageBtn.style.display = 'none'; prevPageBtn.disabled = true; }
        if (nextPageBtn) { nextPageBtn.style.display = 'none'; nextPageBtn.disabled = true; }
        return;
    }

    // Garante que a imagem e os botões estejam visíveis se houver uma obra
    imgDisplay.style.display = 'block';
    if (prevPageBtn) prevPageBtn.style.display = 'inline-block';
    if (nextPageBtn) nextPageBtn.style.display = 'inline-block';

    const marcadores = Array.from(textoContainer.querySelectorAll('.marcador-pagina'));
    if (marcadores.length === 0) {
        legendaDisplay.textContent = 'Nenhum marcador de página nesta obra.';
        if (prevPageBtn) prevPageBtn.disabled = true;
        if (nextPageBtn) nextPageBtn.disabled = true;
        return;
    }

    let activePageMarker = null; // Guarda o elemento DOM do marcador atualmente ativo

    // Função que rola o texto para um marcador específico
    function scrollToMarker(marker) {
        if (!marker) return;
        // Calcula a posição do marcador relativa ao topo do container de texto e centraliza um pouco
        const scrollOffset = marker.offsetTop - textoContainer.offsetTop - (textoContainer.clientHeight * 0.3);
        textoContainer.scrollTo({
            top: scrollOffset,
            behavior: 'smooth'
        });
    }

    // Função única que atualiza a imagem, legenda, e o estado dos botões.
    function updateActivePage(markerToActivate) {
        if (markerToActivate && markerToActivate !== activePageMarker) {
            activePageMarker = markerToActivate;
            const imageUrl = activePageMarker.dataset.facs;
            const pageNum = activePageMarker.dataset.paginaNumero;
            const currentIndex = marcadores.indexOf(activePageMarker);

            if (imageUrl) {
                if (imgDisplay.src !== imageUrl) {
                    imgDisplay.src = imageUrl;
                }
                imgDisplay.alt = `Imagem da página ${pageNum || 'desconhecida'}`;
            } else {
                imgDisplay.src = ''; // Limpa a imagem se não houver URL
                imgDisplay.alt = `Imagem não disponível para a página ${pageNum || 'desconhecida'}`;
            }
            legendaDisplay.textContent = `Página: ${pageNum || '?'}`;
            
            // Atualiza o estado dos botões
            if (prevPageBtn) prevPageBtn.disabled = (currentIndex <= 0);
            if (nextPageBtn) nextPageBtn.disabled = (currentIndex >= marcadores.length - 1);
        }
    }


    // --- LÓGICA DO INTERSECTION OBSERVER (SIMPLIFICADA E CORRIGIDA) ---
    const observerOptions = {
        root: textoContainer, // O elemento de rolagem é o container de texto
        rootMargin: "-40% 0px -60% 0px", // Uma linha imaginária a 40% do topo
        threshold: 0
    };
    
    const intersectionCallback = (entries) => {
        // Encontra o último marcador que está INTERSECTANDO (visível na zona de observação)
        const visibleMarkers = entries.filter(entry => entry.isIntersecting);
        if (visibleMarkers.length > 0) {
            // Pega o último da lista, que geralmente é o mais relevante ao rolar para baixo
            const markerToActivate = visibleMarkers[visibleMarkers.length - 1].target;
            updateActivePage(markerToActivate);
        }
    };
    const observer = new IntersectionObserver(intersectionCallback, observerOptions);
    marcadores.forEach(marcador => observer.observe(marcador));


    // --- LÓGICA DOS BOTÕES ---
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => {
            const currentIndex = marcadores.indexOf(activePageMarker);
            if (currentIndex > 0) {
                const prevMarker = marcadores[currentIndex - 1];
                scrollToMarker(prevMarker);
                // A atualização da imagem será feita pelo IntersectionObserver ao rolar,
                // mas podemos chamar diretamente para uma resposta mais rápida.
                updateActivePage(prevMarker);
            }
        });
    }

    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', () => {
            const currentIndex = marcadores.indexOf(activePageMarker);
            if (currentIndex < marcadores.length - 1) {
                const nextMarker = marcadores[currentIndex + 1];
                scrollToMarker(nextMarker);
                updateActivePage(nextMarker);
            }
        });
    }


    // --- LÓGICA DE INICIALIZAÇÃO ---
    function initializeView() {
        const initialHash = window.location.hash;
        let initialMarker = null;

        if (initialHash) {
            const targetId = initialHash.substring(1);
            initialMarker = document.getElementById(targetId);
        }
        
        // Se não achou marcador pela âncora, pega o primeiro marcador com imagem, ou apenas o primeiro marcador
        if (!initialMarker || !marcadores.includes(initialMarker)) {
            initialMarker = marcadores.find(m => m.dataset.facs) || marcadores[0];
        }

        if (initialMarker) {
            updateActivePage(initialMarker);
            // Se a página foi carregada com âncora, o navegador já tenta rolar.
            // Vamos dar um empurrãozinho para garantir a posição correta.
            if (initialHash) {
                setTimeout(() => scrollToMarker(initialMarker), 100);
            }
        } else {
             // Se não há marcadores, desabilita os botões
             if (prevPageBtn) prevPageBtn.disabled = true;
             if (nextPageBtn) nextPageBtn.disabled = true;
        }
    }
    initializeView();
});