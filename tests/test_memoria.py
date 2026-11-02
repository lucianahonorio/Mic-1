import os
import tempfile
import unittest

from mic1.memoria import Memoria
from mic1.registradores import Registradores
from mic1.cpu import CPU


def arquivo_dados(pasta, valores):
    caminho = os.path.join(pasta, "dados.txt")
    with open(caminho, "w") as f:
        for v in valores:
            f.write(format(v, "032b") + "\n")
    return caminho


class TestMemoria(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        caminho = arquivo_dados(self.pasta.name, [0, 0, 1, 2, 4, 8, 16, 32])
        self.mem = Memoria(caminho)
        self.mem.carregar()

    def tearDown(self):
        self.pasta.cleanup()

    def test_carregar(self):
        self.assertEqual(self.mem.copia(), [0, 0, 1, 2, 4, 8, 16, 32])

    def test_ler(self):
        self.assertEqual(self.mem.ler(5), 8)

    def test_escrever(self):
        self.mem.escrever(1, 0x1FFFFFFFF)
        self.assertEqual(self.mem.ler(1), 0xFFFFFFFF)

    def test_endereco_invalido(self):
        with self.assertRaises(IndexError):
            self.mem.ler(8)
        with self.assertRaises(IndexError):
            self.mem.escrever(-1, 0)

    def test_salvar_em_copia(self):
        self.mem.escrever(0, 7)
        copia = os.path.join(self.pasta.name, "copia.txt")
        self.mem.salvar(copia)
        with open(copia) as f:
            self.assertEqual(f.readline().strip(), format(7, "032b"))
        # o arquivo de entrada continua igual
        original = Memoria(self.mem.caminho)
        original.carregar()
        self.assertEqual(original.ler(0), 0)


class TestCpuMemoria(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        caminho = arquivo_dados(self.pasta.name, [0, 0, 0, 0, 2, 0, 0, 0])
        self.mem = Memoria(caminho)
        self.mem.carregar()
        self.regs = Registradores()
        self.regs.valores["MAR"] = 4
        self.regs.valores["SP"] = 4
        self.cpu = CPU(self.regs, self.mem)

    def tearDown(self):
        self.pasta.cleanup()

    def test_read(self):
        # SP = SP + 1; rd -> MDR = mem[MAR], com MAR = 4
        self.cpu.executar("00110101000001000010100")
        self.assertEqual(self.regs.valores["SP"], 5)
        self.assertEqual(self.regs.valores["MDR"], 2)

    def test_write_depois_do_barramento_c(self):
        # MAR = SP; wr -> a escrita usa o MAR já atualizado pela ULA
        self.regs.valores["SP"] = 5
        self.regs.valores["MDR"] = 9
        self.cpu.executar("00110100000000001100100")
        self.assertEqual(self.regs.valores["MAR"], 5)
        self.assertEqual(self.mem.ler(5), 9)

    def test_read_depois_do_barramento_c(self):
        # MAR = H; rd, com H = 4. O exemplo (6) do PDF usa C = 100000000,
        # que habilita o H (bit 8); para o MAR o certo é 000000001 (bit 0)
        self.regs.valores["H"] = 4
        self.regs.valores["MAR"] = 0
        self.cpu.executar("00111000000000001010000")
        self.assertEqual(self.regs.valores["MAR"], 4)
        self.assertEqual(self.regs.valores["MDR"], 2)


if __name__ == "__main__":
    unittest.main()
