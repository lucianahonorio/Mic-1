import argparse

from mic1.registradores import Registradores
from mic1.memoria import Memoria
from mic1.cpu import CPU
from mic1.tradutor import traduzir
from mic1.log import Log
from mic1.ula import ula, operacao
from mic1.bits import mask32, bin32

A_ETAPA1 = 0xFFFFFFFF
B_ETAPA1 = 1
A_ETAPA2 = 1
B_ETAPA2 = 0x80000000
MOSTRAR_A_INVERTIDO = False


def ler_linhas(caminho):
    with open(caminho) as f:
        return [l.strip() for l in f if l.strip()]


def executar_ula(caminho, log, a, b, etapa2):
    with open(caminho) as f:
        linhas = [l.strip() for l in f]

    log.escrever("b = " + bin32(b))
    log.escrever("a = " + bin32(a))
    log.escrever()
    log.escrever("Start of Program")
    log.separador()

    pc = 0
    while True:
        pc += 1
        log.escrever("Cycle " + str(pc))
        log.escrever()
        log.escrever("PC = " + str(pc))

        if pc > len(linhas) or linhas[pc - 1] == "":
            log.escrever("> Line is empty, EOP.")
            log.escrever()
            break

        ir = linhas[pc - 1]
        log.escrever("IR = " + ir)

        if etapa2:
            controle = ir
        else:
            controle = "00" + ir

        try:
            sd, vai_um, n, z = ula(controle, a, b)
        except ValueError:
            log.escrever("> Error, invalid control signals.")
            log.separador()
            continue

        s, vai_um = operacao(controle[2:], a, b)

        a_mostrado = a if controle[4] == "1" else 0
        b_mostrado = b if controle[5] == "1" else 0
        if MOSTRAR_A_INVERTIDO and controle[6] == "1":
            a_mostrado = mask32(~a_mostrado)

        log.escrever("b = " + bin32(b_mostrado))
        log.escrever("a = " + bin32(a_mostrado))
        log.escrever("s = " + bin32(s))
        if etapa2:
            log.escrever("sd = " + bin32(sd))
            log.escrever("n = " + str(n))
            log.escrever("z = " + str(z))
        log.escrever("co = " + str(vai_um))
        log.separador()


def executar_micro(caminho, caminho_regs, log):
    linhas = ler_linhas(caminho)

    regs = Registradores()
    regs.carregar(caminho_regs)
    cpu = CPU(regs)

    for linha in linhas:
        log.escrever(linha)
    log.escrever()
    log.separador(53)
    log.registradores("> Initial register states", regs.valores)
    log.escrever()
    log.separador(53)
    log.escrever("Start of program")
    log.separador(53)

    ciclo = 0
    for palavra in linhas:
        ciclo += 1
        controle, seletor_c, memoria, codigo_b = cpu.decodificar(palavra)
        nome_b = regs.nome_b(int(codigo_b, 2))
        nomes_c = regs.habilitados_c(seletor_c)

        log.escrever("Cycle " + str(ciclo))
        log.escrever("ir = " + controle + " " + seletor_c + " " + codigo_b)
        log.escrever()
        log.escrever("b_bus = " + nome_b.lower())
        log.escrever("c_bus = " + ", ".join(nome.lower() for nome in nomes_c))
        log.escrever()
        log.registradores("> Registers before instruction", regs.copia())

        cpu.executar(palavra)

        log.escrever()
        log.registradores("> Registers after instruction", regs.copia())
        log.separador(53)

    log.escrever("Cycle " + str(ciclo + 1))
    log.escrever("No more lines, EOP.")


def executar_etapa3(caminho, caminho_regs, caminho_dados, caminho_dados_saida, log):
    linhas = ler_linhas(caminho)

    regs = Registradores()
    regs.carregar(caminho_regs)
    mem = Memoria(caminho_dados)
    mem.carregar()
    cpu = CPU(regs, mem)

    log.separador()
    log.memoria("Initial memory state", mem.copia())
    log.escrever("*" * 31)
    log.registradores("Initial register state", regs.valores, estrelas=True)
    log.separador()
    log.escrever("Start of Program")
    log.separador()

    ciclo = 0
    for palavra in linhas:
        ciclo += 1
        controle, seletor_c, memoria, codigo_b = cpu.decodificar(palavra)
        nome_b = regs.nome_b(int(codigo_b, 2))
        nomes_c = regs.habilitados_c(seletor_c)

        if ciclo > 1:
            log.separador()
        log.escrever("Cycle " + str(ciclo))
        log.escrever("ir = " + controle + " " + seletor_c + " " + memoria + " " + codigo_b)
        log.escrever("b = " + nome_b.lower())
        log.escrever("c = " + ", ".join(nome.lower() for nome in nomes_c))
        log.escrever()
        log.registradores("> Registers before instruction", regs.copia(), estrelas=True)

        try:
            cpu.executar(palavra)
        except IndexError as erro:
            log.escrever()
            log.escrever("> Error: " + str(erro) + ". EOP.")
            mem.salvar(caminho_dados_saida)
            return

        log.escrever()
        log.registradores("> Registers after instruction", regs.copia(), estrelas=True)
        log.escrever()
        log.memoria("> Memory after instruction", mem.copia())

    log.separador(53)
    log.escrever("Cycle " + str(ciclo + 1))
    log.escrever("No more lines, EOP.")

    # a memória final vai para uma cópia, o arquivo de entrada não muda
    mem.salvar(caminho_dados_saida)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--etapa1")
    p.add_argument("--etapa2")
    p.add_argument("--micro")
    p.add_argument("--etapa3")
    p.add_argument("--ijvm")
    p.add_argument("--regs", default="entradas/registradores.txt")
    p.add_argument("--dados", default="entradas/dados.txt")
    p.add_argument("--saida", default="saidas/log.txt")
    p.add_argument("--dados-saida", default="saidas/dados.txt")
    args = p.parse_args()

    log = Log(args.saida)

    if args.etapa1:
        executar_ula(args.etapa1, log, A_ETAPA1, B_ETAPA1, False)
    elif args.etapa2:
        executar_ula(args.etapa2, log, A_ETAPA2, B_ETAPA2, True)
    elif args.micro:
        executar_micro(args.micro, args.regs, log)
    elif args.etapa3:
        executar_etapa3(args.etapa3, args.regs, args.dados, args.dados_saida, log)
    elif args.ijvm:
        pass
    else:
        p.print_help()
        return

    log.salvar()


if __name__ == "__main__":
    main()
