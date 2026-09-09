# Sistema de Controle Financeiro Residencial

Sistema de gerenciamento financeiro desenvolvido em Python, com arquitetura estritamente baseada em Programação Orientada a Objetos (POO). O software permite o registro de despesas mensais, definição de limites por categoria, emissão de alertas automáticos e exportação de relatórios em PDF.

## 🚀 Como Executar o Projeto

1. Certifique-se de ter o Python 3 instalado em sua máquina.
2. Instale a biblioteca necessária para a geração dos relatórios em PDF:
   ```bash
   pip install -r requirements.txt


3. A partir da pasta raiz do projeto, execute a interface gráfica:
   Bash: python src/gui.py

O sistema foi desenhado separando claramente a lógica de negócios da camada de apresentação:

Domínio (main.py): As classes Categoria e Despesa são responsáveis unicamente por encapsular e calcular os próprios dados locais. A classe ControleFinanceiro atua como mediadora, orquestrando as análises complexas (como variações percentuais e comparativos mensais) a partir das somas locais das categorias.

Interface Gráfica (gui.py): Desenvolvida com tkinter nativo. Não contém lógica de negócios, sendo responsável apenas por coletar inputs de forma validada, formatar a exibição em tela e invocar os métodos do controlador.

Exportação (relatorio_pdf.py): Módulo isolado utilizando fpdf2 que apenas consome os dados processados pelo sistema para desenhar o layout final em PDF, sem alterar o estado da aplicação.

Persistência de Dados: Implementada via serialização JSON (dados.json), preservando fielmente a estrutura de instâncias, listas e dicionários em memória durante o ciclo de vida da aplicação.


O repositório já inclui um arquivo dados.json populado com categorias (com seus respectivos limites) e despesas fictícias cadastradas nos meses de Agosto e Setembro, permitindo o teste imediato do fluxo de comparação mensal, alertas de estouro de orçamento e detecção de aumento significativo (>30%).

Desenvolvido por Guilherme Flach.

