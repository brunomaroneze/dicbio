from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path


VERBETE_RE = re.compile(r"^### --- VERBETE:\s*(.*?)\s*---\s*$")
SEPARADOR = "#------------------------------------------------------------"


def normalizar_nome_arquivo(nome_verbete: str) -> str:
    texto = unicodedata.normalize("NFKD", nome_verbete.strip().lower())
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = re.sub(r"\s+", "_", texto)
    texto = re.sub(r"[<>:\"/\\|?*]", "", texto)
    texto = re.sub(r"[^a-z0-9_-]", "", texto)
    return texto.strip("._-")


def extrair_prefixos(linhas: list[str]) -> tuple[str, int]:
    for i, linha in enumerate(linhas):
        if VERBETE_RE.match(linha.strip()):
            prefixos = "".join(linhas[:i]).rstrip() + "\n\n"
            return prefixos, i
    raise ValueError("Nenhum marcador de verbete foi encontrado no arquivo de entrada.")


def dividir_ttl_por_verbete(arquivo_entrada: Path, pasta_saida: Path) -> int:
    texto = arquivo_entrada.read_text(encoding="utf-8")
    linhas = texto.splitlines(keepends=True)

    prefixos, i = extrair_prefixos(linhas)
    pasta_saida.mkdir(parents=True, exist_ok=True)

    nomes_usados: dict[str, int] = {}
    total = 0

    while i < len(linhas):
        marcador = VERBETE_RE.match(linhas[i].strip())
        if not marcador:
            i += 1
            continue

        nome_verbete = marcador.group(1).strip()
        nome_base = normalizar_nome_arquivo(nome_verbete)
        if not nome_base:
            raise ValueError(f"Nome de verbete invalido para arquivo: {nome_verbete!r}")

        inicio = i
        j = i + 1
        while j < len(linhas):
            linha_atual = linhas[j].strip()
            if linha_atual == SEPARADOR:
                break
            if VERBETE_RE.match(linha_atual):
                break
            j += 1

        bloco = "".join(linhas[inicio:j]).strip() + "\n"

        contador = nomes_usados.get(nome_base, 0) + 1
        nomes_usados[nome_base] = contador
        nome_arquivo = f"{nome_base}.ttl" if contador == 1 else f"{nome_base}_{contador}.ttl"

        conteudo_saida = prefixos + bloco + "\n"
        (pasta_saida / nome_arquivo).write_text(conteudo_saida, encoding="utf-8")
        total += 1

        i = j + 1 if j < len(linhas) and linhas[j].strip() == SEPARADOR else j

    return total


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Divide um arquivo TTL em varios arquivos, um por verbete."
    )
    parser.add_argument(
        "entrada",
        nargs="?",
        default="data/entries/DicionarioBiologia.ttl",
        help="Arquivo TTL de entrada.",
    )
    parser.add_argument(
        "saida",
        nargs="?",
        default="data/entries/verbetes_ttl",
        help="Pasta de saida para os arquivos TTL por verbete.",
    )
    args = parser.parse_args()

    arquivo_entrada = Path(args.entrada)
    pasta_saida = Path(args.saida)

    if not arquivo_entrada.exists():
        raise FileNotFoundError(f"Arquivo de entrada nao encontrado: {arquivo_entrada}")

    total = dividir_ttl_por_verbete(arquivo_entrada, pasta_saida)
    print(f"Arquivos gerados: {total}")
    print(f"Pasta de saida: {pasta_saida}")


if __name__ == "__main__":
    main()
