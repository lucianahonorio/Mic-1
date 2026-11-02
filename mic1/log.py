ORDEM_LOG = ["MAR", "MDR", "PC", "MBR", "SP", "LV", "CPP", "TOS", "OPC", "H"]


class Log:
    def __init__(self, caminho):
        self.caminho = caminho
        self.linhas = []

    def escrever(self, texto=""):
        print(texto)
        self.linhas.append(texto)

    def separador(self, tamanho=60):
        self.escrever("=" * tamanho)

    def registradores(self, titulo, valores, estrelas=False):
        self.escrever(titulo)
        if estrelas:
            self.escrever("*" * 31)
        for nome in ORDEM_LOG:
            if nome == "MBR":
                bits = format(valores[nome], "08b")
            else:
                bits = format(valores[nome], "032b")
            self.escrever(nome.lower() + " = " + bits)

    def memoria(self, titulo, linhas):
        self.escrever(titulo)
        self.escrever("*" * 31)
        for valor in linhas:
            self.escrever(format(valor, "032b"))

    def salvar(self):
        with open(self.caminho, "w") as f:
            f.write("\n".join(self.linhas) + "\n")
