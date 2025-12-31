"""
Value Objects - Objetos de valor imutáveis.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from src.config.constants import FORMATO_DATA_BR, FORMATO_DATA_DB


@dataclass(frozen=True)
class Dinheiro:
    """Representa um valor monetário."""
    valor: float
    moeda: str = "BRL"

    def __str__(self) -> str:
        return f"R$ {self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def __add__(self, other: 'Dinheiro') -> 'Dinheiro':
        if isinstance(other, Dinheiro):
            return Dinheiro(self.valor + other.valor, self.moeda)
        return Dinheiro(self.valor + other, self.moeda)

    def __sub__(self, other: 'Dinheiro') -> 'Dinheiro':
        if isinstance(other, Dinheiro):
            return Dinheiro(self.valor - other.valor, self.moeda)
        return Dinheiro(self.valor - other, self.moeda)

    def __mul__(self, factor: float) -> 'Dinheiro':
        return Dinheiro(self.valor * factor, self.moeda)

    def __truediv__(self, divisor: float) -> 'Dinheiro':
        return Dinheiro(self.valor / divisor, self.moeda)

    @classmethod
    def zero(cls) -> 'Dinheiro':
        return cls(0.0)

    @classmethod
    def from_string(cls, valor_str: str) -> 'Dinheiro':
        """Converte string para Dinheiro."""
        valor_limpo = valor_str.replace("R$", "").replace(" ", "")
        valor_limpo = valor_limpo.replace(".", "").replace(",", ".")
        return cls(float(valor_limpo))


@dataclass(frozen=True)
class Periodo:
    """Representa um período (mês/ano)."""
    mes: int
    ano: int

    def __str__(self) -> str:
        from src.config.constants import MESES
        return f"{MESES[self.mes - 1]}/{self.ano}"

    def __lt__(self, other: 'Periodo') -> bool:
        if self.ano != other.ano:
            return self.ano < other.ano
        return self.mes < other.mes

    def __le__(self, other: 'Periodo') -> bool:
        return self == other or self < other

    @classmethod
    def atual(cls) -> 'Periodo':
        """Retorna o período atual."""
        hoje = date.today()
        return cls(hoje.month, hoje.year)

    def proximo(self) -> 'Periodo':
        """Retorna o próximo período."""
        if self.mes == 12:
            return Periodo(1, self.ano + 1)
        return Periodo(self.mes + 1, self.ano)

    def anterior(self) -> 'Periodo':
        """Retorna o período anterior."""
        if self.mes == 1:
            return Periodo(12, self.ano - 1)
        return Periodo(self.mes - 1, self.ano)

    def adicionar_meses(self, quantidade: int) -> 'Periodo':
        """Adiciona uma quantidade de meses ao período."""
        periodo = self
        for _ in range(abs(quantidade)):
            if quantidade > 0:
                periodo = periodo.proximo()
            else:
                periodo = periodo.anterior()
        return periodo

    def primeiro_dia(self) -> date:
        """Retorna o primeiro dia do período."""
        return date(self.ano, self.mes, 1)

    def ultimo_dia(self) -> date:
        """Retorna o último dia do período."""
        if self.mes == 12:
            proximo_ano = date(self.ano + 1, 1, 1)
        else:
            proximo_ano = date(self.ano, self.mes + 1, 1)
        return proximo_ano - timedelta(days=1)


from datetime import timedelta


def formatar_data(data: Optional[str], formato_origem: str = FORMATO_DATA_DB, 
                   formato_destino: str = FORMATO_DATA_BR) -> str:
    """Formata uma data de um formato para outro."""
    if not data:
        return ""
    try:
        dt = datetime.strptime(data, formato_origem)
        return dt.strftime(formato_destino)
    except ValueError:
        return data


def parse_data(data_str: str, formato: str = FORMATO_DATA_BR) -> Optional[date]:
    """Converte string para date."""
    if not data_str:
        return None
    try:
        return datetime.strptime(data_str, formato).date()
    except ValueError:
        return None
