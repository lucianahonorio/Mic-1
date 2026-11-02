# Mic-1

Projeto da segunda avaliação de Arquitetura de Computadores II (UFPB).

Simulador da Mic-1 modificada em Python, executando microinstruções e as instruções ILOAD, DUP e BIPUSH da IJVM.

## Como rodar

Precisa de Python 3.

Etapa 1 (ULA):

    python main.py --etapa1 entradas/programa_etapa1.txt

Microinstruções (etapas 2 e 3):

    python main.py --micro entradas/microinstrucoes.txt --regs entradas/registradores.txt --dados entradas/dados.txt

Instruções IJVM:

    python main.py --ijvm entradas/instrucoes.txt --regs entradas/registradores.txt --dados entradas/dados.txt

O log aparece no terminal e é salvo em `saidas/log.txt` (dá pra mudar com `--saida`).

## Pastas

- `mic1/`: código da máquina (ULA, registradores, memória, CPU, tradutor, log)
- `entradas/`: arquivos de programa, registradores e dados
- `gabaritos/`: saídas de exemplo da professora
- `saidas/`: logs gerados
- `tests/`: comparação das saídas com os gabaritos
