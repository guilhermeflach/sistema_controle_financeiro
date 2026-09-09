from datetime import datetime
from pathlib import Path

from main import ControleFinanceiro
from relatorio_pdf import gerar_relatorio_pdf


def _validar_data(entrada: str) -> tuple[bool, str]:
    try:
        datetime.strptime(entrada, "%d/%m/%Y")
        return True, entrada
    except ValueError:
        return False, f"Data inválida. Use o formato DD/MM/AAAA."


def _validar_valor(entrada: str) -> tuple[bool, float]:
    try:
        valor = float(entrada.replace(",", "."))
        if valor <= 0:
            return False, "O valor deve ser positivo."
        return True, valor
    except ValueError:
        return False, "Valor inválido. Use um número."


def _validar_mes_ano(entrada_mes: str, entrada_ano: str) -> tuple[bool, tuple[int, int]]:
    try:
        mes = int(entrada_mes)
        ano = int(entrada_ano)
        if not (1 <= mes <= 12):
            return False, (0, 0)  # type: ignore
        if ano < 2000 or ano > 2100:
            return False, (0, 0)  # type: ignore
        return True, (mes, ano)
    except ValueError:
        return False, (0, 0)  # type: ignore


class InterfaceCLI:
    def __init__(self) -> None:
        self.controle = ControleFinanceiro()

    def exibir_menu(self) -> None:
        print("\n=== Sistema de Controle Financeiro Residencial ===")
        print("1. Criar categoria")
        print("2. Registrar despesa")
        print("3. Ver relatório mensal")
        print("4. Ver alertas")
        print("5. Comparar com mês anterior")
        print("6. Exportar relatório em PDF")
        print("7. Sair")

    def criar_categoria(self) -> None:
        nome = input("Nome da categoria: ").strip()
        if not nome:
            print("Nome não pode ser vazio.")
            return
        if nome in self.controle.categorias:
            print(f"A categoria '{nome}' já existe.")
            return
        
        limite_entrada = input("Limite mensal (deixe em branco para sem limite): ").strip()
        limite: float | None = None
        if limite_entrada:
            valido, valor = _validar_valor(limite_entrada)
            if not valido:
                print(valor)
                return
            limite = valor
        
        try:
            self.controle.criar_categoria(nome, limite)
            print(f"Categoria '{nome}' criada com sucesso.")
        except ValueError as e:
            print(f"Erro: {e}")

    def registrar_despesa(self) -> None:
        if not self.controle.categorias:
            print("Nenhuma categoria cadastrada. Crie uma categoria primeiro.")
            return
        
        print("\nCategorias disponíveis:")
        for i, nome in enumerate(self.controle.categorias.keys(), 1):
            print(f"  {i}. {nome}")
        
        escolha = input("Escolha o número da categoria: ").strip()
        try:
            idx = int(escolha) - 1
            categorias = list(self.controle.categorias.keys())
            if idx < 0 or idx >= len(categorias):
                print("Escolha inválida.")
                return
            nome_categoria = categorias[idx]
        except ValueError:
            print("Escolha inválida.")
            return
        
        valor_entrada = input("Valor da despesa (R$): ").strip()
        valido_valor, valor = _validar_valor(valor_entrada)
        if not valido_valor:
            print(valor)
            return
        
        data_entrada = input("Data (DD/MM/AAAA): ").strip()
        valido_data, data = _validar_data(data_entrada)
        if not valido_data:
            print(data)
            return
        
        descricao = input("Descrição (opcional): ").strip()
        
        try:
            self.controle.registrar_despesa(nome_categoria, valor, data, descricao)
            print(f"Despesa de R$ {valor:.2f} registrada em '{nome_categoria}'.")
        except (KeyError, ValueError) as e:
            print(f"Erro ao registrar despesa: {e}")

    def relatorio_mensal(self) -> None:
        mes_entrada = input("Mês (1-12): ").strip()
        ano_entrada = input("Ano: ").strip()
        
        valido, (mes, ano) = _validar_mes_ano(mes_entrada, ano_entrada)
        if not valido:
            print("Mês ou ano inválido.")
            return
        
        relatorio = self.controle.relatorio_mensal(mes, ano)
        total = relatorio["gasto_total_geral"]
        gastos = relatorio["gasto_por_categoria"]
        percentuais = relatorio["percentual_por_categoria"]
        
        print(f"\n=== Relatório de {mes:02d}/{ano} ===")
        print(f"Gasto total geral: R$ {total:.2f}")
        
        if gastos:
            print("\nGasto por categoria:")
            for nome, valor in gastos.items():
                if isinstance(valor, (int, float)) and valor > 0:
                    pct = percentuais.get(nome, 0)
                    print(f"  {nome}: R$ {valor:.2f} ({pct:.2f}%)")
        else:
            print("Sem gastos registrados neste período.")

    def alertas(self) -> None:
        mes_entrada = input("Mês (1-12): ").strip()
        ano_entrada = input("Ano: ").strip()
        
        valido, (mes, ano) = _validar_mes_ano(mes_entrada, ano_entrada)
        if not valido:
            print("Mês ou ano inválido.")
            return
        
        alertas_limite = self.controle.verificar_alertas(mes, ano)
        aumentos = self.controle.categorias_com_aumento_significativo(mes, ano)
        
        print(f"\n=== Alertas de {mes:02d}/{ano} ===")
        if alertas_limite:
            print("Limites ultrapassados:")
            for alerta in alertas_limite:
                print(f"  ⚠ {alerta}")
        
        if aumentos:
            print("Categorias com aumento > 30%:")
            for nome in aumentos:
                print(f"  ⚠ {nome}")
        
        if not alertas_limite and not aumentos:
            print("Sem alertas para este período.")

    def comparar_com_anterior(self) -> None:
        mes_entrada = input("Mês (1-12): ").strip()
        ano_entrada = input("Ano: ").strip()
        
        valido, (mes, ano) = _validar_mes_ano(mes_entrada, ano_entrada)
        if not valido:
            print("Mês ou ano inválido.")
            return
        
        relatorio = self.controle.relatorio_mensal(mes, ano)
        var_total_abs = relatorio["variacao_total_absoluta"]
        var_total_pct = relatorio["variacao_total_percentual"]
        var_por_cat_pct = relatorio["variacao_por_categoria_percentual"]
        
        mes_ant, ano_ant = self.controle._mes_anterior(mes, ano)
        print(f"\n=== Comparação: {mes:02d}/{ano} vs {mes_ant:02d}/{ano_ant} ===")
        
        if isinstance(var_total_abs, str):
            print(f"Variação total: {var_total_abs}")
        else:
            print(f"Variação total: R$ {var_total_abs:.2f}")
            if isinstance(var_total_pct, (int, float)):
                print(f"Variação percentual: {var_total_pct:.2f}%")
        
        if isinstance(var_por_cat_pct, dict) and var_por_cat_pct:
            print("\nVariação por categoria:")
            for nome, pct in var_por_cat_pct.items():
                print(f"  {nome}: {pct:+.2f}%")

    def exportar_pdf(self) -> None:
        mes_entrada = input("Mês (1-12): ").strip()
        ano_entrada = input("Ano: ").strip()
        
        valido, (mes, ano) = _validar_mes_ano(mes_entrada, ano_entrada)
        if not valido:
            print("Mês ou ano inválido.")
            return
        
        caminho = input("Caminho do arquivo (ex: relatorio.pdf): ").strip()
        if not caminho:
            print("Caminho não pode ser vazio.")
            return
        
        try:
            gerar_relatorio_pdf(self.controle, mes, ano, caminho)
            print(f"Relatório exportado para '{caminho}'.")
        except Exception as e:
            print(f"Erro ao exportar PDF: {e}")

    def executar(self) -> None:
        while True:
            self.exibir_menu()
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.criar_categoria()
            elif opcao == "2":
                self.registrar_despesa()
            elif opcao == "3":
                self.relatorio_mensal()
            elif opcao == "4":
                self.alertas()
            elif opcao == "5":
                self.comparar_com_anterior()
            elif opcao == "6":
                self.exportar_pdf()
            elif opcao == "7":
                print("Até logo!")
                break
            else:
                print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    cli = InterfaceCLI()
    cli.executar()
