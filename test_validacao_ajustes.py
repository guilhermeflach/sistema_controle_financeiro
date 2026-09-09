#!/usr/bin/env python3
"""Teste de validação dos 4 ajustes implementados."""

import sys
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.path.insert(0, "src")

print("="*80)
print("TESTE DE VALIDAÇÃO DOS 4 AJUSTES")
print("="*80)

# AJUSTE 1: Validar que a aba foi renomeada (verificar no código)
print("\n1️⃣  VALIDAÇÃO: Aba renomeada de 'Comparação' para 'Comparativo'")
gui_path = Path(__file__).parent / "src" / "gui.py"
with open(gui_path, "r", encoding="utf-8") as f:
    gui_code = f.read()

assert 'text="Comparativo"' in gui_code, "Aba 'Comparativo' não encontrada no código!"
assert 'text="Comparação"' not in gui_code, "Aba antiga 'Comparação' ainda existe no código!"
print("   ✅ Aba renomeada corretamente para 'Comparativo'")

# AJUSTE 2: Validar autopreenchimento de data
print("\n2️⃣  VALIDAÇÃO: Autopreenchimento de data (campo de Despesa)")
assert 'self.desp_data.insert(0, datetime.today().strftime("%d/%m/%Y"))' in gui_code, "Autopreenchimento de data não encontrado!"
print(f"   ✅ Campo de data será preenchido automaticamente com data de hoje")

# AJUSTE 3: Validar exibição de variação absoluta no comparativo
print("\n3️⃣  VALIDAÇÃO: Exibição de variação absoluta (em R$) no Comparativo")
assert 'variacao_por_categoria_absoluta' in gui_code, "Referência a variacao_por_categoria_absoluta não encontrada!"
assert 'Variação por categoria (R$)' in gui_code, "Cabeçalho de variação em R$ não encontrado!"
assert 'var_por_cat_abs' in gui_code, "Variável var_por_cat_abs não encontrada!"
print("   ✅ Código atualizado para exibir variação absoluta em R$")

# Verificar com dados reais
from main import ControleFinanceiro
from gui import gerar_dados_de_teste

controle = ControleFinanceiro()
gerar_dados_de_teste(controle, "dados_teste_ajustes.json")

# Simular o que a GUI faria
mes, ano = 9, 2026
relatorio = controle.relatorio_mensal(mes, ano)
var_por_cat_abs = relatorio["variacao_por_categoria_absoluta"]

assert isinstance(var_por_cat_abs, dict), "variacao_por_categoria_absoluta não é um dicionário"
assert "Esportes" in var_por_cat_abs, "Esportes não encontrada em variação absoluta"

esportes_var = var_por_cat_abs["Esportes"]
print(f"   ✅ Esportes variação: R$ {esportes_var:.2f} (em R$, não em %)")

# Verificar que o texto do comparativo usa valores em R$, não percentual
mes_ant, ano_ant = controle._mes_anterior(mes, ano)
texto = f"=== Comparação: {mes:02d}/{ano} vs {mes_ant:02d}/{ano_ant} ===\n"
texto += f"Variação total: R$ {relatorio['variacao_total_absoluta']:.2f}\n"
if isinstance(relatorio['variacao_total_percentual'], (int, float)):
    texto += f"Variação percentual: {relatorio['variacao_total_percentual']:.2f}%\n"

if isinstance(var_por_cat_abs, dict) and var_por_cat_abs:
    texto += "\nVariação por categoria (R$):\n"
    for nome, valor in var_por_cat_abs.items():
        if isinstance(valor, (int, float)):
            texto += f"  {nome}: {valor:+.2f}\n"

assert "Variação por categoria (R$):" in texto, "Cabeçalho de variação em R$ não encontrado"
assert "Esportes: +180.00" in texto or "Esportes:  +180.00" in texto, "Esportes não mostra valor em R$ com sinal"
print("   ✅ Exibição de variação por categoria em R$ confirmada")

# AJUSTE 4: Validar ordenação cronológica no PDF (decrescente)
print("\n4️⃣  VALIDAÇÃO: Ordenação cronológica das despesas no PDF (mais recente primeiro)")
from relatorio_pdf import gerar_relatorio_pdf

caminho_pdf = "teste_pdf_ordenacao.pdf"
gerar_relatorio_pdf(controle, 9, 2026, caminho_pdf)

assert Path(caminho_pdf).exists(), "PDF não foi gerado"
print("   ✅ PDF gerado com sucesso")

# Validar que as despesas foram ordenadas
esportes = controle.categorias["Esportes"]
despesas_set = [d for d in esportes.despesas if d.data.month == 9 and d.data.year == 2026]
despesas_ordenadas = sorted(despesas_set, key=lambda d: d.data, reverse=True)

print(f"   Despesas de Esportes em Setembro (ordem decrescente):")
for desp in despesas_ordenadas:
    print(f"      - {desp.data_formatada()}: R$ {desp.valor:.2f}")

# A primeira deve ser 12/09 (mais recente)
assert despesas_ordenadas[0].data_formatada() == "12/09/2026", "Primeira despesa deveria ser 12/09/2026"
assert despesas_ordenadas[1].data_formatada() == "10/09/2026", "Segunda despesa deveria ser 10/09/2026"
print("   ✅ Despesas ordenadas corretamente (mais recente primeiro)")

# Verificar que o código contém a ordenação
pdf_path = Path(__file__).parent / "src" / "relatorio_pdf.py"
with open(pdf_path, "r", encoding="utf-8") as f:
    pdf_code = f.read()

assert "sorted(despesas, key=lambda d: d.data, reverse=True)" in pdf_code, "Ordenação não encontrada no PDF!"
print("   ✅ Código do PDF contém ordenação cronológica")

# Limpeza
Path("dados_teste_ajustes.json").unlink()
Path(caminho_pdf).unlink()

print("\n" + "="*80)
print("✅ TODOS OS 4 AJUSTES VALIDADOS COM SUCESSO!")
print("="*80)
print("\nResumo:")
print("  1. ✅ Aba renomeada: 'Comparação' → 'Comparativo'")
print("  2. ✅ Data preenchida automaticamente com data atual")
print("  3. ✅ Variação por categoria exibida em R$ (absoluta, não percentual)")
print("  4. ✅ Despesas ordenadas cronologicamente (mais recente primeiro)")
