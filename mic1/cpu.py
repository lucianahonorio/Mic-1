from mic1.ula import ula
from mic1.registradores import Registradores
from mic1.memoria import Memoria


class CPU:
    def __init__(self, registradores, memoria=None):
        self.regs = registradores
        self.mem = memoria

    def decodificar(self, palavra):
        pass

    def executar(self, palavra):
        pass
