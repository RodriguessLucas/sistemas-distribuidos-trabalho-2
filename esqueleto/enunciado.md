# SISTEMAS DISTRIBUÍDOS · TRABALHO PRÁTICO

# Exclusão Mútua Centralizada e Eleição de Líder

### O Algoritmo do Valentão (Bully) diante da falha do coordenador

**Curso de Ciência da Computação · Python 3.10+ · sockets TCP · gRPC · pytest**

## Sumário

1. Objetivos
2. O que você vai construir
3. Fundamentos: os três mecanismos
4. O protocolo de mensagens
5. Arquitetura de um processo
6. O que você implementa
7. Armadilhas de concorrência
8. Testes: a especificação executável
9. Visualizando a execução
10. Roteiro da apresentação
11. Avaliação e entregáveis
12. Questões para o relatório

---

## 1. Objetivos

Neste trabalho você implementa, em Python, dois mecanismos clássicos de coordenação em sistemas distribuídos e os faz funcionar juntos:

- **Exclusão mútua com coordenador central:** um processo distinto, o coordenador, serializa o acesso de todos os demais a uma região crítica (RC), usando uma fila.

- **Eleição de líder pelo Algoritmo do Valentão (Bully):** quando o coordenador falha, os processos restantes percebem a falha e elegem um substituto, de modo que o sistema continue atendendo pedidos.

O ponto central do trabalho é a interação entre os dois: o que acontece com quem estava na fila, ou dentro da RC, quando o coordenador cai?

Ao final você deverá demonstrar o sistema funcionando sem falhas (Cenário 1) e com a falha do coordenador no meio da execução (Cenário 2).

**Conceitos exercitados:** comunicação por sockets TCP; chamada de procedimento remoto com gRPC e Protocol Buffers; exclusão mútua com fila; detecção de falhas por heartbeat; eleição de líder; threads, locks e events; testes automatizados como especificação.

## 2. O que você vai construir

O sistema tem N = 5 processos (P1...P5) rodando na mesma máquina, cada um escutando em uma porta TCP, e um servidor de log acessado por gRPC.

Todo processo é, ao mesmo tempo, um cliente que pode pedir a RC e um coordenador em potencial.

No início, o coordenador é o de maior ID (P5), exatamente quem o Valentão elegeria se todos estivessem vivos.

### Topologia do sistema

```text
    P1       P2       P3       P4       P5
                                        |
                               Coordenador inicial

    Comunicação entre processos:
    sockets TCP (qualquer par de processos)
                     |
                     | gRPC: RegistrarAcesso
                     | (ENTRADA / SAIDA)
                     v
             +------------------+
             |    LogServer     |
             |   gRPC :60051    |
             |   Árbitro da RC  |
             +------------------+
```

_Figura 1. Topologia padrão: cinco processos em localhost, cada um em sua porta, e o servidor de log._

Quando um processo entra na RC, ele avisa o servidor de log (RPC `RegistrarAcesso`, evento `ENTRADA`) e, ao sair, avisa de novo (evento `SAIDA`).

Como o servidor de log vê todas as entradas e saídas, ele funciona como um **árbitro independente**: mostra quem está na RC a cada momento e denuncia em vermelho qualquer violação de exclusão mútua.

Esse servidor já vem pronto.

## 3. Fundamentos: os três mecanismos

Cada mecanismo abaixo é apresentado em quatro partes: para que serve, quais são as peças, como funciona e qual o seu papel no sistema.

### 3.1 Exclusão mútua centralizada

**PARA QUE SERVE**

Garantir que no máximo um processo esteja na RC em cada instante (segurança) e que todo pedido seja atendido em algum momento (vivacidade).

**PEÇAS**

No coordenador: `titular_rc` (quem está na RC) e `fila_requests` (FIFO).

Mensagens: `REQUEST`, `GRANT`, `RELEASE`.

**COMO FUNCIONA**

O cliente pede (`REQUEST`). RC livre: o coordenador concede (`GRANT`). Ocupada: o pedido vai para o fim da fila.

Ao sair, o cliente avisa (`RELEASE`) e o primeiro da fila recebe o `GRANT`.

**PAPEL NO SISTEMA**

É o serviço que o sistema oferece. Custa 3 mensagens por acesso, mas concentra todo o estado em um único processo: se ele cai, o estado cai junto.

