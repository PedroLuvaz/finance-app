"""
Repositories - Padrão Repository para acesso a dados.
Cada repository é responsável por uma entidade específica.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from datetime import datetime

from .database import get_database

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Classe base para repositories."""
    
    def __init__(self):
        self.db = get_database()
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Obtém um registro por ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Obtém todos os registros."""
        pass
    
    @abstractmethod
    def create(self, entity: T) -> int:
        """Cria um novo registro."""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> bool:
        """Atualiza um registro existente."""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Remove um registro."""
        pass


class PessoaRepository(BaseRepository):
    """Repository para entidade Pessoa."""
    
    def get_by_id(self, id: int) -> Optional[dict]:
        return self.db.fetch_one(
            "SELECT * FROM pessoas WHERE id = ?", (id,)
        )
    
    def get_all(self, apenas_ativas: bool = True) -> List[dict]:
        query = "SELECT * FROM pessoas"
        if apenas_ativas:
            query += " WHERE ativo = 1"
        query += " ORDER BY nome"
        return self.db.fetch_all(query)
    
    def get_by_nome(self, nome: str) -> Optional[dict]:
        return self.db.fetch_one(
            "SELECT * FROM pessoas WHERE nome = ?", (nome,)
        )
    
    def create(self, nome: str, cor: str = '#3498db') -> int:
        return self.db.insert(
            "INSERT INTO pessoas (nome, cor) VALUES (?, ?)",
            (nome, cor)
        )
    
    def update(self, id: int, nome: str, cor: str) -> bool:
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE pessoas SET nome = ?, cor = ? WHERE id = ?",
                (nome, cor, id)
            )
        return True
    
    def delete(self, id: int) -> bool:
        """Soft delete - desativa a pessoa."""
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE pessoas SET ativo = 0 WHERE id = ?",
                (id,)
            )
        return True
    
    def reativar(self, id: int) -> bool:
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE pessoas SET ativo = 1 WHERE id = ?",
                (id,)
            )
        return True


class CategoriaRepository(BaseRepository):
    """Repository para entidade Categoria."""
    
    def get_by_id(self, id: int) -> Optional[dict]:
        return self.db.fetch_one(
            "SELECT * FROM categorias WHERE id = ?", (id,)
        )
    
    def get_all(self) -> List[dict]:
        return self.db.fetch_all(
            "SELECT * FROM categorias ORDER BY nome"
        )
    
    def get_by_nome(self, nome: str) -> Optional[dict]:
        return self.db.fetch_one(
            "SELECT * FROM categorias WHERE nome = ?", (nome,)
        )
    
    def create(self, nome: str, icone: str = '📦') -> int:
        return self.db.insert(
            "INSERT INTO categorias (nome, icone) VALUES (?, ?)",
            (nome, icone)
        )
    
    def update(self, id: int, nome: str, icone: str) -> bool:
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE categorias SET nome = ?, icone = ? WHERE id = ?",
                (nome, icone, id)
            )
        return True
    
    def delete(self, id: int) -> bool:
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM categorias WHERE id = ?", (id,))
        return True


