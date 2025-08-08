target = '\U0001D197'  # Caractere U+1D197

with open('corpus_digital/obras/compendio1brotero.xml', encoding='utf-8') as f:
    for lineno, line in enumerate(f, 1):
        for colno, char in enumerate(line, 1):
            if char == target:
                print(f"Linha {lineno}, coluna {colno}: '{char}' (U+{ord(char):04X})")