```text
P1                  P2                  P5 (Coordenador)
 |                   |                         |
 |------ REQUEST ----------------------------->|
 |                   |                  RC livre
 |<------- GRANT ------------------------------|
 |                   |                  titular = P1
 |                   |                         |
 |                   |------ REQUEST --------->|
 |                   |                  RC ocupada
 |                   |                  fila = [P2]
 |                   |                         |
 |------ RELEASE ----------------------------->|
 |                   |                  titular = P2
 |                   |                  fila = []
 |                   |<------- GRANT ----------|
 |                   |                         |
 |                   |------ RELEASE --------->|
 |                   |                  RC livre
 |                   |                         |
```

_Figura 2. Exclusão mútua centralizada. P1 e P2 acessam a RC em sequência, sob controle de P5. Três mensagens por acesso._

### 3.2 Detecção de falhas por heartbeat

**PARA QUE SERVE**

Perceber, sem intervenção humana, que o coordenador parou de responder.

**PEÇAS**

Uma thread por processo; mensagens `PING`/`PONG`; `INTERVALO_HEARTBEAT` e `TIMEOUT_RESPOSTA`.

**COMO FUNCIONA**

A cada intervalo, cada processo que não é o coordenador envia `PING` a ele.

Se o `PONG` não vem dentro do timeout, o coordenador é dado como morto e a eleição começa.

**PAPEL NO SISTEMA**

É o gatilho da eleição. Timeout curto detecta rápido, mas pode acusar um coordenador apenas lento (suspeita falsa); timeout longo deixa o sistema parado mais tempo.

```text
Tempo -------------------------------------------------------->

PING          PING          PING
 |             |             |
 v             v             v
PONG          PONG         Sem resposta
 OK            OK             X
                             |
                          P5 falhou
                             |
                    TIMEOUT_RESPOSTA
                             |
                             v
                       Inicia eleição
                             |
                             v
                       P4 é eleito

<---------- INTERVALO_HEARTBEAT ---------->
```

_Figura 3. Detecção de falha: a queda é percebida quando um PING não recebe resposta dentro do timeout._

### 3.3 Eleição: o Algoritmo do Valentão (Bully)

**PARA QUE SERVE**

Escolher um novo coordenador, de forma que todos os processos vivos concordem sobre quem ele é.

**PEÇAS**

IDs totalmente ordenados; mensagens `ELECTION`, `ANSWER`, `COORDINATOR` (+ `ACK`); `TIMEOUT_ELEICAO`.

**COMO FUNCIONA**

Quem suspeita da falha desafia todos os maiores. Um maior vivo responde `ANSWER` e assume a disputa.

Quem não ouve resposta de nenhum maior é o maior vivo: vence e anuncia `COORDINATOR` a todos.

**PAPEL NO SISTEMA**

Restaura o serviço após a falha. Vence sempre o maior ID vivo, daí o nome: o "valentão" se impõe aos menores.

**As regras, vistas pelo processo Pi:**

1. Pi envia `ELECTION` a todos os Pj com j > i.

2. Todo Pj que recebe `ELECTION` responde `ANSWER` imediatamente e inicia a sua própria eleição entre os maiores que ele. Isso vale até para quem já é o coordenador: ele simplesmente se reafirma.

3. Se Pi não recebe nenhum `ANSWER`, ele é o maior vivo: torna-se coordenador e envia `COORDINATOR` a todos.

4. Se recebe algum `ANSWER`, aguarda o `COORDINATOR`. Se ele não chegar a tempo (o maior caiu no meio), Pi recomeça.

5. Um processo que volta ao sistema presumindo ser o coordenador também faz uma eleição, em vez de assumir o posto às cegas. Sem isso, um P5 reiniciado conviveria com o P4 eleito em sua ausência: dois coordenadores.

**Exemplo de eleição após a falha de P5:**

```text
Processos: P1, P2, P3, P4, P5
                           X
                       P5 falhou

1. P2 detecta a falha de P5.

   P2 ---- ELECTION ----> P3
   P2 ---- ELECTION ----> P4
   P2 ---- ELECTION ----> P5 (sem resposta)

2. Processos maiores respondem.

   P3 ---- ANSWER -----> P2
   P4 ---- ANSWER -----> P2

   P2 aguarda o novo coordenador.

3. P3 e P4 iniciam suas próprias eleições.

   P3 ---- ELECTION ----> P4
   P3 ---- ELECTION ----> P5 (sem resposta)

   P4 ---- ANSWER -----> P3

   P4 ---- ELECTION ----> P5 (sem resposta)

4. P4 não recebe resposta de nenhum processo maior.

   P4 é o maior processo vivo.
   P4 vence a eleição.

5. P4 anuncia o novo coordenador.

   P4 ---- COORDINATOR ----> P1
   P4 ---- COORDINATOR ----> P2
   P4 ---- COORDINATOR ----> P3

   Novo coordenador: P4
```

