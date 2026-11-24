# Diário de desenvolvimento — solução Lucas

O commit inicial da main preserva os 17 arquivos originais, incluindo README, enunciados Markdown e PDF. O desenvolvimento ocorre em feature/solucao-lucas. Nenhum teste original será alterado. Os comentários e contratos são preservados; cada `raise NotImplementedError` substituído permanece registrado como comentário junto à implementação.

Cada caso parametrizado é executado isoladamente pelo script `validacao/executar.py`, com saída completa em `validacao/*.log`. As seções descrevem a proposta e seu motivo; a lista registra o resultado efetivamente observado de cada caso. Falhas terão análise e nova execução documentadas.

## Nível 1 — infraestrutura original

Proposta: validar protocolo, parsing, preservação de EXTRA, PING/PONG e destino indisponível sem alterar a infraestrutura. Os testes verificam diretamente esses contratos. Não se presume aprovação antes da execução.

### Execução: -m nivel1

- **test_n1_01_montar_e_parsear_ida_e_volta[ACK]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[ACK].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[ANSWER]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[ANSWER].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[COORDINATOR]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[COORDINATOR].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[ELECTION]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[ELECTION].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[GRANT]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[GRANT].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[PING]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[PING].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[PONG]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[PONG].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[RELEASE]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[RELEASE].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[REQUEST]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[REQUEST].log>).
- **test_n1_02_parsear_rejeita_malformadas[lixo sem pipes]: PASSOU.** Evidência: [log](<validacao/test_n1_02_parsear_rejeita_malformadas[lixo sem pipes].log>).
- **test_n1_02_parsear_rejeita_malformadas[]: PASSOU.** Evidência: [log](<validacao/test_n1_02_parsear_rejeita_malformadas[].log>).
- **test_n1_02_parsear_rejeita_malformadas[REQUEST|]: PASSOU.** Evidência: [log](<validacao/test_n1_02_parsear_rejeita_malformadas[REQUEST|].log>).
- **test_n1_02_parsear_rejeita_malformadas[REQUEST|abc|]: PASSOU.** Evidência: [log](<validacao/test_n1_02_parsear_rejeita_malformadas[REQUEST|abc|].log>).
- **test_n1_02_parsear_rejeita_malformadas[|3|]: PASSOU.** Evidência: [log](<validacao/test_n1_02_parsear_rejeita_malformadas[|3|].log>).
- **test_n1_03_extra_preserva_pipes: PASSOU.** Evidência: [log](<validacao/test_n1_03_extra_preserva_pipes.log>).
- **test_n1_04_ping_pong_pela_rede: FALHOU.** Falha de preparação por restrição de sockets; diagnóstico abaixo. O log de mesmo nome foi substituído pela repetição aprovada antes da adoção de diretórios por execução.
- **test_n1_05_enviar_para_processo_inexistente_retorna_false: FALHOU.** Falha de preparação por restrição de sockets; diagnóstico abaixo. O log de mesmo nome foi substituído pela repetição aprovada antes da adoção de diretórios por execução.

Resultado: 15/17 casos passaram.

## Parte A — coordenador (n2_06 a n2_11)

- n2_06: reservar titular sob `_lock_rc` e conceder fora do lock; evita duas concessões concorrentes e espera de rede dentro do lock.
- n2_07: adicionar pedidos à cauda enquanto há titular, preservando FIFO.
- n2_08: retirar a cabeça da fila no RELEASE e reservar o próximo titular antes do envio.
- n2_09: ignorar RELEASE de outro processo, sem alterar titular ou fila.
- n2_10: testar presença na fila antes de inserir, evitando duplicação.
- n2_11: novo REQUEST do titular entra na fila; não se reenvia GRANT antes de processar RELEASE. Isso trata conexões recebidas fora de ordem.

### Execução: -k n2_06 or n2_07 or n2_08 or n2_09 or n2_10 or n2_11

