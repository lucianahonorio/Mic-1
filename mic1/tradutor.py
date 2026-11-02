def iload(x):
    return []


def dup():
    return []


def bipush(byte):
    return []


def traduzir(linha):
    partes = linha.split()
    op = partes[0].upper()
    if op == "ILOAD":
        return iload(int(partes[1]))
    if op == "DUP":
        return dup()
    if op == "BIPUSH":
        return bipush(partes[1])
    raise ValueError("instrucao desconhecida: " + linha)
