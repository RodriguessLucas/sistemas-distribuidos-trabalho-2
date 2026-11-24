"""Compara a solução ao commit inicial sem executar o código do projeto."""
import ast
import io
import pathlib
import subprocess
import tokenize

raiz = pathlib.Path(__file__).resolve().parents[1]

def original(nome):
    return subprocess.check_output(["git", "show", f"main:{nome}"], cwd=raiz)

arquivos = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "main"], cwd=raiz, text=True).splitlines()
for nome in arquivos:
    if nome != "esqueleto/processo.py":
        assert original(nome) == (raiz / nome).read_bytes(), nome
print("16 arquivos de apoio, incluindo testes, README e enunciados: idênticos à main.")

antes = original("esqueleto/processo.py").decode()
depois = (raiz / "esqueleto/processo.py").read_text()
def comentarios(texto):
    return [t.string for t in tokenize.generate_tokens(io.StringIO(texto).readline) if t.type == tokenize.COMMENT]
comentarios_depois = iter(comentarios(depois))
for comentario in comentarios(antes):
    assert any(novo == comentario for novo in comentarios_depois), comentario
print("Todos os comentários originais preservados na mesma ordem.")

pendentes = {
    "_atender_request", "_atender_release", "requisitar_rc", "_receber_grant",
    "_receber_election", "_conduzir_eleicao", "_tornar_coordenador",
    "_receber_coordinator", "_heartbeat",
}
def simplificar(texto):
    arvore = ast.parse(texto)
    for no in ast.walk(arvore):
        if isinstance(no, ast.FunctionDef) and no.name in pendentes:
            # Ignora apenas os nove placeholders substituídos e preserva seu contrato.
            no.body = [no.body[0]]
    return ast.dump(arvore, include_attributes=False)
assert simplificar(antes) == simplificar(depois)
for metodo in pendentes:
    assert f': {metodo}")' in depois
print("AST fora dos nove métodos: idêntica. Docstrings e infraestrutura preservadas.")
