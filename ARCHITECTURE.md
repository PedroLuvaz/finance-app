# 🏗️ Arquitetura do Projeto Finance_App

Este documento detalha a arquitetura técnica do projeto **Controle de Finanças**. O sistema foi desenvolvido seguindo uma **Arquitetura em Camadas (Layered Architecture)** utilizando o **Padrão Repository** para abstração do acesso a dados.

## 📐 Visão Geral

O projeto visa desacoplar a interface gráfica (GUI) da lógica de negócios e do acesso ao banco de dados. Isso facilita a manutenção, testes e futuras migrações de tecnologias (ex: mudar de SQLite para PostgreSQL ou de CustomTkinter para Web).

### Padrão Adotado: **Camadas com Repository Pattern**

O fluxo de dependência segue o sentido:
`GUI -> Services -> Core <- Data`

## 📂 Estrutura de Diretórios (`src/`)

```
src/
├── config/           # Configurações globais e constantes
├── core/             # Núcleo do domínio (Entidades Puras)
├── data/             # Camada de persistência (Banco de Dados)
├── services/         # Regras de negócio e orquestração
├── gui/              # Interface Gráfica (CustomTkinter)
└── utils/            # Funções auxiliares
```

---

## 🧱 Detalhamento das Camadas

### 1. Camada Core (`src/core`)
Esta é a camada mais interna e não depende de nenhuma outra. Ela define o "formato" dos dados que transitam pelo sistema.
*   **Responsabilidade:** Definir as Entidades e Value Objects.
*   **Componentes Principais:**
    *   `entities.py`: Classes de dados (`@dataclass`) como `Pessoa`, `Conta`, `Categoria`, `DivisaoConta`.
    *   Inclui métodos de conversão `from_dict`/`to_dict` para serialização.

### 2. Camada Data (`src/data`)
Responsável por toda a comunicação com o banco de dados SQLite.
*   **Responsabilidade:** CRUD (Create, Read, Update, Delete) e mapeamento de dados.
*   **Componentes Principais:**
    *   `database.py`: Gerenciador de conexão SQLite (Singleton/Context Manager).
    *   `repositories.py`: Implementação do padrão Repository.
        *   `BaseRepository`: Classe abstrata com métodos genéricos.
        *   `ContaRepository`: Consultas SQL específicas para Contas.
        *   `PessoaRepository`: Consultas SQL específicas para Pessoas.

### 3. Camada Services (`src/services`)
Contém a lógica de negócio pura. A GUI não acessa o banco diretamente; ela pede ações aos Services.
*   **Responsabilidade:** Validação de dados, cálculos complexos e orquestração de repositórios.
*   **Exemplo de Lógica:**
    *   Ao criar uma conta parcelada (`ContaService`), o serviço calcula as datas futuras, gera múltiplas entradas no banco e calcula a divisão proporcional para cada pessoa.
*   **Componentes Principais:**
    *   `conta_service.py`: Lógica para contas e parcelamento.
    *   `pessoa_service.py`: Gestão de usuários.

### 4. Camada GUI (`src/gui`)
A camada de apresentação, construída com `customtkinter`.
*   **Responsabilidade:** Exibir dados ao usuário e capturar interações.
*   **Componentes Principais:**
    *   `app.py`: Classe principal `FinanceApp` e gerenciamento de janelas.
    *   `pages/`: Telas individuais (Dashboard, Contas, Pessoas).
    *   `dialogs/`: Janelas modais (Adicionar Conta, Editar Pessoa).
    *   `components/`: Widgets reutilizáveis.

---

## 🔄 Fluxo de Dados (Exemplo: Criar Conta)

1.  **Usuário**: Preenche o formulário na `DialogoConta` (GUI) e clica em Salvar.
2.  **GUI**: Captura os dados, cria um objeto DTO (`DadosConta`) e chama `conta_service.criar_conta()`.
3.  **Service**:
    *   Valida os dados (valor > 0, descrição não vazia).
    *   Verifica se é parcelado. Se sim, calcula as parcelas futuras.
    *   Chama `repo.create()` para persistir.
4.  **Repository**: Monta a query SQL `INSERT INTO contas...` e executa no banco.
5.  **Database**: Grava no arquivo `.db`.
6.  **Retorno**: O sucesso percorre o caminho inverso até a GUI atualizar a lista.

---

## 🗄️ Modelo de Dados (SQLite)

O banco de dados relacional possui as seguintes tabelas principais:

*   **`pessoas`**: Cadastros de quem divide as contas.
*   **`categorias`**: Tipos de despesa (Casa, Mercado, Lazer).
*   **`contas`**: A despesa em si.
    *   `grupo_parcela_id`: UUID que liga várias parcelas da mesma compra.
*   **`divisao_contas`**: Tabela associativa (N:N) entre `contas` e `pessoas`.
    *   Armazena quanto cada pessoa paga de uma conta específica.

## 🛠️ Tecnologias e Decisões

*   **CustomTkinter**: Escolhido por oferecer uma interface moderna (Dark Mode nativo) com facilidade de uso do Tkinter padrão.
*   **SQLite**: Ideal para aplicações desktop locais (serverless), sem necessidade de configuração complexa pelo usuário final.
*   **Dataclasses**: Reduzem o código boilerplate para definição de classes de modelo.
