# Monta o texto de uma microinstrução a partir dos bits, como "MAR = SP = SP+1; rd".
# Serve para o log mostrar o que cada ciclo faz.

from mic1.registradores import ORDEM_B, ORDEM_C

# F0 F1 ENA ENB INVA INC -> operação da ULA (tabela do livro), com A = H e B = barramento B
OPERACOES = {
    "011000": "{a}",
    "010100": "{b}",
    "011010": "NOT {a}",
    "101100": "NOT {b}",
    "111100": "{a}+{b}",
    "111101": "{a}+{b}+1",
    "111001": "{a}+1",
    "110101": "{b}+1",
    "111111": "{b}-{a}",
    "110110": "{b}-1",
    "111011": "-{a}",
    "001100": "{a} AND {b}",
    "011100": "{a} OR {b}",
    "010000": "0",
    "110001": "1",
    "110010": "-1",
}


def soma_texto(bits):
    # F0 F1 = 11 (somador): Sd = (A com ENA e INVA) + (B com ENB) + INC
    ena, enb, inva, inc = bits[2], bits[3], bits[4], bits[5]
    termos = []
    if ena == "1":
        termos.append("NOT {a}" if inva == "1" else "{a}")
    elif inva == "1":
        termos.append("-1")  # A zerado e invertido: todos os bits em 1
    if enb == "1":
        termos.append("{b}")
    if inc == "1":
        termos.append("1")
    if len(termos) > 1 and termos[0] == "NOT {a}":
        termos[0] = "(NOT {a})"  # deixa claro que o NOT é só do A
    return "+".join(termos) or "0"


def logica_texto(bits):
    # F0 F1 = 00 (AND), 01 (OR) ou 10 (NOT B); o INC não entra nessas operações
    f, ena, enb, inva = bits[:2], bits[2], bits[3], bits[4]
    if ena == "1":
        a = "NOT {a}" if inva == "1" else "{a}"
    else:
        a = "-1" if inva == "1" else "0"
    b = "{b}" if enb == "1" else "0"
    if f == "10":
        return "NOT {b}" if enb == "1" else "-1"
    if f == "00":
        if a == "0" or b == "0":
            return "0"
        return b if a == "-1" else a + " AND " + b
    if a == "-1":
        return "-1"
    if a == "0" or b == "0":
        return a if b == "0" else b
    return a + " OR " + b


def operacao_texto(controle, a="A", b="B"):
    # controle tem 8 bits: SLL8 SRA1 F0 F1 ENA ENB INVA INC
    bits = controle[2:]
    modelo = OPERACOES.get(bits)
    if modelo is None:
        modelo = soma_texto(bits) if bits[:2] == "11" else logica_texto(bits)
    texto = modelo.format(a=a, b=b)
    if controle[0] == "1":
        texto = "(" + texto + ") << 8"
    if controle[1] == "1":
        texto = "(" + texto + ") >> 1"
    return texto


def descrever(controle, seletor_c, memoria, codigo_b):
    # memoria = None nas microinstruções de 21 bits (etapa 2), que não têm READ/WRITE
    if memoria == "11":
        return "fetch (MBR = " + controle + "; H = MBR)"

    codigo = int(codigo_b, 2)
    nome_b = ORDEM_B[codigo] if codigo < len(ORDEM_B) else "?"
    expressao = operacao_texto(controle, "H", nome_b)

    # destinos na ordem MAR, MDR, PC, SP, LV, CPP, TOS, OPC, H (bit 0 ... bit 8)
    destinos = [ORDEM_C[i] for i in range(9) if seletor_c[8 - i] == "1"]
    texto = " = ".join(destinos + [expressao])

    if memoria == "01":
        texto += "; rd"
    elif memoria == "10":
        texto += "; wr"
    return texto
