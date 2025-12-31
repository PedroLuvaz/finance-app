"""
Diálogos e janelas popup para o aplicativo de finanças.
"""
import customtkinter as ctk
from tkinter import messagebox, colorchooser
from typing import Callable, Optional, List
from datetime import datetime


class DialogBase(ctk.CTkToplevel):
    """Classe base para diálogos."""
    
    def __init__(self, parent, title: str, width: int = 400, height: int = 300):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Centralizar na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.result = None

    def show(self):
        """Exibe o diálogo e aguarda fechamento."""
        self.wait_window()
        return self.result


class DialogoPessoa(DialogBase):
    """Diálogo para adicionar/editar pessoa."""
    
    def __init__(self, parent, pessoa: dict = None):
        title = "Editar Pessoa" if pessoa else "Nova Pessoa"
        super().__init__(parent, title, 400, 250)
        
        self.pessoa = pessoa
        self.cor_selecionada = pessoa.get('cor', '#3498db') if pessoa else '#3498db'
        
        self.criar_widgets()
        
        if pessoa:
            self.entry_nome.insert(0, pessoa.get('nome', ''))
            self.atualizar_cor()

    def criar_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Nome
        ctk.CTkLabel(main_frame, text="Nome:", font=("Segoe UI", 14)).pack(anchor="w", pady=(0, 5))
        self.entry_nome = ctk.CTkEntry(main_frame, width=360, height=40, font=("Segoe UI", 14))
        self.entry_nome.pack(fill="x", pady=(0, 15))
        
        # Cor
        ctk.CTkLabel(main_frame, text="Cor:", font=("Segoe UI", 14)).pack(anchor="w", pady=(0, 5))
        
        cor_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        cor_frame.pack(fill="x", pady=(0, 20))
        
        self.btn_cor = ctk.CTkButton(
            cor_frame, 
            text="", 
            width=50, 
            height=40,
            fg_color=self.cor_selecionada,
            hover_color=self.cor_selecionada,
            command=self.escolher_cor
        )
        self.btn_cor.pack(side="left")
        
        self.label_cor = ctk.CTkLabel(
            cor_frame, 
            text=self.cor_selecionada, 
            font=("Segoe UI", 12)
        )
        self.label_cor.pack(side="left", padx=10)
        
        # Botões
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            btn_frame, 
            text="Cancelar", 
            width=100,
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=self.cancelar
        ).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(
            btn_frame, 
            text="Salvar", 
            width=100,
            fg_color="#28a745",
            hover_color="#218838",
            command=self.salvar
        ).pack(side="right")

    def escolher_cor(self):
        cor = colorchooser.askcolor(color=self.cor_selecionada, title="Escolher Cor")
        if cor[1]:
            self.cor_selecionada = cor[1]
            self.atualizar_cor()

    def atualizar_cor(self):
        self.btn_cor.configure(fg_color=self.cor_selecionada, hover_color=self.cor_selecionada)
        self.label_cor.configure(text=self.cor_selecionada)

    def salvar(self):
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "O nome é obrigatório!")
            return
        
        self.result = {
            'nome': nome,
            'cor': self.cor_selecionada
        }
        if self.pessoa:
            self.result['id'] = self.pessoa.get('id')
        
        self.destroy()

    def cancelar(self):
        self.destroy()


