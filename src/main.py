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

    def total_no_periodo(self, mes: int, ano: int) -> float:
        return sum(
            despesa.valor
            for despesa in self.despesas
            if despesa.data.month == mes and despesa.data.year == ano
        )

    def ultrapassou_limite(self, mes: int, ano: int) -> bool:
        return self.limite is not None and self.total_no_periodo(mes, ano) > self.limite


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

    @staticmethod
    def _mes_anterior(mes: int, ano: int) -> tuple[int, int]:
        if mes == 1:
            return 12, ano - 1
        return mes - 1, ano

    def _totais_por_categoria(self, mes: int, ano: int) -> dict[str, float]:
        return {
            nome: categoria.total_no_periodo(mes, ano)
            for nome, categoria in self.categorias.items()
        }

    def comparar_com_mes_anterior(self, mes: int, ano: int) -> dict[str, object]:
        mes_anterior, ano_anterior = self._mes_anterior(mes, ano)
        atuais = self._totais_por_categoria(mes, ano)
        anteriores = self._totais_por_categoria(mes_anterior, ano_anterior)
        total_atual = sum(atuais.values())
        total_anterior = sum(anteriores.values())

        if total_anterior == 0:
            comparativo: object = "não há dados do mês anterior"
            return {
                "variacao_total_absoluta": comparativo,
                "variacao_total_percentual": comparativo,
                "variacao_por_categoria_absoluta": comparativo,
                "variacao_por_categoria_percentual": comparativo,
            }

        variacao_absoluta = {}
        variacao_percentual = {}
        for nome, total_atual_categoria in atuais.items():
            total_anterior_categoria = anteriores.get(nome, 0)
            if total_anterior_categoria == 0:
                continue
            diferenca = total_atual_categoria - total_anterior_categoria
            variacao_absoluta[nome] = diferenca
            variacao_percentual[nome] = (diferenca / total_anterior_categoria) * 100

        diferenca_total = total_atual - total_anterior
        return {
            "variacao_total_absoluta": diferenca_total,
            "variacao_total_percentual": (diferenca_total / total_anterior) * 100,
            "variacao_por_categoria_absoluta": variacao_absoluta,
            "variacao_por_categoria_percentual": variacao_percentual,
        }

    def relatorio_mensal(self, mes: int, ano: int) -> dict[str, object]:
        gastos_por_categoria = self._totais_por_categoria(mes, ano)
        total_geral = sum(gastos_por_categoria.values())
        percentuais = {
            nome: (total / total_geral) * 100 if total_geral else 0.0
            for nome, total in gastos_por_categoria.items()
        }

        relatorio: dict[str, object] = {
            "gasto_total_geral": total_geral,
            "gasto_por_categoria": gastos_por_categoria,
            "percentual_por_categoria": percentuais,
        }
        relatorio.update(self.comparar_com_mes_anterior(mes, ano))
        return relatorio

    def categorias_com_aumento_significativo(
        self, mes: int, ano: int
    ) -> list[str]:
        comparacao = self.comparar_com_mes_anterior(mes, ano)
        variacoes = comparacao["variacao_por_categoria_percentual"]
        if not isinstance(variacoes, dict):
            return []
        return [nome for nome, percentual in variacoes.items() if percentual > 30]

    def verificar_alertas(self, mes: int, ano: int) -> list[str]:
        return [
            f"A categoria '{nome}' ultrapassou o limite mensal."
            for nome, categoria in self.categorias.items()
            if categoria.ultrapassou_limite(mes, ano)
        ]