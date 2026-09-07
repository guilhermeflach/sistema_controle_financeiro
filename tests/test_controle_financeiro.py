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

        relatorio = controle.relatorio_mensal(9, 2026)

        self.assertEqual(relatorio["gasto_total_geral"], 130)
        self.assertEqual(
            relatorio["gasto_por_categoria"],
            {"Alimentação": 100, "Transporte": 30},
        )
        self.assertAlmostEqual(relatorio["percentual_por_categoria"]["Alimentação"], 100 * 100 / 130)
        self.assertEqual(relatorio["variacao_total_absoluta"], 80)

    def test_relatorio_calcula_variacoes_e_ignora_categoria_nova(self):
        controle = ControleFinanceiro()
        controle.criar_categoria("Alimentação")
        controle.criar_categoria("Transporte")
        controle.registrar_despesa("Alimentação", 100, "05/08/2026")
        controle.registrar_despesa("Transporte", 50, "05/08/2026")
        controle.registrar_despesa("Alimentação", 140, "05/09/2026")
        controle.registrar_despesa("Transporte", 25, "05/09/2026")

        relatorio = controle.relatorio_mensal(9, 2026)

        self.assertEqual(relatorio["variacao_total_absoluta"], 15)
        self.assertEqual(relatorio["variacao_por_categoria_absoluta"], {"Alimentação": 40, "Transporte": -25})
        self.assertEqual(relatorio["variacao_por_categoria_percentual"]["Alimentação"], 40)
        self.assertEqual(controle.categorias_com_aumento_significativo(9, 2026), ["Alimentação"])

    def test_categoria_nova_nao_tem_variacao_calculada(self):
        controle = ControleFinanceiro()
        controle.criar_categoria("Alimentação")
        controle.criar_categoria("Lazer")
        controle.registrar_despesa("Alimentação", 100, "05/08/2026")
        controle.registrar_despesa("Alimentação", 100, "05/09/2026")
        controle.registrar_despesa("Lazer", 70, "05/09/2026")

        relatorio = controle.relatorio_mensal(9, 2026)

        self.assertNotIn("Lazer", relatorio["variacao_por_categoria_absoluta"])
        self.assertNotIn("Lazer", relatorio["variacao_por_categoria_percentual"])

    def test_primeiro_mes_preenche_comparativos_com_mensagem(self):
        controle = ControleFinanceiro()
        controle.criar_categoria("Alimentação")
        controle.registrar_despesa("Alimentação", 90, "05/09/2026")

        relatorio = controle.relatorio_mensal(9, 2026)

        mensagem = "não há dados do mês anterior"
        self.assertEqual(relatorio["variacao_total_absoluta"], mensagem)
        self.assertEqual(relatorio["variacao_total_percentual"], mensagem)
        self.assertEqual(relatorio["variacao_por_categoria_absoluta"], mensagem)
        self.assertEqual(relatorio["variacao_por_categoria_percentual"], mensagem)

    def test_alerta_considera_apenas_o_mes_informado(self):
        controle = ControleFinanceiro()
        controle.criar_categoria("Energia", limite=100)
        controle.registrar_despesa("Energia", 150, "05/08/2026")
        controle.registrar_despesa("Energia", 80, "05/09/2026")

        self.assertEqual(controle.verificar_alertas(9, 2026), [])
        self.assertEqual(
            controle.verificar_alertas(8, 2026),
            ["A categoria 'Energia' ultrapassou o limite mensal."],
        )


if __name__ == "__main__":
    unittest.main()