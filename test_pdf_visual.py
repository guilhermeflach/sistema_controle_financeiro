#!/usr/bin/env python3
"""Teste de geração de PDF com dados de teste para validação visual."""

import sys
from pathlib import Path

sys.path.insert(0, "src")

from main import ControleFinanceiro
from gui import gerar_dados_de_teste
from relatorio_pdf import gerar_relatorio_pdf

# Criar controle e gerar dados de teste
controle = ControleFinanceiro()
gerar_dados_de_teste(controle, "dados_teste_pdf.json")

# Gerar PDF para Setembro 2026 (mês com aumentos e alertas)
caminho_pdf = "relatorio_setembro_2026.pdf"
try:
    gerar_relatorio_pdf(controle, 9, 2026, caminho_pdf)
    print(f"✓ PDF gerado com sucesso: {caminho_pdf}")
    
    # Verificar que o arquivo foi criado
    assert Path(caminho_pdf).exists(), "Arquivo PDF não foi criado!"
    
    # Verificar tamanho mínimo (deve ter conteúdo)
    tamanho = Path(caminho_pdf).stat().st_size
    assert tamanho > 1000, f"Arquivo PDF muito pequeno ({tamanho} bytes)"
    print(f"✓ Tamanho do PDF: {tamanho} bytes")
    
    # Validar que é um PDF válido (começa com %PDF)
    with open(caminho_pdf, "rb") as f:
        header = f.read(4)
        assert header == b"%PDF", "Arquivo não é um PDF válido"
    print("✓ Arquivo é um PDF válido")
    
    # Validar relatório de Agosto também
    caminho_pdf_ago = "relatorio_agosto_2026.pdf"
    gerar_relatorio_pdf(controle, 8, 2026, caminho_pdf_ago)
    assert Path(caminho_pdf_ago).exists(), "PDF de Agosto não foi criado!"
    print(f"✓ PDF de Agosto também gerado: {caminho_pdf_ago}")
    
    # Limpeza
    Path("dados_teste_pdf.json").unlink()
    
    print("\n✅ Teste de geração de PDF passou!")
    print(f"\n📄 Arquivos gerados para inspeção visual:")
    print(f"   - {caminho_pdf} (com alertas de limite e aumento > 30%)")
    print(f"   - {caminho_pdf_ago} (relatório base)")
    
except Exception as e:
    print(f"❌ Erro ao gerar PDF: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
