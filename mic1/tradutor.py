# Traduz as instruções da IJVM em microinstruções de 23 bits:
#   ULA (8) | barramento C (9) | memória (2: WRITE READ) | barramento B (4)

# controle da ULA: SLL8 SRA1 F0 F1 ENA ENB INVA INC
ULA_B = "00110100"        # Sd = B
ULA_B_MAIS_1 = "00110101"  # Sd = B + 1
ULA_A = "00111000"        # Sd = A (= H)
ULA_A_MAIS_1 = "00111001"  # Sd = A + 1

# barramento C: H OPC TOS CPP LV SP PC MDR MAR (bit 8 ... bit 0)
C_NADA = "000000000"
C_H = "100000000"
C_MAR = "000000001"
C_MAR_SP = "000001001"
C_TOS = "001000000"
C_MDR = "000000010"
C_MDR_TOS = "001000010"

# memória: WRITE READ
NADA = "00"
RD = "01"
WR = "10"
FETCH = "11"

# barramento B
B_MDR = "0000"
B_SP = "0100"
B_LV = "0101"
B_TOS = "0111"
B_NENHUM = "0000"  # quando ENB = 0 o valor do barramento B não é usado


def micro(texto, ula, c, mem, b):
    return texto, ula + c + mem + b


def iload(x):
    if x < 0:
        raise ValueError("ILOAD precisa de um argumento >= 0")
    lista = [micro("H = LV", ULA_B, C_H, NADA, B_LV)]
    for _ in range(x):
        lista.append(micro("H = H+1", ULA_A_MAIS_1, C_H, NADA, B_NENHUM))
    lista.append(micro("MAR = H; rd", ULA_A, C_MAR, RD, B_NENHUM))
    lista.append(micro("MAR = SP = SP+1; wr", ULA_B_MAIS_1, C_MAR_SP, WR, B_SP))
    lista.append(micro("TOS = MDR", ULA_B, C_TOS, NADA, B_MDR))
    return lista


def dup():
    return [
        micro("MAR = SP = SP+1", ULA_B_MAIS_1, C_MAR_SP, NADA, B_SP),
        micro("MDR = TOS; wr", ULA_B, C_MDR, WR, B_TOS),
    ]


def ler_byte(texto):
    # aceita 8 bits em binário (como no PDF) ou um número (decimal, 0x.., 0b..)
    if len(texto) == 8 and set(texto) <= {"0", "1"}:
        return texto
    valor = int(texto, 0)
    if valor < -128 or valor > 255:
        raise ValueError("BIPUSH precisa de um byte: " + texto)
    return format(valor & 0xFF, "08b")


def bipush(byte):
    byte = ler_byte(byte)
    return [
        micro("SP = MAR = SP+1", ULA_B_MAIS_1, C_MAR_SP, NADA, B_SP),
        # fetch: os 8 primeiros bits vão para o MBR e depois para o H, sem passar pela ULA
        micro("fetch (MBR = " + byte + "; H = MBR)", byte, C_NADA, FETCH, B_NENHUM),
        micro("MDR = TOS = H; wr", ULA_A, C_MDR_TOS, WR, B_NENHUM),
    ]


def traduzir(linha):
    partes = linha.split()
    op = partes[0].upper()
    if op == "ILOAD" and len(partes) == 2:
        return iload(int(partes[1]))
    if op == "DUP" and len(partes) == 1:
        return dup()
    if op == "BIPUSH" and len(partes) == 2:
        return bipush(partes[1])
    raise ValueError("instrucao invalida: " + linha)
