import argparse
import os

from mic1.registradores import Registradores
from mic1.memoria import Memoria
from mic1.cpu import CPU
from mic1.tradutor import traduzir
from mic1.desmontador import descrever, operacao_texto
from mic1.log import Log
from mic1.ula import ula, operacao
from mic1.bits import mask32, bin32

A_ETAPA1 = 0xFFFFFFFF
B_ETAPA1 = 1
A_ETAPA2 = 1
B_ETAPA2 = 0x80000000
MOSTRAR_A_INVERTIDO = False


def ler_linhas(caminho):
    with open(caminho, encoding="utf-8-sig") as f:
        return [l.strip() for l in f if l.strip()]


def executar_ula(caminho, log, a, b, etapa2):
    with open(caminho, encoding="utf-8-sig") as f:
        linhas = [l.strip() for l in f]

    log.escrever("b = " + bin32(b))
    log.escrever("a = " + bin32(a))
    log.escrever()
    log.escrever("Start of Program")
    log.separador()

    pc = 0
    while True:
        pc += 1
        ir = linhas[pc - 1] if pc <= len(linhas) else ""
        controle = ir if etapa2 else "00" + ir
        valida = (len(controle) == 8 and all(c in "01" for c in controle)
                  and controle[:2] != "11")
        if ir != "" and valida:
            nome_s = "Sd" if etapa2 else "S"
            log.escrever("Cycle " + str(pc) + "  " + nome_s + " = " + operacao_texto(controle))
        else:
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

        # a palavra tem que ter 6 bits (etapa 1) ou 8 bits (etapa 2), só com 0 e 1
        if len(controle) != 8 or any(c not in "01" for c in controle):
            log.escrever("> Error, invalid control signals.")
            log.separador()
            continue

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

        log.escrever("Cycle " + str(ciclo) + "  " + descrever(controle, seletor_c, None, codigo_b))
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
        log.escrever("Cycle " + str(ciclo) + "  " + descrever(controle, seletor_c, memoria, codigo_b))
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


def ler_instrucoes(caminho):
    instrucoes = []
    with open(caminho, encoding="utf-8-sig") as f:
        for linha in f:
            # permite comentários com # no arquivo de instruções
            linha = linha.split("#")[0].strip()
            if linha:
                instrucoes.append(linha)
    return instrucoes


def executar_ijvm(caminho, caminho_regs, caminho_dados, caminho_dados_saida, log):
    instrucoes = ler_instrucoes(caminho)

    regs = Registradores()
    regs.carregar(caminho_regs)
    mem = Memoria(caminho_dados)
    mem.carregar()
    cpu = CPU(regs, mem)

    log.separador()
    log.escrever("Program")
    log.escrever("*" * 31)
    for instrucao in instrucoes:
        log.escrever(instrucao)
    log.separador()
    log.memoria("Initial memory state", mem.copia())
    log.escrever("*" * 31)
    log.registradores("Initial register state", regs.valores, estrelas=True)
    log.separador()
    log.escrever("Start of Program")

    ciclo = 0
    for numero, instrucao in enumerate(instrucoes, 1):
        try:
            micros = traduzir(instrucao)
        except ValueError as erro:
            log.separador()
            log.escrever("> Error: " + str(erro) + ". EOP.")
            mem.salvar(caminho_dados_saida)
            return

        log.separador()
        log.separador()
        log.escrever("Instruction " + str(numero) + ": " + instrucao
                     + " (" + str(len(micros)) + " microinstructions)")
        log.separador()

        for i, (texto, palavra) in enumerate(micros):
            ciclo += 1
            controle, seletor_c, memoria, codigo_b = cpu.decodificar(palavra)

            if i > 0:
                log.separador()
            log.escrever("Cycle " + str(ciclo) + "  [" + instrucao + "]  " + texto)
            log.escrever("ir = " + controle + " " + seletor_c + " " + memoria + " " + codigo_b)
            if memoria == "11":
                # fetch não usa a ULA nem os barramentos
                log.escrever("b = -")
                log.escrever("c = -")
            else:
                nomes_c = regs.habilitados_c(seletor_c)
                # com ENB = 0 o barramento B não entra na ULA
                usa_b = controle[5] == "1"
                log.escrever("b = " + (regs.nome_b(int(codigo_b, 2)).lower() if usa_b else "-"))
                log.escrever("c = " + (", ".join(n.lower() for n in nomes_c) or "-"))
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

        log.separador()
        log.memoria("> Memory after " + instrucao, mem.copia())

    log.separador()
    log.separador()
    log.escrever("No more instructions, EOP.")
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
    p.add_argument("--saida")
    p.add_argument("--dados-saida")
    args = p.parse_args()

    # cada modo salva no próprio arquivo, com o mesmo nome do gabarito
    if args.etapa1:
        nome = "etapa1"
    elif args.etapa2:
        nome = "etapa2_tarefa1"
    elif args.micro:
        nome = "etapa2_tarefa2"
    elif args.etapa3:
        nome = "etapa3_tarefa1"
    else:
        nome = "ijvm"
    if args.saida is None:
        args.saida = "saidas/saida_" + nome + ".txt"
    if args.dados_saida is None:
        args.dados_saida = "saidas/dados_" + nome + ".txt"
    for caminho in (args.saida, args.dados_saida):
        pasta = os.path.dirname(caminho)
        if pasta:
            os.makedirs(pasta, exist_ok=True)

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
        executar_ijvm(args.ijvm, args.regs, args.dados, args.dados_saida, log)
    else:
        p.print_help()
        return

    log.salvar()


if __name__ == "__main__":
    main()
