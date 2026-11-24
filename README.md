# Trabalho 2 — Sistemas Distribuídos

Implementação de exclusão mútua centralizada, eleição Bully e heartbeat, incluindo os cinco desafios.

O material fornecido está em `esqueleto/`. A branch `main` contém somente os arquivos originais; a solução está em `feature/solucao-lucas`. O README e os enunciados originais permanecem intactos nessa pasta.

## Preparação

Na raiz do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r esqueleto/requirements.txt
python esqueleto/gen_proto.py
```

## Executar

```bash
cd esqueleto
python -m pytest -q                         # suíte completa e desafios
python -m pytest -m "not desafio"           # requisitos obrigatórios
python -m pytest -m desafio                 # cinco desafios
python cenarios.py todos --sem-cores        # quatro cenários e HTMLs
```

Para apresentação manual, consulte `esqueleto/README.md`. São necessários sockets TCP locais nas portas 50051 a 50055 e gRPC na 60051. Em ambientes restritos, autorize a abertura dessas portas antes dos testes.

## Registro e reprodução da validação

O [diário](DESENVOLVIMENTO.md) registra a proposta para cada teste, os resultados, a falha encontrada e sua correção. As evidências estão em `validacao/`.

Na raiz, com o ambiente virtual ativo:

```bash
python validacao/executar.py -m nivel2       # roda cada caso separadamente
python validacao/integracao.py              # suíte conjunta e cenários
python validacao/preservacao.py             # compara ao material da main
```

O executor individual guarda novas execuções em diretórios separados e acrescenta resultados ao diário. Os HTMLs gerados ficam em `esqueleto/saida/` e podem ser regenerados pelo comando de cenários.

A solução segue o modelo didático do enunciado: processos locais e falhas por parada. Detecção por timeout não garante segurança diante de partições arbitrárias; queda de um cliente dentro da RC requer uma extensão, como lease, discutida no enunciado.
