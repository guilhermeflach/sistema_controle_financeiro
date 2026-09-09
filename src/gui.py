import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path

from main import ControleFinanceiro
from relatorio_pdf import gerar_relatorio_pdf


def _validar_data(entrada: str) -> tuple[bool, str]:
    try:
        datetime.strptime(entrada, "%d/%m/%Y")
        return True, entrada
    except ValueError:
        return False, "Data inválida. Use o formato DD/MM/AAAA."


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


def gerar_dados_de_teste(controle: ControleFinanceiro, arquivo_dados: str) -> None:
    """Gera dados de teste com 5 categorias e despesas de Agosto e Setembro de 2026."""
    # Criar categorias com limites
    controle.criar_categoria("Alimentação", 500)
    controle.criar_categoria("Esportes", 250)
    controle.criar_categoria("Cuidados Pessoais", 150)
    controle.criar_categoria("Compras", 400)
    controle.criar_categoria("Educação", 300)
    
    # Despesas de Agosto de 2026
    controle.registrar_despesa("Alimentação", 45.00, "10/08/2026", "Créditos RU Trindade")
    controle.registrar_despesa("Esportes", 119.90, "15/08/2026", "Mensalidade Selfit")
    controle.registrar_despesa("Cuidados Pessoais", 55.00, "20/08/2026", "Corte Rud Barbearia")
    controle.registrar_despesa("Compras", 150.00, "22/08/2026", "Compra Mercado Livre")
    controle.registrar_despesa("Educação", 180.00, "25/08/2026", "Material Odyssée B1")
    
    # Despesas de Setembro de 2026
    controle.registrar_despesa("Alimentação", 30.00, "05/09/2026", "Créditos RU CCA")
    controle.registrar_despesa("Esportes", 119.90, "10/09/2026", "Mensalidade Selfit")
    controle.registrar_despesa("Esportes", 180.00, "12/09/2026", "Mensalidade Rilion Gracie")
    controle.registrar_despesa("Cuidados Pessoais", 55.00, "18/09/2026", "Corte Rud Barbearia")
    controle.registrar_despesa("Compras", 80.00, "20/09/2026", "Compra Mercado Livre")
    
    # Salvar dados
    controle.salvar_dados(arquivo_dados)


class InterfaceGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sistema de Controle Financeiro Residencial")
        self.root.geometry("600x500")
        self.controle = ControleFinanceiro()
        self.arquivo_dados = "dados.json"
        
        # Carregar dados ou gerar dados de teste se arquivo não existe
        if not Path(self.arquivo_dados).exists():
            gerar_dados_de_teste(self.controle, self.arquivo_dados)
        else:
            self.controle.carregar_dados(self.arquivo_dados)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.setup_abas()

    def setup_abas(self) -> None:
        self.aba_categoria = ttk.Frame(self.notebook)
        self.aba_despesa = ttk.Frame(self.notebook)
        self.aba_relatorio = ttk.Frame(self.notebook)
        self.aba_alertas = ttk.Frame(self.notebook)
        self.aba_comparacao = ttk.Frame(self.notebook)
        self.aba_pdf = ttk.Frame(self.notebook)

        self.notebook.add(self.aba_categoria, text="Categoria")
        self.notebook.add(self.aba_despesa, text="Despesa")
        self.notebook.add(self.aba_relatorio, text="Relatório")
        self.notebook.add(self.aba_alertas, text="Alertas")
        self.notebook.add(self.aba_comparacao, text="Comparação")
        self.notebook.add(self.aba_pdf, text="Exportar PDF")

        self.setup_aba_categoria()
        self.setup_aba_despesa()
        self.setup_aba_relatorio()
        self.setup_aba_alertas()
        self.setup_aba_comparacao()
        self.setup_aba_pdf()

    def setup_aba_categoria(self) -> None:
        frame = ttk.Frame(self.aba_categoria, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Nome da categoria:").pack(anchor=tk.W)
        self.cat_nome = ttk.Entry(frame, width=30)
        self.cat_nome.pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="Limite mensal (opcional):").pack(anchor=tk.W, pady=(10, 0))
        self.cat_limite = ttk.Entry(frame, width=30)
        self.cat_limite.pack(anchor=tk.W, pady=5)

        def criar():
            nome = self.cat_nome.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Nome não pode ser vazio.")
                return
            
            limite: float | None = None
            if self.cat_limite.get().strip():
                valido, valor = _validar_valor(self.cat_limite.get())
                if not valido:
                    messagebox.showerror("Erro", valor)
                    return
                limite = valor
            
            try:
                self.controle.criar_categoria(nome, limite)
                self.controle.salvar_dados(self.arquivo_dados)
                messagebox.showinfo("Sucesso", f"Categoria '{nome}' criada com sucesso.")
                self.cat_nome.delete(0, tk.END)
                self.cat_limite.delete(0, tk.END)
                self.atualizar_categorias()
                self.atualizar_dropdown_categorias()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(frame, text="Criar Categoria", command=criar).pack(pady=20)

        ttk.Label(frame, text="Categorias cadastradas:", font=("", 10, "bold")).pack(anchor=tk.W, pady=(20, 0))
        self.cat_listbox = tk.Listbox(frame, height=10)
        self.cat_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.atualizar_categorias()

    def atualizar_categorias(self) -> None:
        self.cat_listbox.delete(0, tk.END)
        for nome, cat in self.controle.categorias.items():
            limite_str = f" (limite: R$ {cat.limite:.2f})" if cat.limite else ""
            self.cat_listbox.insert(tk.END, f"{nome}{limite_str}")

    def setup_aba_despesa(self) -> None:
        frame = ttk.Frame(self.aba_despesa, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Categoria:").pack(anchor=tk.W)
        self.desp_categoria = ttk.Combobox(frame, width=27, state="readonly")
        self.desp_categoria.pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="Valor (R$):").pack(anchor=tk.W, pady=(10, 0))
        self.desp_valor = ttk.Entry(frame, width=30)
        self.desp_valor.pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="Data (DD/MM/AAAA):").pack(anchor=tk.W, pady=(10, 0))
        self.desp_data = ttk.Entry(frame, width=30)
        self.desp_data.pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="Descrição (opcional):").pack(anchor=tk.W, pady=(10, 0))
        self.desp_descricao = ttk.Entry(frame, width=30)
        self.desp_descricao.pack(anchor=tk.W, pady=5)

        def registrar():
            categoria = self.desp_categoria.get()
            if not categoria:
                messagebox.showerror("Erro", "Selecione uma categoria.")
                return
            
            valido_valor, valor = _validar_valor(self.desp_valor.get())
            if not valido_valor:
                messagebox.showerror("Erro", valor)
                return
            
            valido_data, data = _validar_data(self.desp_data.get())
            if not valido_data:
                messagebox.showerror("Erro", data)
                return
            
            descricao = self.desp_descricao.get().strip()
            
            try:
                self.controle.registrar_despesa(categoria, valor, data, descricao)
                self.controle.salvar_dados(self.arquivo_dados)
                messagebox.showinfo("Sucesso", f"Despesa de R$ {valor:.2f} registrada.")
                self.desp_valor.delete(0, tk.END)
                self.desp_data.delete(0, tk.END)
                self.desp_descricao.delete(0, tk.END)
            except (KeyError, ValueError) as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(frame, text="Registrar Despesa", command=registrar).pack(pady=20)

    def atualizar_dropdown_categorias(self) -> None:
        self.desp_categoria["values"] = list(self.controle.categorias.keys())

    def setup_aba_relatorio(self) -> None:
        frame = ttk.Frame(self.aba_relatorio, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Mês (1-12):").pack(anchor=tk.W)
        self.rel_mes = ttk.Entry(frame, width=30)
        self.rel_mes.pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="Ano:").pack(anchor=tk.W, pady=(10, 0))
        self.rel_ano = ttk.Entry(frame, width=30)
        self.rel_ano.pack(anchor=tk.W, pady=5)

        def gerar():
            valido, (mes, ano) = _validar_mes_ano(self.rel_mes.get(), self.rel_ano.get())
            if not valido:
                messagebox.showerror("Erro", "Mês ou ano inválido.")
                return
            
            relatorio = self.controle.relatorio_mensal(mes, ano)
            total = relatorio["gasto_total_geral"]
            gastos = relatorio["gasto_por_categoria"]
            percentuais = relatorio["percentual_por_categoria"]
            
            texto = f"=== Relatório de {mes:02d}/{ano} ===\n"
            texto += f"Gasto total geral: R$ {total:.2f}\n\n"
            
            if gastos:
                texto += "Gasto por categoria:\n"
                for nome, valor in gastos.items():
                    if isinstance(valor, (int, float)) and valor > 0:
                        pct = percentuais.get(nome, 0)
                        texto += f"  {nome}: R$ {valor:.2f} ({pct:.2f}%)\n"
            else:
                texto += "Sem gastos registrados neste período."
            
            self.rel_texto.config(state=tk.NORMAL)
            self.rel_texto.delete(1.0, tk.END)
            self.rel_texto.insert(1.0, texto)
            self.rel_texto.config(state=tk.DISABLED)

        ttk.Button(frame, text="Gerar Relatório", command=gerar).pack(pady=20)

        self.rel_texto = tk.Text(frame, height=15, width=60, state=tk.DISABLED)
        self.rel_texto.pack(fill=tk.BOTH, expand=True)

    def setup_aba_alertas(self) -> None:
        frame = ttk.Frame(self.aba_alertas, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Mês (1-12):").pack(anchor=tk.W)
        self.ale_mes = ttk.Entry(frame, width=30)
        self.ale_mes.pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="Ano:").pack(anchor=tk.W, pady=(10, 0))
        self.ale_ano = ttk.Entry(frame, width=30)
        self.ale_ano.pack(anchor=tk.W, pady=5)

        def verificar():
            valido, (mes, ano) = _validar_mes_ano(self.ale_mes.get(), self.ale_ano.get())
            if not valido:
                messagebox.showerror("Erro", "Mês ou ano inválido.")
                return
            
            alertas_limite = self.controle.verificar_alertas(mes, ano)
            aumentos = self.controle.categorias_com_aumento_significativo(mes, ano)
            
            texto = f"=== Alertas de {mes:02d}/{ano} ===\n"
            if alertas_limite:
                texto += "Limites ultrapassados:\n"
                for alerta in alertas_limite:
                    texto += f"  ⚠ {alerta}\n"
            
            if aumentos:
                texto += "\nCategorias com aumento > 30%:\n"
                for nome in aumentos:
                    texto += f"  ⚠ {nome}\n"
            
            if not alertas_limite and not aumentos:
                texto += "Sem alertas para este período."
            
            self.ale_texto.config(state=tk.NORMAL)
            self.ale_texto.delete(1.0, tk.END)
            self.ale_texto.insert(1.0, texto)
            self.ale_texto.config(state=tk.DISABLED)

        ttk.Button(frame, text="Verificar Alertas", command=verificar).pack(pady=20)

        self.ale_texto = tk.Text(frame, height=15, width=60, state=tk.DISABLED)
        self.ale_texto.pack(fill=tk.BOTH, expand=True)

    def setup_aba_comparacao(self) -> None:
        frame = ttk.Frame(self.aba_comparacao, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Mês (1-12):").pack(anchor=tk.W)
        self.comp_mes = ttk.Entry(frame, width=30)
        self.comp_mes.pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="Ano:").pack(anchor=tk.W, pady=(10, 0))
        self.comp_ano = ttk.Entry(frame, width=30)
        self.comp_ano.pack(anchor=tk.W, pady=5)

        def comparar():
            valido, (mes, ano) = _validar_mes_ano(self.comp_mes.get(), self.comp_ano.get())
            if not valido:
                messagebox.showerror("Erro", "Mês ou ano inválido.")
                return
            
            relatorio = self.controle.relatorio_mensal(mes, ano)
            var_total_abs = relatorio["variacao_total_absoluta"]
            var_total_pct = relatorio["variacao_total_percentual"]
            var_por_cat_pct = relatorio["variacao_por_categoria_percentual"]
            
            mes_ant, ano_ant = self.controle._mes_anterior(mes, ano)
            texto = f"=== Comparação: {mes:02d}/{ano} vs {mes_ant:02d}/{ano_ant} ===\n"
            
            if isinstance(var_total_abs, str):
                texto += f"Variação total: {var_total_abs}\n"
            else:
                texto += f"Variação total: R$ {var_total_abs:.2f}\n"
                if isinstance(var_total_pct, (int, float)):
                    texto += f"Variação percentual: {var_total_pct:.2f}%\n"
            
            if isinstance(var_por_cat_pct, dict) and var_por_cat_pct:
                texto += "\nVariação por categoria:\n"
                for nome, pct in var_por_cat_pct.items():
                    texto += f"  {nome}: {pct:+.2f}%\n"
            
            self.comp_texto.config(state=tk.NORMAL)
            self.comp_texto.delete(1.0, tk.END)
            self.comp_texto.insert(1.0, texto)
            self.comp_texto.config(state=tk.DISABLED)

        ttk.Button(frame, text="Comparar", command=comparar).pack(pady=20)

        self.comp_texto = tk.Text(frame, height=15, width=60, state=tk.DISABLED)
        self.comp_texto.pack(fill=tk.BOTH, expand=True)

    def setup_aba_pdf(self) -> None:
        frame = ttk.Frame(self.aba_pdf, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Mês (1-12):").pack(anchor=tk.W)
        self.pdf_mes = ttk.Entry(frame, width=30)
        self.pdf_mes.pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="Ano:").pack(anchor=tk.W, pady=(10, 0))
        self.pdf_ano = ttk.Entry(frame, width=30)
        self.pdf_ano.pack(anchor=tk.W, pady=5)

        def exportar():
            valido, (mes, ano) = _validar_mes_ano(self.pdf_mes.get(), self.pdf_ano.get())
            if not valido:
                messagebox.showerror("Erro", "Mês ou ano inválido.")
                return
            
            caminho = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if not caminho:
                return
            
            try:
                gerar_relatorio_pdf(self.controle, mes, ano, caminho)
                messagebox.showinfo("Sucesso", f"Relatório exportado para '{caminho}'.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar PDF: {e}")

        ttk.Button(frame, text="Exportar PDF", command=exportar).pack(pady=20)

        ttk.Label(frame, text="Clique no botão para escolher o local de salvamento.").pack(pady=20)

    def run(self) -> None:
        self.atualizar_dropdown_categorias()
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    gui = InterfaceGUI(root)
    gui.run()
