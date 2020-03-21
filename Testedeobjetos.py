class Pai():
    def __init__(self, *args, **kwargs):
        self.valor = self._process(*args, **kwargs)

    def _process(self, *args, **kwargs):
        return "Valor da Classe Pai"


class Filho(Pai):
    def _process(self, *args, **kwargs):
        return "Valor da Classe Filho"

print(Filho().valor)
