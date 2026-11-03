import os
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SINAL = "11111111111111111111111110000001"
ZEROS = "00000000000000000000000010000001"

DIVERGENCIAS_2_1 = {
    13: ("sd = 00000000000000000000001000000000",
         "sd = 00000000000000000000000100000000",
         "SLL8 desloca 8 bits (PDF): 0x80000001 << 8 = 0x100; o exemplo deslocou 9"),
    26: ("n = 0",
         "n = 1",
         "Sd = 0xC0000000 tem o bit 31 em 1, entao e negativo e N = 1"),
}

DIVERGENCIAS_2_2 = {
    4: ("101110001000000000111", None,
        "essa linha nao esta no programa_etapa2_tarefa2.txt"),
    45: ("sp = " + ZEROS, "sp = " + SINAL, "codigo 2 = MBR com sinal (PDF)"),
    46: ("lv = " + ZEROS, "lv = " + SINAL, "codigo 2 = MBR com sinal (PDF)"),
    63: ("sp = " + ZEROS, "sp = " + SINAL, "inicio do ciclo 2 = fim do ciclo 1"),
    64: ("lv = " + ZEROS, "lv = " + SINAL, "inicio do ciclo 2 = fim do ciclo 1"),
    75: ("sp = " + SINAL, "sp = " + ZEROS, "codigo 3 = MBRU com zeros (PDF)"),
    76: ("lv = " + ZEROS, "lv = " + SINAL, "lv vem do ciclo 1"),
    85: ("b_bus = opc", "b_bus = tos", "codigo 7 = TOS (PDF)"),
    94: ("lv = " + ZEROS, "lv = " + SINAL, "lv vem do ciclo 1"),
    105: ("sp = " + SINAL, "sp = " + ZEROS, "sp vem do ciclo 2"),
    106: ("lv = " + ZEROS, "lv = " + SINAL, "lv vem do ciclo 1"),
    110: ("h = 00000000000000000000000000000010",
          "h = 00000000000000000000000000000100",
          "H + TOS + 1 = 1 + 2 + 1 = 4; o exemplo usou OPC"),
    112: ("Cycle 3", "Cycle 4", "contagem certa de ciclos"),
}


def rodar(*argumentos):
    with tempfile.TemporaryDirectory() as pasta:
        saida = os.path.join(pasta, "log.txt")
        dados = os.path.join(pasta, "dados.txt")
        comando = [sys.executable, "main.py"] + list(argumentos)
        comando += ["--saida", saida, "--dados-saida", dados]
        subprocess.run(comando, cwd=RAIZ, check=True, capture_output=True)
        with open(saida, encoding="utf-8") as f:
            return f.read().splitlines()


def gabarito(nome):
    with open(os.path.join(RAIZ, "gabaritos", nome), encoding="utf-8") as f:
        return f.read().splitlines()


def corrigir(linhas, divergencias):
    resultado = []
    for numero, linha in enumerate(linhas, 1):
        if numero in divergencias:
            nossa = divergencias[numero][1]
            if nossa is not None:
                resultado.append(nossa)
        else:
            resultado.append(linha)
    return resultado


class TestEtapas(unittest.TestCase):
    def confere_divergencias(self, linhas, divergencias):
        for numero, (original, nossa, motivo) in divergencias.items():
            self.assertEqual(linhas[numero - 1], original, motivo)

    def test_etapa1(self):
        saida = rodar("--etapa1", "entradas/programa_etapa1_teste.txt")
        self.assertEqual(saida, gabarito("saída_etapa1.txt"))

    def test_etapa1_linha_invalida(self):
        with tempfile.TemporaryDirectory() as pasta:
            programa = os.path.join(pasta, "programa.txt")
            with open(programa, "w") as f:
                f.write("1111\n11a100\n111100\n")
            saida = rodar("--etapa1", programa)
        self.assertEqual(saida.count("> Error, invalid control signals."), 2)
        self.assertIn("co = 1", saida)
        self.assertIn("> Line is empty, EOP.", saida)

    def test_etapa2_tarefa1(self):
        saida = rodar("--etapa2", "entradas/programa_etapa2_tarefa1.txt")
        esperado = gabarito("saída_etapa2_tarefa1.txt")
        self.confere_divergencias(esperado, DIVERGENCIAS_2_1)
        self.assertEqual(saida, corrigir(esperado, DIVERGENCIAS_2_1))

    def test_etapa2_tarefa2(self):
        saida = rodar("--micro", "entradas/programa_etapa2_tarefa2.txt",
                      "--regs", "entradas/registradores_etapa2_tarefa2.txt")
        esperado = gabarito("saída_etapa2_tarefa2.txt")
        self.confere_divergencias(esperado, DIVERGENCIAS_2_2)
        self.assertEqual(saida, corrigir(esperado, DIVERGENCIAS_2_2))

    def test_etapa3_tarefa1(self):
        # o gabarito parte de outro estado inicial (MAR = SP = 4, mem[4] = 2,
        # 16 linhas), então usamos os arquivos _teste copiados dele
        saida = rodar("--etapa3", "entradas/microinstruções_etapa3_tarefa1.txt",
                      "--regs", "entradas/registradores_etapa3_tarefa1_teste.txt",
                      "--dados", "entradas/dados_etapa3_tarefa1_teste.txt")
        self.assertEqual(saida, gabarito("saída_etapa3_tarefa1.txt"))

    def test_etapa3_tarefa1_original(self):
        # com os arquivos originais só conferimos que roda até o fim
        saida = rodar("--etapa3", "entradas/microinstruções_etapa3_tarefa1.txt",
                      "--regs", "entradas/registradores_etapa3_tarefa1.txt",
                      "--dados", "entradas/dados_etapa3_tarefa1.txt")
        self.assertEqual(saida[-2:], ["Cycle 3", "No more lines, EOP."])


if __name__ == "__main__":
    unittest.main()
