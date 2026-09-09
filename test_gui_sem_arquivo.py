#!/usr/bin/env python3
"""Teste simulando GUI iniciando sem arquivo dados.json."""

import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, "src")

# Backup se existir
arquivo = "dados.json"
backup = None
if Path(arquivo).exists():
    import shutil
    backup = arquivo + ".bak"
    shutil.move(arquivo, backup)

try:
    # Criar GUI sem arquivo (deve gerar dados de teste)
    with patch("tkinter.Tk"):
        from gui import InterfaceGUI
        mock_root = MagicMock()
        gui = InterfaceGUI(mock_root)
    
    print("✓ GUI instanciada sem arquivo de dados")
    
    # Verificar que arquivo foi criado
    assert Path(arquivo).exists(), "Arquivo dados.json não foi criado!"
    print("✓ Arquivo dados.json criado automaticamente")
    
    # Verificar categorias
    assert len(gui.controle.categorias) == 5, f"Esperado 5 categorias, encontrado {len(gui.controle.categorias)}"
    print("✓ 5 categorias criadas")
    
    # Verificar estrutura do JSON
    with open(arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)
    
    assert len(dados["categorias"]) == 5, "JSON não tem 5 categorias"
    print("✓ JSON contém estrutura correta")
    
    # Verificar limites
    limites = {cat["nome"]: cat["limite"] for cat in dados["categorias"]}
    assert limites["Alimentação"] == 500, "Limite de Alimentação incorreto"
    assert limites["Esportes"] == 250, "Limite de Esportes incorreto"
    assert limites["Cuidados Pessoais"] == 150, "Limite de Cuidados Pessoais incorreto"
    assert limites["Compras"] == 400, "Limite de Compras incorreto"
    assert limites["Educação"] == 300, "Limite de Educação incorreto"
    print("✓ Todos os limites corretos")
    
    # Verificar despesas de Agosto (mês 1)
    despesas_agosto = []
    despesas_setembro = []
    for cat in dados["categorias"]:
        for desp in cat["despesas"]:
            if desp["data"].endswith("/08/2026"):
                despesas_agosto.append(desp)
            elif desp["data"].endswith("/09/2026"):
                despesas_setembro.append(desp)
    
    assert len(despesas_agosto) == 5, f"Esperado 5 despesas em Agosto, encontrado {len(despesas_agosto)}"
    print("✓ 5 despesas de Agosto registradas")
    
    # Verificar despesas de Setembro (mês 2)
    assert len(despesas_setembro) == 5, f"Esperado 5 despesas em Setembro, encontrado {len(despesas_setembro)}"
    print("✓ 5 despesas de Setembro registradas")
    
    # Verificar aumento em Esportes (119.90 + 119.90 + 180.00 = 419.80)
    esportes_dados = next(cat for cat in dados["categorias"] if cat["nome"] == "Esportes")
    sept_despesas = [d for d in esportes_dados["despesas"] if d["data"].endswith("/09/2026")]
    total_sept_esportes = sum(d["valor"] for d in sept_despesas)
    assert total_sept_esportes > 250, f"Esperado estouro de limite em Esportes (>{250}), encontrado {total_sept_esportes}"
    print(f"✓ Esportes em Setembro: R$ {total_sept_esportes:.2f} (ultrapassa limite de 250)")
    
    print("\n✅ Teste completo de inicialização sem arquivo passou!")
    
finally:
    # Limpar
    if Path(arquivo).exists():
        Path(arquivo).unlink()
    if backup and Path(backup).exists():
        import shutil
        shutil.move(backup, arquivo)
