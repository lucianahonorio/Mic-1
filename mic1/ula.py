from mic1.bits import mask32, com_sinal


def ula1bit(controle, a, b, vem_um=None):
    f0 = int(controle[0])
    f1 = int(controle[1])
    ena = int(controle[2])
    enb = int(controle[3])
    inva = int(controle[4])
    inc = int(controle[5])

    # None indica o bit 0: o INC entra como vem-um (A + 1, e -A com INVA + INC)
    if vem_um is None:
        vem_um = inc

    # como na Figura 1: A passa pelo AND com ENA e depois pelo XOR com INVA
    a = a & ena
    b = b & enb
    a = a ^ inva

    # só o somador gera vai-um; em AND, OR e NOT B ele é 0
    if f0 == 0 and f1 == 0:
        return a & b, 0
    if f0 == 0 and f1 == 1:
        return a | b, 0
    if f0 == 1 and f1 == 0:
        return 1 - b, 0
    s = a ^ b ^ vem_um
    vai_um = (a & b) | (a & vem_um) | (b & vem_um)
    return s, vai_um


def operacao(controle, a, b):
    a = mask32(a)
    b = mask32(b)
    s = 0
    vai_um = None
    for i in range(32):
        # o vai-um de cada bit vira o vem-um do próximo; o do bit 31 é o co final
        bit, vai_um = ula1bit(controle, (a >> i) & 1, (b >> i) & 1, vai_um)
        s = s | (bit << i)
    return s, vai_um


def deslocador(controle, s):
    sll8 = controle[0] == "1"
    sra1 = controle[1] == "1"
    if sll8 and sra1:
        raise ValueError("sinais de controle invalidos")
    if sll8:
        return mask32(s << 8)
    if sra1:
        return mask32(com_sinal(s) >> 1)
    return s


def ula(controle, a, b):
    s, vai_um = operacao(controle[2:], a, b)
    sd = deslocador(controle, s)
    n = sd >> 31
    z = 1 if sd == 0 else 0
    return sd, vai_um, n, z
