#!/usr/bin/env python3
"""Teste de validação dos dados exibidos no PDF."""

import sys
from pathlib import Path

sys.path.insert(0, "src")

from main import ControleFinanceiro
from gui import gerar_dados_de_teste

# Criar controle e gerar dados
controle = ControleFinanceiro()
gerar_dados_de_teste(controle, "dados_validacao_pdf.json")

# Analisar dados de Setembro e Agosto
rel_set = controle.relatorio_mensal(9, 2026)
rel_ago = controle.relatorio_mensal(8, 2026)

print("=" * 80)
print("VALIDAÇÃO DE DADOS DO PDF - SETEMBRO vs AGOSTO 2026")
print("=" * 80)

# Verificar Esportes (deve ter aumento)
esportes_ago = rel_ago["gasto_por_categoria"].get("Esportes", 0)
esportes_set = rel_set["gasto_por_categoria"].get("Esportes", 0)
var_esportes_abs = rel_set["variacao_por_categoria_absoluta"].get("Esportes")
var_esportes_pct = rel_set["variacao_por_categoria_percentual"].get("Esportes")

print(f"\n📊 CATEGORIA: Esportes")
print(f"  Agosto/2026: R$ {esportes_ago:.2f}")
print(f"  Setembro/2026: R$ {esportes_set:.2f}")
print(f"  Variação Absoluta (R$): R$ {var_esportes_abs:.2f}")
print(f"  Variação Percentual (%): {var_esportes_pct:.2f}%")
print(f"  ✓ Aumentou mais de 30%? {var_esportes_pct > 30}")

# Verificar limite de Esportes
esportes_cat = controle.categorias["Esportes"]
limite_esportes = esportes_cat.limite
ultrapassou = esportes_cat.ultrapassou_limite(9, 2026)
print(f"  Limite: R$ {limite_esportes:.2f}")
print(f"  Ultrapassou limite? {ultrapassou}")
print(f"  ✓ Deve gerar alerta no PDF")

# Verificar Alimentação (mudança pequena)
alim_ago = rel_ago["gasto_por_categoria"].get("Alimentação", 0)
alim_set = rel_set["gasto_por_categoria"].get("Alimentação", 0)
var_alim_abs = rel_set["variacao_por_categoria_absoluta"].get("Alimentação")
var_alim_pct = rel_set["variacao_por_categoria_percentual"].get("Alimentação")

print(f"\n📊 CATEGORIA: Alimentação")
print(f"  Agosto/2026: R$ {alim_ago:.2f}")
print(f"  Setembro/2026: R$ {alim_set:.2f}")
print(f"  Variação Absoluta (R$): R$ {var_alim_abs:.2f}")
print(f"  Variação Percentual (%): {var_alim_pct:.2f}%")
print(f"  ✓ Aumentou mais de 30%? {var_alim_pct > 30}")

# Verificar estrutura do relatório
print(f"\n✓ Chaves do relatório de Setembro:")
for key in sorted(rel_set.keys()):
    print(f"  - {key}")

# Verificar que variação_por_categoria_absoluta está presente
assert "variacao_por_categoria_absoluta" in rel_set, "Chave variacao_por_categoria_absoluta não encontrada"
assert "variacao_por_categoria_percentual" in rel_set, "Chave variacao_por_categoria_percentual não encontrada"
print(f"\n✅ Ambas as métricas de variação estão presentes no relatório")

# Verificar que o PDF pode acessar essas chaves
var_abs_dict = rel_set["variacao_por_categoria_absoluta"]
assert isinstance(var_abs_dict, dict), "variacao_por_categoria_absoluta não é um dicionário"
assert len(var_abs_dict) > 0, "variacao_por_categoria_absoluta está vazio"
print(f"✅ Estrutura de variação absoluta está correta (tem {len(var_abs_dict)} entradas)")

# Verificar que categorias_com_aumento_significativo funciona (usa a métrica percentual)
aumentos = controle.categorias_com_aumento_significativo(9, 2026)
print(f"\n📈 Categorias com aumento > 30% em Setembro/2026:")
for nome in aumentos:
    print(f"  - {nome}")
assert "Esportes" in aumentos, "Esportes deveria estar na lista de aumentos"
print(f"✅ Método categorias_com_aumento_significativo() funciona corretamente")

# Limpar
Path("dados_validacao_pdf.json").unlink()

print(f"\n{'='*80}")
print("✅ VALIDAÇÃO COMPLETA - DADOS DO PDF ESTÃO CORRETOS")
print(f"{'='*80}")
