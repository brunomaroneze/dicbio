const $ = id => document.getElementById(id);
const ROTULO = { head: 'título', p: 'parágrafo', note: 'nota', item: 'item de lista', l: 'verso', cell: 'célula',
  form: 'verbete', sense: 'definição', signed: 'assinatura', trailer: 'fecho', titlePart: 'folha de rosto',
  docImprint: 'folha de rosto', byline: 'autoria', epigraph: 'epígrafe', salute: 'saudação' };
let repo, obras, obra, pags = [], atual = 0, pendentes = new Set(), zoom = 100, ultimo = null;
// Rascunhos: {idPagina: {t: {índice: {h, txt}}, obs, ok}}, guardados só neste navegador.
let rasc = {};
const chave = () => 'conferencia:' + obra;
function grava() {
  try { localStorage.setItem(chave(), JSON.stringify(rasc)); }
  catch { $('situacao').dataset.aviso = 'O navegador não permitiu guardar o rascunho: envie antes de fechar.'; }
  atualiza();
}
function situacao(p) {
  if (rasc[p.id]?.ok) return '● salva, falta enviar';
  if (p.conferida) return '✔ conferida por ' + p.conferida;
  if (pendentes.has(p.id)) return '… enviada, aguardando o coordenador';
  return rasc[p.id] ? '✎ em andamento' : '';
}
function atualiza() {
  pags.forEach((p, i) => {
    const s = situacao(p);
    $('pagina').options[i].text = 'p. ' + p.n + (s ? '  ' + s[0] : '');
  });
  const q = Object.values(rasc).filter(r => r.ok).length;
  $('enviar').disabled = !q;
  $('enviar').textContent = q ? `Enviar (${q} página${q > 1 ? 's' : ''})` : 'Enviar';
  $('progresso').textContent = pags.filter(p => p.conferida).length + ' de ' + pags.length + ' conferidas';
  $('situacao').textContent = [pags[atual] && situacao(pags[atual]), $('situacao').dataset.aviso].filter(Boolean).join(' · ');
}
function valor(p, i) { const r = rasc[p.id]?.t[i]; return r && r.h === p.segs[i].h ? r.txt : p.segs[i].t; }
function altura(ta) { ta.style.height = 'auto'; ta.style.height = ta.scrollHeight + 2 + 'px'; }
function marca(div, seg, txt) {
  div.classList.toggle('mudou', limpa(txt) !== limpa(seg.t));
  div.classList.toggle('erro', notas(txt) !== notas(seg.t));
}
function rascunho(p) { return rasc[p.id] ||= { t: {}, obs: '', ok: false }; }
function mostra(i) {
  atual = Math.max(0, Math.min(pags.length - 1, i));
  const p = pags[atual];
  $('pagina').value = atual;
  $('ant').disabled = atual === 0; $('prox').disabled = atual === pags.length - 1;
  $('semimg').hidden = !!p.img; $('img').hidden = !p.img; $('abre').hidden = !p.img;
  if (p.img) { $('img').src = p.img; $('abre').href = p.img; } else $('img').removeAttribute('src');
  $('moldura').scrollTo(0, 0); $('lado-txt').scrollTo(0, 0);
  $('texto').replaceChildren(...p.segs.map((s, k) => {
    const div = document.createElement('div'), rot = document.createElement('small'), ta = document.createElement('textarea');
    div.className = 'seg ' + s.tipo;
    rot.textContent = s.nota ? 'nota ' + s.nota : (ROTULO[s.tipo] || s.tipo) + (s.cont ? ' (continuação)' : '');
    ta.value = valor(p, k); ta.spellcheck = false; ta.rows = 1; ta.setAttribute('aria-label', rot.textContent);
    ta.addEventListener('keydown', e => { if (e.key === 'Enter') e.preventDefault(); });
    ta.addEventListener('focus', () => ultimo = ta);
    ta.addEventListener('input', () => {
      altura(ta); marca(div, s, ta.value);
      const r = rascunho(p); r.ok = false; delete r.env;
      if (limpa(ta.value) === limpa(s.t)) delete r.t[k]; else r.t[k] = { h: s.h, txt: ta.value };
      grava();
    });
    div.append(rot, ta); marca(div, s, ta.value);
    return div;
  }));
  if (!p.segs.length) $('texto').textContent = 'Não há texto transcrito nesta página.';
  $('texto').querySelectorAll('textarea').forEach(altura);
  $('obs').value = rasc[p.id]?.obs || '';
  history.replaceState(null, '', '#' + obra + '/' + p.id);
  if (pags[atual + 1]?.img) new Image().src = pags[atual + 1].img;
  atualiza();
}
async function abre(id, pagId) {
  pendentes = new Set();
  const dados = await (await fetch('dados/' + id + '.json', { cache: 'no-cache' })).json();
  obra = id; $('obra').value = id; pags = dados;
  try { rasc = JSON.parse(localStorage.getItem(chave())) || {}; } catch { rasc = {}; }
  const mudaram = [];
  limpaEnviadas();
  for (const id of Object.keys(rasc)) {
    const p = pags.find(x => x.id === id);
    if (!p) { delete rasc[id]; continue; }
    const velhas = Object.entries(rasc[id].t).filter(([k, r]) => p.segs[k]?.h !== r.h);
    if (!velhas.length) continue;
    mudaram.push(p.n); rasc[id].ok = false;
    velhas.forEach(([k]) => delete rasc[id].t[k]);
  }
  if (mudaram.length) alert('O texto mudou no site depois do seu rascunho. Confira de novo: p. ' + mudaram.join(', '));
  $('pagina').replaceChildren(...pags.map((p, i) => new Option('', i)));
  mostra(Math.max(0, pags.findIndex(p => p.id === pagId)));
  grava(); botaoConfirma();
  buscaPendentes();
}
// Tira do rascunho o que foi enviado e já chegou ao GitHub, mesmo sem confirmação manual.
// r.env guarda a situação da página no momento do envio.
function limpaEnviadas() {
  for (const p of pags) {
    const e = rasc[p.id]?.env;
    if (e && ((p.conferida && !e.conferida) || (pendentes.has(p.id) && !e.pendente))) delete rasc[p.id];
  }
}
function botaoConfirma() { $('confirma').hidden = !Object.values(rasc).some(r => r.env); }
// Páginas já enviadas cujo pull request ainda não foi aceito.
async function buscaPendentes() {
  pendentes = new Set();
  const desta = obra;
  try {
    const r = await fetch(`https://api.github.com/repos/${repo}/issues?labels=conferencia&state=open&per_page=100`);
    if (!r.ok) return;
    const lista = await r.json();
    if (obra !== desta) return;
    for (const it of lista) {
      const m = /```json\s*(\{[^]*?\})\s*```/.exec(it.body || '');
      if (!m) continue;
      try { const d = JSON.parse(m[1]); if (d.obra === obra) d.paginas.forEach(p => pendentes.add(p.id)); } catch { }
    }
    limpaEnviadas(); grava(); botaoConfirma();
  } catch { }
}
$('pend').onclick = () => {
  const livre = p => !p.conferida && !pendentes.has(p.id) && !rasc[p.id]?.ok;
  for (let k = 1; k <= pags.length; k++) { const i = (atual + k) % pags.length; if (livre(pags[i])) return mostra(i); }
  alert('Todas as páginas já foram conferidas ou enviadas.');
};
$('salvar').onclick = () => {
  if ($('texto').querySelector('.erro')) return alert('Uma marca de nota ⟦ ⟧ foi alterada. Corrija o campo em vermelho.');
  rascunho(pags[atual]).ok = true; grava();
  if (atual < pags.length - 1) mostra(atual + 1);
};
$('desfaz').onclick = () => {
  if (rasc[pags[atual].id] && confirm('Descartar as alterações desta página?')) { delete rasc[pags[atual].id]; grava(); mostra(atual); }
};
$('obs').oninput = () => { const r = rascunho(pags[atual]); r.obs = $('obs').value; r.ok = false; delete r.env; grava(); };
function montaEnvio() {
  const prontas = pags.filter(p => rasc[p.id]?.ok);
  const dados = { v: 1, obra, paginas: prontas.map(p => ({
    id: p.id, obs: rasc[p.id].obs.trim(),
    eds: Object.entries(rasc[p.id].t).map(([k, r]) => ({ i: +k, h: r.h, ops: diferencas(p.segs[k].t, limpa(r.txt)) })).filter(e => e.ops.length)
  })) };
  const json = JSON.stringify(dados).replace(/`/g, '\\u0060');
  const ns = prontas.map(p => p.n).join(', ');
  return { prontas, corpo: 'Não altere o texto abaixo. Basta clicar no botão de envio.\n\n```json\n' + json + '\n```\n',
    titulo: `[Conferência] ${obra}: p. ` + (ns.length > 80 ? prontas.length + ' páginas' : ns) };
}
$('enviar').onclick = async () => {
  const { prontas, corpo, titulo } = montaEnvio();
  if (corpo.length > 60000) return alert('Há páginas demais para um só envio. Desmarque algumas (edite e deixe sem salvar) e envie em partes.');
  const base = `https://github.com/${repo}/issues/new?title=` + encodeURIComponent(titulo);
  const url = base + '&body=' + encodeURIComponent(corpo);
  if (url.length < 6000) window.open(url, '_blank', 'noopener');
  else {
    $('copia').value = corpo; $('irGit').href = base; $('longo').showModal();
    try { await navigator.clipboard.writeText(corpo); } catch { $('copia').select(); }
    await new Promise(r => $('longo').addEventListener('close', r, { once: true }));
  }
  prontas.forEach(p => rasc[p.id].env = { conferida: !!p.conferida, pendente: pendentes.has(p.id) });
  grava(); botaoConfirma();
};
$('confirma').onclick = () => {
  pags.filter(p => rasc[p.id]?.env).forEach(p => { delete rasc[p.id]; pendentes.add(p.id); });
  grava(); botaoConfirma(); mostra(atual);
};
$('ant').onclick = () => mostra(atual - 1); $('prox').onclick = () => mostra(atual + 1);
$('pagina').onchange = e => mostra(+e.target.value);
$('obra').onchange = e => { abre(e.target.value); };
$('ajudaBt').onclick = () => $('ajuda').showModal(); $('fecha').onclick = () => $('ajuda').close(); $('fechaLongo').onclick = () => $('longo').close();
$('img').onerror = () => { $('semimg').hidden = false; $('img').hidden = true; };
function aplicaZoom(z) { zoom = Math.max(50, Math.min(400, z)); $('img').style.width = zoom + '%'; }
$('mais').onclick = () => aplicaZoom(zoom + 25); $('menos').onclick = () => aplicaZoom(zoom - 25); $('ajusta').onclick = () => aplicaZoom(100);
let arr = null;
$('moldura').onpointerdown = e => { if (e.target === $('img')) { arr = [e.clientX, e.clientY, $('moldura').scrollLeft, $('moldura').scrollTop]; e.preventDefault(); } };
$('img').ondragstart = () => false;
window.addEventListener('pointermove', e => { if (arr) $('moldura').scrollTo(arr[2] + arr[0] - e.clientX, arr[3] + arr[1] - e.clientY); });
window.addEventListener('pointerup', () => arr = null);
window.addEventListener('resize', () => document.querySelectorAll('#texto textarea').forEach(altura));
for (const c of 'ãõẽĩũâêôàèìòùáéíóúçñæœ&§†℞℥ʒ℈') {
  const b = document.createElement('button'); b.textContent = c;
  b.onmousedown = e => e.preventDefault();
  b.onclick = () => { if (ultimo?.isConnected) { ultimo.focus(); ultimo.setRangeText(c, ultimo.selectionStart, ultimo.selectionEnd, 'end'); ultimo.dispatchEvent(new Event('input')); } };
  $('teclas').append(b);
}
(async () => {
  const ind = await (await fetch('dados/indice.json', { cache: 'no-cache' })).json();
  repo = ind.repositorio; obras = ind.obras;
  if (!obras.length) { $('texto').textContent = 'Nenhuma obra aberta para conferência.'; return; }
  $('obra').replaceChildren(...obras.map(o => new Option(o.titulo, o.id)));
  const [o, p] = decodeURIComponent(location.hash.slice(1)).split('/');
  await abre(obras.some(x => x.id === o) ? o : obras[0].id, p);
})();
