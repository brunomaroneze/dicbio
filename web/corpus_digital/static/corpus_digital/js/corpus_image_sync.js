// web/corpus_digital/static/corpus_digital/js/corpus_image_sync.js

document.addEventListener('DOMContentLoaded', function () {
    const djangoVarsElement = document.getElementById('django-vars');
    if (!djangoVarsElement) {
        return;
    }
    const djangoData = JSON.parse(djangoVarsElement.textContent);
    const obraAtualExiste = djangoData.obraAtualExiste;

    const textoContainer = document.getElementById('texto-obra-container');
    const imgDisplay = document.getElementById('imagem-pagina-ativa');
    const legendaDisplay = document.getElementById('legenda-pagina-ativa');
    const prevPageBtn = document.getElementById('prev-page-btn');
    const nextPageBtn = document.getElementById('next-page-btn');

    if (!obraAtualExiste || !textoContainer || !imgDisplay || !legendaDisplay) {
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
        legendaDisplay.textContent = 'Nenhum marcador de página nesta obra.';
        imgDisplay.src = '';
        imgDisplay.alt = 'Nenhum marcador de página';
        if (prevPageBtn) prevPageBtn.disabled = true;
        if (nextPageBtn) nextPageBtn.disabled = true;
        return;
    }

    let activePageMarker = null; // Guarda o elemento DOM do marcador atualmente ativo
    let currentPageIndex = -1;   // Guarda o índice da página ativa na lista `marcadores`. Inicializa como -1.

    function updateNavigationButtons() {
        if (prevPageBtn) prevPageBtn.disabled = currentPageIndex <= 0;
        if (nextPageBtn) nextPageBtn.disabled = currentPageIndex >= marcadores.length - 1;
    }

    // Função que atualiza a imagem, legenda, e o estado dos botões de navegação.
    // Esta função é a única responsável por mudar activePageMarker e currentPageIndex.
    function updateImageAndCaption(markerToActivate) {
        if (markerToActivate && marcadores.includes(markerToActivate)) { // Garante que é um marcador válido
            activePageMarker = markerToActivate; // Atualiza o marcador DOM ativo
            currentPageIndex = marcadores.indexOf(activePageMarker); // Atualiza o índice

            const imageUrl = activePageMarker.dataset.facs;
            const pageNum = activePageMarker.dataset.paginaNumero;

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
            updateNavigationButtons(); // Atualiza o estado dos botões após a mudança de página
        }
    }

    // --- Lógica de Inicialização (carregamento inicial, link de âncora) ---
    // Tenta definir uma imagem inicial (o primeiro marcador com 'data-facs')
    const primeiroMarcadorComImagem = marcadores.find(m => m.dataset.facs);
    if (primeiroMarcadorComImagem) {
        updateImageAndCaption(primeiroMarcadorComImagem);
    } else if (marcadores.length > 0) {
        updateImageAndCaption(marcadores[0]); // Pega o primeiro para a legenda, mesmo sem imagem
    } else {
        updateNavigationButtons(); // Se não há marcadores, desabilita tudo
    }

    // Lógica para URLs com âncora (#pagina_N) - Esta parte é executada NO CARREGAMENTO DA PÁGINA
    const initialHash = window.location.hash;
    if (initialHash) {
        const targetId = initialHash.substring(1); // Remove o '#'
        const targetMarker = document.getElementById(targetId);

        if (targetMarker && marcadores.includes(targetMarker)) {
            // Se o targetMarker já tem um `data-facs` e é o `activePageMarker` inicial, não rola de novo.
            // A rolagem para a âncora é feita pelo navegador, então o JS apenas atualiza a imagem.
            updateImageAndCaption(targetMarker); 

            // Rola para o marcador para garantir que ele esteja bem visível no container de texto,
            // mesmo que o navegador já tenha rolado para a âncora.
            // Um pequeno atraso pode ajudar a sincronizar com a rolagem padrão do navegador.
            setTimeout(() => {
                const containerRect = textoContainer.getBoundingClientRect();
                const markerRect = targetMarker.getBoundingClientRect();
                // Ajusta o scroll para posicionar o marcador mais acima na tela, se ele não estiver lá
                const scrollOffset = markerRect.top - containerRect.top + textoContainer.scrollTop - (containerRect.height * 0.3);
                
                textoContainer.scrollTo({
                    top: scrollOffset,
                    behavior: 'smooth'
                });
            }, 100);
        }
    }
    // --- FIM DA Lógica de Inicialização ---


    // IntersectionObserver para detectar qual marcador está visível durante a rolagem manual
    const observerOptions = {
        root: textoContainer,
        rootMargin: "-30% 0px -70% 0px", // Zona de "ativação" do marcador (terço superior do container)
        threshold: 0
    };
    
    const intersectionCallback = (entries) => {
        let bestCandidate = activePageMarker; // O marcador que consideramos o "melhor" para exibir a imagem
        let bestCandidateRect = activePageMarker ? activePageMarker.getBoundingClientRect() : null;

        entries.forEach(entry => {
            if (entry.isIntersecting) {
                let currentEntryRect = entry.target.getBoundingClientRect();
                // Se o elemento entrou na zona ativa e está mais para cima do que o candidato atual, ou não há candidato
                if (!bestCandidate || (currentEntryRect.top < bestCandidateRect.top && currentEntryRect.top >= observerOptions.rootMargin.split(' ')[0].replace('-', ''))) {
                    bestCandidate = entry.target;
                    bestCandidateRect = currentEntryRect;
                }
            }
        });

        // Se o melhor candidato encontrado for diferente do que está atualmente ativo, atualiza a imagem.
        if (bestCandidate && bestCandidate !== activePageMarker) {
            updateImageAndCaption(bestCandidate);
        }
    };

    const observer = new IntersectionObserver(intersectionCallback, observerOptions);
    marcadores.forEach(marcador => observer.observe(marcador));

    // Opcional: Adicionar clique nos marcadores para navegação e atualização
    marcadores.forEach(marcador => {
        marcador.addEventListener('click', (event) => {
            event.preventDefault(); // Previne comportamento padrão do link de âncora se houver

            const containerRect = textoContainer.getBoundingClientRect();
            const markerRect = marcador.getBoundingClientRect();
            // Ajusta o scroll para posicionar o marcador no terço superior do container
            const scrollOffset = markerRect.top - containerRect.top + textoContainer.scrollTop - (containerRect.height * 0.3);
            
            textoContainer.scrollTo({
                top: scrollOffset,
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

    // Inicializa o estado dos botões ao carregar a página (chamar no final do script)
    // Isso é importante caso a página carregue sem hash e sem imagem no primeiro marcador.
    updateNavigationButtons(); 

});