- **test_n2_06_request_com_rc_livre_concede_na_hora: PASSOU.** Evidência: [log](<validacao/test_n2_06_request_com_rc_livre_concede_na_hora.log>).
- **test_n2_07_request_com_rc_ocupada_vai_para_o_fim_da_fila: PASSOU.** Evidência: [log](<validacao/test_n2_07_request_com_rc_ocupada_vai_para_o_fim_da_fila.log>).
- **test_n2_08_release_passa_a_rc_ao_proximo_da_fila: PASSOU.** Evidência: [log](<validacao/test_n2_08_release_passa_a_rc_ao_proximo_da_fila.log>).
- **test_n2_09_release_de_quem_nao_e_titular_e_ignorado: PASSOU.** Evidência: [log](<validacao/test_n2_09_release_de_quem_nao_e_titular_e_ignorado.log>).
- **test_n2_10_request_repetido_nao_duplica_a_fila: PASSOU.** Evidência: [log](<validacao/test_n2_10_request_repetido_nao_duplica_a_fila.log>).
- **test_n2_11_request_que_ultrapassa_o_release: PASSOU.** Evidência: [log](<validacao/test_n2_11_request_que_ultrapassa_o_release.log>).

Resultado: 6/6 casos passaram.

### Execução: -m nivel1

- **test_n1_01_montar_e_parsear_ida_e_volta[ACK]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[ACK].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[ANSWER]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[ANSWER].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[COORDINATOR]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[COORDINATOR].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[ELECTION]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[ELECTION].log>).

### Diagnóstico da primeira execução

Os 15 casos de protocolo passaram. Os dois casos de rede do nível 1 falharam na preparação do servidor gRPC, antes da lógica do exercício: `socket: Operation not permitted` ao abrir 127.0.0.1:60051. Trata-se de restrição do ambiente, não de erro de protocolo. Nova execução solicitada fora dessa restrição. Os seis testes isolados da Parte A passaram: as asserções confirmaram titular, FIFO, concessões e rejeição de RELEASE indevido.
- **test_n1_01_montar_e_parsear_ida_e_volta[GRANT]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[GRANT].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[PING]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[PING].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[PONG]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[PONG].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[RELEASE]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[RELEASE].log>).
- **test_n1_01_montar_e_parsear_ida_e_volta[REQUEST]: PASSOU.** Evidência: [log](<validacao/test_n1_01_montar_e_parsear_ida_e_volta[REQUEST].log>).
- **test_n1_02_parsear_rejeita_malformadas[lixo sem pipes]: PASSOU.** Evidência: [log](<validacao/test_n1_02_parsear_rejeita_malformadas[lixo sem pipes].log>).
- **test_n1_02_parsear_rejeita_malformadas[]: PASSOU.** Evidência: [log](<validacao/test_n1_02_parsear_rejeita_malformadas[].log>).
- **test_n1_02_parsear_rejeita_malformadas[REQUEST|]: PASSOU.** Evidência: [log](<validacao/test_n1_02_parsear_rejeita_malformadas[REQUEST|].log>).
- **test_n1_02_parsear_rejeita_malformadas[REQUEST|abc|]: PASSOU.** Evidência: [log](<validacao/test_n1_02_parsear_rejeita_malformadas[REQUEST|abc|].log>).
- **test_n1_02_parsear_rejeita_malformadas[|3|]: PASSOU.** Evidência: [log](<validacao/test_n1_02_parsear_rejeita_malformadas[|3|].log>).
- **test_n1_03_extra_preserva_pipes: PASSOU.** Evidência: [log](<validacao/test_n1_03_extra_preserva_pipes.log>).
- **test_n1_04_ping_pong_pela_rede: PASSOU.** Evidência: [log](<validacao/test_n1_04_ping_pong_pela_rede.log>).
- **test_n1_05_enviar_para_processo_inexistente_retorna_false: PASSOU.** Evidência: [log](<validacao/test_n1_05_enviar_para_processo_inexistente_retorna_false.log>).

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

