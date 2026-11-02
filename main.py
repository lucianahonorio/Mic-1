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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--etapa1")
    p.add_argument("--etapa2")
    p.add_argument("--micro")
    p.add_argument("--ijvm")
    p.add_argument("--regs", default="entradas/registradores.txt")
    p.add_argument("--dados", default="entradas/dados.txt")
    p.add_argument("--saida", default="saidas/log.txt")
    args = p.parse_args()

    log = Log(args.saida)

    if args.etapa1:
        executar_ula(args.etapa1, log, A_ETAPA1, B_ETAPA1, False)
    elif args.etapa2:
        executar_ula(args.etapa2, log, A_ETAPA2, B_ETAPA2, True)
    elif args.micro:
        pass
    elif args.ijvm:
        pass
    else:
        p.print_help()
        return

    log.salvar()


if __name__ == "__main__":
    main()
