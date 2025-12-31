"""
Serviço de relatórios e estatísticas.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from src.data.repositories import ContaRepository, DivisaoRepository, PessoaRepository
from src.core.entities import ResumoGeral, ResumoPessoa


@dataclass
class RelatorioMensal:
    """Relatório mensal completo."""
    mes: int
    ano: int
    resumo_geral: ResumoGeral
    totais_por_pessoa: List[ResumoPessoa]
    gastos_por_categoria: List[Dict]
    contas_pendentes: List[Dict]
    contas_pagas: List[Dict]


class RelatorioService:
    """Serviço para geração de relatórios e estatísticas."""
    
    def __init__(self):
        self.conta_repo = ContaRepository()
        self.divisao_repo = DivisaoRepository()
        self.pessoa_repo = PessoaRepository()
    
    def get_resumo_geral(self, mes: int = None, ano: int = None) -> dict:
        """Obtém resumo geral das finanças."""
        return self.conta_repo.get_resumo_geral(mes, ano)
    
    def get_total_por_pessoa(self, mes: int = None, ano: int = None) -> List[dict]:
        """Obtém totais por pessoa."""
        return self.divisao_repo.get_total_por_pessoa(mes, ano)
    
    def get_gastos_por_categoria(self, mes: int = None, ano: int = None) -> List[dict]:
        """Obtém gastos agrupados por categoria."""
        return self.conta_repo.get_por_categoria(mes, ano)
    
    def get_relatorio_mensal(self, mes: int, ano: int) -> RelatorioMensal:
        """Gera relatório mensal completo."""
        resumo_dict = self.get_resumo_geral(mes, ano)
        resumo = ResumoGeral.from_dict(resumo_dict)
        
        totais_pessoa = [
            ResumoPessoa.from_dict(p) 
            for p in self.get_total_por_pessoa(mes, ano)
        ]
        
        categorias = self.get_gastos_por_categoria(mes, ano)
        
        contas = self.conta_repo.get_all(mes=mes, ano=ano)
        contas_pendentes = [c for c in contas if c.get('status') == 'pendente']
        contas_pagas = [c for c in contas if c.get('status') == 'pago']
        
        return RelatorioMensal(
            mes=mes,
            ano=ano,
            resumo_geral=resumo,
            totais_por_pessoa=totais_pessoa,
            gastos_por_categoria=categorias,
            contas_pendentes=contas_pendentes,
            contas_pagas=contas_pagas
        )
    
    def get_detalhes_pessoa(self, pessoa_id: int, mes: int = None, 
                             ano: int = None) -> Dict:
        """Obtém detalhes financeiros de uma pessoa."""
        pessoa = self.pessoa_repo.get_by_id(pessoa_id)
        if not pessoa:
            return {}
        
        divisoes = self.divisao_repo.get_by_pessoa(pessoa_id, mes, ano)
        
        total = sum(d.get('valor', 0) for d in divisoes)
        total_pago = sum(d.get('valor', 0) for d in divisoes if d.get('pago'))
        total_pendente = total - total_pago
        
        return {
            'pessoa': pessoa,
            'divisoes': divisoes,
            'total': total,
            'total_pago': total_pago,
            'total_pendente': total_pendente,
            'quantidade_contas': len(divisoes)
        }
    
    def get_evolucao_mensal(self, ano: int) -> List[Dict]:
        """Obtém a evolução mensal de um ano."""
        evolucao = []
        
        for mes in range(1, 13):
            resumo = self.get_resumo_geral(mes, ano)
            evolucao.append({
                'mes': mes,
                'total': resumo.get('valor_total', 0),
                'pago': resumo.get('valor_pago', 0),
                'pendente': resumo.get('valor_pendente', 0)
            })
        
        return evolucao
    
    def get_comparativo_pessoas(self, mes: int = None, ano: int = None) -> List[Dict]:
        """Obtém comparativo entre pessoas."""
        totais = self.get_total_por_pessoa(mes, ano)
        total_geral = sum(t.get('total', 0) for t in totais)
        
        comparativo = []
        for t in totais:
            percentual = (t.get('total', 0) / total_geral * 100) if total_geral > 0 else 0
            comparativo.append({
                **t,
                'percentual_do_total': round(percentual, 2)
            })
        
        return sorted(comparativo, key=lambda x: x.get('total', 0), reverse=True)
