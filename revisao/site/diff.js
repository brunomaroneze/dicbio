// Funções puras, também testadas com Node (revisao/testes.py).
function hashTexto(t) {
  let h = 0x811c9dc5;
  for (const b of new TextEncoder().encode(t)) h = Math.imul(h ^ b, 0x01000193) >>> 0;
  return h.toString(16).padStart(8, '0');
}
// Não normaliza o Unicode aqui, para não mexer no que o revisor não tocou.
function limpa(t) { return t.replace(/\s+/g, ' ').trim(); }
function notas(t) { return (t.match(/⟦[^⟧]*⟧|[⟦⟧]/g) || []).join(); }

// Diferença palavra a palavra: [[posição em caracteres Unicode, apagado, inserido], …]
function diferencas(velho, novo) {
  const sep = t => t.match(/⟦\d+⟧|[\p{L}\p{M}\p{N}]+|\s+|[^]/gu) || [];
  const a = sep(velho), b = sep(novo), tam = s => Array.from(s).length;
  let i = 0, fa = a.length, fb = b.length;
  while (i < fa && i < fb && a[i] === b[i]) i++;
  while (fa > i && fb > i && a[fa - 1] === b[fb - 1]) { fa--; fb--; }
  let pos = tam(a.slice(0, i).join(''));
  const x = a.slice(i, fa), y = b.slice(i, fb), L = y.length + 1;
  const T = new Uint16Array((x.length + 1) * L);
  for (let p = x.length - 1; p >= 0; p--) for (let q = y.length - 1; q >= 0; q--)
    T[p * L + q] = x[p] === y[q] ? T[(p + 1) * L + q + 1] + 1 : Math.max(T[(p + 1) * L + q], T[p * L + q + 1]);
  const ops = []; let p = 0, q = 0, del = '', ins = '';
  const fecha = () => { if (del || ins) { ops.push([pos, del, ins]); pos += tam(del); del = ins = ''; } };
  while (p < x.length || q < y.length) {
    if (p < x.length && q < y.length && x[p] === y[q]) { fecha(); pos += tam(x[p]); p++; q++; }
    else if (q >= y.length || (p < x.length && T[(p + 1) * L + q] >= T[p * L + q + 1])) del += x[p++];
    else ins += y[q++];
  }
  fecha();
  return ops;
}
if (typeof module !== 'undefined') module.exports = { hashTexto, limpa, notas, diferencas };
