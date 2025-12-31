"""
Páginas/Views da aplicação.
"""

import customtkinter as ctk
from typing import Callable, Optional
from datetime import datetime

from .components import Card, ActionButton, ConfirmDialog
from .dialogs import DialogoPessoa, DialogoConta, DialogoExcluirParcelas
from src.services import ContaService, PessoaService, RelatorioService
from src.services.conta_service import DadosConta
from src.utils.formatters import formatar_moeda, formatar_data
from src.config.constants import MESES


class BasePage(ctk.CTkFrame):
    """Classe base para páginas."""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)


class DashboardPage(BasePage):
    """Página do Dashboard."""
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        self.conta_service = ContaService()
        self.relatorio_service = RelatorioService()
        
        self.carregar()
    
    def carregar(self):
        """Carrega/recarrega o dashboard."""
        # Limpar widgets existentes
        for widget in self.winfo_children():
            widget.destroy()
        
        mes = self.app.mes_atual
        ano = self.app.ano_atual
        
        # Título
        ctk.CTkLabel(
            self,
            text=f"📊 Dashboard - {MESES[mes-1]}/{ano}",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Container com scroll
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Resumo geral
        resumo = self.relatorio_service.get_resumo_geral(mes, ano)
        
        # Cards
        Card(
            container,
            "💰 Total",
            formatar_moeda(resumo.get('valor_total', 0)),
            "#3498db"
        ).grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        Card(
            container,
            "✅ Pago",
            formatar_moeda(resumo.get('valor_pago', 0)),
            "#27ae60"
        ).grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        Card(
            container,
            "⏳ Pendente",
            formatar_moeda(resumo.get('valor_pendente', 0)),
            "#e74c3c"
        ).grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        # Totais por pessoa
        frame_pessoas = ctk.CTkFrame(container)
        frame_pessoas.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=20, padx=(0, 10))
        
        ctk.CTkLabel(
            frame_pessoas,
            text="👥 Total por Pessoa",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=15)
        
        totais = self.relatorio_service.get_total_por_pessoa(mes, ano)
        
        for pessoa in totais:
            self._criar_linha_pessoa(frame_pessoas, pessoa)
        
        if not totais:
            ctk.CTkLabel(
                frame_pessoas,
                text="Nenhuma pessoa cadastrada",
                text_color="gray"
            ).pack(pady=20)
        
        # Gastos por categoria
        frame_cat = ctk.CTkFrame(container)
        frame_cat.grid(row=1, column=2, sticky="nsew", pady=20, padx=(10, 0))
        
        ctk.CTkLabel(
            frame_cat,
            text="📁 Por Categoria",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=15)
        
        categorias = self.relatorio_service.get_gastos_por_categoria(mes, ano)
        
        for cat in categorias:
            if cat.get('total', 0) > 0:
                self._criar_linha_categoria(frame_cat, cat)
        
        # Últimas contas
        frame_contas = ctk.CTkFrame(container)
        frame_contas.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=10)
        
        header = ctk.CTkFrame(frame_contas, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            header,
            text="📋 Últimas Contas",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        ActionButton(
            header,
            text="+ Nova Conta",
            style="success",
            width=130,
            command=self.app.adicionar_conta
        ).pack(side="right")
        
        contas = self.conta_service.listar_contas(mes=mes, ano=ano)[:5]
        
        for conta in contas:
            self._criar_linha_conta(frame_contas, conta)
        
        if not contas:
            ctk.CTkLabel(
                frame_contas,
                text="Nenhuma conta neste período",
                text_color="gray"
            ).pack(pady=20)
    
    def _criar_linha_pessoa(self, parent, pessoa: dict):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        
        cor = ctk.CTkFrame(frame, width=8, height=30, fg_color=pessoa.get('cor', '#3498db'))
        cor.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            frame,
            text=pessoa.get('nome', ''),
            font=ctk.CTkFont(size=14),
            width=150,
            anchor="w"
        ).pack(side="left")
        
        pendente = pessoa.get('total_pendente', 0)
        ctk.CTkLabel(
            frame,
            text=formatar_moeda(pendente),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e74c3c" if pendente > 0 else "#27ae60"
        ).pack(side="right", padx=10)
        
        ctk.CTkLabel(
            frame,
            text=f"Total: {formatar_moeda(pessoa.get('total', 0))}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(side="right", padx=10)
    
    def _criar_linha_categoria(self, parent, cat: dict):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            frame,
            text=f"{cat.get('icone', '📦')} {cat.get('nome', '')}",
            font=ctk.CTkFont(size=13),
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            frame,
            text=formatar_moeda(cat.get('total', 0)),
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="right")
    
    def _criar_linha_conta(self, parent, conta: dict):
        frame = ctk.CTkFrame(parent, fg_color=("gray85", "gray20"))
        frame.pack(fill="x", padx=20, pady=3)
        
        ctk.CTkLabel(
            frame,
            text=conta.get('categoria_icone', '📦'),
            font=ctk.CTkFont(size=16)
        ).pack(side="left", padx=10)
        
        desc = conta.get('descricao', '')
        if conta.get('total_parcelas', 1) > 1:
            desc += f" ({conta.get('parcela_atual', 1)}/{conta.get('total_parcelas', 1)})"
        
        ctk.CTkLabel(
            frame,
            text=desc,
            font=ctk.CTkFont(size=13),
            anchor="w"
        ).pack(side="left", padx=5, fill="x", expand=True)
        
        status = conta.get('status', 'pendente')
        ctk.CTkLabel(
            frame,
            text="✅" if status == 'pago' else "⏳",
            font=ctk.CTkFont(size=14)
        ).pack(side="right", padx=5)
        
        ctk.CTkLabel(
            frame,
            text=formatar_moeda(conta.get('valor_total', 0)),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#27ae60" if status == 'pago' else "#e74c3c"
        ).pack(side="right", padx=10)