_Figura 4. Algoritmo do Valentão após a queda de P5 (ACKs omitidos). P4, o maior processo vivo, vence._

No pior caso (o menor processo detecta a falha), o Valentão troca O(N²) mensagens; no melhor (o segundo maior detecta), N−2 anúncios bastam.

### 3.4 Quando os mecanismos se encontram: o estado que se perde

O novo coordenador não herda a fila nem o titular do anterior: esse estado morreu com ele.

Duas consequências precisam ser tratadas:

**1. Quem estava na fila do coordenador morto**

Precisa refazer o pedido ao novo coordenador.

Esperar o `GRANT` até estourar `TIMEOUT_GRANT` (60 s) deixaria o sistema parado à toa.

A infraestrutura pronta (`_aguardar_grant`) já percebe a troca de coordenador e devolve `COORD_MUDOU`; cabe a você refazer o pedido.

**2. Quem estava dentro da RC**

Foi autorizado por um coordenador que não existe mais.

Se o novo coordenador achar que a RC está livre, deixará outro processo entrar: violação.

Por isso, o anúncio `COORDINATOR` é respondido com `ACK`, e quem está na RC responde `ACK|id|NA_RC`.

Esta é a parte desafio do trabalho.

**Exemplo de reconstrução do estado da RC:**

```text
P1                  P2                  P4                  P5
 |                   |                   |                   |
 |<------------------------ GRANT ---------------------------|
 |                   |                   |                   |
 P1 entra na RC      |                   |                   |
 |                   |                   |                   |
 |                   |                   |                P5 falha
 |                   |                   |                   X
 |                   |                   |
 |                   |                P4 vence
 |                   |                a eleição
 |                   |                   |
 |<----------- COORDINATOR -------------|
 |                   |<-- COORDINATOR ---|
 |                   |                   |
 |---- ACK|1|NA_RC --------------------->|
 |                   |                   |
 |                   |                   titular = P1
 |                   |                   |
 |                   |---- REQUEST ----->|
 |                   |                   |
 |                   |                   RC ocupada
 |                   |                   fila = [P2]
 |                   |                   |
 |------ RELEASE ----------------------->|
 |                   |                   |
 |                   |<------ GRANT -----|
 |                   |                   |
 P1 saiu da RC       P2 entra na RC      |
```

_Figura 5. O novo coordenador reconstrói o estado da RC: P1, que entrou com autorização de P5, responde ACK com NA_RC._

## 4. O protocolo de mensagens

Toda mensagem é uma linha de texto terminada em `\n`, no formato `TIPO|ID_ORIGEM|EXTRA` (EXTRA pode ser vazio, mas o último `|` permanece).

Cada mensagem viaja em uma conexão TCP própria: abre, envia, opcionalmente lê uma linha de resposta, fecha.

As funções `montar` e `parsear` de `config.py` já fazem a codificação.

| Tipo        | Estilo     | De → Para             | Significado                         | Exemplo            |
| ----------- | ---------- | --------------------- | ----------------------------------- | ------------------ |
| REQUEST     | Assíncrono | Cliente → Coordenador | Quero entrar na RC                  | `REQUEST\|3\|`     |
| GRANT       | Assíncrono | Coordenador → Cliente | Pode entrar                         | `GRANT\|5\|`       |
| RELEASE     | Assíncrono | Cliente → Coordenador | Saí da RC                           | `RELEASE\|3\|`     |
| ELECTION    | Síncrono   | Pi → Pj, j > i        | Estou em eleição                    | `ELECTION\|2\|`    |
| ANSWER      | Resposta   | Pj → Pi               | Estou vivo e sou maior              | `ANSWER\|4\|`      |
| COORDINATOR | Síncrono   | Vencedor → Todos      | Sou o novo coordenador              | `COORDINATOR\|4\|` |
| ACK         | Resposta   | Todos → Vencedor      | Ciente; NA_RC se estou dentro da RC | `ACK\|1\|NA_RC`    |
| PING / PONG | Síncrono   | Cliente ↔ Coordenador | Você está vivo? / Estou             | `PING\|3\|`        |

