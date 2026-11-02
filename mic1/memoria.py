from mic1.bits import mask32


class Memoria:
    def __init__(self, caminho):
        self.caminho = caminho
        self.linhas = []

    def carregar(self):
        # cada linha do arquivo é uma palavra de 32 bits; a linha i é o endereço i
        self.linhas = []
        with open(self.caminho) as f:
            for linha in f:
                linha = linha.strip()
                if linha == "":
                    continue
                self.linhas.append(int(linha, 2))

    def confere(self, endereco):
        if endereco < 0 or endereco >= len(self.linhas):
            raise IndexError("endereco fora da memoria: " + str(endereco)
                             + " (a memoria tem " + str(len(self.linhas)) + " linhas)")

    def ler(self, endereco):
        self.confere(endereco)
        return self.linhas[endereco]

    def escrever(self, endereco, valor):
        self.confere(endereco)
        self.linhas[endereco] = mask32(valor)

    def copia(self):
        return list(self.linhas)

    def salvar(self, caminho=None):
        # por padrão salva numa cópia, para não estragar o arquivo de entrada
        if caminho is None:
            caminho = self.caminho
        with open(caminho, "w") as f:
            for valor in self.linhas:
                f.write(format(valor, "032b") + "\n")
