"""Confere a suíte conjunta e os quatro cenários sem alterar os testes originais."""
import pathlib
import subprocess
import sys

raiz = pathlib.Path(__file__).resolve().parents[1]
comandos = [
    ("suite-completa", ["-m", "pytest", "-q"]),
    ("cenarios", ["cenarios.py", "todos", "--sem-cores"]),
]
falhas = 0
for nome, argumentos in comandos:
    resultado = subprocess.run(
        [sys.executable, *argumentos], cwd=raiz / "esqueleto",
        text=True, capture_output=True,
    )
    caminho = raiz / "validacao" / f"{nome}.log"
    caminho.write_text(resultado.stdout + resultado.stderr)
    status = "PASSOU" if resultado.returncode == 0 else "FALHOU"
    with (raiz / "DESENVOLVIMENTO.md").open("a") as diario:
        diario.write(f"\nValidação conjunta **{nome}: {status}**. [Log](validacao/{nome}.log).\n")
    print(f"{nome}: {status}", flush=True)
    print('\n'.join(resultado.stdout.splitlines()[-4:]), flush=True)
    falhas += resultado.returncode != 0
    if resultado.returncode:
        break
sys.exit(bool(falhas))
