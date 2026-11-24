"""Serviço da VPS que recebe as conferências e cria a issue no GitHub.

Só atende o nginx local, que já exigiu a senha e informa o usuário em X-Revisor.
O token (permissão: Issues, leitura e escrita) é entregue pelo systemd e nunca
sai deste processo. Só usa a biblioteca padrão.
"""
import hashlib
import json
import os
import re
import sys
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = os.environ.get("DICBIO_REPO", "brunomaroneze/dicbio")
API = os.environ.get("DICBIO_API", "https://api.github.com")
PORTA = int(os.environ.get("DICBIO_PORTA", "8377"))
LIMITE = 200_000
feitos = {}             # evita issue duplicada se o mesmo envio for repetido
trava = threading.Lock()


class Recusa(Exception):
    pass


def token():
    return (Path(os.environ["CREDENTIALS_DIRECTORY"]) / "token").read_text().strip()


def monta(dados, revisor):
    if not re.fullmatch(r"[\w.-]{1,40}", revisor):
        raise Recusa("usuário inválido")
    if not (isinstance(dados, dict) and dados.get("v") == 1
            and isinstance(dados.get("obra"), str) and re.fullmatch(r"[A-Za-z0-9_-]{1,60}", dados["obra"])
            and isinstance(dados.get("paginas"), list) and dados["paginas"]):
        raise Recusa("dados inválidos")
    limpo = {"v": 1, "obra": dados["obra"], "revisor": revisor, "paginas": dados["paginas"]}
    texto = json.dumps(limpo, ensure_ascii=False, separators=(",", ":")).replace("`", "\\u0060")
    corpo = f"Enviado pela tela de conferência. Não altere o texto abaixo.\n\n```json\n{texto}\n```\n"
    if len(corpo) > 64000:
        raise Recusa("há páginas demais para um só envio")
    n = len(dados["paginas"])
    return {"title": f"[Conferência] {dados['obra']}: {n} página{'s' if n > 1 else ''} ({revisor})", "body": corpo}


def cria_issue(issue):
    marca = hashlib.sha256(issue["body"].encode()).hexdigest()
    with trava:
        if marca in feitos:
            return feitos[marca]
        req = urllib.request.Request(
            f"{API}/repos/{REPO}/issues", data=json.dumps(issue).encode(), method="POST",
            headers={"Authorization": f"Bearer {token()}", "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json", "User-Agent": "conferencia-tei",
                     "X-GitHub-Api-Version": "2022-11-28"})
        with urllib.request.urlopen(req, timeout=30) as r:
            feitos[marca] = json.load(r)["number"]
        return feitos[marca]


class Atende(BaseHTTPRequestHandler):
    def responde(self, codigo, obj):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        self.close_connection = True
        # Outro site não consegue mandar este cabeçalho sem permissão (evita CSRF).
        if self.path != "/api/enviar" or self.headers.get("X-Conferencia") != "1":
            return self.responde(403, {"erro": "pedido recusado"})
        try:
            tam = int(self.headers.get("Content-Length", ""))
            if not 0 < tam <= LIMITE:
                raise Recusa("envio grande demais")
            dados = json.loads(self.rfile.read(tam).decode("utf-8"))
            n = cria_issue(monta(dados, self.headers.get("X-Revisor", "")))
        except (Recusa, ValueError) as e:
            return self.responde(400, {"erro": str(e) if isinstance(e, Recusa) else "dados inválidos"})
        except urllib.error.HTTPError as e:
            print("GitHub respondeu", e.code, e.read()[:300], file=sys.stderr, flush=True)
            return self.responde(502, {"erro": f"o GitHub recusou o envio (código {e.code})"})
        except OSError as e:
            print("Falha:", e, file=sys.stderr, flush=True)
            return self.responde(502, {"erro": "não foi possível falar com o GitHub"})
        self.responde(200, {"issue": n})

    def log_message(self, formato, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORTA), Atende).serve_forever()
