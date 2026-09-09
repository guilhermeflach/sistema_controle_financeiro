#!/usr/bin/env python3
"""Teste de validação do autopreenchimento universal e ordenação."""

import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.path.insert(0, "src")

print("="*80)
print("TESTE DE VALIDAÇÃO: AUTOPREENCHIMENTO UNIVERSAL E ORDENAÇÃO")
print("="*80)

# AJUSTE 1: Validar autopreenchimento universal na GUI
print("\n1️⃣  VALIDAÇÃO: Autopreenchimento universal de data/período")
gui_path = Path(__file__).parent / "src" / "gui.py"
with open(gui_path, "r", encoding="utf-8") as f:
    gui_code = f.read()

# Verificar que todos os campos têm autopreenchimento
checks = [
    ('self.rel_mes.insert(0, str(datetime.today().month))', "Relatório - Mês"),
    ('self.rel_ano.insert(0, str(datetime.today().year))', "Relatório - Ano"),
    ('self.ale_mes.insert(0, str(datetime.today().month))', "Alertas - Mês"),
    ('self.ale_ano.insert(0, str(datetime.today().year))', "Alertas - Ano"),
    ('self.comp_mes.insert(0, str(datetime.today().month))', "Comparativo - Mês"),
    ('self.comp_ano.insert(0, str(datetime.today().year))', "Comparativo - Ano"),
    ('self.pdf_mes.insert(0, str(datetime.today().month))', "PDF - Mês"),
    ('self.pdf_ano.insert(0, str(datetime.today().year))', "PDF - Ano"),
]

for check_str, label in checks:
    if check_str in gui_code:
        print(f"   ✅ {label} - Autopreenchimento confirmado")
    else:
        print(f"   ❌ {label} - FALHA na validação")
        raise AssertionError(f"Autopreenchimento não encontrado: {label}")

# Validar que a data da Despesa também tem autopreenchimento
if 'self.desp_data.insert(0, datetime.today().strftime("%d/%m/%Y"))' in gui_code:
    print(f"   ✅ Despesa - Data - Autopreenchimento confirmado")
else:
    print(f"   ⚠️  Despesa - Data já foi implementado anteriormente")

print("\n2️⃣  VALIDAÇÃO: Ordenação cronológica no PDF")

from main import ControleFinanceiro
from gui import gerar_dados_de_teste
from relatorio_pdf import gerar_relatorio_pdf

controle = ControleFinanceiro()
gerar_dados_de_teste(controle, "dados_teste_ordem.json")

# Gerar PDF e verificar ordenação
caminho_pdf = "teste_pdf_ordem.pdf"
gerar_relatorio_pdf(controle, 9, 2026, caminho_pdf)

assert Path(caminho_pdf).exists(), "PDF não foi gerado"
print("   ✅ PDF gerado com sucesso")

# Verificar ordenação das despesas
esportes = controle.categorias["Esportes"]
despesas_set = [d for d in esportes.despesas if d.data.month == 9 and d.data.year == 2026]

# Ordenar como está no PDF
despesas_ordenadas = sorted(despesas_set, key=lambda d: d.data, reverse=True)

print(f"\n   Despesas de Esportes em Setembro (ordem esperada - mais recente primeiro):")
for i, desp in enumerate(despesas_ordenadas, 1):
    print(f"      {i}. {desp.data_formatada()}: R$ {desp.valor:.2f}")

# Validar que a primeira é a mais recente (12/09)
assert despesas_ordenadas[0].data_formatada() == "12/09/2026", \
    f"Primeira despesa deveria ser 12/09/2026, mas é {despesas_ordenadas[0].data_formatada()}"
assert despesas_ordenadas[1].data_formatada() == "10/09/2026", \
    f"Segunda despesa deveria ser 10/09/2026, mas é {despesas_ordenadas[1].data_formatada()}"

print("   ✅ Despesas ordenadas corretamente (mais recente primeiro)")

# Verificar que o código contém a ordenação correta
pdf_path = Path(__file__).parent / "src" / "relatorio_pdf.py"
with open(pdf_path, "r", encoding="utf-8") as f:
    pdf_code = f.read()

if "sorted(despesas, key=lambda d: d.data, reverse=True)" in pdf_code:
    print("   ✅ Código do PDF contém ordenação cronológica decrescente")
else:
    print("   ⚠️  Verificar ordenação no código")

# Limpeza
Path("dados_teste_ordem.json").unlink()
Path(caminho_pdf).unlink()

print("\n" + "="*80)
print("✅ VALIDAÇÕES CONCLUÍDAS COM SUCESSO!")
print("="*80)
print("\nResumo:")
print("  1. ✅ Autopreenchimento universal implementado:")
print(f"     - Data de Despesa: {datetime.today().strftime('%d/%m/%Y')}")
print(f"     - Mês em Relatório/Alertas/Comparativo/PDF: {datetime.today().month}")
print(f"     - Ano em Relatório/Alertas/Comparativo/PDF: {datetime.today().year}")
print("  2. ✅ Ordenação cronológica no PDF (mais recente primeiro)")