- **test_n2_06_request_com_rc_livre_concede_na_hora: PASSOU.** Evidência: [log](<validacao/test_n2_06_request_com_rc_livre_concede_na_hora.log>).
- **test_n2_07_request_com_rc_ocupada_vai_para_o_fim_da_fila: PASSOU.** Evidência: [log](<validacao/test_n2_07_request_com_rc_ocupada_vai_para_o_fim_da_fila.log>).
- **test_n2_08_release_passa_a_rc_ao_proximo_da_fila: PASSOU.** Evidência: [log](<validacao/test_n2_08_release_passa_a_rc_ao_proximo_da_fila.log>).
- **test_n2_09_release_de_quem_nao_e_titular_e_ignorado: PASSOU.** Evidência: [log](<validacao/test_n2_09_release_de_quem_nao_e_titular_e_ignorado.log>).
- **test_n2_10_request_repetido_nao_duplica_a_fila: PASSOU.** Evidência: [log](<validacao/test_n2_10_request_repetido_nao_duplica_a_fila.log>).
- **test_n2_11_request_que_ultrapassa_o_release: PASSOU.** Evidência: [log](<validacao/test_n2_11_request_que_ultrapassa_o_release.log>).
- **test_n2_12_request_grant_release: PASSOU.** Evidência: [log](<validacao/test_n2_12_request_grant_release.log>).
- **test_n2_13_coordenador_tambem_pode_usar_a_rc: PASSOU.** Evidência: [log](<validacao/test_n2_13_coordenador_tambem_pode_usar_a_rc.log>).
- **test_n2_14_fila_respeita_a_ordem_de_chegada: PASSOU.** Evidência: [log](<validacao/test_n2_14_fila_respeita_a_ordem_de_chegada.log>).
- **test_n2_15_estresse_nunca_dois_na_rc: PASSOU.** Evidência: [log](<validacao/test_n2_15_estresse_nunca_dois_na_rc.log>).
- **test_n2_16_grant_que_nao_foi_pedido_e_ignorado: PASSOU.** Evidência: [log](<validacao/test_n2_16_grant_que_nao_foi_pedido_e_ignorado.log>).
- **test_n2_17_estados_do_cliente: PASSOU.** Evidência: [log](<validacao/test_n2_17_estados_do_cliente.log>).

Resultado: 12/12 casos passaram.

## Resultado da Parte B

Os 12 testes do nível 2 passaram individualmente. As verificações de FIFO, máquina de estados, gRPC e monitor de exclusão mútua confirmaram a proposta das partes A e B.

## Parte C — eleição (n3_18 a n3_22, n3_25 e n3_26)

- n3_18: responder ANSWER na mesma conexão, sem bloquear pela eleição local.
- n3_19: iniciar eleição em thread própria inclusive no coordenador atual; anunciar vitória a todos os outros IDs.
- n3_20: atualizar coordenador conhecido, acordar quem aguarda anúncio e devolver ACK.
- n3_21: desafiar todos os IDs maiores; se nenhum responder, assumir coordenação e anunciar. Caso haja resposta, esperar anúncio com prazo e repetir se faltar.
- n3_22: a mesma regra elimina sucessivamente os maiores indisponíveis, permitindo que P3 vença quando P5 e P4 caem.
- n3_25: usar a proteção pronta de iniciar_eleicao e rearmar evento antes dos envios para convergir em eleições simultâneas.
- n3_26: sem maiores vivos, eleger a si mesmo e usar o caminho local do cliente para a RC.

Nesta etapa o estado do novo coordenador é inicializado vazio; preservação em reafirmação e reconstrução por ACK ficam para os desafios.

### Execução: -m nivel3 -k not heartbeat

