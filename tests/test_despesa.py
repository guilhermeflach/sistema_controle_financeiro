import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from main import Despesa


class DespesaTestCase(unittest.TestCase):
    def test_converte_data_e_formata_exibicao(self):
        despesa = Despesa(42.5, "Alimentação", "07/09/2026", "Mercado")

        self.assertEqual(despesa.data, date(2026, 9, 7))
        self.assertEqual(despesa.data_formatada(), "07/09/2026")

    def test_rejeita_valor_nao_positivo(self):
        with self.assertRaises(ValueError):
            Despesa(0, "Energia", "01/09/2026")

    def test_rejeita_data_em_formato_invalido(self):
        with self.assertRaises(ValueError):
            Despesa(10, "Energia", "2026-09-01")


if __name__ == "__main__":
    unittest.main()