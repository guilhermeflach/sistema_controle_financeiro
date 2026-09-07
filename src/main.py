from datetime import date, datetime


class Despesa:
    def __init__(
        self,
        valor: float,
        categoria: str,
        data: str,
        descricao: str = "",
    ) -> None:
        self.valor = float(valor)
        if self.valor <= 0:
            raise ValueError("O valor da despesa deve ser positivo.")

        self.categoria = categoria
        self.data: date = datetime.strptime(data, "%d/%m/%Y").date()
        self.descricao = descricao

    def data_formatada(self) -> str:
        return self.data.strftime("%d/%m/%Y")

    def __repr__(self) -> str:
        return (
            f"Despesa(valor={self.valor!r}, categoria={self.categoria!r}, "
            f"data={self.data_formatada()!r}, descricao={self.descricao!r})"
        )

    def __str__(self) -> str:
        return (
            f"{self.data_formatada()} - {self.categoria}: "
            f"R$ {self.valor:.2f} - {self.descricao}"
        )


class Categoria:
    def __init__(self, nome: str, limite: float | None = None) -> None:
        self.nome = nome
        self.limite = float(limite) if limite is not None else None
        self.despesas: list[Despesa] = []

    def adicionar_despesa(self, despesa: Despesa) -> None:
        if despesa.categoria != self.nome:
            raise ValueError(
                "A categoria da despesa não corresponde à categoria de destino."
            )
        self.despesas.append(despesa)

    def total_gasto(self) -> float:
        return sum(despesa.valor for despesa in self.despesas)

    def total_no_periodo(self, mes: int, ano: int) -> float:
        return sum(
            despesa.valor
            for despesa in self.despesas
            if despesa.data.month == mes and despesa.data.year == ano
        )

    def ultrapassou_limite(self) -> bool:
        return self.limite is not None and self.total_gasto() > self.limite


class ControleFinanceiro:
    def __init__(self) -> None:
        self.categorias: dict[str, Categoria] = {}

    def criar_categoria(
        self, nome: str, limite: float | None = None
    ) -> Categoria:
        if nome in self.categorias:
            raise ValueError(f"A categoria '{nome}' já existe.")

        categoria = Categoria(nome, limite)
        self.categorias[nome] = categoria
        return categoria

    def registrar_despesa(
        self,
        nome_categoria: str,
        valor: float,
        data: str,
        descricao: str = "",
    ) -> Despesa:
        if nome_categoria not in self.categorias:
            raise KeyError(f"A categoria '{nome_categoria}' não existe.")

        despesa = Despesa(valor, nome_categoria, data, descricao)
        self.categorias[nome_categoria].adicionar_despesa(despesa)
        return despesa

    def relatorio_mensal(self, mes: int, ano: int) -> dict[str, float]:
        return {
            nome: categoria.total_no_periodo(mes, ano)
            for nome, categoria in self.categorias.items()
        }