### Por que o GRANT é assíncrono?

Porque o coordenador pode levar muito tempo para conceder (a RC pode estar ocupada por uma fila inteira).

Manter a conexão do `REQUEST` aberta durante esse tempo seria frágil; em vez disso, o coordenador abre uma conexão nova quando chegar a vez do cliente.

Já `PING`, `ELECTION` e `COORDINATOR` esperam a resposta na mesma conexão, porque a ausência dessa resposta é a informação que interessa.

### Primitivas de envio

Para enviar, use as duas primitivas prontas:

**Envio assíncrono:**

```python
# Assíncrona: True se a mensagem foi entregue
ok = self._enviar(destino, REQUEST)
```

**Envio síncrono:**

```python
# Síncrona: Mensagem (com .tipo, .origem, .extra) ou None
resp = self._enviar_e_aguardar(destino, PING)

if resp is not None and resp.tipo == PONG:
    ...
```

## 5. Arquitetura de um processo

Cada processo é uma instância da classe `Processo`, com várias threads compartilhando estado:

| Thread      | O que faz                                                                                           |
| ----------- | --------------------------------------------------------------------------------------------------- |
| Principal   | Linha de comando: `request`, `status`, `eleicao`, `sair`, `ajuda`                                   |
| `srv-P<id>` | Aceita conexões; cada conexão ganha uma thread curta que decodifica a mensagem e chama `_despachar` |
| `hb-P<id>`  | Heartbeat (Parte D)                                                                                 |
| Sob demanda | Eleições (`_nova_thread`) e pedidos de RC disparados pela CLI                                       |

Cada grupo de estado tem o seu lock. Toque nesses atributos somente segurando o lock correspondente:

| Lock            | Protege                                         | Papel       |
| --------------- | ----------------------------------------------- | ----------- |
| `_lock_rc`      | `titular_rc`, `fila_requests`                   | Coordenador |
| `_lock_cliente` | `estado`, `_coord_do_pedido`, `_evento_grant`   | Cliente     |
| `_lock_eleicao` | `_em_eleicao` (já tratado em `iniciar_eleicao`) | Eleição     |

### Máquina de estados do cliente

O papel de cliente segue a máquina de estados abaixo.

O `GRANT` só é aceito no estado `AGUARDANDO` e se vier do coordenador a quem o pedido foi feito (`_coord_do_pedido`).

Qualquer outro `GRANT` é atrasado ou espúrio e deve ser ignorado.

```text
                      requisitar_rc()
              +----------------------------+
              |                            v
          +--------+                 +------------+
          | OCIOSO |                 | AGUARDANDO |
          +--------+                 +------------+
              ^                            |
              |                       GRANT aceito
              |                            |
              |                            v
              |                       +--------+
              |                       | NA_RC  |
              |                       +--------+
              |                            |
              |                      liberar_rc()
              |                            |
              +----------------------------+
                       RELEASE

Outras transições:

AGUARDANDO
    |
    | Coordenador mudou
    v
Refaz o REQUEST ao novo coordenador
    |
    v
AGUARDANDO

AGUARDANDO
    |
    | Desistiu (falhas = tentativas)
    v
OCIOSO
```

_Figura 6. Máquina de estados do papel de cliente (atributo `estado`)._

## 6. O que você implementa

Tudo o que envolve rede, log, visualização e CLI já está pronto.

Você completa nove métodos de `processo.py`, marcados com `TODO`.

Em cada um deles, a docstring é o contrato (o que o método deve garantir, e que os testes verificam) e o `TODO` traz dicas: perguntas, ferramentas relevantes e armadilhas.

O como é decisão sua. Siga a ordem das partes: cada uma é verificada por um nível dos testes.

