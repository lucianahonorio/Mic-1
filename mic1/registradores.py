from mic1.bits import mask32, estende_sinal8

NOMES = ["H", "OPC", "TOS", "CPP", "LV", "SP", "PC", "MDR", "MAR", "MBR"]

ORDEM_B = ["MDR", "PC", "MBR", "MBRU", "SP", "LV", "CPP", "TOS", "OPC"]

ORDEM_C = ["MAR", "MDR", "PC", "SP", "LV", "CPP", "TOS", "OPC", "H"]


class Registradores:
    def __init__(self):
        self.valores = {nome: 0 for nome in NOMES}

    def carregar(self, caminho):
        pass

    def barramento_b(self, codigo):
        pass

    def escrever_c(self, seletor, valor):
        pass

    def copia(self):
        return dict(self.valores)
