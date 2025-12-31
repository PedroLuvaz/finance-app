# 💰 Controle de Finanças

Aplicativo desktop em Python para controle de finanças pessoais e familiares.

## ✨ Funcionalidades

- **👥 Gerenciamento de Pessoas**: Cadastre pai, mãe, namorada, tia, ou qualquer pessoa que compartilhe despesas
- **📋 Controle de Contas**: Registre contas com descrição, valor, data de vencimento
- **🔢 Parcelas**: Suporte a faturas parceladas (ex: 3/12)
- **💸 Divisão de Despesas**: Divida contas entre múltiplas pessoas (valor fixo ou igual)
- **📊 Dashboard**: Visualize resumo geral, totais por pessoa e por categoria
- **📈 Relatórios**: Acompanhe pendências e pagamentos de cada pessoa
- **🎨 Interface Moderna**: Design escuro/claro com CustomTkinter

## 📁 Estrutura do Projeto

```
Finance_App/
├── main.py              # Ponto de entrada do aplicativo
├── database.py          # Gerenciamento do banco de dados SQLite
├── models.py            # Modelos de dados (Pessoa, Conta, etc.)
├── requirements.txt     # Dependências do projeto
├── financas.db          # Banco de dados (criado automaticamente)
└── gui/
    ├── __init__.py
    ├── main_window.py   # Janela principal
    └── dialogs.py       # Diálogos e popups
```

## 🚀 Instalação

### 1. Clone ou baixe o projeto

### 2. Crie um ambiente virtual (recomendado)
```bash
python -m venv venv
```

### 3. Ative o ambiente virtual
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

### 5. Execute o aplicativo
```bash
python main.py
```

## 📖 Como Usar

### 1. Cadastrar Pessoas
- Vá em "👥 Pessoas" no menu lateral
- Clique em "+ Nova Pessoa"
- Adicione nome e escolha uma cor para identificação
- Cadastre todas as pessoas que dividem despesas (Eu, Pai, Mãe, Namorada, etc.)

### 2. Adicionar Contas
- Vá em "📋 Contas" ou clique em "+ Nova Conta" no Dashboard
- Preencha:
  - **Descrição**: Nome da conta (ex: "Cartão Nubank")
  - **Valor Total**: Valor da fatura
  - **Parcela**: Se parcelado, informe X de Y (ex: 3 de 12)
  - **Vencimento**: Data do vencimento
  - **Categoria**: Tipo de despesa
- **Dividir entre pessoas**: 
  - Marque as pessoas que dividem essa conta
  - Use "Dividir Igual" para repartir igualmente
  - Ou informe o valor de cada um manualmente

### 3. Acompanhar Pagamentos
- O **Dashboard** mostra:
  - Total geral do mês
  - Valor pago e pendente
  - Resumo por pessoa
  - Últimas contas
- Use os **Relatórios** para análise detalhada

### 4. Marcar como Pago
- Na lista de contas, clique no ✅ para marcar como pago
- O status é atualizado automaticamente no resumo

## 🔧 Funcionalidades Futuras (Selenium)

O projeto está preparado para integração com Selenium para:
- Importar faturas automaticamente de bancos
- Sincronizar com planilhas online
- Exportar relatórios em PDF

## 💡 Dicas

- Use o seletor de **Período** (mês/ano) para navegar entre meses
- Alterne entre **Modo Claro/Escuro** na sidebar
- Cada pessoa tem uma **cor única** para fácil identificação
- O banco de dados é salvo automaticamente (financas.db)

## 🛠️ Tecnologias

- **Python 3.10+**
- **CustomTkinter** - Interface gráfica moderna
- **SQLite** - Banco de dados local
- **Selenium** - Automação web (preparado para futuro uso)

## 📝 Licença

Este projeto é de uso pessoal. Sinta-se livre para modificar e adaptar às suas necessidades.
