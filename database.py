"""
Módulo de banco de dados para o controle de finanças.
Utiliza SQLite para persistência local.
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple
import os


class Database:
    def __init__(self, db_name: str = "financas.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Estabelece conexão com o banco de dados."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """Cria as tabelas necessárias no banco de dados."""
        # Tabela de pessoas (pai, mãe, namorada, etc.)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                cor TEXT DEFAULT '#3498db',
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de categorias de despesas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                icone TEXT DEFAULT '💰',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de contas/faturas
        self.cursor.execute("""
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
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id)
            )
        """)

        # Tabela de divisão de contas entre pessoas
        self.cursor.execute("""
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

        # Inserir categorias padrão
        categorias_padrao = [
            ('Cartão de Crédito', '💳'),
            ('Aluguel', '🏠'),
            ('Água', '💧'),
            ('Luz', '💡'),
            ('Internet', '🌐'),
            ('Mercado', '🛒'),
            ('Saúde', '🏥'),
            ('Transporte', '🚗'),
            ('Lazer', '🎮'),
            ('Outros', '📦')
        ]
        
        for nome, icone in categorias_padrao:
            try:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO categorias (nome, icone) VALUES (?, ?)",
                    (nome, icone)
                )
            except sqlite3.IntegrityError:
                pass

        self.conn.commit()

    # ==================== PESSOAS ====================
    
    def adicionar_pessoa(self, nome: str, cor: str = '#3498db') -> int:
        """Adiciona uma nova pessoa ao sistema."""
        self.cursor.execute(
            "INSERT INTO pessoas (nome, cor) VALUES (?, ?)",
            (nome, cor)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def listar_pessoas(self, apenas_ativas: bool = True) -> List[dict]:
        """Lista todas as pessoas cadastradas."""
        query = "SELECT * FROM pessoas"
        if apenas_ativas:
            query += " WHERE ativo = 1"
        query += " ORDER BY nome"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]

    def atualizar_pessoa(self, pessoa_id: int, nome: str, cor: str):
        """Atualiza dados de uma pessoa."""
        self.cursor.execute(
            "UPDATE pessoas SET nome = ?, cor = ? WHERE id = ?",
            (nome, cor, pessoa_id)
        )
        self.conn.commit()

    def desativar_pessoa(self, pessoa_id: int):
        """Desativa uma pessoa (soft delete)."""
        self.cursor.execute(
            "UPDATE pessoas SET ativo = 0 WHERE id = ?",
            (pessoa_id,)
        )
        self.conn.commit()

    def reativar_pessoa(self, pessoa_id: int):
        """Reativa uma pessoa."""
        self.cursor.execute(
            "UPDATE pessoas SET ativo = 1 WHERE id = ?",
            (pessoa_id,)
        )
        self.conn.commit()

    # ==================== CATEGORIAS ====================
    
    def listar_categorias(self) -> List[dict]:
        """Lista todas as categorias."""
        self.cursor.execute("SELECT * FROM categorias ORDER BY nome")
        return [dict(row) for row in self.cursor.fetchall()]

    def adicionar_categoria(self, nome: str, icone: str = '📦') -> int:
        """Adiciona uma nova categoria."""
        self.cursor.execute(
            "INSERT INTO categorias (nome, icone) VALUES (?, ?)",
            (nome, icone)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    # ==================== CONTAS ====================
    
    def adicionar_conta(self, descricao: str, valor_total: float, 
                        parcela_atual: int = 1, total_parcelas: int = 1,
                        data_vencimento: str = None, categoria_id: int = None,
                        observacao: str = None) -> int:
        """Adiciona uma nova conta/fatura."""
        self.cursor.execute("""
            INSERT INTO contas 
            (descricao, valor_total, parcela_atual, total_parcelas, 
             data_vencimento, categoria_id, observacao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (descricao, valor_total, parcela_atual, total_parcelas,
              data_vencimento, categoria_id, observacao))
        self.conn.commit()
        return self.cursor.lastrowid

    def listar_contas(self, status: str = None, mes: int = None, ano: int = None) -> List[dict]:
        """Lista contas com filtros opcionais."""
        query = """
            SELECT c.*, cat.nome as categoria_nome, cat.icone as categoria_icone
            FROM contas c
            LEFT JOIN categorias cat ON c.categoria_id = cat.id
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND c.status = ?"
            params.append(status)
        
        if mes and ano:
            query += " AND strftime('%m', c.data_vencimento) = ? AND strftime('%Y', c.data_vencimento) = ?"
            params.append(f"{mes:02d}")
            params.append(str(ano))
        
        query += " ORDER BY c.data_vencimento DESC, c.criado_em DESC"
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def obter_conta(self, conta_id: int) -> Optional[dict]:
        """Obtém uma conta específica pelo ID."""
        self.cursor.execute("""
            SELECT c.*, cat.nome as categoria_nome, cat.icone as categoria_icone
            FROM contas c
            LEFT JOIN categorias cat ON c.categoria_id = cat.id
            WHERE c.id = ?
        """, (conta_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def atualizar_conta(self, conta_id: int, **kwargs):
        """Atualiza dados de uma conta."""
        campos = []
        valores = []
        for campo, valor in kwargs.items():
            campos.append(f"{campo} = ?")
            valores.append(valor)
        valores.append(conta_id)
        
        query = f"UPDATE contas SET {', '.join(campos)} WHERE id = ?"
        self.cursor.execute(query, valores)
        self.conn.commit()

    def excluir_conta(self, conta_id: int):
        """Exclui uma conta e suas divisões."""
        self.cursor.execute("DELETE FROM contas WHERE id = ?", (conta_id,))
        self.conn.commit()

    def marcar_conta_paga(self, conta_id: int):
        """Marca uma conta como paga."""
        self.cursor.execute(
            "UPDATE contas SET status = 'pago' WHERE id = ?",
            (conta_id,)
        )
        self.conn.commit()

    # ==================== DIVISÃO DE CONTAS ====================
    
    def adicionar_divisao(self, conta_id: int, pessoa_id: int, 
                          valor: float, percentual: float = None) -> int:
        """Adiciona uma divisão de conta para uma pessoa."""
        self.cursor.execute("""
            INSERT OR REPLACE INTO divisao_contas 
            (conta_id, pessoa_id, valor, percentual)
            VALUES (?, ?, ?, ?)
        """, (conta_id, pessoa_id, valor, percentual))
        self.conn.commit()
        return self.cursor.lastrowid

    def listar_divisoes_conta(self, conta_id: int) -> List[dict]:
        """Lista todas as divisões de uma conta."""
        self.cursor.execute("""
            SELECT dc.*, p.nome as pessoa_nome, p.cor as pessoa_cor
            FROM divisao_contas dc
            JOIN pessoas p ON dc.pessoa_id = p.id
            WHERE dc.conta_id = ?
            ORDER BY p.nome
        """, (conta_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def remover_divisoes_conta(self, conta_id: int):
        """Remove todas as divisões de uma conta."""
        self.cursor.execute(
            "DELETE FROM divisao_contas WHERE conta_id = ?",
            (conta_id,)
        )
        self.conn.commit()

    def marcar_divisao_paga(self, divisao_id: int):
        """Marca uma divisão como paga."""
        self.cursor.execute("""
            UPDATE divisao_contas 
            SET pago = 1, data_pagamento = ?
            WHERE id = ?
        """, (datetime.now().strftime('%Y-%m-%d'), divisao_id))
        self.conn.commit()

    # ==================== RELATÓRIOS ====================
    
    def total_por_pessoa(self, mes: int = None, ano: int = None) -> List[dict]:
        """Calcula o total devido por cada pessoa."""
        query = """
            SELECT p.id, p.nome, p.cor,
                   COALESCE(SUM(dc.valor), 0) as total,
                   COALESCE(SUM(CASE WHEN dc.pago = 1 THEN dc.valor ELSE 0 END), 0) as total_pago,
                   COALESCE(SUM(CASE WHEN dc.pago = 0 THEN dc.valor ELSE 0 END), 0) as total_pendente
            FROM pessoas p
            LEFT JOIN divisao_contas dc ON p.id = dc.pessoa_id
            LEFT JOIN contas c ON dc.conta_id = c.id
            WHERE p.ativo = 1
        """
        params = []
        
        if mes and ano:
            query += " AND strftime('%m', c.data_vencimento) = ? AND strftime('%Y', c.data_vencimento) = ?"
            params.append(f"{mes:02d}")
            params.append(str(ano))
        
        query += " GROUP BY p.id, p.nome, p.cor ORDER BY p.nome"
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def resumo_geral(self, mes: int = None, ano: int = None) -> dict:
        """Retorna um resumo geral das finanças."""
        query_base = """
            SELECT 
                COUNT(*) as total_contas,
                COALESCE(SUM(valor_total), 0) as valor_total,
                COALESCE(SUM(CASE WHEN status = 'pago' THEN valor_total ELSE 0 END), 0) as valor_pago,
                COALESCE(SUM(CASE WHEN status = 'pendente' THEN valor_total ELSE 0 END), 0) as valor_pendente
            FROM contas WHERE 1=1
        """
        params = []
        
        if mes and ano:
            query_base += " AND strftime('%m', data_vencimento) = ? AND strftime('%Y', data_vencimento) = ?"
            params.append(f"{mes:02d}")
            params.append(str(ano))
        
        self.cursor.execute(query_base, params)
        row = self.cursor.fetchone()
        return dict(row) if row else {}

    def contas_por_categoria(self, mes: int = None, ano: int = None) -> List[dict]:
        """Retorna totais agrupados por categoria."""
        query = """
            SELECT cat.nome, cat.icone,
                   COUNT(c.id) as quantidade,
                   COALESCE(SUM(c.valor_total), 0) as total
            FROM categorias cat
            LEFT JOIN contas c ON cat.id = c.categoria_id
            WHERE 1=1
        """
        params = []
        
        if mes and ano:
            query += " AND strftime('%m', c.data_vencimento) = ? AND strftime('%Y', c.data_vencimento) = ?"
            params.append(f"{mes:02d}")
            params.append(str(ano))
        
        query += " GROUP BY cat.id, cat.nome, cat.icone ORDER BY total DESC"
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()


# Singleton para acesso global ao banco de dados
_db_instance = None

def get_database() -> Database:
    """Retorna a instância única do banco de dados."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
