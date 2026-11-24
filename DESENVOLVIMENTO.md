# Diário de desenvolvimento — solução Lucas

O commit inicial da main preserva os 17 arquivos originais, incluindo README, enunciados Markdown e PDF. O desenvolvimento ocorre em feature/solucao-lucas. Nenhum teste original será alterado. Os comentários e contratos são preservados; cada `raise NotImplementedError` substituído permanece registrado como comentário junto à implementação.

Cada caso parametrizado é executado isoladamente pelo script `validacao/executar.py`, com saída completa em `validacao/*.log`. As seções descrevem a proposta e seu motivo; a lista registra o resultado efetivamente observado de cada caso. Falhas terão análise e nova execução documentadas.

## Nível 1 — infraestrutura original

Proposta: validar protocolo, parsing, preservação de EXTRA, PING/PONG e destino indisponível sem alterar a infraestrutura. Os testes verificam diretamente esses contratos. Não se presume aprovação antes da execução.

### Execução: -m nivel1

- **test_n1_01_montar_e_parsear_ida_e_volta[ACK]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[ACK].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[ANSWER]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[ANSWER].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[COORDINATOR]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[COORDINATOR].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[ELECTION]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[ELECTION].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[GRANT]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[GRANT].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[PING]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[PING].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[PONG]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[PONG].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[RELEASE]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[RELEASE].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[REQUEST]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[REQUEST].log).
- **test_n1_02_parsear_rejeita_malformadas[lixo sem pipes]: PASSOU.** Evidência: [log](validacao/test_n1_02_parsear_rejeita_malformadas[lixo sem pipes].log).
- **test_n1_02_parsear_rejeita_malformadas[]: PASSOU.** Evidência: [log](validacao/test_n1_02_parsear_rejeita_malformadas[].log).
- **test_n1_02_parsear_rejeita_malformadas[REQUEST|]: PASSOU.** Evidência: [log](validacao/test_n1_02_parsear_rejeita_malformadas[REQUEST|].log).
- **test_n1_02_parsear_rejeita_malformadas[REQUEST|abc|]: PASSOU.** Evidência: [log](validacao/test_n1_02_parsear_rejeita_malformadas[REQUEST|abc|].log).
- **test_n1_02_parsear_rejeita_malformadas[|3|]: PASSOU.** Evidência: [log](validacao/test_n1_02_parsear_rejeita_malformadas[|3|].log).
- **test_n1_03_extra_preserva_pipes: PASSOU.** Evidência: [log](validacao/test_n1_03_extra_preserva_pipes.log).
- **test_n1_04_ping_pong_pela_rede: FALHOU.** Evidência: [log](validacao/test_n1_04_ping_pong_pela_rede.log).
- **test_n1_05_enviar_para_processo_inexistente_retorna_false: FALHOU.** Evidência: [log](validacao/test_n1_05_enviar_para_processo_inexistente_retorna_false.log).

Resultado: 15/17 casos passaram.

## Parte A — coordenador (n2_06 a n2_11)

- n2_06: reservar titular sob `_lock_rc` e conceder fora do lock; evita duas concessões concorrentes e espera de rede dentro do lock.
- n2_07: adicionar pedidos à cauda enquanto há titular, preservando FIFO.
- n2_08: retirar a cabeça da fila no RELEASE e reservar o próximo titular antes do envio.
- n2_09: ignorar RELEASE de outro processo, sem alterar titular ou fila.
- n2_10: testar presença na fila antes de inserir, evitando duplicação.
- n2_11: novo REQUEST do titular entra na fila; não se reenvia GRANT antes de processar RELEASE. Isso trata conexões recebidas fora de ordem.

### Execução: -k n2_06 or n2_07 or n2_08 or n2_09 or n2_10 or n2_11

- **test_n2_06_request_com_rc_livre_concede_na_hora: PASSOU.** Evidência: [log](validacao/test_n2_06_request_com_rc_livre_concede_na_hora.log).
- **test_n2_07_request_com_rc_ocupada_vai_para_o_fim_da_fila: PASSOU.** Evidência: [log](validacao/test_n2_07_request_com_rc_ocupada_vai_para_o_fim_da_fila.log).
- **test_n2_08_release_passa_a_rc_ao_proximo_da_fila: PASSOU.** Evidência: [log](validacao/test_n2_08_release_passa_a_rc_ao_proximo_da_fila.log).
- **test_n2_09_release_de_quem_nao_e_titular_e_ignorado: PASSOU.** Evidência: [log](validacao/test_n2_09_release_de_quem_nao_e_titular_e_ignorado.log).
- **test_n2_10_request_repetido_nao_duplica_a_fila: PASSOU.** Evidência: [log](validacao/test_n2_10_request_repetido_nao_duplica_a_fila.log).
- **test_n2_11_request_que_ultrapassa_o_release: PASSOU.** Evidência: [log](validacao/test_n2_11_request_que_ultrapassa_o_release.log).

Resultado: 6/6 casos passaram.

### Execução: -m nivel1

- **test_n1_01_montar_e_parsear_ida_e_volta[ACK]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[ACK].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[ANSWER]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[ANSWER].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[COORDINATOR]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[COORDINATOR].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[ELECTION]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[ELECTION].log).

### Diagnóstico da primeira execução

