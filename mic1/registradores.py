from mic1.bits import mask32, estende_sinal8

NOMES = ["H", "OPC", "TOS", "CPP", "LV", "SP", "PC", "MDR", "MAR", "MBR"]

ORDEM_B = ["MDR", "PC", "MBR", "MBRU", "SP", "LV", "CPP", "TOS", "OPC"]

ORDEM_C = ["MAR", "MDR", "PC", "SP", "LV", "CPP", "TOS", "OPC", "H"]


class Registradores:
    def __init__(self):
        self.valores = {nome: 0 for nome in NOMES}

    def carregar(self, caminho):
        with open(caminho) as f:
            for linha in f:
                linha = linha.strip()
                if linha == "":
                    continue
                nome, bits = linha.split("=")
                self.valores[nome.strip().upper()] = int(bits.strip(), 2)

    def nome_b(self, codigo):
        return ORDEM_B[codigo]

    def barramento_b(self, codigo):
        nome = ORDEM_B[codigo]
        if nome == "MBR":
            return estende_sinal8(self.valores["MBR"])
        if nome == "MBRU":
            return self.valores["MBR"] & 0xFF
        return self.valores[nome]

    def habilitados_c(self, seletor):
        nomes = []
        for i in range(9):
            if seletor[i] == "1":
                nomes.append(ORDEM_C[8 - i])
        return nomes

    def escrever_c(self, seletor, valor):
        for nome in self.habilitados_c(seletor):
            self.valores[nome] = mask32(valor)

    def copia(self):
        return dict(self.valores)