- **test_n3_18_election_e_respondido_com_answer: PASSOU.** Evidência: [log](<validacao/test_n3_18_election_e_respondido_com_answer.log>).
- **test_n3_19_quem_responde_answer_assume_e_se_anuncia: PASSOU.** Evidência: [log](<validacao/test_n3_19_quem_responde_answer_assume_e_se_anuncia.log>).
- **test_n3_20_coordinator_atualiza_a_visao_e_responde_ack: PASSOU.** Evidência: [log](<validacao/test_n3_20_coordinator_atualiza_a_visao_e_responde_ack.log>).
- **test_n3_21_maior_processo_vivo_vence: PASSOU.** Evidência: [log](<validacao/test_n3_21_maior_processo_vivo_vence.log>).
- **test_n3_22_eleicao_em_cascata: PASSOU.** Evidência: [log](<validacao/test_n3_22_eleicao_em_cascata.log>).
- **test_n3_25_eleicoes_simultaneas_convergem: PASSOU.** Evidência: [log](<validacao/test_n3_25_eleicoes_simultaneas_convergem.log>).

- **test_n3_26_processo_sozinho_se_elege_e_usa_a_rc: PASSOU.** Evidência: [log](<validacao/test_n3_26_processo_sozinho_se_elege_e_usa_a_rc.log>).

Resultado: 7/7 casos passaram.

## Parte D — heartbeat (n3_23 e n3_24)

- n3_23: esperar um intervalo, enviar PING ao coordenador atual e disparar eleição se não houver PONG. A eleição já implementada escolhe o maior vivo.
- n3_24: PONG válido mantém a coordenação, sem eleição espúria; coordenador não vigia a si mesmo.

Usar Event.wait tanto no jitter quanto no intervalo permite encerramento imediato. Se a coordenação mudar durante um PING, sua resposta antiga não inicia eleição contra o novo coordenador.

### Execução: -m nivel3 -k heartbeat

- **test_n3_23_heartbeat_detecta_a_queda_sozinho: PASSOU.** Evidência: [log](<validacao/test_n3_23_heartbeat_detecta_a_queda_sozinho.log>).

- **test_n3_24_heartbeat_nao_dispara_eleicao_sem_falha: PASSOU.** Evidência: [log](<validacao/test_n3_24_heartbeat_nao_dispara_eleicao_sem_falha.log>).

Resultado: 2/2 casos passaram.

## Integração de continuidade — nível 4

- n4_27: após queda, falha de entrega causa eleição, novo REQUEST e acesso autorizado pelo novo líder.
- n4_28: pedido durante eleição aguarda sua conclusão por iniciar_eleicao; não deve gastar tentativas repetidamente com o coordenador morto.
- n4_29: `_aguardar_grant` reconhece a mudança de coordenador; cliente refaz REQUEST imediatamente, sem consumir tentativa nem esperar TIMEOUT_GRANT.

A suíte obrigatória não exige neste ponto o reconhecimento do titular anterior; isso é verificado especificamente por n5_30. O cenário demonstrativo será conferido após os desafios.

### Execução: -m nivel4

- **test_n4_27_falha_e_reentrada_na_rc: PASSOU.** Evidência: [log](<validacao/test_n4_27_falha_e_reentrada_na_rc.log>).
- **test_n4_28_pedido_durante_a_eleicao_nao_desiste: PASSOU.** Evidência: [log](<validacao/test_n4_28_pedido_durante_a_eleicao_nao_desiste.log>).
- **test_n4_29_fila_do_coordenador_morto_e_redirecionada: PASSOU.** Evidência: [log](<validacao/test_n4_29_fila_do_coordenador_morto_e_redirecionada.log>).

Resultado: 3/3 casos passaram.

## Fechamento dos requisitos obrigatórios

Todos os 41 casos obrigatórios passaram individualmente: 17 no nível 1, 12 no nível 2, 9 no nível 3 e 3 no nível 4. No nível 3, as asserções confirmaram vencedor e convergência, resposta ANSWER/ACK e ausência de eleições desnecessárias; no nível 4, os pedidos foram concluídos com o coordenador substituto dentro dos prazos exigidos. Com isso, inicia-se a etapa de desafios.

## Desafio n5_30 — reconhecer o titular anterior

Proposta: cada ACK informa NA_RC sob o lock do cliente. O vencedor mantém `_lock_rc` durante todos os anúncios e reconstrói o titular a partir dos ACKs, incluindo seu próprio estado de cliente. REQUEST e RELEASE aguardam essa barreira; assim nenhuma concessão usa estado parcialmente reconstruído. Esta é a exceção justificada ao conselho de não segurar lock durante rede. A garantia assume o modelo do exercício (processos comunicáveis, falha por parada), não partições arbitrárias de rede.

