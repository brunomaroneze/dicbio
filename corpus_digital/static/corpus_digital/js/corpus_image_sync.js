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

    // Sem imagem no site: aviso e, se houver, link para a imagem no site de origem.
    const avisoImagem = document.getElementById('imagem-indisponivel');
    function mostrarImagemIndisponivel() {
        imgDisplay.style.display = 'none';
        if (!avisoImagem) return;
        const origem = activePageMarker && activePageMarker.dataset.origem;
        const link = avisoImagem.querySelector('a');
        link.hidden = !origem;
        if (origem) link.href = origem;
        avisoImagem.hidden = false;
    }
    imgDisplay.addEventListener('error', mostrarImagemIndisponivel);
    imgDisplay.addEventListener('load', () => {
        if (avisoImagem) avisoImagem.hidden = true;
        imgDisplay.style.display = 'block';
    });

    let activePageMarker = null; // Guarda o elemento DOM do marcador atualmente ativo

    // Função que rola o texto para um marcador específico
    function scrollToMarker(marker) {
        if (!marker) return;
        segurarPaginaAtiva();
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

        // --- NOVA LÓGICA DE DESTAQUE DO MARCADOR ---
        // 1. Remove o destaque do marcador antigo (se houver)
        if (activePageMarker) {
            activePageMarker.classList.remove('marcador-ativo');
        }

        // 2. Adiciona o destaque ao novo marcador
        markerToActivate.classList.add('marcador-ativo');
        // --- FIM DA NOVA LÓGICA ---
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
                imgDisplay.removeAttribute('src');
                imgDisplay.alt = '';
                mostrarImagemIndisponivel();
            }
            const real = activePageMarker.dataset.paginaReal;
            legendaDisplay.textContent = `Página: ${pageNum || '?'}${real ? `, recte ${real}` : ''}`;
            
            // Atualiza o estado dos botões
            if (prevPageBtn) prevPageBtn.disabled = (currentIndex <= 0);
            if (nextPageBtn) nextPageBtn.disabled = (currentIndex >= marcadores.length - 1);
        }
    }


    // --- ROLAGEM DO TEXTO ---
    // A página ativa é a do último marcador acima de uma linha a 40% do topo;
    // no início do texto, é sempre a primeira.
    // Durante a rolagem provocada pelos botões, vale a página que eles escolheram:
    // páginas curtas (folha de rosto, em branco) podem não alcançar essa linha.
    let rolagemAutomatica = null;

    function segurarPaginaAtiva() {
        clearTimeout(rolagemAutomatica);
        rolagemAutomatica = setTimeout(() => { rolagemAutomatica = null; }, 200);
    }

    function ativarPaginaVisivel() {
        let visivel = marcadores[0];
        if (textoContainer.scrollTop > 1) {
            const linha = textoContainer.getBoundingClientRect().top + textoContainer.clientHeight * 0.4;
            for (const marcador of marcadores) {
                if (marcador.getBoundingClientRect().top > linha) break;
                visivel = marcador;
            }
        }
        updateActivePage(visivel);
    }

    let quadroPedido = false;
    textoContainer.addEventListener('scroll', () => {
        if (rolagemAutomatica !== null) {
            segurarPaginaAtiva(); // até que a rolagem automática termine
            return;
        }
        if (quadroPedido) return;
        quadroPedido = true;
        requestAnimationFrame(() => {
            quadroPedido = false;
            if (rolagemAutomatica === null) ativarPaginaVisivel();
        });
    });


    // --- LÓGICA DOS BOTÕES ---
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => {
            const currentIndex = marcadores.indexOf(activePageMarker);
            if (currentIndex > 0) {
                const prevMarker = marcadores[currentIndex - 1];
                scrollToMarker(prevMarker);
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