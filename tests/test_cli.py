import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from cli import InterfaceCLI, _validar_data, _validar_valor, _validar_mes_ano


class CLITestCase(unittest.TestCase):
    def test_instancia_cli_sem_erros(self):
        cli = InterfaceCLI()
        self.assertIsNotNone(cli.controle)
        self.assertEqual(cli.controle.categorias, {})

    def test_validador_data_aceita_formato_correto(self):
        valido, resultado = _validar_data("07/09/2026")
        self.assertTrue(valido)
        self.assertEqual(resultado, "07/09/2026")

    def test_validador_data_rejeita_formato_errado(self):
        valido, resultado = _validar_data("2026-09-07")
        self.assertFalse(valido)
        self.assertIn("inválida", resultado.lower())

    def test_validador_valor_aceita_numero_positivo(self):
        valido, valor = _validar_valor("42.50")
        self.assertTrue(valido)
        self.assertEqual(valor, 42.50)

    def test_validador_valor_rejeita_numero_negativo(self):
        valido, mensagem = _validar_valor("-10")
        self.assertFalse(valido)

    def test_validador_valor_rejeita_zero(self):
        valido, mensagem = _validar_valor("0")
        self.assertFalse(valido)

    def test_validador_mes_ano_aceita_valores_validos(self):
        valido, (mes, ano) = _validar_mes_ano("9", "2026")
        self.assertTrue(valido)
        self.assertEqual(mes, 9)
        self.assertEqual(ano, 2026)

    def test_validador_mes_ano_rejeita_mes_invalido(self):
        valido, _ = _validar_mes_ano("13", "2026")
        self.assertFalse(valido)

    def test_validador_mes_ano_rejeita_ano_muito_antigo(self):
        valido, _ = _validar_mes_ano("9", "1999")
        self.assertFalse(valido)


if __name__ == "__main__":
    unittest.main()
