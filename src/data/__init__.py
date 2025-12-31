"""
Módulo de acesso a dados (Data Access Layer).
"""

from .database import Database, get_database
from .repositories import (
    PessoaRepository,
    CategoriaRepository,
    ContaRepository,
    DivisaoRepository
)

__all__ = [
    'Database',
    'get_database',
    'PessoaRepository',
    'CategoriaRepository', 
    'ContaRepository',
    'DivisaoRepository'
]