| Parte               | Métodos                                                                                       | O que fazem                                                                                                                | Testes       |
| ------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------ |
| **A — Coordenador** | `_atender_request`<br>`_atender_release`                                                      | Concede, enfileira ou ignora pedidos repetidos; repassa a RC ao próximo da fila; ignora `RELEASE` de quem não é o titular. | Nível 2      |
| **B — Cliente**     | `requisitar_rc`<br>`_receber_grant`                                                           | Pede a RC, espera o `GRANT` (refazendo o pedido se o coordenador mudar), entra, sai; aceita só o `GRANT` esperado.         | Nível 2      |
| **C — Eleição**     | `_receber_election`<br>`_conduzir_eleicao`<br>`_tornar_coordenador`<br>`_receber_coordinator` | O Algoritmo do Valentão: responder e assumir a disputa, desafiar os maiores, vencer e anunciar, aceitar o anúncio.         | Nível 3      |
| **D — Heartbeat**   | `_heartbeat`                                                                                  | `PING` periódico ao coordenador; eleição se não houver `PONG`.                                                             | Níveis 3 e 4 |

### Métodos prontos que você vai usar

- `_enviar`
- `_enviar_e_aguardar`
- `_conceder` — entrega o `GRANT`, inclusive ao próprio coordenador.
- `_aguardar_grant` — devolve `CONCEDIDO`, `COORD_MUDOU`, `ESGOTADO` ou `ENCERRADO`.
- `_executar_rc`
- `_liberar_rc`
- `iniciar_eleicao` — garante uma eleição por vez e chama o seu `_conduzir_eleicao`.
- `_nova_thread`
- `_log`

Leia as docstrings deles antes de começar: entender o que cada um faz é metade do trabalho.

### Desafios (bônus)

Os itens marcados com `[DESAFIO]` nos `TODOs` tratam situações de borda:

- Reconstruir quem está na RC após a falha (`ACK` com `NA_RC`).
- Contestar o anúncio de um processo menor.
- Devolver um `GRANT` que não foi pedido.
- Preservar a fila quando o coordenador apenas se reafirma.

São verificados pelo **nível 5 dos testes**.

## 7. Armadilhas de concorrência

Os erros abaixo são os mais comuns neste trabalho. Todos produzem programas que parecem funcionar na maioria das execuções.

### 7.1 Mensagens do mesmo remetente podem chegar fora de ordem

Como cada mensagem usa uma conexão própria, e cada conexão é tratada por uma thread própria no destino, não há garantia de ordem.

Um cliente que sai da RC e logo pede de novo pode ter o `REQUEST` processado antes do `RELEASE`.

Por isso, a regra de `_atender_request` é: um `REQUEST` do próprio titular vai para a fila, como qualquer outro.

"Reenviar o `GRANT` ao titular", que parece inofensivo, põe dois processos na RC.

```text
P1                                     P5 (Coordenador)
 |                                            |
 | Sai da RC                                 |
 |                                            |
 |--- RELEASE (conexão A, demora) ---------->|
 |                                            |
 |--- REQUEST (conexão B) ------------------>|
 |                                            |
 |                                    1º: REQUEST
 |                                    P1 ainda é o titular
 |                                    Pedido vai para a fila
 |                                            |
 |                                    2º: RELEASE
 |                                    Libera a RC
 |                                            |
```

_Figura 7. Cada mensagem usa uma conexão TCP própria; por isso, mensagens do mesmo remetente podem chegar fora de ordem._

### 7.2 O GRANT pode chegar antes do que você espera

O `GRANT` pode chegar antes mesmo de `_enviar(coord, REQUEST)` retornar.

Se, nesse instante, o processo ainda não tiver registrado a quem fez o pedido, `_receber_grant` não terá como reconhecê-lo e o descartará como atrasado.

Pense na ordem em que as coisas acontecem.

### 7.3 Quem envia ELECTION está esperando

`_receber_election` roda na thread da conexão, e o remetente espera a resposta com um timeout.

Se a sua eleição for conduzida ali mesmo, o `ANSWER` só sai no fim; o remetente desiste de esperar e conclui que é o maior vivo.

A resposta e a sua eleição não podem depender uma da outra.

### 7.4 Outras dicas

- Segurar um lock enquanto se espera a rede deixa todas as outras threads paradas e pode causar deadlock. Há uma situação, no desafio de reconstrução do estado, em que segurar o lock durante a comunicação é justamente o que se quer: descubra qual e explique por quê no relatório.

- Um `threading.Event` de sinalização pode ter ficado ligado de uma eleição anterior, e o anúncio da eleição atual pode chegar antes de você começar a esperar por ele. Pense em quando rearmá-lo.

- A troca de coordenador não é uma falha do pedido: o pedido feito ao antigo simplesmente se perdeu com ele.

