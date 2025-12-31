"""
Serviço de gestão de contas e parcelas.
Contém a lógica de negócio para criação de contas parceladas.
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from uuid import uuid4

from src.data.repositories import ContaRepository, DivisaoRepository, CategoriaRepository
from src.core.entities import Conta
from src.config.constants import FORMATO_DATA_DB, FORMATO_DATA_BR, MAX_PARCELAS


@dataclass
class ResultadoOperacao:
    """Resultado de uma operação de serviço."""
    sucesso: bool
    mensagem: str = ""
    dados: any = None


@dataclass
class DadosConta:
    """Dados para criação/edição de conta."""
    descricao: str
    valor_total: float
    parcela_atual: int = 1
    total_parcelas: int = 1
    data_vencimento: Optional[str] = None
    categoria_id: Optional[int] = None
    observacao: Optional[str] = None
    gerar_parcelas_futuras: bool = False
    divisoes: List[Dict] = None

    def __post_init__(self):
        if self.divisoes is None:
            self.divisoes = []


class ContaService:
    """Serviço para operações com contas."""
    
    def __init__(self):
        self.conta_repo = ContaRepository()
        self.divisao_repo = DivisaoRepository()
        self.categoria_repo = CategoriaRepository()
    
    def listar_contas(self, status: str = None, mes: int = None, 
                       ano: int = None) -> List[dict]:
        """Lista contas com filtros opcionais."""
        return self.conta_repo.get_all(status, mes, ano)
    
    def obter_conta(self, conta_id: int) -> Optional[dict]:
        """Obtém uma conta pelo ID."""
        conta = self.conta_repo.get_by_id(conta_id)
        if conta:
            conta['divisoes'] = self.divisao_repo.get_by_conta(conta_id)
        return conta
    
    def listar_categorias(self) -> List[dict]:
        """Lista todas as categorias."""
        return self.categoria_repo.get_all()
    
    def criar_conta(self, dados: DadosConta) -> ResultadoOperacao:
        """
        Cria uma nova conta.
        Se gerar_parcelas_futuras=True e total_parcelas > 1,
        gera automaticamente as parcelas para os meses seguintes.
        """
        # Validações
        validacao = self._validar_dados_conta(dados)
        if not validacao.sucesso:
            return validacao
        
        try:
            # Se for parcelada e deve gerar parcelas futuras
            if dados.gerar_parcelas_futuras and dados.total_parcelas > 1:
                return self._criar_conta_parcelada(dados)
            else:
                return self._criar_conta_simples(dados)
        
        except Exception as e:
            return ResultadoOperacao(False, f"Erro ao criar conta: {str(e)}")
    
    def _validar_dados_conta(self, dados: DadosConta) -> ResultadoOperacao:
        """Valida os dados da conta."""
        if not dados.descricao or not dados.descricao.strip():
            return ResultadoOperacao(False, "A descrição é obrigatória")
        
        if dados.valor_total <= 0:
            return ResultadoOperacao(False, "O valor deve ser maior que zero")
        
        if dados.total_parcelas < 1:
            return ResultadoOperacao(False, "O número de parcelas deve ser pelo menos 1")
        
        if dados.total_parcelas > MAX_PARCELAS:
            return ResultadoOperacao(False, f"O número máximo de parcelas é {MAX_PARCELAS}")
        
        if dados.parcela_atual < 1 or dados.parcela_atual > dados.total_parcelas:
            return ResultadoOperacao(False, "Número da parcela inválido")
        
        return ResultadoOperacao(True)
    
    def _criar_conta_simples(self, dados: DadosConta) -> ResultadoOperacao:
        """Cria uma conta simples (sem gerar parcelas futuras)."""
        conta_id = self.conta_repo.create(
            descricao=dados.descricao.strip(),
            valor_total=dados.valor_total,
            parcela_atual=dados.parcela_atual,
            total_parcelas=dados.total_parcelas,
            data_vencimento=dados.data_vencimento,
            categoria_id=dados.categoria_id,
            observacao=dados.observacao
        )
        
        # Adicionar divisões
        if dados.divisoes:
            self._criar_divisoes(conta_id, dados.divisoes)
        
        return ResultadoOperacao(
            True, 
            "Conta criada com sucesso",
            {'conta_id': conta_id}
        )
    
    def _criar_conta_parcelada(self, dados: DadosConta) -> ResultadoOperacao:
        """
        Cria uma conta parcelada gerando automaticamente todas as parcelas.
        Cada parcela é criada para o mês seguinte com a mesma divisão.
        """
        # Gerar ID único para o grupo de parcelas
        grupo_id = str(uuid4())
        
        # Calcular valor de cada parcela
        valor_parcela = dados.valor_total / dados.total_parcelas
        
        # Data base para vencimento
        if dados.data_vencimento:
            try:
                data_base = datetime.strptime(dados.data_vencimento, FORMATO_DATA_DB).date()
            except ValueError:
                try:
                    data_base = datetime.strptime(dados.data_vencimento, FORMATO_DATA_BR).date()
                except ValueError:
                    data_base = date.today()
        else:
            data_base = date.today()
        
        contas_criadas = []
        
        # Criar cada parcela
        for i in range(dados.total_parcelas):
            parcela_num = i + 1
            
            # Calcular data de vencimento (adiciona meses)
            data_vencimento = data_base + relativedelta(months=i)
            
            # Criar a conta/parcela
            conta_id = self.conta_repo.create(
                descricao=dados.descricao.strip(),
                valor_total=valor_parcela,  # Valor da parcela individual
                parcela_atual=parcela_num,
                total_parcelas=dados.total_parcelas,
                data_vencimento=data_vencimento.strftime(FORMATO_DATA_DB),
                categoria_id=dados.categoria_id,
                observacao=dados.observacao,
                grupo_parcela_id=grupo_id
            )
            
            contas_criadas.append(conta_id)
            
            # Criar divisões com os mesmos percentuais/valores proporcionais
            if dados.divisoes:
                divisoes_parcela = self._calcular_divisoes_parcela(
                    dados.divisoes, 
                    valor_parcela,
                    dados.valor_total
                )
                self._criar_divisoes(conta_id, divisoes_parcela)
        
        return ResultadoOperacao(
            True,
            f"Conta parcelada criada com sucesso! {dados.total_parcelas} parcelas geradas.",
            {
                'grupo_id': grupo_id,
                'contas_ids': contas_criadas,
                'total_parcelas': dados.total_parcelas
            }
        )
    
    def _calcular_divisoes_parcela(self, divisoes_originais: List[Dict], 
                                    valor_parcela: float,
                                    valor_total: float) -> List[Dict]:
        """
        Calcula as divisões para uma parcela baseado nas divisões originais.
        Mantém a mesma proporção de divisão.
        """
        divisoes_parcela = []
        
        # Calcular total das divisões originais
        total_divisoes = sum(d.get('valor', 0) for d in divisoes_originais)
        
        for div in divisoes_originais:
            valor_original = div.get('valor', 0)
            
            if total_divisoes > 0:
                # Calcular proporcionalmente
                proporcao = valor_original / total_divisoes
                valor_na_parcela = valor_parcela * proporcao
            else:
                valor_na_parcela = 0
            
            divisoes_parcela.append({
                'pessoa_id': div['pessoa_id'],
                'valor': round(valor_na_parcela, 2),
                'percentual': div.get('percentual')
            })
        
        return divisoes_parcela
    
    def _criar_divisoes(self, conta_id: int, divisoes: List[Dict]):
        """Cria as divisões de uma conta."""
        for div in divisoes:
            if div.get('valor', 0) > 0:
                self.divisao_repo.create(
                    conta_id=conta_id,
                    pessoa_id=div['pessoa_id'],
                    valor=div['valor'],
                    percentual=div.get('percentual')
                )
    
    def atualizar_conta(self, conta_id: int, dados: DadosConta) -> ResultadoOperacao:
        """Atualiza uma conta existente."""
        conta = self.conta_repo.get_by_id(conta_id)
        if not conta:
            return ResultadoOperacao(False, "Conta não encontrada")
        
        validacao = self._validar_dados_conta(dados)
        if not validacao.sucesso:
            return validacao
        
        try:
            self.conta_repo.update(
                conta_id,
                descricao=dados.descricao.strip(),
                valor_total=dados.valor_total,
                parcela_atual=dados.parcela_atual,
                total_parcelas=dados.total_parcelas,
                data_vencimento=dados.data_vencimento,
                categoria_id=dados.categoria_id,
                observacao=dados.observacao
            )
            
            # Atualizar divisões
            self.divisao_repo.delete_by_conta(conta_id)
            if dados.divisoes:
                self._criar_divisoes(conta_id, dados.divisoes)
            
            return ResultadoOperacao(True, "Conta atualizada com sucesso")
        
        except Exception as e:
            return ResultadoOperacao(False, f"Erro ao atualizar conta: {str(e)}")
    
    def excluir_conta(self, conta_id: int, excluir_grupo: bool = False) -> ResultadoOperacao:
        """
        Exclui uma conta.
        Se excluir_grupo=True e a conta faz parte de um grupo de parcelas,
        exclui todas as parcelas do grupo.
        """
        conta = self.conta_repo.get_by_id(conta_id)
        if not conta:
            return ResultadoOperacao(False, "Conta não encontrada")
        
        try:
            if excluir_grupo and conta.get('grupo_parcela_id'):
                # Excluir todas as parcelas do grupo
                self.conta_repo.delete_by_grupo(conta['grupo_parcela_id'])
                return ResultadoOperacao(
                    True, 
                    "Todas as parcelas foram excluídas"
                )
            else:
                self.conta_repo.delete(conta_id)
                return ResultadoOperacao(True, "Conta excluída com sucesso")
        
        except Exception as e:
            return ResultadoOperacao(False, f"Erro ao excluir conta: {str(e)}")
    
    def marcar_paga(self, conta_id: int) -> ResultadoOperacao:
        """Marca uma conta como paga."""
        conta = self.conta_repo.get_by_id(conta_id)
        if not conta:
            return ResultadoOperacao(False, "Conta não encontrada")
        
        try:
            self.conta_repo.marcar_pago(conta_id)
            return ResultadoOperacao(True, "Conta marcada como paga")
        except Exception as e:
            return ResultadoOperacao(False, f"Erro ao marcar conta: {str(e)}")
    
    def obter_parcelas_grupo(self, grupo_id: str) -> List[dict]:
        """Obtém todas as parcelas de um grupo."""
        return self.conta_repo.get_by_grupo(grupo_id)
    
    def get_divisoes_conta(self, conta_id: int) -> List[dict]:
        """Obtém as divisões de uma conta."""
        return self.divisao_repo.get_by_conta(conta_id)
