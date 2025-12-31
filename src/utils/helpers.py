"""
Funções auxiliares gerais.
"""

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any

from src.config.constants import MESES


def get_mes_atual() -> int:
    """Retorna o mês atual."""
    return date.today().month


def get_ano_atual() -> int:
    """Retorna o ano atual."""
    return date.today().year


def get_nome_mes(mes: int) -> str:
    """Retorna o nome do mês."""
    if 1 <= mes <= 12:
        return MESES[mes - 1]
    return ""


def get_indice_mes(nome: str) -> int:
    """Retorna o índice do mês (1-12) pelo nome."""
    try:
        return MESES.index(nome) + 1
    except ValueError:
        return 1


def adicionar_meses(data: date, meses: int) -> date:
    """Adiciona meses a uma data."""
    return data + relativedelta(months=meses)


def calcular_divisao_igual(valor_total: float, num_pessoas: int) -> float:
    """Calcula divisão igual entre pessoas."""
    if num_pessoas <= 0:
        return 0
    return round(valor_total / num_pessoas, 2)


def calcular_divisao_proporcional(valor_total: float, 
                                   proporcoes: List[float]) -> List[float]:
    """Calcula divisão proporcional."""
    total_proporcoes = sum(proporcoes)
    if total_proporcoes <= 0:
        return [0] * len(proporcoes)
    
    return [round(valor_total * (p / total_proporcoes), 2) for p in proporcoes]


def agrupar_por(lista: List[Dict], chave: str) -> Dict[Any, List[Dict]]:
    """Agrupa uma lista de dicionários por uma chave."""
    resultado = {}
    for item in lista:
        valor_chave = item.get(chave)
        if valor_chave not in resultado:
            resultado[valor_chave] = []
        resultado[valor_chave].append(item)
    return resultado


def ordenar_por(lista: List[Dict], chave: str, reverso: bool = False) -> List[Dict]:
    """Ordena uma lista de dicionários por uma chave."""
    return sorted(lista, key=lambda x: x.get(chave, ''), reverse=reverso)


def filtrar_por(lista: List[Dict], **filtros) -> List[Dict]:
    """Filtra uma lista de dicionários por múltiplos critérios."""
    resultado = lista
    for chave, valor in filtros.items():
        resultado = [item for item in resultado if item.get(chave) == valor]
    return resultado


def somar_campo(lista: List[Dict], campo: str) -> float:
    """Soma os valores de um campo em uma lista de dicionários."""
    return sum(item.get(campo, 0) for item in lista)
