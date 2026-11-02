# Mic-1

Projeto da 2ª avaliação de Arquitetura de Computadores II (UFPB, 2026.2), com a profª Sarah Pontes Madruga.

É um simulador da Mic-1 modificada feito em Python. Ele roda as microinstruções da máquina e, no final, as instruções ILOAD, DUP e BIPUSH da IJVM.

## Grupo

- Luciana Nascimento - [lucianahonorio](https://github.com/lucianahonorio)
- Pierre Queiroz - [pierrequeiroz2006](https://github.com/pierrequeiroz2006)
- Sofia Araujo - [sofiaoaraujo](https://github.com/sofiaoaraujo)

## Como rodar

Só precisa do Python 3.

Etapa 1 (ULA):

    python3 main.py --etapa1 entradas/programa_etapa1.txt

Etapa 2, tarefa 1 (ULA com deslocador):

    python3 main.py --etapa2 entradas/programa_etapa2_tarefa1.txt

Etapa 2, tarefa 2 (caminho de dados):

    python3 main.py --micro entradas/programa_etapa2_tarefa2.txt --regs entradas/registradores_etapa2_tarefa2.txt

Etapa 3, tarefa 1 (memória, microinstrução de 23 bits):

    python3 main.py --etapa3 entradas/microinstruções_etapa3_tarefa1.txt --regs entradas/registradores_etapa3_tarefa1.txt --dados entradas/dados_etapa3_tarefa1.txt

O arquivo de dados não é alterado: a memória final fica salva em `saidas/dados.txt`. Para salvar em outro lugar, use `--dados-saida`.

Instruções da IJVM (ainda não terminado):

    python3 main.py --ijvm entradas/instruções.txt --regs entradas/registradores_etapa3_tarefa1.txt --dados entradas/dados_etapa3_tarefa1.txt

O log sai no terminal e também fica salvo em `saidas/log.txt`. Para salvar em outro lugar, use `--saida`.

## Testes

Usamos o `unittest`, que já vem com o Python. Na pasta do projeto:

    python3 -m unittest -v

O `test_ula.py` testa as operações da ULA com valores que calculamos à mão. O `test_caminho.py` testa os barramentos B e C, os exemplos do PDF e o fetch. O `test_memoria.py` testa a leitura e a escrita na memória, e se o READ/WRITE usa o MAR já atualizado pelo barramento C. O `test_etapas.py` roda o programa em cada modo e compara o log com as saídas de exemplo da professora. As linhas que dão diferente estão listadas nele, cada uma com o motivo.

## Diferenças em relação aos exemplos

Seguimos o PDF do enunciado. Alguns arquivos de exemplo parecem ser de uma versão mais antiga do projeto, então nem tudo bate:

- Etapa 1: a primeira linha do `programa_etapa1.txt` é `111110`, mas a saída de exemplo mostra `IR = 111100`. Por isso criamos o `programa_etapa1_teste.txt`, igual ao original com essa linha trocada.
- Etapa 2, tarefa 1: no ciclo 1 o exemplo dá `sd = 0x200`, mas o SLL8 de `0x80000001` dá `0x100`. No ciclo 2 o exemplo mostra `n = 0`, só que `Sd = 0xC0000000` é negativo, então o certo é N = 1.
- Etapa 2, tarefa 2: no exemplo o MBR é completado com zeros e o MBRU com o sinal (o PDF pede o contrário), e o código 7 do barramento B aparece como OPC (no PDF é TOS). Ele também lista no começo uma linha que não está no programa e termina em `Cycle 3`, quando o certo seria `Cycle 4`.
- O próprio PDF se contradiz nos exemplos (3) e (4). O texto diz que o barramento B é o LV, mas os bits são `0100`. Pela tabela do decodificador, `0100` é o SP (o LV é `0101`), e o exemplo (5) usa os mesmos `0100` chamando de SP. Seguimos a tabela, então `001111000000000100100` faz MDR = MDR + SP.
- Etapa 3, tarefa 1: a saída de exemplo começa com MAR = SP = 4, mem[4] = 2 e 16 linhas de memória, mas os arquivos `registradores_etapa3_tarefa1.txt` e `dados_etapa3_tarefa1.txt` têm outro estado (SP = 7, LV = 2, TOS = 32). Por isso criamos o `registradores_etapa3_tarefa1_teste.txt` e o `dados_etapa3_tarefa1_teste.txt`, copiados do estado inicial do exemplo. Com eles o log sai igual ao exemplo.
- Exemplo (6) do PDF: para `MAR = H; rd` ele dá `00111000100000000010000`, mas o campo C `100000000` habilita o H (bit 8), não o MAR. O certo seria `00111000000000001010000`.

## Pastas

- `mic1/`: código da máquina (ULA, registradores, memória, CPU, tradutor e log)
- `entradas/`: programas, registradores e dados
- `gabaritos/`: saídas de exemplo da professora
- `saidas/`: logs gerados
- `tests/`: testes
