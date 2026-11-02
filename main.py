import argparse

from mic1.registradores import Registradores
from mic1.memoria import Memoria
from mic1.cpu import CPU
from mic1.tradutor import traduzir
from mic1.log import Log


def ler_linhas(caminho):
    with open(caminho) as f:
        return [l.strip() for l in f if l.strip()]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--etapa1")
    p.add_argument("--micro")
    p.add_argument("--ijvm")
    p.add_argument("--regs", default="entradas/registradores.txt")
    p.add_argument("--dados", default="entradas/dados.txt")
    p.add_argument("--saida", default="saidas/log.txt")
    args = p.parse_args()

    log = Log(args.saida)

    if args.etapa1:
        pass
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
