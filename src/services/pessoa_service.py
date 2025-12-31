"""
Serviço de gestão de pessoas.
"""

from typing import List, Optional
from dataclasses import dataclass

from src.data.repositories import PessoaRepository
from src.core.entities import Pessoa
from src.config.constants import CORES_PADRAO


@dataclass
class ResultadoOperacao:
    """Resultado de uma operação de serviço."""
    sucesso: bool
    mensagem: str = ""
    dados: any = None


class PessoaService:
    """Serviço para operações com pessoas."""
    
    def __init__(self):
        self.repository = PessoaRepository()
    
    def listar_todas(self, apenas_ativas: bool = True) -> List[dict]:
        """Lista todas as pessoas cadastradas."""
        return self.repository.get_all(apenas_ativas)
    
    def obter_por_id(self, pessoa_id: int) -> Optional[dict]:
        """Obtém uma pessoa pelo ID."""
        return self.repository.get_by_id(pessoa_id)
    
    def criar(self, nome: str, cor: str = None) -> ResultadoOperacao:
        """Cria uma nova pessoa."""
        # Validações
        if not nome or not nome.strip():
            return ResultadoOperacao(False, "O nome é obrigatório")
        
        nome = nome.strip()
        
        # Verificar duplicidade
        existente = self.repository.get_by_nome(nome)
        if existente:
            return ResultadoOperacao(False, f"Já existe uma pessoa com o nome '{nome}'")
        
        # Cor padrão se não informada
        if not cor:
            pessoas = self.repository.get_all(apenas_ativas=False)
            indice = len(pessoas) % len(CORES_PADRAO)
            cor = CORES_PADRAO[indice]
        
        try:
            pessoa_id = self.repository.create(nome, cor)
            return ResultadoOperacao(
                True, 
                f"Pessoa '{nome}' criada com sucesso",
                {'id': pessoa_id}
            )
        except Exception as e:
            return ResultadoOperacao(False, f"Erro ao criar pessoa: {str(e)}")
    
    def atualizar(self, pessoa_id: int, nome: str, cor: str) -> ResultadoOperacao:
        """Atualiza uma pessoa existente."""
        if not nome or not nome.strip():
            return ResultadoOperacao(False, "O nome é obrigatório")
        
        nome = nome.strip()
        
        # Verificar se existe
        pessoa = self.repository.get_by_id(pessoa_id)
        if not pessoa:
            return ResultadoOperacao(False, "Pessoa não encontrada")
        
        # Verificar duplicidade (exceto a própria pessoa)
        existente = self.repository.get_by_nome(nome)
        if existente and existente['id'] != pessoa_id:
            return ResultadoOperacao(False, f"Já existe uma pessoa com o nome '{nome}'")
        
        try:
            self.repository.update(pessoa_id, nome, cor)
            return ResultadoOperacao(True, f"Pessoa '{nome}' atualizada com sucesso")
        except Exception as e:
            return ResultadoOperacao(False, f"Erro ao atualizar pessoa: {str(e)}")
    
    def desativar(self, pessoa_id: int) -> ResultadoOperacao:
        """Desativa uma pessoa (soft delete)."""
        pessoa = self.repository.get_by_id(pessoa_id)
        if not pessoa:
            return ResultadoOperacao(False, "Pessoa não encontrada")
        
        try:
            self.repository.delete(pessoa_id)
            return ResultadoOperacao(True, f"Pessoa '{pessoa['nome']}' removida")
        except Exception as e:
            return ResultadoOperacao(False, f"Erro ao remover pessoa: {str(e)}")
    
    def reativar(self, pessoa_id: int) -> ResultadoOperacao:
        """Reativa uma pessoa."""
        try:
            self.repository.reativar(pessoa_id)
            return ResultadoOperacao(True, "Pessoa reativada com sucesso")
        except Exception as e:
            return ResultadoOperacao(False, f"Erro ao reativar pessoa: {str(e)}")
    
    def sugerir_cor(self) -> str:
        """Sugere uma cor para nova pessoa."""
        pessoas = self.repository.get_all(apenas_ativas=False)
        indice = len(pessoas) % len(CORES_PADRAO)
        return CORES_PADRAO[indice]
