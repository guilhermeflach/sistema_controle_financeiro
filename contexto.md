# Contexto: Sistema de Controle Financeiro Residencial (Python, POO)

## Objetivo

Implementar um sistema de controle financeiro residencial em Python orientado a objetos,
seguindo ESTRITAMENTE a arquitetura descrita abaixo. Não improvise estrutura de classes,
não adicione camadas extras, não use dataclasses — todas as classes devem ser escritas
manualmente com `__init__` explícito.

Implemente na seguinte ORDEM, do mais específico para o mais geral, e não avance para a
próxima etapa sem concluir e revisar a anterior:

1. Classe `Despesa`
2. Classe `Categoria`
3. Classe `ControleFinanceiro`
4. Operações de análise (comparação mensal, detecção de aumento, alertas de limite)
5. Menu/interface de linha de comando
6. Exportação de relatório em PDF (biblioteca `fpdf`)

As categorias (Educação, Energia, Água, Internet, Alimentação, Transporte, Residência,
Entretenimento) citadas no enunciado original são apenas EXEMPLOS. Não há lista fixa de
categorias válidas — o usuário cria quantas categorias quiser, com o nome que quiser, através
do `ControleFinanceiro`. Toda despesa só pode ser registrada em uma categoria que já exista.

---

## 1. Classe `Despesa`

Representa o registro de uma única despesa. É um objeto passivo — não cria outras despesas,
não sabe nada sobre outras categorias, não faz cálculos de agregação, e não se auto-registra
em lugar nenhum.

**Atributos:**
- `valor: float` — deve ser positivo; validar no `__init__` e levantar `ValueError` se
  `valor <= 0`.
- `categoria: str` — nome da categoria à qual a despesa pertence. É passado como parâmetro no
  momento da criação, pelo `ControleFinanceiro` (ver seção 3) — o usuário escolhe esse nome a
  partir de uma categoria já existente, nunca digitando um nome arbitrário. Mantenha este
  atributo mesmo parecendo redundante com a estrutura de containment (é fidelidade literal ao
  enunciado, e serve de dado de consistência — ver validação na seção 2).
- `data: date` — internamente é um objeto `datetime.date`. O construtor deve aceitar a entrada
  como string no formato `"DD/MM/AAAA"` e converter internamente com `datetime.strptime`. Nunca
  exponha `date` cru para o usuário final — toda exibição/exportação deve formatar de volta para
  `"DD/MM/AAAA"` via `strftime`.
- `descricao: str` — texto livre, pode ser vazio por padrão (`""`).

**Métodos:**
- `__init__` com as validações acima.
- Um método de formatação de exibição (ex.: `data_formatada()` retornando string `"DD/MM/AAAA"`).
- `__repr__` ou `__str__` legível, útil para depuração e reaproveitável em relatórios.
- NÃO adicione método de "criar despesa" dentro desta classe — a criação é feita pelo `__init__`,
  chamado externamente pelo `ControleFinanceiro`.

---

## 2. Classe `Categoria`

Representa uma categoria de gastos definida pelo usuário (nome livre).

**Atributos:**
- `nome: str` — nome da categoria, definido pelo usuário na criação.
- `limite: float | None` — opcional; se `None`, a categoria não tem limite de gasto definido.
- `despesas: list[Despesa]` — lista interna, inicializada vazia. É a ÚNICA fonte de verdade
  sobre quais despesas pertencem a esta categoria.

**Métodos:**
- `adicionar_despesa(despesa: Despesa)` — recebe uma instância de `Despesa` JÁ PRONTA (construída
  pelo `ControleFinanceiro`) e apenas a anexa à lista `despesas`. A `Categoria` NÃO cria despesas,
  apenas as armazena.
  - Deve validar consistência antes de aceitar: `despesa.categoria == self.nome`. Se não
    corresponder, levantar uma exceção (ex.: `ValueError`) em vez de aceitar silenciosamente.
    Essa validação é uma rede de segurança — na prática, como o parâmetro de categoria vem de
    uma escolha do usuário entre categorias já existentes, os dois lados devem sempre coincidir,
    mas a checagem evita que um erro de programação futuro guarde uma despesa na categoria
    errada sem ser notado.
- `total_gasto() -> float` — soma o valor de todas as despesas da lista.
- `total_no_periodo(mes: int, ano: int) -> float` — soma apenas despesas cujo `.data.month` e
  `.data.year` correspondem ao período informado. Essencial para a análise mensal.
- `ultrapassou_limite() -> bool` — retorna `True` se `limite` estiver definido e `total_gasto()`
  o exceder; retorna `False` se não houver limite definido.
- NÃO adicione método de "criar categoria" dentro desta classe — uma instância de `Categoria`
  não cria outras categorias; isso é responsabilidade do `ControleFinanceiro`.
- NÃO adicione método de "registrar despesa" (que constrói e guarda) — a criação da `Despesa`
  agora é responsabilidade do `ControleFinanceiro`, não da `Categoria`.

---

## 3. Classe `ControleFinanceiro`