### Execução: -k n5_30

- **test_n5_30_novo_coordenador_reconhece_quem_esta_na_rc: PASSOU.** Evidência: [log](<validacao/20261123-212321-830488/test_n5_30_novo_coordenador_reconhece_quem_esta_na_rc.log>).

Resultado: 1/1 casos passaram.

Resultado n5_30: passou; as asserções confirmaram titular_rc == 1 em P4 e ausência de sobreposição tanto no monitor quanto no árbitro gRPC.

## Desafio n5_31 — retorno do antigo coordenador

Proposta: aproveitar a eleição de entrada já fornecida em iniciar() e a implementação do Bully, sem assumir coordenação às cegas. Quando P5 volta, desafia os maiores (não há), anuncia sua vitória e os demais atualizam sua visão. Não foi necessário alterar o ciclo de vida original. O teste exige convergência novamente em P5 e um acesso autorizado por ele.

### Execução: -k n5_31

- **test_n5_31_antigo_coordenador_volta_e_retoma: FALHOU.** Evidência: [log](<validacao/20261123-212332-622209/test_n5_31_antigo_coordenador_volta_e_retoma.log>).

Resultado: 0/1 casos passaram.

### Falha n5_31 e revisão da proposta

O teste falhou: após retorno de P5, as visões ficaram {P5: P4, P4: P5, P3: P5}. O log mostra anúncio de P4 ainda em trânsito chegando a P5 durante seu próprio anúncio. Aceitar qualquer COORDINATOR permite que o maior aceite um menor e também cria espera cruzada entre os locks de anúncio. Portanto a eleição de entrada, sozinha, não basta. A correção depende da regra de contestação de n5_32: rejeitar anúncio de menor antes de adquirir `_lock_rc`, responder imediatamente e iniciar eleição em outra thread. O log dessa falha permanece salvo em seu diretório de execução.

## Desafio n5_32 — contestar anúncio de menor

Proposta: comparar o ID anunciado com o próprio ID; se for menor, não atualizar a visão, responder ACK sem aguardar a eleição local e disparar contestação em thread separada. O retorno rápido evita a espera cruzada dos anúncios concorrentes. Depois de validar esse contrato, repetir n5_31.

### Execução: -k n5_32 or n5_31

- **test_n5_31_antigo_coordenador_volta_e_retoma: PASSOU.** Evidência: [log](<validacao/20261123-212358-902160/test_n5_31_antigo_coordenador_volta_e_retoma.log>).
- **test_n5_32_anuncio_de_um_menor_e_contestado: PASSOU.** Evidência: [log](<validacao/20261123-212358-902160/test_n5_32_anuncio_de_um_menor_e_contestado.log>).

Resultado: 2/2 casos passaram.

Resultado da correção n5_31/n5_32: ambos passaram. O retorno convergiu em P5 com acesso autorizado por ele; a contestação reafirmou o maior e atualizou o menor.

## Desafio n5_33 — devolver concessão sem pedido

Proposta: se GRANT não corresponde ao pedido e veio do coordenador atual, devolver RELEASE fora do lock do cliente, desde que o cliente não esteja NA_RC. Isso desfaz a reserva fantasma sem liberar antecipadamente uma RC ocupada ao receber duplicata. Concessões antigas continuam ignoradas. Para o próprio coordenador, usar liberação local.

### Execução: -k n5_33

- **test_n5_33_grant_inesperado_do_coordenador_e_devolvido: PASSOU.** Evidência: [log](<validacao/20261123-212418-644094/test_n5_33_grant_inesperado_do_coordenador_e_devolvido.log>).

Resultado: 1/1 casos passaram.

Resultado n5_33: passou; o titular fantasma foi liberado e o monitor confirmou que P1 não entrou espontaneamente na RC.

## Desafio n5_34 — reafirmação preserva estado

