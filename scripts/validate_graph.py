# Código gerado pelo ChatGPT para validar o grafo RDF usando SHACL

from pathlib import Path
import sys

from rdflib import Graph
from pyshacl import validate


# Arquivo SHACL
# SHACL_FILE = Path("data/dicbio-shapes-1.0.ttl")
SHACL_FILE = Path("data/dicbio-shacl-shapes.ttl")


def validate_ttl(data_file):
    # Carrega o grafo de dados
    data_graph = Graph()
    data_graph.parse(data_file, format="turtle")

    # Carrega as shapes SHACL
    shacl_graph = Graph()
    shacl_graph.parse(SHACL_FILE, format="turtle")

    # Executa a validação
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shacl_graph,
        inference="none",
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
    )

    print("=" * 70)
    print(f"Arquivo: {data_file}")
    print("=" * 70)

    if conforms:
        print("✓ GRAFO VÁLIDO")
    else:
        print("✗ GRAFO INVÁLIDO")
        print()
        print(results_text)

    return conforms


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Uso:")
        print("  python validate_graph.py arquivo.ttl")
        sys.exit(1)

    data_file = Path(sys.argv[1])

    if not data_file.exists():
        print(f"Erro: arquivo não encontrado: {data_file}")
        sys.exit(1)

    valid = validate_ttl(data_file)

    sys.exit(0 if valid else 1)