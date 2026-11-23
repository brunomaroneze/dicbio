"""Teste com correções aleatórias em todas as obras: python revisao/testes.py (requer Node).

Passa pelo mesmo caminho do uso real: diferença calculada em diff.js, aplicada em nucleo.py.
"""
import json
import random
import subprocess
import sys

from gerar_site import AQUI, RAIZ, le
from nucleo import ErroConferencia, aplica, hash_texto, paginas

sys.stdout.reconfigure(encoding="utf-8")
random.seed(1)
JS = ("const d=require(process.argv[1]);const x=JSON.parse(require('fs').readFileSync(0,'utf8'));"
      "process.stdout.write(JSON.stringify(x.map(([a,b])=>[d.hashTexto(a),d.diferencas(a,d.limpa(b))])))")


def bagunca(t):
    partes = t.split(" ")
    for _ in range(random.randint(1, 4)):
        k = random.randrange(len(partes))
        if "⟦" in partes[k]:
            continue
        op = random.randrange(5)
        if op == 0:
            partes[k] += " & <nova>"
        elif op == 1 and len(partes) > 1:
            partes.pop(k)
        elif op == 2:
            partes[k] = "Zaõ"
        elif op == 3:
            partes[k] = partes[k][:1] + "ſ" + partes[k][1:]
        else:
            partes[k] = partes[k][:2] + " " + partes[k][2:]
    return " ".join(partes)


for arq in sorted((RAIZ / "corpus_digital/obras").glob("*.xml")):
    xml = le(arq)
    ps = paginas(xml)
    assert len({p.id for p in ps}) == len(ps)
    assert aplica(xml, {})[0] == xml
    com_texto = [p for p in ps if p.segs]
    alvos = [(p, i, bagunca(p.segs[i].texto)) for p in random.sample(com_texto, 15)
             for i in random.sample(range(len(p.segs)), min(2, len(p.segs)))]
    r = subprocess.run(["node", "-e", JS, str(AQUI / "site/diff.js")],
                       input=json.dumps([[p.segs[i].texto, n] for p, i, n in alvos]),
                       capture_output=True, text=True, encoding="utf-8", check=True)
    ok = falhas = 0
    for (p, i, _n), (h, ops) in zip(alvos, json.loads(r.stdout)):
        assert h == hash_texto(p.segs[i].texto)
        try:
            aplica(xml, {p.id: [{"i": i, "h": h, "ops": ops}]})
            ok += 1
        except ErroConferencia as e:
            falhas += 1
            print("  FALHA", p.n, p.segs[i].tipo, e, ops)
    print(arq.name, len(ps), "páginas; aplicadas", ok, "falhas", falhas, flush=True)