Proposta: limpar titular e fila apenas quando este processo ainda não era o coordenador. Uma reafirmação mantém seu estado de serviço, embora anuncie novamente a vitória. O teste provoca eleição com P5 vivo durante acesso e fila pendente; exige ordem [1, 2] sem perder pedido nem aguardar TIMEOUT_GRANT.

### Execução: -k n5_34

- **test_n5_34_reeleicao_do_mesmo_coordenador_preserva_a_fila: PASSOU.** Evidência: [log](<validacao/20261123-212433-151737/test_n5_34_reeleicao_do_mesmo_coordenador_preserva_a_fila.log>).

Resultado: 1/1 casos passaram.

Resultado n5_34: passou; a reafirmação manteve fila e titular e o acesso de P2 ocorreu após P1 dentro do prazo. Os cinco desafios já passaram individualmente, após a correção documentada de n5_31/n5_32. Falta a regressão conjunta e os cenários.

Validação conjunta **suite-completa: PASSOU**. [Log](<validacao/suite-completa.log>).

Validação conjunta **cenarios: PASSOU**. [Log](<validacao/cenarios.log>).

## Por que os testes da infraestrutura passaram

- n1_01, nove tipos de mensagem: montar/parsear preservam tipo, origem e EXTRA, inclusive o acesso por campos e por posição.
- n1_02, cinco entradas malformadas: parsear rejeita cada uma com ValueError, conforme o contrato original.
- n1_03: o conteúdo EXTRA mantém seus pipes internos.
- n1_04: o servidor TCP responde PONG com o ID esperado.
- n1_05: destino inexistente retorna False no envio assíncrono e None no síncrono.

Os 15 casos sem rede passaram desde a primeira execução. Os dois com rede passaram após autorizar sockets locais, sem alterar código de infraestrutura.

## Resumo final

| Etapa | Casos | Resultado final |
|---|---:|---|
| Nível 1 — protocolo e infraestrutura | 17 | Todos passaram |
| Nível 2 — coordenador e cliente | 12 | Todos passaram |
| Nível 3 — eleição e heartbeat | 9 | Todos passaram |
| Nível 4 — continuidade | 3 | Todos passaram |
| Nível 5 — desafios | 5 | Todos passaram |
| Suíte completa em uma execução | 46 | 46 passed in 23.82s |
| Cenários fila, falha, retorno e simultanea | 4 | Todos passaram; zero violações no árbitro |

A implementação completa os nove métodos previstos. Coordenador reserva titular sob lock e mantém FIFO; cliente valida concessões, executa e libera a RC; Bully escolhe o maior vivo; heartbeat detecta falha automaticamente. Os desafios acrescentam reconstrução da RC por ACK, contestação de menor, retomada após reinício, devolução de concessão inesperada e preservação da fila na reafirmação.

A única falha de lógica observada foi n5_31: anúncio atrasado de líder menor durante retorno do maior. A correção de n5_32 resolveu essa corrida; ambos passaram na repetição, e depois todos passaram na suíte conjunta. A outra falha inicial foi do ambiente, que bloqueava sockets. As primeiras execuções reusavam os nomes de log; desde os desafios, cada execução individual recebe diretório próprio para preservar também as falhas.

A comparação automática confirmou: 16 arquivos originais de apoio, incluindo testes, README e enunciados, estão byte a byte iguais à main; todos os comentários originais permanecem na ordem; a AST fora dos nove métodos está intacta e suas docstrings foram mantidas. Os placeholders NotImplementedError substituídos permanecem como comentários identificados. O verificador pode ser repetido com `python validacao/preservacao.py`.

O README da raiz documenta preparação e execução. Nenhum teste original foi modificado. Os resultados confirmam os casos fornecidos e os cenários, sem constituir garantia para partições de rede ou queda de cliente dentro da RC, que exigem mecanismos adicionais. Este diário é o registro de desenvolvimento solicitado; não substitui o relatório acadêmico de até quatro páginas nem o vídeo/apresentação previstos no enunciado.
