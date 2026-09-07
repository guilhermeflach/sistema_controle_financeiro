import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from main import Categoria, Despesa


class CategoriaTestCase(unittest.TestCase):
    def test_adiciona_despesa_e_calcula_total(self):
        categoria = Categoria("Alimentação")
        despesa = Despesa(42.5, "Alimentação", "07/09/2026", "Mercado")

        categoria.adicionar_despesa(despesa)

        self.assertEqual(categoria.despesas, [despesa])
        self.assertEqual(categoria.total_gasto(), 42.5)
        self.assertFalse(categoria.ultrapassou_limite())

    def test_rejeita_despesa_de_categoria_diferente(self):
        categoria = Categoria("Alimentação")
        despesa = Despesa(10, "Energia", "01/09/2026")

        with self.assertRaises(ValueError):
            categoria.adicionar_despesa(despesa)

        self.assertEqual(categoria.despesas, [])

    def test_calcula_total_apenas_do_periodo(self):
        categoria = Categoria("Transporte")
        categoria.adicionar_despesa(Despesa(20, "Transporte", "31/08/2026"))
        categoria.adicionar_despesa(Despesa(35, "Transporte", "05/09/2026"))
        categoria.adicionar_despesa(Despesa(15, "Transporte", "20/09/2025"))

        self.assertEqual(categoria.total_no_periodo(9, 2026), 35)

    def test_identifica_limite_excedido(self):
        categoria = Categoria("Energia", limite=100)
        categoria.adicionar_despesa(Despesa(60, "Energia", "01/09/2026"))
        categoria.adicionar_despesa(Despesa(45, "Energia", "02/09/2026"))

        self.assertTrue(categoria.ultrapassou_limite())


if __name__ == "__main__":
    unittest.main()