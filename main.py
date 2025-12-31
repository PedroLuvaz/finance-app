"""
Controle de Finanças - Aplicativo para gerenciamento de despesas familiares.

Este aplicativo permite:
- Cadastrar e gerenciar pessoas (pai, mãe, namorada, etc.)
- Registrar contas e faturas com parcelas (x/x)
- Dividir despesas entre múltiplas pessoas
- Visualizar totais por pessoa
- Acompanhar pagamentos pendentes

Autor: Pedro Andrade
Data: 2024
"""

from gui import MainWindow


def main():
    """Inicia o aplicativo de controle de finanças."""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
