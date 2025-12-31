"""
Diálogos da aplicação.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import List, Optional
from datetime import datetime

from .components import ActionButton, ColorButton, LabeledEntry
from src.config.constants import FORMATO_DATA_BR, FORMATO_DATA_DB
from src.utils.validators import ValidadorConta, ValidadorPessoa
from src.utils.formatters import formatar_data


class DialogBase(ctk.CTkToplevel):
    """Classe base para diálogos."""
    
    def __init__(self, parent, title: str, width: int = 400, height: int = 300):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Centralizar
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.result = None

    def show(self):
        self.wait_window()
        return self.result


class DialogoPessoa(DialogBase):
    """Diálogo para adicionar/editar pessoa."""
    
    def __init__(self, parent, pessoa: dict = None, cor_sugerida: str = "#3498db"):
        title = "Editar Pessoa" if pessoa else "Nova Pessoa"
        super().__init__(parent, title, 450, 280)
        
        self.pessoa = pessoa
        self.cor_inicial = pessoa.get('cor', cor_sugerida) if pessoa else cor_sugerida
        
        self._criar_widgets()
        
        if pessoa:
            self.entry_nome.set(pessoa.get('nome', ''))

    def _criar_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Nome
        self.entry_nome = LabeledEntry(main_frame, "Nome:", "Digite o nome...")
        self.entry_nome.pack(fill="x", pady=(0, 20))
        
        # Cor
        ctk.CTkLabel(
            main_frame,
            text="Cor de identificação:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        cor_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        cor_frame.pack(fill="x", pady=(0, 25))
        
        self.color_btn = ColorButton(
            cor_frame,
            cor_inicial=self.cor_inicial,
            on_color_change=self._on_cor_change
        )
        self.color_btn.pack(side="left")
        
        self.label_cor = ctk.CTkLabel(
            cor_frame,
            text=self.cor_inicial,
            font=ctk.CTkFont(size=12)
        )
        self.label_cor.pack(side="left", padx=15)
        
        # Botões
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")
        
        ActionButton(
            btn_frame,
            text="Cancelar",
            style="secondary",
            width=110,
            command=self.destroy
        ).pack(side="right", padx=(10, 0))
        
        ActionButton(
            btn_frame,
            text="Salvar",
            style="success",
            width=110,
            command=self._salvar
        ).pack(side="right")

    def _on_cor_change(self, cor: str):
        self.label_cor.configure(text=cor)

    def _salvar(self):
        nome = self.entry_nome.get().strip()
        
        # Validar
        valido, msg = ValidadorPessoa.validar_nome(nome)
        if not valido:
            messagebox.showerror("Erro", msg)
            return
        
        self.result = {
            'nome': nome,
            'cor': self.color_btn.get_cor()
        }
        
        if self.pessoa:
            self.result['id'] = self.pessoa.get('id')
        
        self.destroy()


class DialogoConta(DialogBase):
    """Diálogo para adicionar/editar conta com geração automática de parcelas."""
    
    def __init__(self, parent, categorias: List[dict], pessoas: List[dict], 
                 conta: dict = None):
        title = "Editar Conta" if conta else "Nova Conta"
        super().__init__(parent, title, 600, 700)
        
        self.conta = conta
        self.categorias = categorias
        self.pessoas = pessoas
        self.divisoes = {}
        
        self._criar_widgets()
        
        if conta:
            self._preencher_dados(conta)

    def _criar_widgets(self):
        # Frame principal com scroll
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Descrição
        self.entry_descricao = LabeledEntry(
            main_frame, 
            "Descrição:", 
            "Ex: Cartão Nubank, Aluguel..."
        )
        self.entry_descricao.pack(fill="x", pady=(0, 15))
        
        # Valor Total
        self.entry_valor = LabeledEntry(
            main_frame, 
            "Valor Total (R$):", 
            "0,00"
        )
        self.entry_valor.pack(fill="x", pady=(0, 15))
        
        # Parcelas
        parcela_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        parcela_container.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            parcela_container,
            text="Parcelas:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        parcela_frame = ctk.CTkFrame(parcela_container, fg_color="transparent")
        parcela_frame.pack(fill="x")
        
        self.entry_parcela_atual = ctk.CTkEntry(
            parcela_frame, 
            width=70, 
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entry_parcela_atual.pack(side="left")
        self.entry_parcela_atual.insert(0, "1")
        
        ctk.CTkLabel(
            parcela_frame,
            text="de",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)
        
        self.entry_total_parcelas = ctk.CTkEntry(
            parcela_frame, 
            width=70, 
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entry_total_parcelas.pack(side="left")
        self.entry_total_parcelas.insert(0, "1")
        
        # Checkbox para gerar parcelas automaticamente
        self.var_gerar_parcelas = ctk.BooleanVar(value=True)
        self.check_gerar = ctk.CTkCheckBox(
            parcela_frame,
            text="Gerar parcelas futuras automaticamente",
            variable=self.var_gerar_parcelas,
            font=ctk.CTkFont(size=12)
        )
        self.check_gerar.pack(side="left", padx=20)
        
        # Info sobre geração de parcelas
        info_frame = ctk.CTkFrame(main_frame, fg_color=("#e8f4fd", "#1a3a4a"))
        info_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            info_frame,
            text="ℹ️ Com esta opção marcada, se você criar uma conta com 3 parcelas,\n"
                 "   serão criadas automaticamente 3 contas (uma para cada mês).",
            font=ctk.CTkFont(size=11),
            justify="left"
        ).pack(padx=10, pady=8)
        
        # Data de Vencimento
        self.entry_vencimento = LabeledEntry(
            main_frame, 
            "Data de Vencimento (DD/MM/AAAA):", 
            "01/01/2025"
        )
        self.entry_vencimento.pack(fill="x", pady=(0, 15))
        
        # Categoria
        ctk.CTkLabel(
            main_frame,
            text="Categoria:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        categorias_display = [f"{c['icone']} {c['nome']}" for c in self.categorias]
        self.combo_categoria = ctk.CTkComboBox(
            main_frame,
            values=categorias_display if categorias_display else ["Sem categoria"],
            width=550,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.combo_categoria.pack(fill="x", pady=(0, 15))
        if categorias_display:
            self.combo_categoria.set(categorias_display[0])
        
        # Observação
        ctk.CTkLabel(
            main_frame,
            text="Observação:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        self.text_observacao = ctk.CTkTextbox(
            main_frame, 
            width=550, 
            height=70,
            font=ctk.CTkFont(size=12)
        )
        self.text_observacao.pack(fill="x", pady=(0, 15))
        
        # Divisão entre pessoas
        divisao_header = ctk.CTkFrame(main_frame, fg_color="transparent")
        divisao_header.pack(fill="x", pady=(10, 10))
        
        ctk.CTkLabel(
            divisao_header,
            text="💰 Dividir entre:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        ActionButton(
            divisao_header,
            text="Dividir Igual",
            style="info",
            width=120,
            command=self._dividir_igual
        ).pack(side="right")
        
        # Lista de pessoas para divisão
        self.divisao_frame = ctk.CTkFrame(main_frame)
        self.divisao_frame.pack(fill="x", pady=(0, 20))
        
        if not self.pessoas:
            ctk.CTkLabel(
                self.divisao_frame,
                text="Nenhuma pessoa cadastrada. Cadastre pessoas primeiro.",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            ).pack(pady=15)
        else:
            for pessoa in self.pessoas:
                self._criar_linha_pessoa(pessoa)
        
        # Botões
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ActionButton(
            btn_frame,
            text="Cancelar",
            style="secondary",
            width=110,
            command=self.destroy
        ).pack(side="right", padx=(10, 0))
        
        ActionButton(
            btn_frame,
            text="Salvar",
            style="success",
            width=110,
            command=self._salvar
        ).pack(side="right")

    def _criar_linha_pessoa(self, pessoa: dict):
        pessoa_frame = ctk.CTkFrame(self.divisao_frame, fg_color="transparent")
        pessoa_frame.pack(fill="x", pady=8, padx=15)
        
        # Checkbox
        var = ctk.BooleanVar(value=False)
        cb = ctk.CTkCheckBox(
            pessoa_frame,
            text="",
            variable=var,
            width=24
        )
        cb.pack(side="left")
        
        # Indicador de cor
        cor_indicator = ctk.CTkFrame(
            pessoa_frame, 
            width=8, 
            height=30,
            fg_color=pessoa['cor']
        )
        cor_indicator.pack(side="left", padx=(5, 10))
        
        # Nome
        ctk.CTkLabel(
            pessoa_frame,
            text=pessoa['nome'],
            font=ctk.CTkFont(size=13),
            width=150,
            anchor="w"
        ).pack(side="left")
        
        # Entry para valor
        ctk.CTkLabel(
            pessoa_frame,
            text="R$",
            font=ctk.CTkFont(size=12)
        ).pack(side="right", padx=(0, 5))
        
        entry_valor = ctk.CTkEntry(
            pessoa_frame, 
            width=120, 
            height=35,
            placeholder_text="0,00"
        )
        entry_valor.pack(side="right")
        
        self.divisoes[pessoa['id']] = {
            'checkbox': var,
            'entry': entry_valor,
            'nome': pessoa['nome']
        }

    def _preencher_dados(self, conta: dict):
        self.entry_descricao.set(conta.get('descricao', ''))
        self.entry_valor.set(str(conta.get('valor_total', '')))
        
        self.entry_parcela_atual.delete(0, 'end')
        self.entry_parcela_atual.insert(0, str(conta.get('parcela_atual', 1)))
        
        self.entry_total_parcelas.delete(0, 'end')
        self.entry_total_parcelas.insert(0, str(conta.get('total_parcelas', 1)))
        
        # Desabilitar geração de parcelas na edição
        self.var_gerar_parcelas.set(False)
        self.check_gerar.configure(state="disabled")
        
        if conta.get('data_vencimento'):
            data_formatada = formatar_data(conta['data_vencimento'])
            self.entry_vencimento.set(data_formatada)
        
        # Categoria
        cat_id = conta.get('categoria_id')
        if cat_id:
            for cat in self.categorias:
                if cat['id'] == cat_id:
                    self.combo_categoria.set(f"{cat['icone']} {cat['nome']}")
                    break
        
        if conta.get('observacao'):
            self.text_observacao.insert("1.0", conta['observacao'])

    def _dividir_igual(self):
        """Divide o valor igualmente entre as pessoas selecionadas."""
        # Validar valor
        valido, msg, valor = ValidadorConta.validar_valor(self.entry_valor.get())
        if not valido:
            messagebox.showerror("Erro", msg)
            return
        
        # Contar pessoas selecionadas
        selecionadas = [
            pid for pid, dados in self.divisoes.items() 
            if dados['checkbox'].get()
        ]
        
        if not selecionadas:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma pessoa!")
            return
        
        valor_por_pessoa = valor / len(selecionadas)
        
        for pid, dados in self.divisoes.items():
            dados['entry'].delete(0, 'end')
            if dados['checkbox'].get():
                dados['entry'].insert(0, f"{valor_por_pessoa:.2f}")

    def _salvar(self):
        # Validar descrição
        descricao = self.entry_descricao.get()
        valido, msg = ValidadorConta.validar_descricao(descricao)
        if not valido:
            messagebox.showerror("Erro", msg)
            return
        
        # Validar valor
        valido, msg, valor = ValidadorConta.validar_valor(self.entry_valor.get())
        if not valido:
            messagebox.showerror("Erro", msg)
            return
        
        # Validar parcelas
        valido, msg, parcela_atual, total_parcelas = ValidadorConta.validar_parcelas(
            self.entry_parcela_atual.get(),
            self.entry_total_parcelas.get()
        )
        if not valido:
            messagebox.showerror("Erro", msg)
            return
        
        # Validar data
        valido, msg, data_vencimento = ValidadorConta.validar_data(
            self.entry_vencimento.get()
        )
        if not valido:
            messagebox.showerror("Erro", msg)
            return
        
        # Categoria
        categoria_id = None
        cat_selecionada = self.combo_categoria.get()
        for cat in self.categorias:
            if f"{cat['icone']} {cat['nome']}" == cat_selecionada:
                categoria_id = cat['id']
                break
        
        # Divisões
        divisoes = []
        for pid, dados in self.divisoes.items():
            if dados['checkbox'].get():
                try:
                    valor_texto = dados['entry'].get().replace(',', '.').strip()
                    valor_div = float(valor_texto) if valor_texto else 0
                    if valor_div > 0:
                        divisoes.append({
                            'pessoa_id': pid,
                            'valor': valor_div
                        })
                except ValueError:
                    pass
        
        self.result = {
            'descricao': descricao.strip(),
            'valor_total': valor,
            'parcela_atual': parcela_atual,
            'total_parcelas': total_parcelas,
            'data_vencimento': data_vencimento,
            'categoria_id': categoria_id,
            'observacao': self.text_observacao.get("1.0", "end-1c").strip(),
            'gerar_parcelas_futuras': self.var_gerar_parcelas.get(),
            'divisoes': divisoes
        }
        
        if self.conta:
            self.result['id'] = self.conta.get('id')
        
        self.destroy()


class DialogoExcluirParcelas(DialogBase):
    """Diálogo para escolher como excluir parcelas."""
    
    def __init__(self, parent, descricao: str, total_parcelas: int):
        super().__init__(parent, "Excluir Parcelas", 450, 220)
        
        self.descricao = descricao
        self.total_parcelas = total_parcelas
        
        self._criar_widgets()

    def _criar_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        ctk.CTkLabel(
            main_frame,
            text=f"A conta '{self.descricao}' faz parte de um parcelamento\n"
                 f"com {self.total_parcelas} parcelas.",
            font=ctk.CTkFont(size=14),
            justify="center"
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(
            main_frame,
            text="O que deseja fazer?",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(0, 15))
        
        # Botões
        ActionButton(
            main_frame,
            text="Excluir apenas esta parcela",
            style="warning",
            width=280,
            command=lambda: self._selecionar('uma')
        ).pack(pady=5)
        
        ActionButton(
            main_frame,
            text="Excluir TODAS as parcelas",
            style="danger",
            width=280,
            command=lambda: self._selecionar('todas')
        ).pack(pady=5)
        
        ActionButton(
            main_frame,
            text="Cancelar",
            style="secondary",
            width=280,
            command=self.destroy
        ).pack(pady=5)

    def _selecionar(self, opcao: str):
        self.result = opcao
        self.destroy()
