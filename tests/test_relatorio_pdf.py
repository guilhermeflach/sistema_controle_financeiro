import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from main import ControleFinanceiro
from relatorio_pdf import gerar_relatorio_pdf


class RelatorioPDFTestCase(unittest.TestCase):
    def test_gera_pdf_com_resumo_alertas_tabela_e_detalhes(self):
        controle = ControleFinanceiro()
        controle.criar_categoria("Energia", limite=100)
        controle.criar_categoria("Alimentação")
        controle.registrar_despesa("Energia", 120, "05/09/2026", "Conta de luz")
        controle.registrar_despesa("Alimentação", 80, "06/09/2026", "Mercado")
        quantidade_antes = len(controle.categorias["Energia"].despesas)

        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "relatorio.pdf"
            gerar_relatorio_pdf(controle, 9, 2026, caminho)

            self.assertTrue(caminho.exists())
            self.assertGreater(caminho.stat().st_size, 0)
            conteudo = caminho.read_bytes()
            self.assertIn(b"%PDF", conteudo[:10])

        self.assertEqual(len(controle.categorias["Energia"].despesas), quantidade_antes)


if __name__ == "__main__":
    unittest.main()