- Um heartbeat que dorme com `time.sleep` continua agindo por até um intervalo depois que o processo foi encerrado. Procure uma forma de espera que seja interrompida pelo encerramento.

## 8. Testes: a especificação executável

A suíte `testes.py` tem 46 testes, organizados em níveis.

O nível 1 já passa com o esqueleto. Cada teste tem limite de 60 s, de modo que um deadlock vira uma falha, e não um terminal travado.

| Nível | Verifica                    | Exemplos                                                                                                                                       |
| ----- | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | Protocolo e rede (prontos)  | Ida e volta de todas as mensagens; PING/PONG; envio a processo inexistente.                                                                    |
| **2** | Exclusão mútua (A e B)      | Lógica da fila sem rede; ordem FIFO; REQUEST que ultrapassa o RELEASE; estresse com 15 acessos simultâneos; GRANT espúrio; estados do cliente. |
| **3** | Eleição e heartbeat (C e D) | Maior vivo vence; cascata (P5 e P4 caídos); eleições simultâneas convergem; heartbeat detecta sozinho; nenhuma eleição sem falha.              |
| **4** | Cenário 2 completo          | Reentrada após a falha; pedido durante a eleição; fila do coordenador morto redirecionada.                                                     |
| **5** | Desafios (bônus)            | Quem estava na RC é reconhecido; antigo coordenador volta e retoma; anúncio de um menor é contestado.                                          |

### Comandos para executar os testes

```bash
# Executa um nível
python -m pytest -m nivel1

# Executa tudo, menos os bônus
python -m pytest -m "not desafio"

# Executa testes com "fila" no nome
python -m pytest -k fila -v

# Para no primeiro erro
python -m pytest -x
```

### Como a exclusão mútua é verificada

Não basta conferir que "todos entraram".

Nos testes, o `_executar_rc` de cada processo é envolvido por um monitor que conta quantos processos estão na RC a cada instante; se houver dois, o teste falha apontando quem.

O servidor de log faz a mesma verificação, de forma independente, via gRPC.

### Quando um teste falha

O pytest imprime o diagrama de sequência daquele teste (seção `Captured stdout`).

Leia-o como leria o log de um sistema real: ele mostra cada mensagem, quem estava na RC e quem era coordenador.

## 9. Visualizando a execução

O script `cenarios.py` executa os cenários automaticamente, com todos os processos em um só programa, confere o resultado e desenha o que aconteceu:

- Um diagrama de sequência no terminal.
- Uma página HTML em `saida/<cenario>.html` com a linha do tempo da RC, o diagrama completo e a tabela de acessos.

### Comandos para executar os cenários

```bash
# Cenário 1
python cenarios.py fila

# Cenário 2, com o log de cada processo
python cenarios.py falha --log

# Extra: P5 volta e retoma a coordenação
python cenarios.py retorno

# Extra: três eleições ao mesmo tempo
python cenarios.py simultanea

# Executa todos os cenários
python cenarios.py todos
```

### Exemplo de execução do Cenário 2

_Figura 8. Trecho de `saida/falha.html`, gerado por `python cenarios.py falha`._

Na figura, P5 cai com P1 dentro da RC e P3 e P4 na fila.

Em cerca de 0,2 s, P4 é eleito; P1 termina seu acesso (ainda em azul, autorizado por P5) e só então P4, P3 e P2 entram, em laranja.

As barras nunca se sobrepõem.

## 10. Roteiro da apresentação

A apresentação é ao vivo, com um terminal por processo, para que se veja a interação entre eles.

Os tempos de `config.py` (`HOLD_RC = 8 s`) foram escolhidos para dar tempo de alternar entre terminais enquanto a RC está ocupada.

### Preparação

Abra seis terminais na pasta do projeto, com o ambiente virtual ativado, ou use `bash apresentacao_tmux.sh` (Linux, macOS ou WSL), que abre todos em uma janela só.

| Terminal | Comando                | Papel                     |
| -------- | ---------------------- | ------------------------- |
| T1       | `python log_server.py` | Servidor de log (árbitro) |
| T2       | `python processo.py 5` | Coordenador inicial       |
| T3       | `python processo.py 4` | Cliente P4                |
| T4       | `python processo.py 3` | Cliente P3                |
| T5       | `python processo.py 2` | Cliente P2                |
| T6       | `python processo.py 1` | Cliente P1                |

