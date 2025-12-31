"""
Formatadores de dados.
"""

from datetime import datetime, date
from typing import Optional

from src.config.constants import FORMATO_DATA_BR, FORMATO_DATA_DB, MESES


def formatar_moeda(valor: float) -> str:
    """Formata valor como moeda brasileira."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(data: Optional[str], 
                   formato_origem: str = FORMATO_DATA_DB,
                   formato_destino: str = FORMATO_DATA_BR) -> str:
    """Converte data entre formatos."""
    if not data:
        return ""
    try:
        dt = datetime.strptime(data, formato_origem)
        return dt.strftime(formato_destino)
    except ValueError:
        return data


def formatar_data_db(data: Optional[str]) -> Optional[str]:
    """Converte data para formato do banco."""
    if not data:
        return None
    try:
        dt = datetime.strptime(data, FORMATO_DATA_BR)
        return dt.strftime(FORMATO_DATA_DB)
    except ValueError:
        return data


def formatar_parcelas(atual: int, total: int) -> str:
    """Formata parcelas no formato X/X."""
    return f"{atual}/{total}"


def formatar_percentual(valor: float) -> str:
    """Formata valor como percentual."""
    return f"{valor:.1f}%"


def formatar_periodo(mes: int, ano: int) -> str:
    """Formata período (mês/ano)."""
    return f"{MESES[mes - 1]}/{ano}"


def parse_valor_moeda(valor_str: str) -> float:
    """Converte string de moeda para float."""
    valor_limpo = valor_str.replace("R$", "").replace(" ", "")
    valor_limpo = valor_limpo.replace(".", "").replace(",", ".")
    return float(valor_limpo)


def parse_data(data_str: str, formato: str = FORMATO_DATA_BR) -> Optional[date]:
    """Converte string para date."""
    if not data_str:
        return None
    try:
        return datetime.strptime(data_str, formato).date()
    except ValueError:
        return None


def abreviar_texto(texto: str, max_len: int = 30) -> str:
    """Abrevia texto se for muito longo."""
    if len(texto) <= max_len:
        return texto
    return texto[:max_len - 3] + "..."
