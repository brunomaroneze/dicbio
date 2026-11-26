"""Serviço da VPS: login dos revisores e envio das conferências como issue no GitHub.

Só atende o nginx local. O login é por formulário e cookie (e não pela janela de
senha do navegador, que proxies de algumas universidades bloqueiam). Usuários e
senhas continuam em /etc/nginx/dicbio.htpasswd (htpasswd -B). Para cada pedido,
o nginx consulta /sessao (auth_request) e só entrega a página se o cookie valer.

O token do GitHub (Issues, leitura e escrita) e o segredo que assina os cookies
são entregues pelo systemd e nunca saem deste processo. Além da biblioteca
padrão, só usa o pacote python3-bcrypt.
"""
import base64
import hashlib
import hmac
import html
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import bcrypt

REPO = os.environ.get("DICBIO_REPO", "brunomaroneze/dicbio")
API = os.environ.get("DICBIO_API", "https://api.github.com")
PORTA = int(os.environ.get("DICBIO_PORTA", "8377"))
SENHAS = Path(os.environ.get("DICBIO_SENHAS", "/etc/nginx/dicbio.htpasswd"))
COOKIE = "dicbio_sessao"
VALIDADE = 30 * 24 * 3600   # o login vale por 30 dias
LIMITE = 200_000
feitos = {}                 # evita issue duplicada se o mesmo envio for repetido
falhas = {}                 # tentativas de login erradas, para frear quem tenta adivinhar
trava = threading.Lock()


class Recusa(Exception):
    pass


def credencial(nome):
    return (Path(os.environ["CREDENTIALS_DIRECTORY"]) / nome).read_text().strip()


def token():
    return credencial("token")


# ---------- usuários e sessões ----------

def hash_de(usuario):
    """Hash bcrypt do usuário no htpasswd, ou None. Lido a cada vez: incluir ou
    remover alguém com htpasswd vale na hora, sem reiniciar o serviço."""
    try:
        linhas = SENHAS.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        print("Não consegui ler", SENHAS, e, file=sys.stderr, flush=True)
        return None
    for linha in linhas:
        nome, _, h = linha.strip().partition(":")
        if nome == usuario and h:
            return h
    return None


def senha_confere(usuario, senha):
    h = hash_de(usuario)
    if not h or not h.startswith("$2"):
        if h:
            print(f"Senha de {usuario!r} não está em bcrypt; refaça com htpasswd -B",
                  file=sys.stderr, flush=True)
        return False
    # $2y$ (htpasswd) e $2b$ (biblioteca) são o mesmo algoritmo.
    h = "$2b$" + h[4:] if h.startswith("$2y$") else h
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), h.encode())
    except ValueError:
        return False


def assinatura(usuario, expira, h):
    # O hash da senha entra na assinatura: trocar a senha encerra as sessões abertas.
    msg = f"{usuario}|{expira}|{h}".encode()
    return hmac.new(credencial("segredo").encode(), msg, hashlib.sha256).hexdigest()


def b64(s):
    return base64.urlsafe_b64encode(s.encode()).decode().rstrip("=")


def de_b64(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4)).decode()


def nova_sessao(usuario):
    expira = int(time.time()) + VALIDADE
    return f"{b64(usuario)}.{expira}.{assinatura(usuario, expira, hash_de(usuario))}"


def revisor_da_sessao(cabecalho_cookie):
    """Nome do revisor se o cookie for válido; senão None."""
    m = re.search(rf"(?:^|;\s*){COOKIE}=([A-Za-z0-9_-]+)\.(\d+)\.([0-9a-f]{{64}})", cabecalho_cookie or "")
    if not m:
        return None
    try:
        usuario = de_b64(m.group(1))
    except ValueError:
        return None
    expira = int(m.group(2))
    h = hash_de(usuario)
    if not h or expira < time.time():
        return None   # vencida, ou o usuário foi removido do htpasswd
    return usuario if hmac.compare_digest(m.group(3), assinatura(usuario, expira, h)) else None


def bloqueado(*chaves):
    agora = time.time()
    with trava:
        for chave, maximo in chaves:
            recentes = [t for t in falhas.get(chave, []) if agora - t < 900]
            falhas[chave] = recentes
            if len(recentes) >= maximo:
                return True
    return False


def anota_falha(*chaves):
    with trava:
        for chave, _ in chaves:
            falhas.setdefault(chave, []).append(time.time())