class ContasPage(BasePage):
    """Página de Contas."""
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        self.conta_service = ContaService()
        self.pessoa_service = PessoaService()
        
        self.carregar()
    
    def carregar(self):
        """Carrega/recarrega a página de contas."""
        for widget in self.winfo_children():
            widget.destroy()
        
        mes = self.app.mes_atual
        ano = self.app.ano_atual
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text=f"📋 Contas - {MESES[mes-1]}/{ano}",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        ActionButton(
            header,
            text="+ Nova Conta",
            style="success",
            width=140,
            height=40,
            command=self._adicionar_conta
        ).pack(side="right")
        
        # Filtros
        filtro_frame = ctk.CTkFrame(self, fg_color="transparent")
        filtro_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.filtro_status = ctk.CTkSegmentedButton(
            filtro_frame,
            values=["Todas", "Pendentes", "Pagas"],
            command=self._filtrar
        )
        self.filtro_status.pack(side="left")
        self.filtro_status.set("Todas")
        
        # Lista
        self.lista_frame = ctk.CTkScrollableFrame(self)
        self.lista_frame.grid(row=2, column=0, sticky="nsew")
        
        self._carregar_lista()
    
    def _carregar_lista(self, status: str = None):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        
        contas = self.conta_service.listar_contas(
            status=status,
            mes=self.app.mes_atual,
            ano=self.app.ano_atual
        )
        
        if not contas:
            ctk.CTkLabel(
                self.lista_frame,
                text="Nenhuma conta encontrada",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            ).pack(pady=50)
            return
        
        for conta in contas:
            self._criar_item_conta(conta)
    
    def _criar_item_conta(self, conta: dict):
        frame = ctk.CTkFrame(self.lista_frame)
        frame.pack(fill="x", pady=5, padx=5)
        
        # Linha principal
        main = ctk.CTkFrame(frame, fg_color="transparent")
        main.pack(fill="x", padx=15, pady=10)
        
        # Ícone
        ctk.CTkLabel(
            main,
            text=conta.get('categoria_icone', '📦'),
            font=ctk.CTkFont(size=20)
        ).pack(side="left", padx=(0, 10))
        
        # Info
        info = ctk.CTkFrame(main, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)
        
        desc = conta.get('descricao', '')
        if conta.get('total_parcelas', 1) > 1:
            desc += f" ({conta.get('parcela_atual', 1)}/{conta.get('total_parcelas', 1)})"
        
        ctk.CTkLabel(
            info,
            text=desc,
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        data = formatar_data(conta.get('data_vencimento', ''))
        ctk.CTkLabel(
            info,
            text=f"{conta.get('categoria_nome', 'Sem categoria')} • Vencimento: {data or 'Não definido'}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        ).pack(anchor="w")
        
        # Valor
        status = conta.get('status', 'pendente')
        ctk.CTkLabel(
            main,
            text=formatar_moeda(conta.get('valor_total', 0)),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#27ae60" if status == 'pago' else "#e74c3c"
        ).pack(side="right", padx=20)
        
        # Botões
        btns = ctk.CTkFrame(main, fg_color="transparent")
        btns.pack(side="right")
        
        if status != 'pago':
            ActionButton(
                btns,
                text="✅",
                style="success",
                width=35,
                height=35,
                command=lambda c=conta: self._marcar_paga(c)
            ).pack(side="left", padx=2)
        
        ActionButton(
            btns,
            text="✏️",
            style="primary",
            width=35,
            height=35,
            command=lambda c=conta: self._editar_conta(c)
        ).pack(side="left", padx=2)
        
        ActionButton(
            btns,
            text="🗑️",
            style="danger",
            width=35,
            height=35,
            command=lambda c=conta: self._excluir_conta(c)
        ).pack(side="left", padx=2)
        
        # Divisões
        divisoes = self.conta_service.get_divisoes_conta(conta['id'])
        if divisoes:
            div_frame = ctk.CTkFrame(frame, fg_color=("gray90", "gray15"))
            div_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            ctk.CTkLabel(
                div_frame,
                text="Divisão:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", padx=10, pady=5)
            
            for div in divisoes:
                row = ctk.CTkFrame(div_frame, fg_color="transparent")
                row.pack(fill="x", padx=10, pady=2)
                
                ctk.CTkLabel(
                    row,
                    text=f"• {div.get('pessoa_nome', '')}",
                    font=ctk.CTkFont(size=12),
                    text_color=div.get('pessoa_cor', '#3498db')
                ).pack(side="left")
                
                pago = "✅" if div.get('pago', 0) else "⏳"
                ctk.CTkLabel(
                    row,
                    text=f"{formatar_moeda(div.get('valor', 0))} {pago}",
                    font=ctk.CTkFont(size=12)
                ).pack(side="right")
    
    def _filtrar(self, valor: str):
        status_map = {"Todas": None, "Pendentes": "pendente", "Pagas": "pago"}
        self._carregar_lista(status_map.get(valor))
    
    def _adicionar_conta(self):
        categorias = self.conta_service.listar_categorias()
        pessoas = self.pessoa_service.listar_todas()
        
        dialog = DialogoConta(self.app, categorias, pessoas)
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
            
            if resultado.sucesso:
                self.carregar()
                self.app.atualizar_dashboard()
    
    def _editar_conta(self, conta: dict):
        categorias = self.conta_service.listar_categorias()
        pessoas = self.pessoa_service.listar_todas()
        
        dialog = DialogoConta(self.app, categorias, pessoas, conta)
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
                divisoes=result['divisoes']
            )
            
            self.conta_service.atualizar_conta(result['id'], dados)
            self.carregar()
            self.app.atualizar_dashboard()
    
    def _excluir_conta(self, conta: dict):
        # Verificar se faz parte de um grupo de parcelas
        if conta.get('grupo_parcela_id') and conta.get('total_parcelas', 1) > 1:
            dialog = DialogoExcluirParcelas(
                self.app,
                conta.get('descricao', ''),
                conta.get('total_parcelas', 1)
            )
            opcao = dialog.show()
            
            if opcao == 'uma':
                self.conta_service.excluir_conta(conta['id'], excluir_grupo=False)
            elif opcao == 'todas':
                self.conta_service.excluir_conta(conta['id'], excluir_grupo=True)
            else:
                return
        else:
            dialog = ConfirmDialog(
                self.app,
                "Excluir Conta",
                f"Deseja excluir '{conta.get('descricao', '')}'?"
            )
            if not dialog.show():
                return
            
            self.conta_service.excluir_conta(conta['id'])
        
        self.carregar()
        self.app.atualizar_dashboard()
    
    def _marcar_paga(self, conta: dict):
        self.conta_service.marcar_paga(conta['id'])
        self.carregar()
        self.app.atualizar_dashboard()


class PessoasPage(BasePage):
    """Página de Pessoas."""
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        self.pessoa_service = PessoaService()
        
        self.carregar()
    
    def carregar(self):
        """Carrega/recarrega a página de pessoas."""
        for widget in self.winfo_children():
            widget.destroy()
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text="👥 Pessoas",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        ActionButton(
            header,
            text="+ Nova Pessoa",
            style="success",
            width=140,
            height=40,
            command=self._adicionar_pessoa
        ).pack(side="right")
        
        # Lista
        lista = ctk.CTkScrollableFrame(self)
        lista.grid(row=1, column=0, sticky="nsew")
        
        pessoas = self.pessoa_service.listar_todas()
        
        if not pessoas:
            ctk.CTkLabel(
                lista,
                text="Nenhuma pessoa cadastrada",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            ).pack(pady=50)
            return
        
        for pessoa in pessoas:
            self._criar_item_pessoa(lista, pessoa)
    
    def _criar_item_pessoa(self, parent, pessoa: dict):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=5, padx=5)
        
        main = ctk.CTkFrame(frame, fg_color="transparent")
        main.pack(fill="x", padx=15, pady=15)
        
        # Cor
        cor = ctk.CTkFrame(main, width=15, height=40, fg_color=pessoa.get('cor', '#3498db'))
        cor.pack(side="left", padx=(0, 15))
        cor.pack_propagate(False)
        
        # Nome
        ctk.CTkLabel(
            main,
            text=pessoa.get('nome', ''),
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        # Botões
        btns = ctk.CTkFrame(main, fg_color="transparent")
        btns.pack(side="right")
        
        ActionButton(
            btns,
            text="✏️ Editar",
            style="primary",
            width=90,
            command=lambda p=pessoa: self._editar_pessoa(p)
        ).pack(side="left", padx=5)
        
        ActionButton(
            btns,
            text="🗑️ Excluir",
            style="danger",
            width=90,
            command=lambda p=pessoa: self._excluir_pessoa(p)
        ).pack(side="left")
    
    def _adicionar_pessoa(self):
        cor_sugerida = self.pessoa_service.sugerir_cor()
        dialog = DialogoPessoa(self.app, cor_sugerida=cor_sugerida)
        result = dialog.show()
        
        if result:
            resultado = self.pessoa_service.criar(result['nome'], result['cor'])
            if resultado.sucesso:
                self.carregar()
    
    def _editar_pessoa(self, pessoa: dict):
        dialog = DialogoPessoa(self.app, pessoa)
        result = dialog.show()
        
        if result:
            self.pessoa_service.atualizar(result['id'], result['nome'], result['cor'])
            self.carregar()
    
    def _excluir_pessoa(self, pessoa: dict):
        dialog = ConfirmDialog(
            self.app,
            "Excluir Pessoa",
            f"Deseja excluir '{pessoa.get('nome', '')}'?"
        )
        
        if dialog.show():
            self.pessoa_service.desativar(pessoa['id'])
            self.carregar()


class RelatoriosPage(BasePage):
    """Página de Relatórios."""
    
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        self.relatorio_service = RelatorioService()
        
        self.carregar()
    
    def carregar(self):
        """Carrega/recarrega a página de relatórios."""
        for widget in self.winfo_children():
            widget.destroy()
        
        mes = self.app.mes_atual
        ano = self.app.ano_atual
        
        # Título
        ctk.CTkLabel(
            self,
            text=f"📈 Relatórios - {MESES[mes-1]}/{ano}",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Container
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_columnconfigure((0, 1), weight=1)
        
        # Resumo por pessoa
        frame_pessoas = ctk.CTkFrame(container)
        frame_pessoas.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        
        ctk.CTkLabel(
            frame_pessoas,
            text="👥 Resumo por Pessoa",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=15)
        
        totais = self.relatorio_service.get_total_por_pessoa(mes, ano)
        
        for pessoa in totais:
            self._criar_relatorio_pessoa(frame_pessoas, pessoa)
        
        if not totais:
            ctk.CTkLabel(
                frame_pessoas,
                text="Nenhum dado disponível",
                text_color="gray"
            ).pack(pady=20)
        
        # Por categoria
        frame_cat = ctk.CTkFrame(container)
        frame_cat.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        
        ctk.CTkLabel(
            frame_cat,
            text="📁 Gastos por Categoria",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=15)
        
        categorias = self.relatorio_service.get_gastos_por_categoria(mes, ano)
        total_geral = sum(c.get('total', 0) for c in categorias)
        
        for cat in categorias:
            if cat.get('total', 0) > 0:
                self._criar_relatorio_categoria(frame_cat, cat, total_geral)
    
    def _criar_relatorio_pessoa(self, parent, pessoa: dict):
        frame = ctk.CTkFrame(parent, fg_color=("gray85", "gray20"))
        frame.pack(fill="x", padx=20, pady=5)
        
        # Cor
        cor = ctk.CTkFrame(frame, width=10, height=60, fg_color=pessoa.get('cor', '#3498db'))
        cor.pack(side="left")
        cor.pack_propagate(False)
        
        # Info
        info = ctk.CTkFrame(frame, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(
            info,
            text=pessoa.get('nome', ''),
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        # Barra de progresso
        total = pessoa.get('total', 0)
        pago = pessoa.get('total_pago', 0)
        percentual = (pago / total * 100) if total > 0 else 0
        
        progress_frame = ctk.CTkFrame(info, fg_color="transparent")
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
        valores = ctk.CTkFrame(frame, fg_color="transparent")
        valores.pack(side="right", padx=15, pady=10)
        
        ctk.CTkLabel(
            valores,
            text=f"Total: {formatar_moeda(total)}",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="e")
        
        pendente = pessoa.get('total_pendente', 0)
        ctk.CTkLabel(
            valores,
            text=f"Pendente: {formatar_moeda(pendente)}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e74c3c" if pendente > 0 else "#27ae60"
        ).pack(anchor="e")
    
    def _criar_relatorio_categoria(self, parent, cat: dict, total_geral: float):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            frame,
            text=f"{cat.get('icone', '📦')} {cat.get('nome', '')}",
            font=ctk.CTkFont(size=14),
            anchor="w"
        ).pack(side="left")
        
        valor = cat.get('total', 0)
        percentual = (valor / total_geral * 100) if total_geral > 0 else 0
        
        ctk.CTkLabel(
            frame,
            text=f"{formatar_moeda(valor)} ({percentual:.1f}%)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right")
