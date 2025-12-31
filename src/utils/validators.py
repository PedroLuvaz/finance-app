"""
Validadores de dados.
"""

import re
from typing import Tuple, Optional
from datetime import datetime

from src.config.constants import FORMATO_DATA_BR, FORMATO_DATA_DB, MAX_PARCELAS


class ValidadorConta:
    """Validador para dados de conta."""
    
    @staticmethod
    def validar_descricao(descricao: str) -> Tuple[bool, str]:
        """Valida a descrição da conta."""
        if not descricao or not descricao.strip():
            return False, "A descrição é obrigatória"
        if len(descricao) > 200:
            return False, "A descrição deve ter no máximo 200 caracteres"
        return True, ""
    
    @staticmethod
    def validar_valor(valor: str) -> Tuple[bool, str, float]:
        """Valida e converte o valor."""
        try:
            valor_limpo = valor.replace("R$", "").replace(" ", "")
            valor_limpo = valor_limpo.replace(".", "").replace(",", ".")
            valor_float = float(valor_limpo)
            
            if valor_float <= 0:
                return False, "O valor deve ser maior que zero", 0
            
            return True, "", valor_float
        except (ValueError, AttributeError):
            return False, "Valor inválido", 0
    
    @staticmethod
    def validar_parcelas(parcela_atual: str, total_parcelas: str) -> Tuple[bool, str, int, int]:
        """Valida as parcelas."""
        try:
            atual = int(parcela_atual)
            total = int(total_parcelas)
            
            if total < 1:
                return False, "O total de parcelas deve ser pelo menos 1", 0, 0
            
            if total > MAX_PARCELAS:
                return False, f"O máximo de parcelas é {MAX_PARCELAS}", 0, 0
            
            if atual < 1 or atual > total:
                return False, "Número da parcela inválido", 0, 0
            
            return True, "", atual, total
        except ValueError:
            return False, "Parcelas inválidas", 0, 0
    
    @staticmethod
    def validar_data(data_str: str) -> Tuple[bool, str, Optional[str]]:
        """Valida e converte a data."""
        if not data_str or not data_str.strip():
            return True, "", None  # Data opcional
        
        # Tentar formato brasileiro
        try:
            data = datetime.strptime(data_str.strip(), FORMATO_DATA_BR)
            return True, "", data.strftime(FORMATO_DATA_DB)
        except ValueError:
            pass
        
        # Tentar formato do banco
        try:
            data = datetime.strptime(data_str.strip(), FORMATO_DATA_DB)
            return True, "", data_str.strip()
        except ValueError:
            pass
        
        return False, "Data inválida. Use o formato DD/MM/AAAA", None


class ValidadorPessoa:
    """Validador para dados de pessoa."""
    
    @staticmethod
    def validar_nome(nome: str) -> Tuple[bool, str]:
        """Valida o nome da pessoa."""
        if not nome or not nome.strip():
            return False, "O nome é obrigatório"
        if len(nome) > 100:
            return False, "O nome deve ter no máximo 100 caracteres"
        return True, ""
    
    @staticmethod
    def validar_cor(cor: str) -> Tuple[bool, str]:
        """Valida a cor (formato hexadecimal)."""
        if not cor:
            return True, ""  # Cor opcional
        
        padrao = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
        if not re.match(padrao, cor):
            return False, "Cor inválida. Use formato hexadecimal (#RRGGBB)"
        
        return True, ""
