import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from gui import InterfaceGUI, _validar_data, _validar_valor, _validar_mes_ano


class GUITestCase(unittest.TestCase):
    def test_validador_data_aceita_formato_correto(self):
        valido, resultado = _validar_data("07/09/2026")
        self.assertTrue(valido)
        self.assertEqual(resultado, "07/09/2026")

    def test_validador_data_rejeita_formato_errado(self):
        valido, resultado = _validar_data("2026-09-07")
        self.assertFalse(valido)

    def test_validador_valor_aceita_numero_positivo(self):
        valido, valor = _validar_valor("42.50")
        self.assertTrue(valido)
        self.assertEqual(valor, 42.50)

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

    @patch("tkinter.Tk")
    def test_instancia_gui_sem_erros(self, mock_tk):
        # Remove arquivo de dados para testar geração de dados de teste
        from pathlib import Path
        arquivo_teste = "dados.json"
        backup = None
        if Path(arquivo_teste).exists():
            import shutil
            backup = arquivo_teste + ".bak"
            shutil.move(arquivo_teste, backup)
        
        try:
            mock_root = MagicMock()
            gui = InterfaceGUI(mock_root)
            self.assertIsNotNone(gui.controle)
            # Verifica que as 5 categorias de teste foram criadas
            self.assertEqual(len(gui.controle.categorias), 5)
            self.assertIn("Alimentação", gui.controle.categorias)
            self.assertIn("Esportes", gui.controle.categorias)
        finally:
            # Restaura arquivo de dados se existia
            if backup and Path(backup).exists():
                import shutil
                shutil.move(backup, arquivo_teste)
            # Remove arquivo de teste se foi criado
            if Path(arquivo_teste).exists():
                Path(arquivo_teste).unlink()


if __name__ == "__main__":
    unittest.main()
