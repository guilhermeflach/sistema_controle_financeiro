from pathlib import Path

from fpdf import FPDF

from main import ControleFinanceiro


def _formatar_valor(valor: object) -> str:
    if isinstance(valor, (int, float)):
        return f"R$ {valor:.2f}"
    return "N/A"


def _formatar_percentual(valor: object) -> str:
    if isinstance(valor, (int, float)):
        return f"{valor:.2f}%"
    return "N/A"


def _mes_em_portugues(mes: int) -> str:
    meses = [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    ]
    return meses[mes - 1]


def gerar_relatorio_pdf(
    controle: ControleFinanceiro,
    mes: int,
    ano: int,
    caminho_saida: str | Path,
) -> None:
    relatorio = controle.relatorio_mensal(mes, ano)
    alertas = controle.verificar_alertas(mes, ano)
    aumentos = controle.categorias_com_aumento_significativo(mes, ano)
    gastos = relatorio["gasto_por_categoria"]
    percentuais = relatorio["percentual_por_categoria"]
    variacoes = relatorio["variacao_por_categoria_percentual"]

    if not isinstance(gastos, dict) or not isinstance(percentuais, dict):
        raise ValueError("Relatório mensal inválido para exportação.")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, f"Relatório financeiro - {_mes_em_portugues(mes)} de {ano}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Gasto total geral: {_formatar_valor(relatorio['gasto_total_geral'])}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Variação absoluta: {_formatar_valor(relatorio['variacao_total_absoluta'])}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Variação percentual: {_formatar_percentual(relatorio['variacao_total_percentual'])}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Alertas", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)  # Remover negrito para multi_cell
    pdf.set_text_color(180, 0, 0)
    if alertas or aumentos:
        for alerta in alertas:
            pdf.multi_cell(0, 6, f"- {alerta}", new_x="LMARGIN", new_y="NEXT")
        for nome in aumentos:
            pdf.multi_cell(0, 6, f"- A categoria '{nome}' aumentou mais de 30%.", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Nenhum alerta para o período.", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    # Tabela com 4 colunas: Categoria, Total gasto, % do total, Variação (absoluta em R$)
    # Ajustadas para caber em A4 com margens de 15mm
    colunas = [("Categoria", 65), ("Total gasto", 35), ("% do total", 25), ("Variação (R$)", 30)]
    for titulo, largura in colunas:
        pdf.cell(largura, 8, titulo, border=1, align="C")
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for nome, total in gastos.items():
        if not isinstance(total, (int, float)) or total <= 0:
            continue
        pdf.cell(65, 7, str(nome)[:18], border=1)  # Trunca nome se muito longo
        pdf.cell(35, 7, _formatar_valor(total), border=1, align="R")
        pdf.cell(25, 7, _formatar_percentual(percentuais.get(nome)), border=1, align="R")
        var_absoluta = relatorio["variacao_por_categoria_absoluta"]
        if isinstance(var_absoluta, dict):
            pdf.cell(30, 7, _formatar_valor(var_absoluta.get(nome)), border=1, align="R")
        else:
            pdf.cell(30, 7, "N/A", border=1, align="R")
        pdf.ln()

    pdf.ln(7)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Detalhamento de despesas", new_x="LMARGIN", new_y="NEXT")
    for nome, categoria in controle.categorias.items():
        despesas = [
            despesa for despesa in categoria.despesas
            if despesa.data.month == mes and despesa.data.year == ano
        ]
        if not despesas:
            continue
        # Ordenar despesas por data (mais recente primeiro)
        despesas = sorted(despesas, key=lambda d: d.data, reverse=True)
        pdf.set_font("Helvetica", "B", 10)
        # Cabeçalho com colunas bem definidas: Data | Valor | Descrição
        # Dimensões ajustadas para caber em A4 com margens
        pdf.cell(40, 7, "Data", border=1, align="C")
        pdf.cell(35, 7, "Valor", border=1, align="C")
        pdf.cell(75, 7, "Descrição", border=1, align="C")
        pdf.ln()
        pdf.set_font("Helvetica", "", 9)
        for despesa in despesas:
            descricao = despesa.descricao or "Sem descrição"
            pdf.cell(40, 6, despesa.data_formatada(), border=1)
            pdf.cell(35, 6, _formatar_valor(despesa.valor), border=1, align="R")
            # Trunca descrição se necessário para caber
            desc_truncada = descricao[:35] if len(descricao) > 35 else descricao
            pdf.cell(75, 6, desc_truncada, border=1)
            pdf.ln()
        pdf.ln(3)

    pdf.output(str(caminho_saida))