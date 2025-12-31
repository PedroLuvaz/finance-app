"""
Controle de Finanças - Aplicativo para gerenciamento de despesas familiares.

Arquitetura do projeto:
├── src/
│   ├── config/          # Configurações e constantes
│   ├── core/            # Modelos e entidades de domínio
│   ├── data/            # Camada de acesso a dados (repositories)
│   ├── services/        # Lógica de negócio
│   ├── gui/             # Interface gráfica
│   └── utils/           # Utilitários e helpers

Autor: Pedro Andrade
Versão: 2.0.0
"""

import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.gui.app import FinanceApp


def main():
    """Ponto de entrada do aplicativo."""
    app = FinanceApp()
    app.run()


if __name__ == "__main__":
    main()