PAGINA = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Entrar · Conferência de transcrições</title>
<style>
body{{margin:0;font-family:system-ui,sans-serif;background:#f4f1ea;color:#222;display:flex;min-height:100vh;align-items:center;justify-content:center}}
form{{background:#fff;padding:2rem;border-radius:8px;box-shadow:0 2px 10px #0002;width:min(20rem,calc(100vw - 4rem))}}
h1{{font-size:1.25rem;margin:0 0 1.25rem;color:#2f4a3c}}
label{{display:block;margin-bottom:1rem;font-size:.95rem}}
input{{display:block;width:100%;box-sizing:border-box;margin-top:.3rem;padding:.5rem;font-size:1rem;border:1px solid #999;border-radius:4px}}
button{{width:100%;padding:.6rem;font-size:1rem;background:#2f4a3c;color:#fff;border:0;border-radius:4px;cursor:pointer}}
.erro{{color:#a00;margin:0 0 1rem}}.aviso{{color:#555;margin:0 0 1rem}}
</style></head><body>
<form method="post" action="/entrar">
<h1>Conferência de transcrições</h1>
{mensagem}
<input type="hidden" name="volta" value="{volta}">
<label>Usuário<input name="usuario" autocomplete="username" autocapitalize="none" required autofocus value="{usuario}"></label>
<label>Senha<input name="senha" type="password" autocomplete="current-password" required></label>
<button>Entrar</button>
</form></body></html>
"""


def destino(volta):
    """Só aceita caminhos deste site (evita redirecionar para outro endereço)."""
    if isinstance(volta, str) and re.fullmatch(r"/(?![/\\])[^\s\\]*", volta) and not volta.startswith("/entrar"):
        return volta
    return "/"


# ---------- envio ----------

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
    def envia(self, codigo, corpo=b"", tipo=None, cabecalhos=()):
        self.send_response(codigo)
        if tipo:
            self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        for k, v in cabecalhos:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(corpo)

    def responde(self, codigo, obj):
        self.envia(codigo, json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def formulario(self, volta="/", usuario="", mensagem="", codigo=200):
        corpo = PAGINA.format(volta=html.escape(volta), usuario=html.escape(usuario), mensagem=mensagem)
        self.envia(codigo, corpo.encode(), "text/html; charset=utf-8", [("X-Robots-Tag", "noindex, nofollow")])

    def do_GET(self):
        self.close_connection = True
        caminho, _, consulta = self.path.partition("?")
        if caminho == "/sessao":            # consultado pelo nginx a cada pedido
            revisor = revisor_da_sessao(self.headers.get("Cookie"))
            return self.envia(204, cabecalhos=[("X-Revisor", revisor)]) if revisor else self.envia(401)
        if caminho == "/entrar":
            volta = destino(urllib.parse.parse_qs(consulta).get("volta", ["/"])[0])
            if revisor_da_sessao(self.headers.get("Cookie")):
                return self.envia(303, cabecalhos=[("Location", volta)])
            return self.formulario(volta)
        if caminho == "/sair":
            return self.envia(303, cabecalhos=[
                ("Set-Cookie", f"{COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax"),
                ("Location", "/entrar")])
        self.envia(404)

    def do_POST(self):
        self.close_connection = True
        if self.path == "/entrar":
            return self.entrar()
        # Outro site não consegue mandar este cabeçalho sem permissão (evita CSRF).
        if self.path != "/api/enviar" or self.headers.get("X-Conferencia") != "1":
            return self.responde(403, {"erro": "pedido recusado"})
        revisor = revisor_da_sessao(self.headers.get("Cookie"))
        if not revisor:
            return self.responde(401, {"erro": "sua sessão expirou. Recarregue a página e entre de novo"})
        try:
            tam = int(self.headers.get("Content-Length", ""))
            if not 0 < tam <= LIMITE:
                raise Recusa("envio grande demais")
            dados = json.loads(self.rfile.read(tam).decode("utf-8"))
            n = cria_issue(monta(dados, revisor))
        except (Recusa, ValueError) as e:
            return self.responde(400, {"erro": str(e) if isinstance(e, Recusa) else "dados inválidos"})
        except urllib.error.HTTPError as e:
            print("GitHub respondeu", e.code, e.read()[:300], file=sys.stderr, flush=True)
            return self.responde(502, {"erro": f"o GitHub recusou o envio (código {e.code})"})
        except OSError as e:
            print("Falha:", e, file=sys.stderr, flush=True)
            return self.responde(502, {"erro": "não foi possível falar com o GitHub"})
        self.responde(200, {"issue": n})

    def entrar(self):
        try:
            tam = int(self.headers.get("Content-Length", ""))
            if not 0 < tam <= 4000:
                raise ValueError
            campos = urllib.parse.parse_qs(self.rfile.read(tam).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return self.formulario(mensagem='<p class="erro">Pedido inválido.</p>', codigo=400)
        usuario = campos.get("usuario", [""])[0].strip()
        senha = campos.get("senha", [""])[0]
        volta = destino(campos.get("volta", ["/"])[0])
        ip = self.headers.get("X-Real-IP", "?")
        # Por usuário e por IP. O limite por IP é alto porque uma universidade
        # inteira pode sair para a internet pelo mesmo endereço.
        chaves = (("u:" + usuario.lower(), 10), ("ip:" + ip, 50))
        if bloqueado(*chaves):
            print(f"Login bloqueado: usuário {usuario!r}, IP {ip}", file=sys.stderr, flush=True)
            return self.formulario(volta, usuario, '<p class="erro">Muitas tentativas erradas. '
                                   'Espere 15 minutos e tente de novo.</p>', 429)
        if not senha_confere(usuario, senha):
            anota_falha(*chaves)
            print(f"Senha errada ou usuário inexistente: {usuario!r}, IP {ip}", file=sys.stderr, flush=True)
            return self.formulario(volta, usuario, '<p class="erro">Usuário ou senha incorretos.</p>')
        print(f"Entrou: {usuario!r}, IP {ip}", file=sys.stderr, flush=True)
        self.envia(303, cabecalhos=[
            ("Set-Cookie", f"{COOKIE}={nova_sessao(usuario)}; Path=/; Max-Age={VALIDADE}; "
                           "HttpOnly; Secure; SameSite=Lax"),
            ("Location", volta)])

    def log_message(self, formato, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORTA), Atende).serve_forever()
