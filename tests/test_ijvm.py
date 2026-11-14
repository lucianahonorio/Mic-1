import os
import subprocess
import sys
import tempfile
import unittest

from mic1.tradutor import traduzir
from mic1.memoria import Memoria
from mic1.registradores import Registradores
from mic1.cpu import CPU

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def palavras(linha):
    return [p for _, p in traduzir(linha)]


class TestTradutor(unittest.TestCase):
    def test_tamanho_das_palavras(self):
        for linha in ["ILOAD 0", "ILOAD 3", "DUP", "BIPUSH 00110011"]:
            for p in palavras(linha):
                self.assertEqual(len(p), 23)

    def test_iload_numero_de_microinstrucoes(self):
        # H = LV, x vezes H = H+1, MAR = H; rd, MAR = SP = SP+1; wr, TOS = MDR
        self.assertEqual(len(traduzir("ILOAD 0")), 4)
        self.assertEqual(len(traduzir("ILOAD 1")), 5)
        self.assertEqual(len(traduzir("ILOAD 3")), 7)

    def test_mar_sp_igual_exemplo_5_do_pdf(self):
        # exemplo (5): SP = MAR = SP + 1 com rd; aqui o ILOAD usa o mesmo com wr
        self.assertEqual(palavras("ILOAD 0")[2], "00110101000001001" + "10" + "0100")

    def test_mar_h_rd(self):
        # o exemplo (6) do PDF habilita o H; o certo é o MAR (bit 0)
        self.assertEqual(palavras("ILOAD 0")[1], "00111000000000001010000")

    def test_bipush_fetch(self):
        # exemplo (7): os 8 primeiros bits são o byte, memória = 11
        self.assertEqual(palavras("BIPUSH 00110011")[1], "00110011000000000110000")

    def test_bipush_aceita_numero(self):
        self.assertEqual(palavras("BIPUSH 51")[1], palavras("BIPUSH 00110011")[1])
        self.assertEqual(palavras("bipush 0x33")[1], palavras("BIPUSH 00110011")[1])

    def test_instrucao_invalida(self):
        for linha in ["IADD", "DUP 1", "ILOAD", "ILOAD -1", "BIPUSH 300"]:
            with self.assertRaises(ValueError):
                traduzir(linha)


class TestExecucao(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        caminho = os.path.join(self.pasta.name, "dados.txt")
        with open(caminho, "w") as f:
            for v in [0, 0, 1, 2, 4, 8, 16, 32, 0, 0, 0, 0, 0, 0, 0, 0]:
                f.write(format(v, "032b") + "\n")
        self.mem = Memoria(caminho)
        self.mem.carregar()
        self.regs = Registradores()
        self.regs.valores.update(SP=7, LV=2, TOS=32)
        self.cpu = CPU(self.regs, self.mem)

    def tearDown(self):
        self.pasta.cleanup()

    def rodar(self, linha):
        for p in palavras(linha):
            self.cpu.executar(p)

    def test_bipush(self):
        self.rodar("BIPUSH 00110011")
        v = self.regs.valores
        self.assertEqual((v["SP"], v["MAR"], v["TOS"], v["MDR"], v["H"], v["MBR"]),
                         (8, 8, 0x33, 0x33, 0x33, 0x33))
        self.assertEqual(self.mem.ler(8), 0x33)

    def test_bipush_negativo_entra_com_zeros_no_h(self):
        self.rodar("BIPUSH 11111111")
        self.assertEqual(self.regs.valores["H"], 0xFF)
        self.assertEqual(self.mem.ler(8), 0xFF)

    def test_dup(self):
        self.rodar("DUP")
        v = self.regs.valores
        self.assertEqual((v["SP"], v["MAR"], v["MDR"], v["TOS"]), (8, 8, 32, 32))
        self.assertEqual(self.mem.ler(8), 32)

    def test_iload(self):
        self.rodar("ILOAD 3")  # LV + 3 = 5, mem[5] = 8
        v = self.regs.valores
        self.assertEqual((v["SP"], v["TOS"], v["H"]), (8, 8, 5))
        self.assertEqual(self.mem.ler(8), 8)

    def test_programa_do_pdf(self):
        for linha in ["BIPUSH 00110011", "DUP", "ILOAD 1"]:
            self.rodar(linha)
        self.assertEqual(self.mem.copia()[8:11], [0x33, 0x33, 2])
        self.assertEqual(self.regs.valores["SP"], 10)
        self.assertEqual(self.regs.valores["TOS"], 2)


class TestModoIjvm(unittest.TestCase):
    def test_main(self):
        with tempfile.TemporaryDirectory() as pasta:
            log = os.path.join(pasta, "log.txt")
            dados = os.path.join(pasta, "dados.txt")
            subprocess.run([sys.executable, "main.py",
                            "--ijvm", "entradas/instruções.txt",
                            "--regs", "entradas/registradores_etapa3_tarefa1.txt",
                            "--dados", "entradas/dados_etapa3_tarefa1.txt",
                            "--saida", log, "--dados-saida", dados],
                           cwd=RAIZ, check=True, capture_output=True)
            with open(log, encoding="utf-8") as f:
                texto = f.read()
            with open(dados) as f:
                final = [int(l, 2) for l in f if l.strip()]
        self.assertIn("Instruction 3: ILOAD 1 (5 microinstructions)", texto)
        self.assertIn("Cycle 10", texto)
        self.assertNotIn("Cycle 11", texto)
        self.assertTrue(texto.rstrip().endswith("No more instructions, EOP."))
        self.assertEqual(final[8:11], [0x33, 0x33, 2])


if __name__ == "__main__":
    unittest.main()