### Cenário 1 — Sem falha

Dispare pedidos em sequência rápida, alternando os terminais: `request operacao-um` em P1, `request operacao-dois` em P2, e assim por diante.

**Mostre:**

1. **No terminal de P5:**
   - RC livre → concedo a P1.
   - RC ocupada por P1 → P2 vai para a fila (`fila: [P2]`).
   - A fila sendo esvaziada a cada `RELEASE`.

2. **Em um cliente, enquanto espera:**
   - O comando `status` mostra `meu estado: AGUARDANDO`.

3. **No servidor de log:**
   - Cada `ENTROU` seguido de `SAIU` antes do próximo `ENTROU`.
   - A ocupação `[RC: P1]` → `[RC: livre]`.

**Exemplo de log:**

```text
#0001 10:41:07.120 ENTROU P1 autorizado por P5 "operacao-um" [RC: P1]
#0002 10:41:15.125 SAIU P1 ficou 8.00s [RC: livre]
#0003 10:41:15.131 ENTROU P2 autorizado por P5 "operacao-dois" [RC: P2]
```

### Cenário 2 — Com falha do coordenador

1. Em P2, execute `request antes-da-falha`: o log mostra o acesso autorizado por P5.

2. Em P1, P3 e P4, faça pedidos em sequência, de modo que P1 entre na RC e os outros fiquem na fila.

3. Com P1 ainda dentro da RC, digite `sair` no terminal de P5: é a falha do coordenador.

4. Em até `INTERVALO_HEARTBEAT + TIMEOUT_RESPOSTA` segundos, um cliente mostra `PING ao coordenador P5 sem resposta → eleição`. Acompanhe os `ELECTION`, os `ANSWER` e o anúncio `SOU O COORDENADOR (P4)`.

5. Mostre que P3 e P4 refazem o pedido ao novo coordenador sem esperar e que, no log, aparece a faixa `coordenador agora é P4 (antes: P5)`.

6. **[DESAFIO]** Mostre no terminal de P4 a linha `P1 está na RC (autorizado pelo coordenador anterior)`.

7. Use `status` em qualquer processo para confirmar `coordenador: P4`. Ao final, `Ctrl+C` no servidor de log imprime o resumo, com zero violações.

### O prompt "sumiu"?

Os logs das threads aparecem a qualquer momento no mesmo terminal do prompt.

O processo não travou: basta digitar o próximo comando (ou pressionar Enter).

## 11. Avaliação e entregáveis

| Item                                                                                            |  Pontos |
| ----------------------------------------------------------------------------------------------- | ------: |
| Cenário 1 ao vivo: exclusão mútua com fila e registro via gRPC                                  |      25 |
| Cenário 2 ao vivo: detecção automática, eleição correta pelo Valentão e continuidade do serviço |      35 |
| Testes dos níveis 1 a 4 (`pytest -m "not desafio"`), proporcional aos que passam                |      25 |
| Qualidade do código, logs informativos e relatório                                              |      15 |
| **Total**                                                                                       | **100** |
| Bônus: testes do nível 5 (2 pontos cada)                                                        | **+10** |

### Entregáveis

Entregue, em um único arquivo `.zip`:

1. **Código-fonte completo**, com a estrutura do projeto.
2. **Vídeo de 3 a 5 minutos** com os dois cenários, ou a apresentação ao vivo, conforme combinado em sala.
3. **Relatório de até 4 páginas**, respondendo às questões da seção 12.

## 12. Questões para o relatório

1. Quais timeouts você usaria em uma rede real, com latência de 50 a 200 ms? Mostre um cenário em que um `TIMEOUT_RESPOSTA` curto demais causa uma eleição desnecessária. O sistema continua correto nesse caso?

2. O que acontece se o cliente que está dentro da RC cair? Proponha um mecanismo (por exemplo, um _lease_: a RC é concedida por tempo limitado) e discuta o seu custo.

3. Por que um processo que volta ao sistema faz uma eleição, em vez de simplesmente assumir que é o coordenador?

4. Conte as mensagens trocadas na eleição do seu Cenário 2 (use o diagrama de `cenarios.py falha`) e compare com o pior caso O(N²).

5. Explique a armadilha da seção 7.1 com um diagrama seu. Que mudança no protocolo eliminaria o problema na origem?
