#!/usr/bin/env python3
"""Teste de geração automática de dados de teste."""

import sys
import json
from pathlib import Path

sys.path.insert(0, "src")

from main import ControleFinanceiro
from gui import gerar_dados_de_teste

# Usar arquivo temporário para teste
arquivo_teste = "dados_teste_temp.json"

# Limpar se existir
if Path(arquivo_teste).exists():
    Path(arquivo_teste).unlink()

# Gerar dados de teste
controle = ControleFinanceiro()
gerar_dados_de_teste(controle, arquivo_teste)

# Verificar se arquivo foi criado
assert Path(arquivo_teste).exists(), "Arquivo não foi criado!"
print("✓ Arquivo criado com sucesso")

# Carregar e validar estrutura
with open(arquivo_teste, "r", encoding="utf-8") as f:
    dados = json.load(f)

# Validar categorias
assert "categorias" in dados, "Chave 'categorias' não encontrada!"
assert len(dados["categorias"]) == 5, f"Esperado 5 categorias, encontrado {len(dados['categorias'])}"
print("✓ 5 categorias criadas")

# Validar nomes e limites
categorias_esperadas = {
    "Alimentação": 500,
    "Esportes": 250,
    "Cuidados Pessoais": 150,
    "Compras": 400,
    "Educação": 300,
}

for cat_data in dados["categorias"]:
    nome = cat_data["nome"]
    limite = cat_data["limite"]
    assert nome in categorias_esperadas, f"Categoria inesperada: {nome}"
    assert limite == categorias_esperadas[nome], f"Limite incorreto para {nome}: {limite}"
print("✓ Todas as categorias e limites validados")

# Contar despesas
total_despesas = sum(len(cat_data["despesas"]) for cat_data in dados["categorias"])
assert total_despesas == 10, f"Esperado 10 despesas, encontrado {total_despesas}"
print("✓ 10 despesas registradas")

# Validar estrutura de despesa
for cat_data in dados["categorias"]:
    for desp in cat_data["despesas"]:
        assert "valor" in desp, "Campo 'valor' não encontrado"
        assert "categoria" in desp, "Campo 'categoria' não encontrado"
        assert "data" in desp, "Campo 'data' não encontrado"
        assert "descricao" in desp, "Campo 'descricao' não encontrado"
print("✓ Estrutura de despesas validada")

# Testar carregamento
controle2 = ControleFinanceiro()
controle2.carregar_dados(arquivo_teste)

assert len(controle2.categorias) == 5, "Categorias não foram carregadas corretamente"
print("✓ Categorias carregadas corretamente")

# Verificar uma despesa específica (Alimentação, 10/08/2026)
alim = controle2.categorias["Alimentação"]
assert len(alim.despesas) >= 1, "Nenhuma despesa em Alimentação"
desp_ago = [d for d in alim.despesas if d.data_formatada() == "10/08/2026"]
assert len(desp_ago) >= 1, "Despesa do dia 10/08/2026 não encontrada"
assert desp_ago[0].valor == 45.00, f"Valor incorreto: {desp_ago[0].valor}"
print("✓ Despesa de teste validada")

# Verificar aumentos em Esportes (Setembro > Agosto)
esportes = controle2.categorias["Esportes"]
total_agosto = esportes.total_no_periodo(8, 2026)
total_setembro = esportes.total_no_periodo(9, 2026)
print(f"  Esportes Agosto: R$ {total_agosto:.2f}")
print(f"  Esportes Setembro: R$ {total_setembro:.2f}")
assert total_agosto > 0, "Nenhuma despesa em Agosto para Esportes"
assert total_setembro > total_agosto, "Setembro deveria ter mais despesas que Agosto"
print("✓ Aumento de despesas em Esportes detectado")

# Limpar arquivo temporário
Path(arquivo_teste).unlink()

print("\n✅ Todos os testes de geração de dados passaram!")
