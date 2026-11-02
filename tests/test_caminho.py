import unittest

from mic1.registradores import Registradores
from mic1.cpu import CPU


class TestCaminho(unittest.TestCase):
    def setUp(self):
        self.regs = Registradores()
        v = self.regs.valores
        v["MDR"] = 10
        v["PC"] = 11
        v["MBR"] = 0x85
        v["SP"] = 14
        v["LV"] = 15
        v["CPP"] = 16
        v["TOS"] = 17
        v["OPC"] = 18
        self.cpu = CPU(self.regs)

    def test_decodificador_b(self):
        esperado = [
            ("MDR", 10),
            ("PC", 11),
            ("MBR", 0xFFFFFF85),
            ("MBRU", 0x00000085),
            ("SP", 14),
            ("LV", 15),
            ("CPP", 16),
            ("TOS", 17),
            ("OPC", 18),
        ]
        for codigo in range(9):
            nome, valor = esperado[codigo]
            self.assertEqual(self.regs.nome_b(codigo), nome)
            self.assertEqual(self.regs.barramento_b(codigo), valor)

    def test_mbr_positivo(self):
        self.regs.valores["MBR"] = 0x05
        self.assertEqual(self.regs.barramento_b(2), 5)
        self.assertEqual(self.regs.barramento_b(3), 5)

    def test_seletor_c_exemplo_pdf(self):
        self.assertEqual(self.regs.habilitados_c("100001000"), ["H", "SP"])
        antes = self.regs.copia()
        self.regs.escrever_c("100001000", 7)
        for nome, valor in self.regs.valores.items():
            if nome in ("H", "SP"):
                self.assertEqual(valor, 7)
            else:
                self.assertEqual(valor, antes[nome])

    def test_seletor_c_todos(self):
        self.regs.escrever_c("111111111", 99)
        for nome in ["H", "OPC", "TOS", "CPP", "LV", "SP", "PC", "MDR", "MAR"]:
            self.assertEqual(self.regs.valores[nome], 99)
        self.assertEqual(self.regs.valores["MBR"], 0x85)

    def test_microinstrucao_escreve_varios(self):
        self.cpu.executar("00110100" + "111000000" + "0000")
        v = self.regs.valores
        self.assertEqual((v["H"], v["OPC"], v["TOS"]), (10, 10, 10))
        self.assertEqual(v["CPP"], 16)

    def test_exemplos_pdf_bits_0100_sao_sp(self):
        v = self.regs.valores
        self.cpu.executar("001101001010000000000")
        self.assertEqual(v["H"], 10)
        self.assertEqual(v["TOS"], 10)
        self.assertEqual(self.regs.nome_b(0b0100), "SP")
        self.cpu.executar("001111000000000100100")
        self.assertEqual(v["MDR"], 10 + 14)

    def test_fetch(self):
        self.cpu.executar("10000101" + "000000000" + "11" + "0000")
        self.assertEqual(self.regs.valores["MBR"], 0x85)
        self.assertEqual(self.regs.valores["H"], 0x00000085)

    def test_fetch_nao_passa_pela_ula(self):
        antes = self.regs.copia()
        self.cpu.executar("11111111" + "000000000" + "11" + "0000")
        self.assertEqual(self.regs.valores["H"], 0xFF)
        for nome in ["OPC", "TOS", "CPP", "LV", "SP", "PC", "MDR", "MAR"]:
            self.assertEqual(self.regs.valores[nome], antes[nome])


if __name__ == "__main__":
    unittest.main()