class DialogoConta(DialogBase):
    """Diálogo para adicionar/editar conta."""
    
    def __init__(self, parent, categorias: List[dict], pessoas: List[dict], conta: dict = None):
        title = "Editar Conta" if conta else "Nova Conta"
        super().__init__(parent, title, 550, 600)
        
        self.conta = conta
        self.categorias = categorias
        self.pessoas = pessoas
        self.divisoes = {}
        
        self.criar_widgets()
        
        if conta:
            self.preencher_dados(conta)

    def criar_widgets(self):
        # Frame principal com scroll
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Descrição
        ctk.CTkLabel(main_frame, text="Descrição:", font=("Segoe UI", 14)).pack(anchor="w", pady=(0, 5))
        self.entry_descricao = ctk.CTkEntry(main_frame, width=500, height=40, font=("Segoe UI", 14))
        self.entry_descricao.pack(fill="x", pady=(0, 15))
        
        # Valor Total
        ctk.CTkLabel(main_frame, text="Valor Total (R$):", font=("Segoe UI", 14)).pack(anchor="w", pady=(0, 5))
        self.entry_valor = ctk.CTkEntry(main_frame, width=500, height=40, font=("Segoe UI", 14))
        self.entry_valor.pack(fill="x", pady=(0, 15))
        
        # Parcelas
        parcela_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        parcela_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(parcela_frame, text="Parcela:", font=("Segoe UI", 14)).pack(side="left")
        self.entry_parcela_atual = ctk.CTkEntry(parcela_frame, width=60, height=40, font=("Segoe UI", 14))
        self.entry_parcela_atual.pack(side="left", padx=5)
        self.entry_parcela_atual.insert(0, "1")
        
        ctk.CTkLabel(parcela_frame, text="de", font=("Segoe UI", 14)).pack(side="left", padx=5)
        self.entry_total_parcelas = ctk.CTkEntry(parcela_frame, width=60, height=40, font=("Segoe UI", 14))
        self.entry_total_parcelas.pack(side="left", padx=5)
        self.entry_total_parcelas.insert(0, "1")
        
        # Data de Vencimento
        ctk.CTkLabel(main_frame, text="Data de Vencimento (DD/MM/AAAA):", font=("Segoe UI", 14)).pack(anchor="w", pady=(0, 5))
        self.entry_vencimento = ctk.CTkEntry(main_frame, width=500, height=40, font=("Segoe UI", 14))
        self.entry_vencimento.pack(fill="x", pady=(0, 15))
        
        # Categoria
        ctk.CTkLabel(main_frame, text="Categoria:", font=("Segoe UI", 14)).pack(anchor="w", pady=(0, 5))
        categorias_display = [f"{c['icone']} {c['nome']}" for c in self.categorias]
        self.combo_categoria = ctk.CTkComboBox(
            main_frame, 
            values=categorias_display if categorias_display else ["Sem categoria"],
            width=500, 
            height=40,
            font=("Segoe UI", 14)
        )
        self.combo_categoria.pack(fill="x", pady=(0, 15))
        if categorias_display:
            self.combo_categoria.set(categorias_display[0])
        
        # Observação
        ctk.CTkLabel(main_frame, text="Observação:", font=("Segoe UI", 14)).pack(anchor="w", pady=(0, 5))
        self.text_observacao = ctk.CTkTextbox(main_frame, width=500, height=80, font=("Segoe UI", 12))
        self.text_observacao.pack(fill="x", pady=(0, 15))
        
        # Divisão entre pessoas
        ctk.CTkLabel(main_frame, text="Dividir entre:", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(10, 10))
        
        self.divisao_frame = ctk.CTkFrame(main_frame)
        self.divisao_frame.pack(fill="x", pady=(0, 15))
        
        for pessoa in self.pessoas:
            pessoa_frame = ctk.CTkFrame(self.divisao_frame, fg_color="transparent")
            pessoa_frame.pack(fill="x", pady=5, padx=10)
            
            # Checkbox
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(
                pessoa_frame, 
                text=pessoa['nome'],
                variable=var,
                font=("Segoe UI", 12),
                text_color=pessoa['cor']
            )
            cb.pack(side="left")
            
            # Entry para valor
            entry_valor = ctk.CTkEntry(pessoa_frame, width=120, height=30, placeholder_text="R$ 0,00")
            entry_valor.pack(side="right", padx=5)
            
            ctk.CTkLabel(pessoa_frame, text="Valor:", font=("Segoe UI", 12)).pack(side="right")
            
            self.divisoes[pessoa['id']] = {
                'checkbox': var,
                'entry': entry_valor,
                'nome': pessoa['nome']
            }
        
        # Botões
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(
            btn_frame, 
            text="Cancelar", 
            width=100,
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=self.cancelar
        ).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(
            btn_frame, 
            text="Salvar", 
            width=100,
            fg_color="#28a745",
            hover_color="#218838",
            command=self.salvar
        ).pack(side="right")
        
        ctk.CTkButton(
            btn_frame, 
            text="Dividir Igual", 
            width=120,
            fg_color="#17a2b8",
            hover_color="#138496",
            command=self.dividir_igual
        ).pack(side="left")

    def preencher_dados(self, conta: dict):
        self.entry_descricao.insert(0, conta.get('descricao', ''))
        self.entry_valor.insert(0, str(conta.get('valor_total', '')))
        
        self.entry_parcela_atual.delete(0, 'end')
        self.entry_parcela_atual.insert(0, str(conta.get('parcela_atual', 1)))
        
        self.entry_total_parcelas.delete(0, 'end')
        self.entry_total_parcelas.insert(0, str(conta.get('total_parcelas', 1)))
        
        if conta.get('data_vencimento'):
            try:
                data = datetime.strptime(conta['data_vencimento'], '%Y-%m-%d')
                self.entry_vencimento.insert(0, data.strftime('%d/%m/%Y'))
            except:
                pass
        
        # Categoria
        cat_id = conta.get('categoria_id')
        if cat_id:
            for i, cat in enumerate(self.categorias):
                if cat['id'] == cat_id:
                    self.combo_categoria.set(f"{cat['icone']} {cat['nome']}")
                    break
        
        if conta.get('observacao'):
            self.text_observacao.insert("1.0", conta['observacao'])

    def dividir_igual(self):
        """Divide o valor igualmente entre as pessoas selecionadas."""
        try:
            valor_texto = self.entry_valor.get().replace(',', '.').strip()
            valor_total = float(valor_texto)
        except ValueError:
            messagebox.showerror("Erro", "Informe um valor válido!")
            return
        
        # Contar pessoas selecionadas
        selecionadas = [pid for pid, dados in self.divisoes.items() if dados['checkbox'].get()]
        
        if not selecionadas:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma pessoa!")
            return
        
        valor_por_pessoa = valor_total / len(selecionadas)
        
        for pid, dados in self.divisoes.items():
            dados['entry'].delete(0, 'end')
            if dados['checkbox'].get():
                dados['entry'].insert(0, f"{valor_por_pessoa:.2f}")

    def salvar(self):
        # Validações
        descricao = self.entry_descricao.get().strip()
        if not descricao:
            messagebox.showerror("Erro", "A descrição é obrigatória!")
            return
        
        try:
            valor_texto = self.entry_valor.get().replace(',', '.').strip()
            valor_total = float(valor_texto)
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido!")
            return
        
        try:
            parcela_atual = int(self.entry_parcela_atual.get())
            total_parcelas = int(self.entry_total_parcelas.get())
        except ValueError:
            messagebox.showerror("Erro", "Parcelas inválidas!")
            return
        
        # Data de vencimento
        data_vencimento = None
        data_texto = self.entry_vencimento.get().strip()
        if data_texto:
            try:
                data = datetime.strptime(data_texto, '%d/%m/%Y')
                data_vencimento = data.strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Erro", "Data inválida! Use o formato DD/MM/AAAA")
                return
        
        # Categoria
        categoria_id = None
        cat_selecionada = self.combo_categoria.get()
        for cat in self.categorias:
            if f"{cat['icone']} {cat['nome']}" == cat_selecionada:
                categoria_id = cat['id']
                break
        
        # Divisões
        divisoes_resultado = []
        for pid, dados in self.divisoes.items():
            if dados['checkbox'].get():
                try:
                    valor_texto = dados['entry'].get().replace(',', '.').strip()
                    valor = float(valor_texto) if valor_texto else 0
                    if valor > 0:
                        divisoes_resultado.append({
                            'pessoa_id': pid,
                            'valor': valor
                        })
                except ValueError:
                    pass
        
        self.result = {
            'descricao': descricao,
            'valor_total': valor_total,
            'parcela_atual': parcela_atual,
            'total_parcelas': total_parcelas,
            'data_vencimento': data_vencimento,
            'categoria_id': categoria_id,
            'observacao': self.text_observacao.get("1.0", "end-1c").strip(),
            'divisoes': divisoes_resultado
        }
        
        if self.conta:
            self.result['id'] = self.conta.get('id')
        
        self.destroy()

    def cancelar(self):
        self.destroy()


class DialogoConfirmacao(DialogBase):
    """Diálogo de confirmação."""
    
    def __init__(self, parent, titulo: str, mensagem: str):
        super().__init__(parent, titulo, 350, 180)
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            main_frame, 
            text=mensagem, 
            font=("Segoe UI", 14),
            wraplength=300
        ).pack(pady=20)
        
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            btn_frame, 
            text="Não", 
            width=100,
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=self.nao
        ).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(
            btn_frame, 
            text="Sim", 
            width=100,
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self.sim
        ).pack(side="right")

    def sim(self):
        self.result = True
        self.destroy()

    def nao(self):
        self.result = False
        self.destroy()
