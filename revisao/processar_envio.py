"""Chamado pelo GitHub Actions: lê a issue enviada pela tela de conferência,
aplica as correções ao XML e prepara o texto do pull request.

O conteúdo da issue é tratado como dado não confiável: nunca vai para o shell.
"""
import datetime
import json
import os
import re
import sys
from pathlib import Path

from gerar_site import AQUI, RAIZ, le
from nucleo import ErroConferencia, aplica, paginas


def cerca(linhas, lingua=""):
    return f"```{lingua}\n" + "\n".join(linhas).replace("`", "ˋ") + "\n```"


def op_valida(o):
    return (isinstance(o, list) and len(o) == 3 and type(o[0]) is int and o[0] >= 0
            and isinstance(o[1], str) and isinstance(o[2], str))


def edicao_valida(e):
    return (isinstance(e, dict) and type(e.get("i")) is int and isinstance(e.get("h"), str)
            and isinstance(e.get("ops"), list) and all(map(op_valida, e["ops"])))


def pagina_valida(p):
    return (isinstance(p, dict) and isinstance(p.get("id"), str) and isinstance(p.get("obs", ""), str)
            and isinstance(p.get("eds"), list) and all(map(edicao_valida, p["eds"])))


def valida(d):
    ps = d.get("paginas") if isinstance(d, dict) and d.get("v") == 1 else None
    if (not isinstance(ps, list) or not ps or not all(map(pagina_valida, ps))
            or len({p["id"] for p in ps}) != len(ps)):
        raise ErroConferencia("os dados enviados não estão no formato esperado")


def processa(issue):
    login = issue["user"]["login"]
    autorizados = {x.strip().lower() for x in le(AQUI / "revisores.txt").splitlines()
                   if x.strip() and not x.startswith("#")}
    if login.lower() not in autorizados:
        raise ErroConferencia("este usuário não está na lista de revisores (revisao/revisores.txt)")
    m = re.search(r"```json\s*(\{.*?\})\s*```", issue.get("body") or "", re.S)
    if not m:
        raise ErroConferencia("não encontrei os dados da conferência no texto da issue")
    try:
        d = json.loads(m.group(1))
    except ValueError:
        raise ErroConferencia("os dados da conferência estão incompletos; copie e cole de novo")
    valida(d)
    cfg = json.loads(le(AQUI / "config.json"))
    obra = next((o for o in cfg["obras"] if o["id"] == d.get("obra") and o["ativa"]), None)
    if obra is None:
        raise ErroConferencia("obra desconhecida ou não aberta para conferência")

    arq = RAIZ / cfg["pasta_obras"] / f"{obra['id']}.xml"
    xml = le(arq)
    por_id = {p.id: p for p in paginas(xml)}
    novo, rel = aplica(xml, {p["id"]: p["eds"] for p in d["paginas"]})
    with open(arq, "w", encoding="utf-8", newline="") as f:
        f.write(novo)

    pasta = AQUI / "conferidas" / obra["id"]
    pasta.mkdir(parents=True, exist_ok=True)
    nomes = []
    for p in d["paginas"]:
        pag = por_id[p["id"]]
        nomes.append(pag.n)
        reg = {"n": pag.n, "revisor": login, "data": datetime.date.today().isoformat(),
               "issue": issue["number"], "obs": p.get("obs", "")}
        (pasta / f"{pag.id}.json").write_text(
            json.dumps(reg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    titulo = f"Conferência de {obra['id']}: p. " + ", ".join(nomes)
    if len(titulo) > 120:
        titulo = f"Conferência de {obra['id']}: {len(nomes)} páginas (p. {nomes[0]} a {nomes[-1]})"
    corpo = [f"**{obra['titulo']}**", "",
             f"Conferido por @{login}. Envio: #{issue['number']}.", "",
             f"Páginas: {', '.join(nomes)}. Correções: {len(rel)}.", ""]
    for p in d["paginas"]:
        if p.get("obs", "").strip():
            corpo += [f"**Observação do revisor (p. {por_id[p['id']].n}):**", "",
                      cerca([p["obs"].strip()[:5000]], "text"), ""]
    marcadas = [r for r in rel if r["tags"]]
    if marcadas:
        nomes_tags = ", ".join(sorted({f"`{t}`" for r in marcadas for t in r["tags"]}))
        corpo += [f"⚠️ {len(marcadas)} correção(ões) dentro de {nomes_tags}: confira os atributos.", ""]
    linhas = []
    for r in rel:
        linhas += [f"@@ p. {r['n']} <{r['tipo']}>" + (f" [{', '.join(r['tags'])}]" if r["tags"] else ""),
                   f"- …{r['antes']}[{r['apaga']}]{r['depois']}…",
                   f"+ …{r['antes']}[{r['insere']}]{r['depois']}…"]
    if linhas:
        texto = cerca(linhas, "diff")
        if len(texto) > 40000:
            texto = "(lista de correções muito longa; veja a aba *Files changed*)"
        corpo += [texto]
    return titulo, "\n".join(corpo)[:64000]


def main():
    evento = json.loads(le(os.environ["GITHUB_EVENT_PATH"]))
    issue = evento["issue"]
    saida = Path(os.environ["RUNNER_TEMP"])
    try:
        titulo, corpo = processa(issue)
    except ErroConferencia as e:
        (saida / "erro.md").write_text(
            f"Não foi possível processar esta conferência: {e}.\n\n"
            "Depois de resolver o problema, edite esta issue ou feche-a e reabra-a para tentar de novo.",
            encoding="utf-8")
        sys.exit(f"Recusado: {e}")
    (saida / "titulo.txt").write_text(titulo, encoding="utf-8")
    (saida / "corpo.md").write_text(corpo, encoding="utf-8")
    u = issue["user"]
    (saida / "commit.txt").write_text(
        f"{titulo}\n\nCo-authored-by: {u['login']} <{u['id']}+{u['login']}@users.noreply.github.com>\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
