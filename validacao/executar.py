"""Executa cada caso selecionado isoladamente e registra evidências reais."""
import datetime
import pathlib
import subprocess
import sys

raiz = pathlib.Path(__file__).resolve().parents[1]
pasta = raiz / "esqueleto"
argumentos = sys.argv[1:]
coleta = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", *argumentos], cwd=pasta, text=True, capture_output=True)
if coleta.returncode:
    print(coleta.stdout + coleta.stderr)
    sys.exit(coleta.returncode)
casos = [linha for linha in coleta.stdout.splitlines() if linha.startswith("testes.py::")]
falhas = 0
execucao = raiz / "validacao" / datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
execucao.mkdir()
with (raiz / "DESENVOLVIMENTO.md").open("a") as diario:
    diario.write(f"\n### Execução: {' '.join(argumentos)}\n\n")
    for caso in casos:
        resultado = subprocess.run([sys.executable, "-m", "pytest", "-q", caso], cwd=pasta, text=True, capture_output=True)
        texto = resultado.stdout + resultado.stderr
        nome = caso.split("::", 1)[1]
        caminho = execucao / (nome.replace("/", "_") + ".log")
        caminho.write_text(texto)
        status = "PASSOU" if resultado.returncode == 0 else "FALHOU"
        falhas += resultado.returncode != 0
        diario.write(f"- **{nome}: {status}.** Evidência: [log](<{caminho.relative_to(raiz).as_posix()}>).\n")
        diario.flush()
        print(f"{nome}: {status}", flush=True)
    diario.write(f"\nResultado: {len(casos) - falhas}/{len(casos)} casos passaram.\n")
sys.exit(bool(falhas))