Os 15 casos de protocolo passaram. Os dois casos de rede do nível 1 falharam na preparação do servidor gRPC, antes da lógica do exercício: `socket: Operation not permitted` ao abrir 127.0.0.1:60051. Trata-se de restrição do ambiente, não de erro de protocolo. Nova execução solicitada fora dessa restrição. Os seis testes isolados da Parte A passaram: as asserções confirmaram titular, FIFO, concessões e rejeição de RELEASE indevido.
- **test_n1_01_montar_e_parsear_ida_e_volta[GRANT]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[GRANT].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[PING]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[PING].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[PONG]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[PONG].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[RELEASE]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[RELEASE].log).
- **test_n1_01_montar_e_parsear_ida_e_volta[REQUEST]: PASSOU.** Evidência: [log](validacao/test_n1_01_montar_e_parsear_ida_e_volta[REQUEST].log).
- **test_n1_02_parsear_rejeita_malformadas[lixo sem pipes]: PASSOU.** Evidência: [log](validacao/test_n1_02_parsear_rejeita_malformadas[lixo sem pipes].log).
- **test_n1_02_parsear_rejeita_malformadas[]: PASSOU.** Evidência: [log](validacao/test_n1_02_parsear_rejeita_malformadas[].log).
- **test_n1_02_parsear_rejeita_malformadas[REQUEST|]: PASSOU.** Evidência: [log](validacao/test_n1_02_parsear_rejeita_malformadas[REQUEST|].log).
- **test_n1_02_parsear_rejeita_malformadas[REQUEST|abc|]: PASSOU.** Evidência: [log](validacao/test_n1_02_parsear_rejeita_malformadas[REQUEST|abc|].log).
- **test_n1_02_parsear_rejeita_malformadas[|3|]: PASSOU.** Evidência: [log](validacao/test_n1_02_parsear_rejeita_malformadas[|3|].log).
- **test_n1_03_extra_preserva_pipes: PASSOU.** Evidência: [log](validacao/test_n1_03_extra_preserva_pipes.log).
- **test_n1_04_ping_pong_pela_rede: PASSOU.** Evidência: [log](validacao/test_n1_04_ping_pong_pela_rede.log).
- **test_n1_05_enviar_para_processo_inexistente_retorna_false: PASSOU.** Evidência: [log](validacao/test_n1_05_enviar_para_processo_inexistente_retorna_false.log).

Resultado: 17/17 casos passaram.

## Parte B — cliente (n2_12 a n2_17)

- n2_12: registrar coordenador do pedido antes do REQUEST; esperar evento, executar RC com registro gRPC e liberar em finally.
- n2_13: tratar REQUEST do próprio coordenador localmente, usando `_atender_request`, pois o transporte recusa envio a si mesmo.
- n2_14: deixar a ordem de acesso sob responsabilidade da fila FIFO do coordenador.
- n2_15: coordenador reserva um único titular sob lock; cliente aceita apenas sua concessão pendente. O teste exercita 15 acessos concorrentes e verifica sobreposições.
- n2_16: ignorar GRANT sem pedido correspondente; não executar trabalho espontaneamente.
- n2_17: passar de OCIOSO para AGUARDANDO, depois NA_RC na aceitação do GRANT e retornar a OCIOSO ao liberar.

A parte cliente também prevê repetição após falha e redirecionamento imediato sem consumir tentativa quando o coordenador muda. Essa integração será verificada no nível 4, depois da eleição.

### Execução: -m nivel2

- **test_n2_06_request_com_rc_livre_concede_na_hora: PASSOU.** Evidência: [log](validacao/test_n2_06_request_com_rc_livre_concede_na_hora.log).
- **test_n2_07_request_com_rc_ocupada_vai_para_o_fim_da_fila: PASSOU.** Evidência: [log](validacao/test_n2_07_request_com_rc_ocupada_vai_para_o_fim_da_fila.log).
- **test_n2_08_release_passa_a_rc_ao_proximo_da_fila: PASSOU.** Evidência: [log](validacao/test_n2_08_release_passa_a_rc_ao_proximo_da_fila.log).
- **test_n2_09_release_de_quem_nao_e_titular_e_ignorado: PASSOU.** Evidência: [log](validacao/test_n2_09_release_de_quem_nao_e_titular_e_ignorado.log).
- **test_n2_10_request_repetido_nao_duplica_a_fila: PASSOU.** Evidência: [log](validacao/test_n2_10_request_repetido_nao_duplica_a_fila.log).
- **test_n2_11_request_que_ultrapassa_o_release: PASSOU.** Evidência: [log](validacao/test_n2_11_request_que_ultrapassa_o_release.log).
- **test_n2_12_request_grant_release: PASSOU.** Evidência: [log](validacao/test_n2_12_request_grant_release.log).
- **test_n2_13_coordenador_tambem_pode_usar_a_rc: PASSOU.** Evidência: [log](validacao/test_n2_13_coordenador_tambem_pode_usar_a_rc.log).
- **test_n2_14_fila_respeita_a_ordem_de_chegada: PASSOU.** Evidência: [log](validacao/test_n2_14_fila_respeita_a_ordem_de_chegada.log).
- **test_n2_15_estresse_nunca_dois_na_rc: PASSOU.** Evidência: [log](validacao/test_n2_15_estresse_nunca_dois_na_rc.log).
- **test_n2_16_grant_que_nao_foi_pedido_e_ignorado: PASSOU.** Evidência: [log](validacao/test_n2_16_grant_que_nao_foi_pedido_e_ignorado.log).
- **test_n2_17_estados_do_cliente: PASSOU.** Evidência: [log](validacao/test_n2_17_estados_do_cliente.log).

Resultado: 12/12 casos passaram.
