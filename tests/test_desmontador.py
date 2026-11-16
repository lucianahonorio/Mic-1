import random
import unittest

from mic1.desmontador import descrever, operacao_texto
from mic1.tradutor import bipush, dup, iload
from mic1.ula import ula

M = 0xFFFFFFFF


def avaliar(texto, a, b):
    # transforma o texto em expressão do Python para conferir com a ULA
    texto = (texto.replace("NOT A", "~A").replace("NOT B", "~B")
             .replace(" AND ", "&").replace(" OR ", "|"))
    deslocar = None
    if texto.endswith(") << 8"):
        texto, deslocar = texto[1:-6], "sll8"
    elif texto.endswith(") >> 1"):
        texto, deslocar = texto[1:-6], "sra1"
    valor = eval(texto, {"A": a, "B": b}) & M
    if deslocar == "sll8":
        valor = (valor << 8) & M
    elif deslocar == "sra1":
        valor = ((valor - (1 << 32) if valor >> 31 else valor) >> 1) & M
    return valor


def separar(palavra):
    return palavra[:8], palavra[8:17], palavra[17:19], palavra[19:]


class TestDesmontador(unittest.TestCase):
    def test_texto_bate_com_a_ula(self):
        # as 64 combinações de F0 F1 ENA ENB INVA INC, com e sem deslocamento
        random.seed(1)
        for desloc in ("00", "10", "01"):
            for i in range(64):
                controle = desloc + format(i, "06b")
                texto = operacao_texto(controle)
                for _ in range(50):
                    a, b = random.getrandbits(32), random.getrandbits(32)
                    self.assertEqual(ula(controle, a, b)[0], avaliar(texto, a, b),
                                     controle + " -> " + texto)

    def test_instrucoes_da_ijvm(self):
        # o texto gerado pelos bits é o mesmo que o tradutor escreve
        # (só o primeiro passo do BIPUSH, que o PDF escreve "SP = MAR", muda a ordem)
        for texto, palavra in iload(2) + dup() + bipush("00110011")[1:]:
            self.assertEqual(descrever(*separar(palavra)), texto)
        self.assertEqual(descrever(*separar(bipush("00110011")[0][1])), "MAR = SP = SP+1")

    def test_exemplos(self):
        self.assertEqual(descrever(*separar("00110101000001000010100")), "SP = SP+1; rd")
        self.assertEqual(descrever(*separar("00110100000000001100100")), "MAR = SP; wr")
        self.assertEqual(descrever("00111101", "100000000", None, "0111"), "H = H+TOS+1")
        self.assertEqual(operacao_texto("00111110"), "(NOT A)+B")


if __name__ == "__main__":
    unittest.main()
