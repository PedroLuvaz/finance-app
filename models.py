"""
Modelos de dados para o controle de finanças.
Classes que representam as entidades do sistema.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class StatusConta(Enum):
    PENDENTE = "pendente"
    PAGO = "pago"
    ATRASADO = "atrasado"
    CANCELADO = "cancelado"


@dataclass
class Pessoa:
    """Representa uma pessoa que pode ter despesas atribuídas."""
    id: Optional[int] = None
    nome: str = ""
    cor: str = "#3498db"
    ativo: bool = True
    criado_em: Optional[datetime] = None

    def __str__(self):
        return self.nome

    @classmethod
    def from_dict(cls, data: dict) -> 'Pessoa':
        return cls(
            id=data.get('id'),
            nome=data.get('nome', ''),
            cor=data.get('cor', '#3498db'),
            ativo=bool(data.get('ativo', 1)),
            criado_em=data.get('criado_em')
        )


@dataclass
class Categoria:
    """Representa uma categoria de despesa."""
    id: Optional[int] = None
    nome: str = ""
    icone: str = "📦"
    criado_em: Optional[datetime] = None

    def __str__(self):
        return f"{self.icone} {self.nome}"

    @classmethod
    def from_dict(cls, data: dict) -> 'Categoria':
        return cls(
            id=data.get('id'),
            nome=data.get('nome', ''),
            icone=data.get('icone', '📦'),
            criado_em=data.get('criado_em')
        )


@dataclass
class DivisaoConta:
    """Representa a divisão de uma conta para uma pessoa específica."""
    id: Optional[int] = None
    conta_id: Optional[int] = None
    pessoa_id: Optional[int] = None
    pessoa_nome: str = ""
    pessoa_cor: str = "#3498db"
    valor: float = 0.0
    percentual: Optional[float] = None
    pago: bool = False
    data_pagamento: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'DivisaoConta':
        return cls(
            id=data.get('id'),
            conta_id=data.get('conta_id'),
            pessoa_id=data.get('pessoa_id'),
            pessoa_nome=data.get('pessoa_nome', ''),
            pessoa_cor=data.get('pessoa_cor', '#3498db'),
            valor=data.get('valor', 0.0),
            percentual=data.get('percentual'),
            pago=bool(data.get('pago', 0)),
            data_pagamento=data.get('data_pagamento')
        )


@dataclass
class Conta:
    """Representa uma conta ou fatura."""
    id: Optional[int] = None
    descricao: str = ""
    valor_total: float = 0.0
    parcela_atual: int = 1
    total_parcelas: int = 1
    data_vencimento: Optional[str] = None
    categoria_id: Optional[int] = None
    categoria_nome: str = ""
    categoria_icone: str = "📦"
    status: str = "pendente"
    observacao: Optional[str] = None
    criado_em: Optional[datetime] = None
    divisoes: List[DivisaoConta] = field(default_factory=list)

    @property
    def valor_parcela(self) -> float:
        """Calcula o valor de cada parcela."""
        if self.total_parcelas > 0:
            return self.valor_total / self.total_parcelas
        return self.valor_total

    @property
    def parcelas_formatado(self) -> str:
        """Retorna as parcelas no formato X/X."""
        return f"{self.parcela_atual}/{self.total_parcelas}"

    @property
    def is_parcelado(self) -> bool:
        """Verifica se a conta é parcelada."""
        return self.total_parcelas > 1

    @property
    def status_enum(self) -> StatusConta:
        """Retorna o status como enum."""
        try:
            return StatusConta(self.status)
        except ValueError:
            return StatusConta.PENDENTE

    def __str__(self):
        parcelas = f" ({self.parcelas_formatado})" if self.is_parcelado else ""
        return f"{self.descricao}{parcelas} - R$ {self.valor_total:.2f}"

    @classmethod
    def from_dict(cls, data: dict) -> 'Conta':
        return cls(
            id=data.get('id'),
            descricao=data.get('descricao', ''),
            valor_total=data.get('valor_total', 0.0),
            parcela_atual=data.get('parcela_atual', 1),
            total_parcelas=data.get('total_parcelas', 1),
            data_vencimento=data.get('data_vencimento'),
            categoria_id=data.get('categoria_id'),
            categoria_nome=data.get('categoria_nome', ''),
            categoria_icone=data.get('categoria_icone', '📦'),
            status=data.get('status', 'pendente'),
            observacao=data.get('observacao'),
            criado_em=data.get('criado_em'),
            divisoes=[]
        )


@dataclass
class ResumoPessoa:
    """Resumo financeiro de uma pessoa."""
    id: int
    nome: str
    cor: str
    total: float = 0.0
    total_pago: float = 0.0
    total_pendente: float = 0.0

    @property
    def percentual_pago(self) -> float:
        """Calcula o percentual já pago."""
        if self.total > 0:
            return (self.total_pago / self.total) * 100
        return 0.0

    @classmethod
    def from_dict(cls, data: dict) -> 'ResumoPessoa':
        return cls(
            id=data.get('id', 0),
            nome=data.get('nome', ''),
            cor=data.get('cor', '#3498db'),
            total=data.get('total', 0.0),
            total_pago=data.get('total_pago', 0.0),
            total_pendente=data.get('total_pendente', 0.0)
        )


@dataclass
class ResumoGeral:
    """Resumo geral das finanças."""
    total_contas: int = 0
    valor_total: float = 0.0
    valor_pago: float = 0.0
    valor_pendente: float = 0.0

    @property
    def percentual_pago(self) -> float:
        """Calcula o percentual já pago."""
        if self.valor_total > 0:
            return (self.valor_pago / self.valor_total) * 100
        return 0.0

    @classmethod
    def from_dict(cls, data: dict) -> 'ResumoGeral':
        return cls(
            total_contas=data.get('total_contas', 0),
            valor_total=data.get('valor_total', 0.0),
            valor_pago=data.get('valor_pago', 0.0),
            valor_pendente=data.get('valor_pendente', 0.0)
        )
