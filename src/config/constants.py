"""
Constantes globais do aplicativo.
"""

from enum import Enum
from typing import List, Tuple


class StatusConta(Enum):
    """Status possíveis de uma conta."""
    PENDENTE = "pendente"
    PAGO = "pago"
    ATRASADO = "atrasado"
    CANCELADO = "cancelado"


class TipoDivisao(Enum):
    """Tipos de divisão de conta."""
    IGUAL = "igual"
    PROPORCIONAL = "proporcional"
    PERSONALIZADO = "personalizado"


# Categorias padrão com ícones
CATEGORIAS_PADRAO: List[Tuple[str, str]] = [
    ("Cartão de Crédito", "💳"),
    ("Aluguel", "🏠"),
    ("Água", "💧"),
    ("Luz", "💡"),
    ("Internet", "🌐"),
    ("Mercado", "🛒"),
    ("Saúde", "🏥"),
    ("Transporte", "🚗"),
    ("Lazer", "🎮"),
    ("Educação", "📚"),
    ("Alimentação", "🍔"),
    ("Vestuário", "👕"),
    ("Streaming", "📺"),
    ("Telefone", "📱"),
    ("Outros", "📦"),
]

# Cores padrão para pessoas
CORES_PADRAO: List[str] = [
    "#3498db",  # Azul
    "#e74c3c",  # Vermelho
    "#27ae60",  # Verde
    "#9b59b6",  # Roxo
    "#f39c12",  # Laranja
    "#1abc9c",  # Turquesa
    "#e91e63",  # Rosa
    "#00bcd4",  # Ciano
    "#ff5722",  # Laranja escuro
    "#795548",  # Marrom
]

# Meses do ano
MESES: List[str] = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"
]

# Anos disponíveis para seleção
ANOS_DISPONIVEIS: List[int] = list(range(2020, 2035))

# Formatos de data
FORMATO_DATA_BR = "%d/%m/%Y"
FORMATO_DATA_DB = "%Y-%m-%d"
FORMATO_DATA_HORA_BR = "%d/%m/%Y %H:%M"

# Limites
MAX_PARCELAS = 48
MAX_DESCRICAO = 200
MAX_OBSERVACAO = 500
