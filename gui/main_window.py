"""
Janela principal do aplicativo de controle de finanças.
Interface moderna usando CustomTkinter.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from typing import Optional
import sys
import os

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_database
from models import Conta, Pessoa, ResumoPessoa, ResumoGeral
from .dialogs import DialogoPessoa, DialogoConta, DialogoConfirmacao


# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    """Janela principal do aplicativo."""
    
    def __init__(self):
        super().__init__()
        
        self.title("💰 Controle de Finanças")
        self.geometry("1200x750")
        self.minsize(1000, 600)
        
        # Banco de dados
        self.db = get_database()
        
        # Mês/Ano atual para filtros
        self.mes_atual = datetime.now().month
        self.ano_atual = datetime.now().year
        
        # Criar interface
        self.criar_layout()
        self.criar_sidebar()
        self.criar_area_principal()
        
        # Carregar dados iniciais
        self.mostrar_dashboard()

    def criar_layout(self):
        """Configura o layout principal."""
        # Grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def criar_sidebar(self):
        """Cria a barra lateral de navegação."""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        # Logo/Título
        logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="💰 Finanças",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))
        
        # Botões de navegação
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar,
            text="📊 Dashboard",
            font=ctk.CTkFont(size=14),
            height=40,
            anchor="w",
            command=self.mostrar_dashboard
        )
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        self.btn_contas = ctk.CTkButton(
            self.sidebar,
            text="📋 Contas",
            font=ctk.CTkFont(size=14),
            height=40,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=self.mostrar_contas
        )
        self.btn_contas.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        self.btn_pessoas = ctk.CTkButton(
            self.sidebar,
            text="👥 Pessoas",
            font=ctk.CTkFont(size=14),
            height=40,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=self.mostrar_pessoas
        )
        self.btn_pessoas.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        self.btn_relatorios = ctk.CTkButton(
            self.sidebar,
            text="📈 Relatórios",
            font=ctk.CTkFont(size=14),
            height=40,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=self.mostrar_relatorios
        )
        self.btn_relatorios.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        
        # Seletor de mês/ano
        periodo_label = ctk.CTkLabel(
            self.sidebar,
            text="Período:",
            font=ctk.CTkFont(size=12)
        )
        periodo_label.grid(row=11, column=0, padx=20, pady=(10, 5), sticky="w")
        
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        
        self.combo_mes = ctk.CTkComboBox(
            self.sidebar,
            values=meses,
            width=160,
            command=self.atualizar_periodo
        )
        self.combo_mes.grid(row=12, column=0, padx=20, pady=5)
        self.combo_mes.set(meses[self.mes_atual - 1])
        
        anos = [str(ano) for ano in range(2020, 2031)]
        self.combo_ano = ctk.CTkComboBox(
            self.sidebar,
            values=anos,
            width=160,
            command=self.atualizar_periodo
        )
        self.combo_ano.grid(row=13, column=0, padx=20, pady=(5, 20))
        self.combo_ano.set(str(self.ano_atual))
        
        # Tema
        self.switch_tema = ctk.CTkSwitch(
            self.sidebar,
            text="Modo Escuro",
            command=self.alternar_tema,
            onvalue="dark",
            offvalue="light"
        )
        self.switch_tema.grid(row=14, column=0, padx=20, pady=20)
        self.switch_tema.select()

    def criar_area_principal(self):
        """Cria a área principal de conteúdo."""
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

    def limpar_area_principal(self):
        """Remove todos os widgets da área principal."""
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def atualizar_botoes_sidebar(self, ativo: str):
        """Atualiza o visual dos botões da sidebar."""
        botoes = {
            'dashboard': self.btn_dashboard,
            'contas': self.btn_contas,
            'pessoas': self.btn_pessoas,
            'relatorios': self.btn_relatorios
        }
        
        for nome, btn in botoes.items():
            if nome == ativo:
                btn.configure(
                    fg_color=("gray75", "gray25"),
                    text_color=("gray10", "gray90")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray10", "gray90")
                )

    def atualizar_periodo(self, *args):
        """Atualiza o período selecionado e recarrega os dados."""
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        
        mes_selecionado = self.combo_mes.get()
        self.mes_atual = meses.index(mes_selecionado) + 1
        self.ano_atual = int(self.combo_ano.get())
        
        # Recarregar a tela atual
        self.mostrar_dashboard()

    def alternar_tema(self):
        """Alterna entre tema claro e escuro."""
        if self.switch_tema.get() == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    # ==================== DASHBOARD ====================
    
    def mostrar_dashboard(self):
        """Exibe o dashboard com resumo geral."""
        self.limpar_area_principal()
        self.atualizar_botoes_sidebar('dashboard')
        
        # Título
        titulo = ctk.CTkLabel(
            self.main_area,
            text=f"📊 Dashboard - {self.combo_mes.get()}/{self.ano_atual}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Container principal
        container = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Resumo geral
        resumo = self.db.resumo_geral(self.mes_atual, self.ano_atual)
        
        # Cards de resumo
        self.criar_card_resumo(container, "💰 Total", f"R$ {resumo.get('valor_total', 0):.2f}", "#3498db", 0, 0)
        self.criar_card_resumo(container, "✅ Pago", f"R$ {resumo.get('valor_pago', 0):.2f}", "#27ae60", 0, 1)
        self.criar_card_resumo(container, "⏳ Pendente", f"R$ {resumo.get('valor_pendente', 0):.2f}", "#e74c3c", 0, 2)
        
        # Totais por pessoa
        frame_pessoas = ctk.CTkFrame(container)
        frame_pessoas.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=20, padx=(0, 10))
        
        ctk.CTkLabel(
            frame_pessoas,
            text="👥 Total por Pessoa",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=15)
        
        totais_pessoas = self.db.total_por_pessoa(self.mes_atual, self.ano_atual)
        
        for pessoa in totais_pessoas:
            self.criar_linha_pessoa(frame_pessoas, pessoa)
        
        if not totais_pessoas:
            ctk.CTkLabel(
                frame_pessoas,
                text="Nenhuma pessoa cadastrada",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            ).pack(pady=20)
        
        # Gastos por categoria
        frame_categorias = ctk.CTkFrame(container)
        frame_categorias.grid(row=1, column=2, sticky="nsew", pady=20, padx=(10, 0))
        
        ctk.CTkLabel(
            frame_categorias,
            text="📁 Por Categoria",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=15)
        
        categorias = self.db.contas_por_categoria(self.mes_atual, self.ano_atual)
        
        for cat in categorias:
            if cat.get('total', 0) > 0:
                self.criar_linha_categoria(frame_categorias, cat)
        
        # Últimas contas
        frame_ultimas = ctk.CTkFrame(container)
        frame_ultimas.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=10)
        
        header_frame = ctk.CTkFrame(frame_ultimas, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            header_frame,
            text="📋 Últimas Contas",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header_frame,
            text="+ Nova Conta",
            width=120,
            fg_color="#27ae60",
            hover_color="#219a52",
            command=self.adicionar_conta
        ).pack(side="right")
        
        contas = self.db.listar_contas(mes=self.mes_atual, ano=self.ano_atual)[:5]
        
        for conta in contas:
            self.criar_linha_conta_resumo(frame_ultimas, conta)
        
        if not contas:
            ctk.CTkLabel(
                frame_ultimas,
                text="Nenhuma conta cadastrada para este período",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            ).pack(pady=20)

    def criar_card_resumo(self, parent, titulo: str, valor: str, cor: str, row: int, col: int):
        """Cria um card de resumo."""
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(
            card,
            text=titulo,
            font=ctk.CTkFont(size=14),
            text_color="gray"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            card,
            text=valor,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=cor
        ).pack(pady=(5, 15))

    def criar_linha_pessoa(self, parent, pessoa: dict):
        """Cria uma linha com o resumo de uma pessoa."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        
        # Cor indicadora
        cor_frame = ctk.CTkFrame(frame, width=8, height=30, fg_color=pessoa.get('cor', '#3498db'))
        cor_frame.pack(side="left", padx=(0, 10))
        
        # Nome
        ctk.CTkLabel(
            frame,
            text=pessoa.get('nome', ''),
            font=ctk.CTkFont(size=14),
            width=150,
            anchor="w"
        ).pack(side="left")
        
        # Total pendente
        ctk.CTkLabel(
            frame,
            text=f"R$ {pessoa.get('total_pendente', 0):.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e74c3c" if pessoa.get('total_pendente', 0) > 0 else "#27ae60"
        ).pack(side="right", padx=10)
        
        # Total
        ctk.CTkLabel(
            frame,
            text=f"Total: R$ {pessoa.get('total', 0):.2f}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(side="right", padx=10)

    def criar_linha_categoria(self, parent, categoria: dict):
        """Cria uma linha com o resumo de uma categoria."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            frame,
            text=f"{categoria.get('icone', '📦')} {categoria.get('nome', '')}",
            font=ctk.CTkFont(size=13),
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            frame,
            text=f"R$ {categoria.get('total', 0):.2f}",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="right")

    def criar_linha_conta_resumo(self, parent, conta: dict):
        """Cria uma linha resumida de uma conta."""
        frame = ctk.CTkFrame(parent, fg_color=("gray85", "gray20"))
        frame.pack(fill="x", padx=20, pady=3)
        
        # Ícone da categoria
        ctk.CTkLabel(
            frame,
            text=conta.get('categoria_icone', '📦'),
            font=ctk.CTkFont(size=16)
        ).pack(side="left", padx=10)
        
        # Descrição
        desc = conta.get('descricao', '')
        if conta.get('total_parcelas', 1) > 1:
            desc += f" ({conta.get('parcela_atual', 1)}/{conta.get('total_parcelas', 1)})"
        
        ctk.CTkLabel(
            frame,
            text=desc,
            font=ctk.CTkFont(size=13),
            anchor="w"
        ).pack(side="left", padx=5, fill="x", expand=True)
        
        # Status
        status = conta.get('status', 'pendente')
        status_cor = "#27ae60" if status == 'pago' else "#e74c3c"
        ctk.CTkLabel(
            frame,
            text="✅" if status == 'pago' else "⏳",
            font=ctk.CTkFont(size=14)
        ).pack(side="right", padx=5)
        
        # Valor
        ctk.CTkLabel(
            frame,
            text=f"R$ {conta.get('valor_total', 0):.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=status_cor
        ).pack(side="right", padx=10)

    # ==================== CONTAS ====================
    
    def mostrar_contas(self):
        """Exibe a lista de contas."""
        self.limpar_area_principal()
        self.atualizar_botoes_sidebar('contas')
        
        # Header
        header = ctk.CTkFrame(self.main_area, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text=f"📋 Contas - {self.combo_mes.get()}/{self.ano_atual}",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="+ Nova Conta",
            width=130,
            height=40,
            fg_color="#27ae60",
            hover_color="#219a52",
            font=ctk.CTkFont(size=14),
            command=self.adicionar_conta
        ).pack(side="right")
        
        # Filtros
        filtro_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        filtro_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.filtro_status = ctk.CTkSegmentedButton(
            filtro_frame,
            values=["Todas", "Pendentes", "Pagas"],
            command=self.filtrar_contas
        )
        self.filtro_status.pack(side="left")
        self.filtro_status.set("Todas")
        
        # Lista de contas
        self.lista_contas_frame = ctk.CTkScrollableFrame(self.main_area)
        self.lista_contas_frame.grid(row=2, column=0, sticky="nsew")
        # Garantir que apenas a linha 2 (lista) expanda para ocupar o espaço disponível.
        self.main_area.grid_rowconfigure(0, weight=0)
        self.main_area.grid_rowconfigure(1, weight=0)
        self.main_area.grid_rowconfigure(2, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)
        
        self.carregar_lista_contas()

    def carregar_lista_contas(self, status: str = None):
        """Carrega a lista de contas."""
        # Limpar lista atual
        for widget in self.lista_contas_frame.winfo_children():
            widget.destroy()
        
        contas = self.db.listar_contas(status=status, mes=self.mes_atual, ano=self.ano_atual)
        
        if not contas:
            ctk.CTkLabel(
                self.lista_contas_frame,
                text="Nenhuma conta encontrada",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            ).pack(pady=50)
            return
        
        for conta in contas:
            self.criar_item_conta(conta)

    def criar_item_conta(self, conta: dict):
        """Cria um item na lista de contas."""
        frame = ctk.CTkFrame(self.lista_contas_frame)
        frame.pack(fill="x", pady=5, padx=5)
        
        # Linha principal
        main_row = ctk.CTkFrame(frame, fg_color="transparent")
        main_row.pack(fill="x", padx=15, pady=10)
        
        # Ícone e descrição
        ctk.CTkLabel(
            main_row,
            text=conta.get('categoria_icone', '📦'),
            font=ctk.CTkFont(size=20)
        ).pack(side="left", padx=(0, 10))
        
        info_frame = ctk.CTkFrame(main_row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        desc = conta.get('descricao', '')
        if conta.get('total_parcelas', 1) > 1:
            desc += f" ({conta.get('parcela_atual', 1)}/{conta.get('total_parcelas', 1)})"
        
        ctk.CTkLabel(
            info_frame,
            text=desc,
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        data_venc = conta.get('data_vencimento', '')
        if data_venc:
            try:
                data = datetime.strptime(data_venc, '%Y-%m-%d')
                data_venc = data.strftime('%d/%m/%Y')
            except:
                pass
        
        ctk.CTkLabel(
            info_frame,
            text=f"{conta.get('categoria_nome', 'Sem categoria')} • Vencimento: {data_venc or 'Não definido'}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        ).pack(anchor="w")
        
        # Valor e ações
        status = conta.get('status', 'pendente')
        valor_cor = "#27ae60" if status == 'pago' else "#e74c3c"
        
        ctk.CTkLabel(
            main_row,
            text=f"R$ {conta.get('valor_total', 0):.2f}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=valor_cor
        ).pack(side="right", padx=20)
        
        # Botões de ação
        btn_frame = ctk.CTkFrame(main_row, fg_color="transparent")
        btn_frame.pack(side="right")
        
        if status != 'pago':
            ctk.CTkButton(
                btn_frame,
                text="✅",
                width=35,
                height=35,
                fg_color="#27ae60",
                hover_color="#219a52",
                command=lambda c=conta: self.marcar_conta_paga(c)
            ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="✏️",
            width=35,
            height=35,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=lambda c=conta: self.editar_conta(c)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️",
            width=35,
            height=35,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=lambda c=conta: self.excluir_conta(c)
        ).pack(side="left", padx=2)
        
        # Divisões (se houver)
        divisoes = self.db.listar_divisoes_conta(conta['id'])
        if divisoes:
            div_frame = ctk.CTkFrame(frame, fg_color=("gray90", "gray15"))
            div_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            ctk.CTkLabel(
                div_frame,
                text="Divisão:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", padx=10, pady=5)
            
            for div in divisoes:
                div_row = ctk.CTkFrame(div_frame, fg_color="transparent")
                div_row.pack(fill="x", padx=10, pady=2)
                
                ctk.CTkLabel(
                    div_row,
                    text=f"• {div.get('pessoa_nome', '')}",
                    font=ctk.CTkFont(size=12),
                    text_color=div.get('pessoa_cor', '#3498db')
                ).pack(side="left")
                
                pago_icon = "✅" if div.get('pago', 0) else "⏳"
                ctk.CTkLabel(
                    div_row,
                    text=f"R$ {div.get('valor', 0):.2f} {pago_icon}",
                    font=ctk.CTkFont(size=12)
                ).pack(side="right")

    def filtrar_contas(self, valor: str):
        """Filtra as contas por status."""
        status_map = {
            "Todas": None,
            "Pendentes": "pendente",
            "Pagas": "pago"
        }
        self.carregar_lista_contas(status_map.get(valor))

    def adicionar_conta(self):
        """Abre o diálogo para adicionar nova conta."""
        categorias = self.db.listar_categorias()
        pessoas = self.db.listar_pessoas()
        
        dialogo = DialogoConta(self, categorias, pessoas)
        resultado = dialogo.show()
        
        if resultado:
            divisoes = resultado.pop('divisoes', [])
            
            conta_id = self.db.adicionar_conta(
                descricao=resultado['descricao'],
                valor_total=resultado['valor_total'],
                parcela_atual=resultado['parcela_atual'],
                total_parcelas=resultado['total_parcelas'],
                data_vencimento=resultado['data_vencimento'],
                categoria_id=resultado['categoria_id'],
                observacao=resultado['observacao']
            )
            
            # Adicionar divisões
            for div in divisoes:
                self.db.adicionar_divisao(conta_id, div['pessoa_id'], div['valor'])
            
            self.mostrar_contas()

    def editar_conta(self, conta: dict):
        """Abre o diálogo para editar uma conta."""
        categorias = self.db.listar_categorias()
        pessoas = self.db.listar_pessoas()
        
        dialogo = DialogoConta(self, categorias, pessoas, conta)
        resultado = dialogo.show()
        
        if resultado:
            conta_id = resultado.pop('id')
            divisoes = resultado.pop('divisoes', [])
            
            self.db.atualizar_conta(conta_id, **resultado)
            
            # Atualizar divisões
            self.db.remover_divisoes_conta(conta_id)
            for div in divisoes:
                self.db.adicionar_divisao(conta_id, div['pessoa_id'], div['valor'])
            
            self.mostrar_contas()

    def excluir_conta(self, conta: dict):
        """Exclui uma conta após confirmação."""
        dialogo = DialogoConfirmacao(
            self,
            "Excluir Conta",
            f"Deseja realmente excluir a conta '{conta.get('descricao', '')}'?"
        )
        
        if dialogo.show():
            self.db.excluir_conta(conta['id'])
            self.mostrar_contas()

    def marcar_conta_paga(self, conta: dict):
        """Marca uma conta como paga."""
        self.db.marcar_conta_paga(conta['id'])
        self.mostrar_contas()

    # ==================== PESSOAS ====================
    
    def mostrar_pessoas(self):
        """Exibe a lista de pessoas."""
        self.limpar_area_principal()
        self.atualizar_botoes_sidebar('pessoas')
        
        # Header
        header = ctk.CTkFrame(self.main_area, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text="👥 Pessoas",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="+ Nova Pessoa",
            width=130,
            height=40,
            fg_color="#27ae60",
            hover_color="#219a52",
            font=ctk.CTkFont(size=14),
            command=self.adicionar_pessoa
        ).pack(side="right")
        
        # Lista de pessoas
        lista_frame = ctk.CTkScrollableFrame(self.main_area)
        lista_frame.grid(row=1, column=0, sticky="nsew")
        self.main_area.grid_rowconfigure(1, weight=1)
        
        pessoas = self.db.listar_pessoas()
        
        if not pessoas:
            ctk.CTkLabel(
                lista_frame,
                text="Nenhuma pessoa cadastrada",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            ).pack(pady=50)
            return
        
        for pessoa in pessoas:
            self.criar_item_pessoa(lista_frame, pessoa)

    def criar_item_pessoa(self, parent, pessoa: dict):
        """Cria um item na lista de pessoas."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=5, padx=5)
        
        main_row = ctk.CTkFrame(frame, fg_color="transparent")
        main_row.pack(fill="x", padx=15, pady=15)
        
        # Cor indicadora
        cor_frame = ctk.CTkFrame(main_row, width=15, height=40, fg_color=pessoa.get('cor', '#3498db'))
        cor_frame.pack(side="left", padx=(0, 15))
        cor_frame.pack_propagate(False)
        
        # Nome
        ctk.CTkLabel(
            main_row,
            text=pessoa.get('nome', ''),
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        # Botões de ação
        btn_frame = ctk.CTkFrame(main_row, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(
            btn_frame,
            text="✏️ Editar",
            width=80,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=lambda p=pessoa: self.editar_pessoa(p)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Excluir",
            width=80,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=lambda p=pessoa: self.excluir_pessoa(p)
        ).pack(side="left")

    def adicionar_pessoa(self):
        """Abre o diálogo para adicionar nova pessoa."""
        dialogo = DialogoPessoa(self)
        resultado = dialogo.show()
        
        if resultado:
            try:
                self.db.adicionar_pessoa(resultado['nome'], resultado['cor'])
                self.mostrar_pessoas()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar pessoa: {str(e)}")

    def editar_pessoa(self, pessoa: dict):
        """Abre o diálogo para editar uma pessoa."""
        dialogo = DialogoPessoa(self, pessoa)
        resultado = dialogo.show()
        
        if resultado:
            try:
                self.db.atualizar_pessoa(resultado['id'], resultado['nome'], resultado['cor'])
                self.mostrar_pessoas()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao editar pessoa: {str(e)}")

    def excluir_pessoa(self, pessoa: dict):
        """Exclui uma pessoa após confirmação."""
        dialogo = DialogoConfirmacao(
            self,
            "Excluir Pessoa",
            f"Deseja realmente excluir '{pessoa.get('nome', '')}'?"
        )
        
        if dialogo.show():
            self.db.desativar_pessoa(pessoa['id'])
            self.mostrar_pessoas()

    # ==================== RELATÓRIOS ====================
    
    def mostrar_relatorios(self):
        """Exibe a tela de relatórios."""
        self.limpar_area_principal()
        self.atualizar_botoes_sidebar('relatorios')
        
        # Título
        ctk.CTkLabel(
            self.main_area,
            text=f"📈 Relatórios - {self.combo_mes.get()}/{self.ano_atual}",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Container
        container = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_columnconfigure((0, 1), weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)
        
        # Resumo por pessoa
        frame_pessoas = ctk.CTkFrame(container)
        frame_pessoas.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        
        ctk.CTkLabel(
            frame_pessoas,
            text="👥 Resumo por Pessoa",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=15)
        
        totais = self.db.total_por_pessoa(self.mes_atual, self.ano_atual)
        
        for pessoa in totais:
            self.criar_relatorio_pessoa(frame_pessoas, pessoa)
        
        if not totais:
            ctk.CTkLabel(
                frame_pessoas,
                text="Nenhum dado disponível",
                text_color="gray"
            ).pack(pady=20)
        
        # Resumo por categoria
        frame_categorias = ctk.CTkFrame(container)
        frame_categorias.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        
        ctk.CTkLabel(
            frame_categorias,
            text="📁 Gastos por Categoria",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=15)
        
        categorias = self.db.contas_por_categoria(self.mes_atual, self.ano_atual)
        
        total_geral = sum(c.get('total', 0) for c in categorias)
        
        for cat in categorias:
            if cat.get('total', 0) > 0:
                self.criar_relatorio_categoria(frame_categorias, cat, total_geral)

    def criar_relatorio_pessoa(self, parent, pessoa: dict):
        """Cria uma linha de relatório por pessoa."""
        frame = ctk.CTkFrame(parent, fg_color=("gray85", "gray20"))
        frame.pack(fill="x", padx=20, pady=5)
        
        # Cor e nome
        cor_frame = ctk.CTkFrame(frame, width=10, height=60, fg_color=pessoa.get('cor', '#3498db'))
        cor_frame.pack(side="left")
        cor_frame.pack_propagate(False)
        
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=pessoa.get('nome', ''),
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        # Barra de progresso
        total = pessoa.get('total', 0)
        pago = pessoa.get('total_pago', 0)
        percentual = (pago / total * 100) if total > 0 else 0
        
        progress_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        progress_frame.pack(fill="x", pady=5)
        
        progress = ctk.CTkProgressBar(progress_frame, width=200)
        progress.pack(side="left")
        progress.set(percentual / 100)
        
        ctk.CTkLabel(
            progress_frame,
            text=f"{percentual:.1f}% pago",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(side="left", padx=10)
        
        # Valores
        valores_frame = ctk.CTkFrame(frame, fg_color="transparent")
        valores_frame.pack(side="right", padx=15, pady=10)
        
        ctk.CTkLabel(
            valores_frame,
            text=f"Total: R$ {total:.2f}",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="e")
        
        ctk.CTkLabel(
            valores_frame,
            text=f"Pendente: R$ {pessoa.get('total_pendente', 0):.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e74c3c" if pessoa.get('total_pendente', 0) > 0 else "#27ae60"
        ).pack(anchor="e")

    def criar_relatorio_categoria(self, parent, categoria: dict, total_geral: float):
        """Cria uma linha de relatório por categoria."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        
        # Ícone e nome
        ctk.CTkLabel(
            frame,
            text=f"{categoria.get('icone', '📦')} {categoria.get('nome', '')}",
            font=ctk.CTkFont(size=14),
            anchor="w"
        ).pack(side="left")
        
        # Valor e percentual
        valor = categoria.get('total', 0)
        percentual = (valor / total_geral * 100) if total_geral > 0 else 0
        
        ctk.CTkLabel(
            frame,
            text=f"R$ {valor:.2f} ({percentual:.1f}%)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right")


def main():
    """Função principal para iniciar o aplicativo."""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
