# Mic-1

Projeto da segunda avaliação de Arquitetura de Computadores II (UFPB).

Simulador da Mic-1 modificada em Python, executando microinstruções e as instruções ILOAD, DUP e BIPUSH da IJVM.

## Como rodar

Precisa de Python 3.

Etapa 1 (ULA):

    python main.py --etapa1 entradas/programa_etapa1.txt

Etapa 2 Tarefa 1 (ULA com deslocador):

    python main.py --etapa2 entradas/programa_etapa2_tarefa1.txt

Microinstruções (etapas 2 e 3):

    python main.py --micro entradas/microinstrucoes.txt --regs entradas/registradores.txt --dados entradas/dados.txt

Instruções IJVM:

    python main.py --ijvm entradas/instrucoes.txt --regs entradas/registradores.txt --dados entradas/dados.txt

O log aparece no terminal e é salvo em `saidas/log.txt` (dá pra mudar com `--saida`).

## Testes

Usam só o `unittest` do Python, não precisa instalar nada. Na raiz do projeto:

    python3 -m unittest -v

- `tests/test_ula.py`: operações da ULA conferidas à mão (AND, OR, NOT B, soma, INVA, INC, enables, vai-um, N, Z, SLL8 e SRA1).
- `tests/test_caminho.py`: decodificador do barramento B, seletor do barramento C, exemplos do PDF e o fetch.
- `tests/test_etapas.py`: roda cada modo e compara com os exemplos em `gabaritos/`. As linhas que podem diferir estão listadas no próprio teste, cada uma com o motivo.

## Divergências com os exemplos

Seguimos o enunciado (PDF 2026.2). Os exemplos da professora parecem vir de uma versão anterior do projeto e diferem dele em alguns pontos:

- Etapa 1: a linha 1 de `programa_etapa1.txt` é `111110`, mas o exemplo de saída mostra `IR = 111100`. Por isso o teste usa `programa_etapa1_teste.txt`, uma cópia com essa linha trocada.
- Etapa 2 Tarefa 1: no ciclo 1 o exemplo mostra `sd = 0x200`, mas SLL8 de `0x80000001` dá `0x100`. No ciclo 2 o exemplo mostra `n = 0` com `Sd = 0xC0000000`, que é negativo, então N = 1.
- Etapa 2 Tarefa 2: o exemplo completa MBR com zeros e MBRU com sinal (o PDF pede o contrário), trata o código 7 do barramento B como OPC (no PDF é TOS), lista no topo uma linha que não está no programa e numera o fim como `Cycle 3` em vez de `Cycle 4`.
- PDF: o próprio enunciado se contradiz. Nos exemplos (3) e (4) o texto diz que o barramento B é LV, mas os bits do barramento B são `0100`. Pela tabela do decodificador, `0100` = 4 é SP e LV é `0101` = 5, e o exemplo (5) usa os mesmos bits `0100` chamando de SP. Seguimos a tabela: a instrução `001111000000000100100` faz MDR = MDR + SP, e não MDR + LV como diz o texto.

## Pastas

- `mic1/`: código da máquina (ULA, registradores, memória, CPU, tradutor, log)
- `entradas/`: arquivos de programa, registradores e dados
- `gabaritos/`: saídas de exemplo da professora
- `saidas/`: logs gerados
- `tests/`: comparação das saídas com os gabaritos
