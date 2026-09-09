import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from main import ControleFinanceiro


class PersistenciaTestCase(unittest.TestCase):
    def test_salva_e_carrega_categorias_com_despesas(self):
        controle1 = ControleFinanceiro()
        controle1.criar_categoria("Energia", limite=100)
        controle1.criar_categoria("Alimentação")
        controle1.registrar_despesa("Energia", 120, "07/09/2026", "Conta de luz")
        controle1.registrar_despesa("Alimentação", 80, "08/09/2026", "Mercado")
        
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.json"
            controle1.salvar_dados(str(caminho))
            
            controle2 = ControleFinanceiro()
            controle2.carregar_dados(str(caminho))
            
            self.assertEqual(len(controle2.categorias), 2)
            self.assertIn("Energia", controle2.categorias)
            self.assertIn("Alimentação", controle2.categorias)
            
            energia = controle2.categorias["Energia"]
            self.assertEqual(energia.limite, 100.0)
            self.assertEqual(len(energia.despesas), 1)
            self.assertEqual(energia.despesas[0].valor, 120)
            self.assertEqual(energia.despesas[0].data_formatada(), "07/09/2026")
            self.assertEqual(energia.despesas[0].descricao, "Conta de luz")

    def test_carrega_arquivo_inexistente_sem_erro(self):
        controle = ControleFinanceiro()
        controle.carregar_dados("/inexistente/arquivo.json")
        self.assertEqual(controle.categorias, {})

    def test_limpa_dados_ao_carregar(self):
        controle = ControleFinanceiro()
        controle.criar_categoria("Antiga")
        controle.registrar_despesa("Antiga", 50, "01/01/2020")
        
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.json"
            
            controle2 = ControleFinanceiro()
            controle2.criar_categoria("Nova", limite=200)
            controle2.registrar_despesa("Nova", 150, "15/09/2026")
            controle2.salvar_dados(str(caminho))
            
            controle.carregar_dados(str(caminho))
            
            self.assertNotIn("Antiga", controle.categorias)
            self.assertIn("Nova", controle.categorias)
            self.assertEqual(controle.categorias["Nova"].limite, 200.0)

    def test_preserva_validacoes_ao_carregar(self):
        controle1 = ControleFinanceiro()
        controle1.criar_categoria("Test")
        controle1.registrar_despesa("Test", 42.5, "07/09/2026", "Descrição")
        
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.json"
            controle1.salvar_dados(str(caminho))
            
            controle2 = ControleFinanceiro()
            controle2.carregar_dados(str(caminho))
            
            despesa = controle2.categorias["Test"].despesas[0]
            self.assertEqual(despesa.valor, 42.5)
            self.assertEqual(despesa.categoria, "Test")
            self.assertGreater(len(despesa.data_formatada()), 0)

    def test_salva_arquivo_em_json_valido(self):
        import json
        
        controle = ControleFinanceiro()
        controle.criar_categoria("Transporte", limite=150)
        controle.registrar_despesa("Transporte", 35, "10/09/2026", "Uber")
        
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "dados.json"
            controle.salvar_dados(str(caminho))
            
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            
            self.assertIn("categorias", dados)
            self.assertEqual(len(dados["categorias"]), 1)
            self.assertEqual(dados["categorias"][0]["nome"], "Transporte")
            self.assertEqual(dados["categorias"][0]["limite"], 150.0)
            self.assertEqual(len(dados["categorias"][0]["despesas"]), 1)


if __name__ == "__main__":
    unittest.main()
