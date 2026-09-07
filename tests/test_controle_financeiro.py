import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from main import ControleFinanceiro, Despesa


class ControleFinanceiroTestCase(unittest.TestCase):
    def test_cria_categoria_e_impede_duplicidade(self):
        controle = ControleFinanceiro()

        categoria = controle.criar_categoria("Alimentação", limite=500)

        self.assertIs(controle.categorias["Alimentação"], categoria)
        self.assertEqual(categoria.limite, 500)
        with self.assertRaises(ValueError):
            controle.criar_categoria("Alimentação")

    def test_registra_despesa_na_categoria_existente(self):
        controle = ControleFinanceiro()
        controle.criar_categoria("Energia")

        despesa = controle.registrar_despesa(
            "Energia", 120, "07/09/2026", "Conta de luz"
        )

        self.assertIsInstance(despesa, Despesa)
        self.assertEqual(controle.categorias["Energia"].despesas, [despesa])
        self.assertFalse(hasattr(controle, "despesas"))

    def test_nao_registra_despesa_em_categoria_inexistente(self):
        controle = ControleFinanceiro()

        with self.assertRaises(KeyError):
            controle.registrar_despesa("Água", 80, "01/09/2026")

        self.assertEqual(controle.categorias, {})

    def test_gera_relatorio_mensal_por_categoria(self):
        controle = ControleFinanceiro()
        controle.criar_categoria("Alimentação")
        controle.criar_categoria("Transporte")
        controle.registrar_despesa("Alimentação", 100, "05/09/2026")
        controle.registrar_despesa("Alimentação", 50, "08/08/2026")
        controle.registrar_despesa("Transporte", 30, "10/09/2026")

        self.assertEqual(
            controle.relatorio_mensal(9, 2026),
            {"Alimentação": 100, "Transporte": 30},
        )


if __name__ == "__main__":
    unittest.main()