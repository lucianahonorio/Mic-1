class Log:
    def __init__(self, caminho):
        self.caminho = caminho
        self.linhas = []

    def escrever(self, texto=""):
        print(texto)
        self.linhas.append(texto)

    def separador(self):
        self.escrever("=" * 60)

    def registradores(self, titulo, valores):
        pass

    def memoria(self, titulo, linhas):
        pass

    def salvar(self):
        with open(self.caminho, "w") as f:
            f.write("\n".join(self.linhas) + "\n")
