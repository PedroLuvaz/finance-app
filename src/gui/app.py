"""
Aplicação principal - FinanceApp.
"""

import customtkinter as ctk
from datetime import datetime

from .pages import DashboardPage, ContasPage, PessoasPage, RelatoriosPage
from .dialogs import DialogoConta
from .components import ActionButton
from src.config.settings import settings
from src.config.constants import MESES, ANOS_DISPONIVEIS
from src.services import ContaService, PessoaService
from src.services.conta_service import DadosConta


class FinanceApp(ctk.CTk):
    """Aplicação principal de controle de finanças."""
    
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.title(f"💰 {settings.app.name}")
        self.geometry(f"{settings.app.window_width}x{settings.app.window_height}")
        self.minsize(settings.app.min_width, settings.app.min_height)
        
        # Configurar tema
        ctk.set_appearance_mode(settings.theme.mode)
        ctk.set_default_color_theme(settings.theme.color_theme)
        
        # Estado
        self.mes_atual = datetime.now().month
        self.ano_atual = datetime.now().year
        self.pagina_atual = None
        
        # Services
        self.conta_service = ContaService()
        self.pessoa_service = PessoaService()
        
        # Criar interface
        self._criar_layout()
        self._criar_sidebar()
        self._criar_area_principal()
        
        # Mostrar dashboard
        self.mostrar_dashboard()
    
    def _criar_layout(self):
        """Configura o layout principal."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    def _criar_sidebar(self):
        """Cria a barra lateral de navegação."""
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        # Logo
        logo = ctk.CTkLabel(
            self.sidebar,
            text="💰 Finanças",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        logo.grid(row=0, column=0, padx=20, pady=(25, 35))
        
        # Botões de navegação
        self.btn_dashboard = self._criar_btn_nav("📊 Dashboard", self.mostrar_dashboard, 1)
        self.btn_contas = self._criar_btn_nav("📋 Contas", self.mostrar_contas, 2)
        self.btn_pessoas = self._criar_btn_nav("👥 Pessoas", self.mostrar_pessoas, 3)
        self.btn_relatorios = self._criar_btn_nav("📈 Relatórios", self.mostrar_relatorios, 4)
        
        # Seletor de período
        ctk.CTkLabel(
            self.sidebar,
            text="📅 Período:",
            font=ctk.CTkFont(size=13)
        ).grid(row=11, column=0, padx=20, pady=(15, 8), sticky="w")
        
        self.combo_mes = ctk.CTkComboBox(
            self.sidebar,
            values=MESES,
            width=180,
            command=self._atualizar_periodo
        )
        self.combo_mes.grid(row=12, column=0, padx=20, pady=5)
        self.combo_mes.set(MESES[self.mes_atual - 1])
        
        anos = [str(a) for a in ANOS_DISPONIVEIS]
        self.combo_ano = ctk.CTkComboBox(
            self.sidebar,
            values=anos,
            width=180,
            command=self._atualizar_periodo
        )
        self.combo_ano.grid(row=13, column=0, padx=20, pady=(5, 20))
        self.combo_ano.set(str(self.ano_atual))
        
        # Switch de tema
        self.switch_tema = ctk.CTkSwitch(
            self.sidebar,
            text="Modo Escuro",
            command=self._alternar_tema,
            onvalue="dark",
            offvalue="light"
        )
        self.switch_tema.grid(row=14, column=0, padx=20, pady=20)
        
        if settings.theme.mode == "dark":
            self.switch_tema.select()
    
    def _criar_btn_nav(self, texto: str, comando, row: int) -> ctk.CTkButton:
        """Cria um botão de navegação."""
        btn = ctk.CTkButton(
            self.sidebar,
            text=texto,
            font=ctk.CTkFont(size=14),
            height=45,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=comando
        )
        btn.grid(row=row, column=0, padx=15, pady=5, sticky="ew")
        return btn
    
    def _criar_area_principal(self):
        """Cria a área principal de conteúdo."""
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)
    
    def _limpar_area_principal(self):
        """Remove todos os widgets da área principal."""
        for widget in self.main_area.winfo_children():
            widget.destroy()
    
    def _atualizar_botoes_nav(self, ativo: str):
        """Atualiza o visual dos botões de navegação."""
        botoes = {
            'dashboard': self.btn_dashboard,
            'contas': self.btn_contas,
            'pessoas': self.btn_pessoas,
            'relatorios': self.btn_relatorios
        }
        
        for nome, btn in botoes.items():
            if nome == ativo:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
    
    def _atualizar_periodo(self, *args):
        """Atualiza o período selecionado."""
        mes_nome = self.combo_mes.get()
        self.mes_atual = MESES.index(mes_nome) + 1
        self.ano_atual = int(self.combo_ano.get())
        
        # Recarregar página atual
        if self.pagina_atual:
            self.pagina_atual.carregar()
    
    def _alternar_tema(self):
        """Alterna entre tema claro e escuro."""
        modo = self.switch_tema.get()
        ctk.set_appearance_mode(modo)
        settings.set_theme_mode(modo)
    
    # ==================== NAVEGAÇÃO ====================
    
    def mostrar_dashboard(self):
        """Exibe o dashboard."""
        self._limpar_area_principal()
        self._atualizar_botoes_nav('dashboard')
        
        self.pagina_atual = DashboardPage(self.main_area, self)
        self.pagina_atual.grid(row=0, column=0, sticky="nsew")
    
    def mostrar_contas(self):
        """Exibe a página de contas."""
        self._limpar_area_principal()
        self._atualizar_botoes_nav('contas')
        
        self.pagina_atual = ContasPage(self.main_area, self)
        self.pagina_atual.grid(row=0, column=0, sticky="nsew")
    
    def mostrar_pessoas(self):
        """Exibe a página de pessoas."""
        self._limpar_area_principal()
        self._atualizar_botoes_nav('pessoas')
        
        self.pagina_atual = PessoasPage(self.main_area, self)
        self.pagina_atual.grid(row=0, column=0, sticky="nsew")
    
    def mostrar_relatorios(self):
        """Exibe a página de relatórios."""
        self._limpar_area_principal()
        self._atualizar_botoes_nav('relatorios')
        
        self.pagina_atual = RelatoriosPage(self.main_area, self)
        self.pagina_atual.grid(row=0, column=0, sticky="nsew")
    
    def atualizar_dashboard(self):
        """Atualiza o dashboard se estiver visível."""
        if isinstance(self.pagina_atual, DashboardPage):
            self.pagina_atual.carregar()
    
    # ==================== AÇÕES GLOBAIS ====================
    
    def adicionar_conta(self):
        """Abre o diálogo para adicionar conta."""
        categorias = self.conta_service.listar_categorias()
        pessoas = self.pessoa_service.listar_todas()
        
        dialog = DialogoConta(self, categorias, pessoas)
        result = dialog.show()
        
        if result:
            dados = DadosConta(
                descricao=result['descricao'],
                valor_total=result['valor_total'],
                parcela_atual=result['parcela_atual'],
                total_parcelas=result['total_parcelas'],
                data_vencimento=result['data_vencimento'],
                categoria_id=result['categoria_id'],
                observacao=result['observacao'],
                gerar_parcelas_futuras=result['gerar_parcelas_futuras'],
                divisoes=result['divisoes']
            )
            
            resultado = self.conta_service.criar_conta(dados)
            
            if resultado.sucesso and self.pagina_atual:
                self.pagina_atual.carregar()
    
    def run(self):
        """Inicia a aplicação."""
        self.mainloop()