class ContaRepository(BaseRepository):
    """Repository para entidade Conta."""
    
    def get_by_id(self, id: int) -> Optional[dict]:
        return self.db.fetch_one("""
            SELECT c.*, cat.nome as categoria_nome, cat.icone as categoria_icone
            FROM contas c
            LEFT JOIN categorias cat ON c.categoria_id = cat.id
            WHERE c.id = ?
        """, (id,))
    
    def get_all(self, status: str = None, mes: int = None, ano: int = None) -> List[dict]:
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
        
        return self.db.fetch_all(query, tuple(params))
    
    def get_by_grupo(self, grupo_id: str) -> List[dict]:
        """Obtém todas as parcelas de um grupo."""
        return self.db.fetch_all("""
            SELECT c.*, cat.nome as categoria_nome, cat.icone as categoria_icone
            FROM contas c
            LEFT JOIN categorias cat ON c.categoria_id = cat.id
            WHERE c.grupo_parcela_id = ?
            ORDER BY c.parcela_atual
        """, (grupo_id,))
    
    def create(self, descricao: str, valor_total: float, parcela_atual: int = 1,
               total_parcelas: int = 1, data_vencimento: str = None,
               categoria_id: int = None, observacao: str = None,
               grupo_parcela_id: str = None) -> int:
        return self.db.insert("""
            INSERT INTO contas 
            (descricao, valor_total, parcela_atual, total_parcelas, 
             data_vencimento, categoria_id, observacao, grupo_parcela_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (descricao, valor_total, parcela_atual, total_parcelas,
              data_vencimento, categoria_id, observacao, grupo_parcela_id))
    
    def update(self, id: int, **kwargs) -> bool:
        if not kwargs:
            return False
        
        campos = []
        valores = []
        for campo, valor in kwargs.items():
            campos.append(f"{campo} = ?")
            valores.append(valor)
        valores.append(id)
        
        with self.db.get_connection() as conn:
            conn.execute(
                f"UPDATE contas SET {', '.join(campos)} WHERE id = ?",
                tuple(valores)
            )
        return True
    
    def delete(self, id: int) -> bool:
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM contas WHERE id = ?", (id,))
        return True
    
    def delete_by_grupo(self, grupo_id: str) -> bool:
        """Exclui todas as parcelas de um grupo."""
        with self.db.get_connection() as conn:
            conn.execute(
                "DELETE FROM contas WHERE grupo_parcela_id = ?",
                (grupo_id,)
            )
        return True
    
    def marcar_pago(self, id: int) -> bool:
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE contas SET status = 'pago' WHERE id = ?",
                (id,)
            )
        return True
    
    def get_resumo_geral(self, mes: int = None, ano: int = None) -> dict:
        query = """
            SELECT 
                COUNT(*) as total_contas,
                COALESCE(SUM(valor_total), 0) as valor_total,
                COALESCE(SUM(CASE WHEN status = 'pago' THEN valor_total ELSE 0 END), 0) as valor_pago,
                COALESCE(SUM(CASE WHEN status = 'pendente' THEN valor_total ELSE 0 END), 0) as valor_pendente
            FROM contas WHERE 1=1
        """
        params = []
        
        if mes and ano:
            query += " AND strftime('%m', data_vencimento) = ? AND strftime('%Y', data_vencimento) = ?"
            params.append(f"{mes:02d}")
            params.append(str(ano))
        
        return self.db.fetch_one(query, tuple(params)) or {}
    
    def get_por_categoria(self, mes: int = None, ano: int = None) -> List[dict]:
        query = """
            SELECT cat.nome, cat.icone,
                   COUNT(c.id) as quantidade,
                   COALESCE(SUM(c.valor_total), 0) as total
            FROM categorias cat
            LEFT JOIN contas c ON cat.id = c.categoria_id
        """
        params = []
        
        if mes and ano:
            query += " AND strftime('%m', c.data_vencimento) = ? AND strftime('%Y', c.data_vencimento) = ?"
            params.append(f"{mes:02d}")
            params.append(str(ano))
        
        query += " GROUP BY cat.id, cat.nome, cat.icone ORDER BY total DESC"
        
        return self.db.fetch_all(query, tuple(params))


class DivisaoRepository(BaseRepository):
    """Repository para entidade DivisaoConta."""
    
    def get_by_id(self, id: int) -> Optional[dict]:
        return self.db.fetch_one("""
            SELECT dc.*, p.nome as pessoa_nome, p.cor as pessoa_cor
            FROM divisao_contas dc
            JOIN pessoas p ON dc.pessoa_id = p.id
            WHERE dc.id = ?
        """, (id,))
    
    def get_all(self) -> List[dict]:
        return self.db.fetch_all("""
            SELECT dc.*, p.nome as pessoa_nome, p.cor as pessoa_cor
            FROM divisao_contas dc
            JOIN pessoas p ON dc.pessoa_id = p.id
        """)
    
    def get_by_conta(self, conta_id: int) -> List[dict]:
        return self.db.fetch_all("""
            SELECT dc.*, p.nome as pessoa_nome, p.cor as pessoa_cor
            FROM divisao_contas dc
            JOIN pessoas p ON dc.pessoa_id = p.id
            WHERE dc.conta_id = ?
            ORDER BY p.nome
        """, (conta_id,))
    
    def get_by_pessoa(self, pessoa_id: int, mes: int = None, ano: int = None) -> List[dict]:
        query = """
            SELECT dc.*, c.descricao, c.parcela_atual, c.total_parcelas,
                   c.data_vencimento, c.status
            FROM divisao_contas dc
            JOIN contas c ON dc.conta_id = c.id
            WHERE dc.pessoa_id = ?
        """
        params = [pessoa_id]
        
        if mes and ano:
            query += " AND strftime('%m', c.data_vencimento) = ? AND strftime('%Y', c.data_vencimento) = ?"
            params.append(f"{mes:02d}")
            params.append(str(ano))
        
        query += " ORDER BY c.data_vencimento"
        
        return self.db.fetch_all(query, tuple(params))
    
    def create(self, conta_id: int, pessoa_id: int, valor: float, 
               percentual: float = None) -> int:
        return self.db.insert("""
            INSERT OR REPLACE INTO divisao_contas 
            (conta_id, pessoa_id, valor, percentual)
            VALUES (?, ?, ?, ?)
        """, (conta_id, pessoa_id, valor, percentual))
    
    def create_batch(self, divisoes: List[dict]) -> bool:
        """Cria múltiplas divisões de uma vez."""
        with self.db.get_connection() as conn:
            conn.executemany("""
                INSERT OR REPLACE INTO divisao_contas 
                (conta_id, pessoa_id, valor, percentual)
                VALUES (:conta_id, :pessoa_id, :valor, :percentual)
            """, divisoes)
        return True
    
    def update(self, id: int, valor: float, percentual: float = None) -> bool:
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE divisao_contas SET valor = ?, percentual = ? WHERE id = ?",
                (valor, percentual, id)
            )
        return True
    
    def delete(self, id: int) -> bool:
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM divisao_contas WHERE id = ?", (id,))
        return True
    
    def delete_by_conta(self, conta_id: int) -> bool:
        with self.db.get_connection() as conn:
            conn.execute(
                "DELETE FROM divisao_contas WHERE conta_id = ?",
                (conta_id,)
            )
        return True
    
    def marcar_pago(self, id: int) -> bool:
        with self.db.get_connection() as conn:
            conn.execute("""
                UPDATE divisao_contas 
                SET pago = 1, data_pagamento = ?
                WHERE id = ?
            """, (datetime.now().strftime('%Y-%m-%d'), id))
        return True
    
    def get_total_por_pessoa(self, mes: int = None, ano: int = None) -> List[dict]:
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
        
        return self.db.fetch_all(query, tuple(params))
