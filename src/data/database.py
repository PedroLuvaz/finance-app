"""
Gerenciador de conexão com o banco de dados SQLite.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Any
from contextlib import contextmanager

from src.config.settings import settings
from src.config.constants import CATEGORIAS_PADRAO


class Database:
    """Gerenciador de conexão com banco de dados SQLite."""
    
    _instance: Optional['Database'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.db_path = settings.database.path
        self._ensure_data_dir()
        self._create_tables()
        self._initialized = True
    
    def _ensure_data_dir(self):
        """Garante que o diretório de dados existe."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexão com o banco."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Executa uma query e retorna o cursor."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """Executa uma query para múltiplos registros."""
        with self.get_connection() as conn:
            conn.executemany(query, params_list)
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[dict]:
        """Executa query e retorna um registro."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[dict]:
        """Executa query e retorna todos os registros."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def insert(self, query: str, params: tuple = ()) -> int:
        """Insere um registro e retorna o ID."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid
    
    def _create_tables(self):
        """Cria as tabelas do banco de dados."""
        with self.get_connection() as conn:
            # Tabela de pessoas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pessoas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    cor TEXT DEFAULT '#3498db',
                    ativo INTEGER DEFAULT 1,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de categorias
            conn.execute("""
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    icone TEXT DEFAULT '💰',
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de contas/faturas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS contas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descricao TEXT NOT NULL,
                    valor_total REAL NOT NULL,
                    parcela_atual INTEGER DEFAULT 1,
                    total_parcelas INTEGER DEFAULT 1,
                    data_vencimento TEXT,
                    categoria_id INTEGER,
                    status TEXT DEFAULT 'pendente',
                    observacao TEXT,
                    grupo_parcela_id TEXT,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
                )
            """)
            
            # Tabela de divisão de contas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS divisao_contas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conta_id INTEGER NOT NULL,
                    pessoa_id INTEGER NOT NULL,
                    valor REAL NOT NULL,
                    percentual REAL,
                    pago INTEGER DEFAULT 0,
                    data_pagamento TEXT,
                    FOREIGN KEY (conta_id) REFERENCES contas(id) ON DELETE CASCADE,
                    FOREIGN KEY (pessoa_id) REFERENCES pessoas(id),
                    UNIQUE(conta_id, pessoa_id)
                )
            """)
            
            # Índices para performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_contas_data 
                ON contas(data_vencimento)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_contas_grupo 
                ON contas(grupo_parcela_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_divisao_conta 
                ON divisao_contas(conta_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_divisao_pessoa 
                ON divisao_contas(pessoa_id)
            """)
            
            # Inserir categorias padrão
            for nome, icone in CATEGORIAS_PADRAO:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO categorias (nome, icone) VALUES (?, ?)",
                        (nome, icone)
                    )
                except sqlite3.IntegrityError:
                    pass


# Singleton global
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """Retorna a instância única do banco de dados."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
