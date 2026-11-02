from mic1.ula import ula
from mic1.registradores import Registradores
from mic1.memoria import Memoria


class CPU:
    def __init__(self, registradores, memoria=None):
        self.regs = registradores
        self.mem = memoria

    def decodificar(self, palavra):
        controle = palavra[0:8]
        seletor_c = palavra[8:17]
        if len(palavra) == 23:
            memoria = palavra[17:19]
            codigo_b = palavra[19:23]
        else:
            memoria = "00"
            codigo_b = palavra[17:21]
        return controle, seletor_c, memoria, codigo_b

    def executar(self, palavra):
        controle, seletor_c, memoria, codigo_b = self.decodificar(palavra)
        v = self.regs.valores

        if memoria == "11":
            v["MBR"] = int(controle, 2)
            v["H"] = v["MBR"]
            return

        a = v["H"]
        b = self.regs.barramento_b(int(codigo_b, 2))
        sd, vai_um, n, z = ula(controle, a, b)
        self.regs.escrever_c(seletor_c, sd)

        if memoria == "10":
            self.mem.escrever(v["MAR"], v["MDR"])
        if memoria == "01":
            v["MDR"] = self.mem.ler(v["MAR"])
