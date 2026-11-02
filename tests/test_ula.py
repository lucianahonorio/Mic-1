import unittest

from mic1.ula import ula, ula1bit


class TestUla(unittest.TestCase):
    def confere(self, controle, a, b, sd, vai_um, n, z):
        self.assertEqual(ula(controle, a, b), (sd, vai_um, n, z))

    def test_exemplo_pdf_1bit(self):
        self.assertEqual(ula1bit("111100", 1, 1), (0, 1))

    def test_and(self):
        self.confere("00001100", 0b1100, 0b1010, 0b1000, 0, 0, 0)

    def test_or(self):
        self.confere("00011100", 0b1100, 0b1010, 0b1110, 0, 0, 0)

    def test_or_nao_gera_vai_um(self):
        self.confere("00011100", 0xFFFFFFFF, 1, 0xFFFFFFFF, 0, 1, 0)

    def test_not_b(self):
        self.confere("00101100", 5, 3, 0xFFFFFFFC, 0, 1, 0)

    def test_not_b_de_menos_um(self):
        self.confere("00100100", 0, 0xFFFFFFFF, 0, 0, 0, 1)

    def test_soma(self):
        self.confere("00111100", 5, 3, 8, 0, 0, 0)

    def test_inva_b_menos_a(self):
        self.confere("00111111", 5, 3, 0xFFFFFFFE, 0, 1, 0)

    def test_inva_menos_a(self):
        self.confere("00111011", 5, 3, 0xFFFFFFFB, 0, 1, 0)

    def test_inc_b_mais_um(self):
        self.confere("00110101", 5, 3, 4, 0, 0, 0)

    def test_ena_zero(self):
        self.confere("00110100", 5, 3, 3, 0, 0, 0)

    def test_enb_zero(self):
        self.confere("00111000", 5, 3, 5, 0, 0, 0)

    def test_enb_zero_and(self):
        self.confere("00001000", 5, 3, 0, 0, 0, 1)

    def test_vai_um(self):
        self.confere("00111100", 0xFFFFFFFF, 1, 0, 1, 0, 1)

    def test_n(self):
        self.confere("00110100", 0, 0x80000000, 0x80000000, 0, 1, 0)

    def test_sll8_negativo(self):
        self.confere("10110100", 0, 0xFFFFFF85, 0xFFFF8500, 0, 1, 0)

    def test_sll8_perde_bit_de_sinal(self):
        self.confere("10110100", 0, 0x80000001, 0x00000100, 0, 0, 0)

    def test_sra1_negativo_par(self):
        self.confere("01110100", 0, 0xFFFFFFF8, 0xFFFFFFFC, 0, 1, 0)

    def test_sra1_negativo_impar(self):
        self.confere("01110100", 0, 0xFFFFFFF9, 0xFFFFFFFC, 0, 1, 0)

    def test_sra1_menos_um(self):
        self.confere("01110100", 0, 0xFFFFFFFF, 0xFFFFFFFF, 0, 1, 0)

    def test_sll8_e_sra1_juntos(self):
        with self.assertRaises(ValueError):
            ula("11111100", 1, 1)


if __name__ == "__main__":
    unittest.main()