É o ponto de entrada do sistema e o mediador de tudo que exige visão do conjunto de categorias.
Também é quem agora cria as instâncias de `Despesa`.

**Atributos:**
- `categorias: dict[str, Categoria]` — dicionário nome → instância de `Categoria`. Inicializado
  vazio.

**Métodos:**
- `criar_categoria(nome, limite=None)` — cria uma nova instância de `Categoria` e a adiciona ao
  dicionário. Deve validar que não existe já uma categoria com esse nome (evitar sobrescrever
  silenciosamente).
- `registrar_despesa(nome_categoria, valor, data, descricao)`:
  1. Verifica se `nome_categoria` existe no dicionário `categorias`. Se não existir, levantar
     erro claro (ex.: `KeyError` ou exceção customizada) — NUNCA criar a categoria
     implicitamente aqui. O usuário só pode escolher entre categorias já cadastradas.
  2. Instancia `Despesa(valor, nome_categoria, data, descricao)` diretamente.
  3. Localiza a `Categoria` correspondente no dicionário e chama
     `categoria.adicionar_despesa(despesa)` para guardar a despesa recém-criada.
  - Esta é a ÚNICA forma de registrar uma despesa no sistema — nem `Despesa` nem `Categoria`
    disparam esse fluxo por conta própria.
- `relatorio_mensal(mes, ano) -> dict` — percorre todas as categorias e retorna um resumo
  (nome da categoria → total gasto naquele período), usando `Categoria.total_no_periodo`.
- NUNCA deve guardar despesas fora das categorias (nenhuma lista paralela de despesas no
  `ControleFinanceiro`) — instancia a `Despesa`, mas o armazenamento definitivo é sempre feito
  por dentro da `Categoria` correspondente.

---

## 4. Operações de análise (dentro de `ControleFinanceiro`)

Construir depois que as três classes acima estiverem completas e testadas:

- `comparar_com_mes_anterior(mes, ano) -> dict` — para cada categoria, compara
  `total_no_periodo(mes, ano)` com o mês anterior e retorna a diferença absoluta/percentual.
- `categorias_com_aumento_significativo(mes, ano, limiar_percentual=20.0) -> list[str]` — usa o
  resultado da comparação acima e filtra categorias cujo aumento percentual excede o limiar.
- `verificar_alertas() -> list[str]` — percorre todas as categorias e retorna mensagens para as
  que tiveram `ultrapassou_limite() == True`.

Estas operações NÃO devem duplicar lógica de soma — sempre reaproveitar os métodos já expostos
por `Categoria` (`total_gasto`, `total_no_periodo`, `ultrapassou_limite`).

---

## 5. Menu / interface de linha de comando

Um loop simples de terminal (`while True` com `input()`) que expõe as operações do
`ControleFinanceiro`: criar categoria, registrar despesa (o usuário escolhe o nome da categoria
a partir de uma lista das já cadastradas — nunca digita um nome livre nesse momento), ver
relatório mensal, ver alertas, comparar com mês anterior, exportar PDF, sair. Validar entradas
do usuário (valores numéricos, datas no formato correto) antes de repassar aos métodos das
classes de domínio — a interface NUNCA deve conter lógica de negócio, apenas coletar dados e
chamar os métodos corretos.

---

## 6. Exportação de relatório em PDF

Usar a biblioteca `fpdf` (`pip install fpdf2`) para gerar um PDF com o relatório mensal:
nome de cada categoria, total gasto, lista de despesas (data formatada, valor, descrição), e
indicação visual das categorias que ultrapassaram o limite. Esta funcionalidade fica isolada
em uma função ou classe separada (ex.: `gerar_relatorio_pdf(controle, mes, ano, caminho_saida)`)
que apenas LÊ dados do `ControleFinanceiro` — nunca modifica o estado do sistema.

---

## Regras gerais de implementação

- Cadeia de responsabilidade final:
  - `Despesa`: não cria nada — é o próprio registro. Validada no seu `__init__`.
  - `Categoria`: NÃO cria despesas — apenas armazena (`adicionar_despesa`), com validação de
    consistência (`despesa.categoria == self.nome`). Não cria outras categorias.
  - `ControleFinanceiro`: cria categorias (`criar_categoria`) E cria despesas
    (`registrar_despesa`, que instancia `Despesa` e delega o armazenamento à `Categoria`
    correta). Centraliza toda operação que exige olhar múltiplas categorias (relatórios,
    comparação mensal, alertas, exportação).
- O usuário nunca escolhe/digita um nome de categoria livremente ao registrar uma despesa —
  sempre seleciona entre as categorias já cadastradas no `ControleFinanceiro`.
- Nenhuma camada deve ser instanciada ou manipulada "pulando" a camada intermediária — por
  exemplo, ninguém deve chamar `categoria.despesas.append(...)` diretamente de fora da própria
  `Categoria`.
- Não adicione bibliotecas, camadas de persistência (banco de dados, arquivos), autenticação de
  usuário ou qualquer funcionalidade não mencionada aqui, mesmo que pareça uma boa prática geral.
- Peça confirmação/mostre o código de cada classe antes de avançar para a próxima etapa da
  ordem definida acima.
