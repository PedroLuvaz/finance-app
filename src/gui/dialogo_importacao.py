"""
Diálogo de importação de faturas.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import List, Optional, Dict
from pathlib import Path

from src.services.importacao_service import ImportacaoService, TransacaoImportada
from src.core.entities import Categoria, Pessoa
from src.utils.formatters import formatar_moeda, formatar_data


class DialogoImportacao(ctk.CTkToplevel):
    """Diálogo para importar faturas de arquivos XLS/XLSX."""
    
    def __init__(
        self, 
        parent, 
        categorias: List[Categoria],
        pessoas: List[Pessoa]
    ):
        super().__init__(parent)
        
        self.categorias = categorias
        self.pessoas = pessoas
        self.importacao_service = ImportacaoService()
        self.transacoes: List[TransacaoImportada] = []
        self.resultado = None
        self.checks_transacoes = []
        self.divisoes_widgets = []
        
        self.title("📥 Importar Fatura")
        self.geometry("900x650")
        self.minsize(800, 550)
        
        self.transient(parent)
        self.grab_set()
        
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface do diálogo usando pack para layout simples."""
        # ========== TOPO: Título e seleção de arquivo ==========
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            topo, text="📥 Importar Fatura",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            topo, text="📁 Selecionar", width=110, height=32,
            command=self._selecionar_arquivo
        ).pack(side="right")
        
        self.entry_arquivo = ctk.CTkEntry(topo, width=350, state="readonly")
        self.entry_arquivo.pack(side="right", padx=10)
        
        bancos = ["Auto"] + self.importacao_service.listar_bancos_suportados()
        self.combo_banco = ctk.CTkComboBox(topo, values=bancos, width=100)
        self.combo_banco.pack(side="right", padx=5)
        self.combo_banco.set("Auto")
        
        ctk.CTkLabel(topo, text="Banco:").pack(side="right", padx=(0, 5))
        
        # ========== MEIO: Lista de transações (expande) ==========
        meio = ctk.CTkFrame(self)
        meio.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.label_preview = ctk.CTkLabel(
            meio, text="📋 Transações encontradas: 0",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label_preview.pack(anchor="w", padx=10, pady=8)
        
        self.scroll_frame = ctk.CTkScrollableFrame(meio)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # ========== RODAPÉ: Opções e Botões (FIXO) ==========
        rodape = ctk.CTkFrame(self)
        rodape.pack(fill="x", padx=15, pady=(5, 15))
        
        # Linha de opções
        opcoes = ctk.CTkFrame(rodape, fg_color="transparent")
        opcoes.pack(fill="x", pady=(5, 10))
        
        ctk.CTkLabel(opcoes, text="Categoria:").pack(side="left", padx=(5, 5))
        
        cat_nomes = self._get_cat_nomes()
        self.combo_categoria = ctk.CTkComboBox(opcoes, values=cat_nomes, width=160)
        self.combo_categoria.pack(side="left", padx=(0, 15))
        if cat_nomes:
            self.combo_categoria.set(cat_nomes[0])
        
        self.var_gerar_parcelas = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            opcoes, text="Gerar próximas parcelas",
            variable=self.var_gerar_parcelas
        ).pack(side="left", padx=(0, 20))
        
        # Divisões
        if self.pessoas:
            ctk.CTkLabel(opcoes, text="Divisão:").pack(side="left", padx=(0, 5))
            for pessoa in self.pessoas[:3]:
                nome = pessoa.get('nome') if isinstance(pessoa, dict) else pessoa.nome
                pessoa_id = pessoa.get('id') if isinstance(pessoa, dict) else pessoa.id
                ctk.CTkLabel(opcoes, text=f"{nome}:").pack(side="left", padx=(5, 2))
                entry = ctk.CTkEntry(opcoes, width=45, placeholder_text="0%")
                entry.pack(side="left", padx=(0, 5))
                self.divisoes_widgets.append((pessoa_id, entry))
        
        # ========== LINHA DE BOTÕES ==========
        botoes = ctk.CTkFrame(rodape, fg_color="transparent")
        botoes.pack(fill="x", pady=(5, 5))
        
        # Cancelar (vermelho, esquerda)
        ctk.CTkButton(
            botoes, text="❌ Cancelar",
            width=130, height=45,
            fg_color="#c0392b", hover_color="#a93226",
            font=ctk.CTkFont(size=14),
            command=self.destroy
        ).pack(side="left", padx=(5, 10))
        
        # Selecionar Todas (azul, centro-esquerda)
        ctk.CTkButton(
            botoes, text="☑️ Selecionar Todas",
            width=160, height=45,
            font=ctk.CTkFont(size=14),
            command=self._selecionar_todas
        ).pack(side="left", padx=10)
        
        # Importar (verde, direita)
        self.btn_importar = ctk.CTkButton(
            botoes, text="✅ Importar Selecionadas",
            width=220, height=45,
            fg_color="#27ae60", hover_color="#1e8449",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._importar_selecionadas,
            state="disabled"
        )
        self.btn_importar.pack(side="right", padx=(10, 5))
    
    def _get_cat_nomes(self) -> List[str]:
        """Retorna lista de nomes de categorias."""
        if not self.categorias:
            return ["📦 Outros"]
        
        if isinstance(self.categorias[0], dict):
            return [f"{c.get('icone', '📦')} {c.get('nome', '')}" for c in self.categorias]
        return [f"{c.icone} {c.nome}" for c in self.categorias]
    
    def _selecionar_arquivo(self):
        """Abre diálogo para selecionar arquivo."""
        arquivo = filedialog.askopenfilename(
            title="Selecionar Fatura",
            filetypes=[
                ("Arquivos CSV", "*.csv"),
                ("Arquivos Excel", "*.xlsx *.xls"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if arquivo:
            self.entry_arquivo.configure(state="normal")
            self.entry_arquivo.delete(0, "end")
            self.entry_arquivo.insert(0, arquivo)
            self.entry_arquivo.configure(state="readonly")
            self._carregar_arquivo()
    
    def _carregar_arquivo(self):
        """Carrega e processa o arquivo selecionado."""
        caminho = self.entry_arquivo.get()
        
        if not caminho:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro!")
            return
        
        banco = self.combo_banco.get()
        if banco == "Auto":
            banco = None
        
        resultado = self.importacao_service.importar_arquivo(caminho, banco)
        
        if not resultado.sucesso:
            messagebox.showerror("Erro", resultado.mensagem)
            return
        
        self.transacoes = resultado.dados
        self._atualizar_preview()
    
    def _atualizar_preview(self):
        """Atualiza a lista de transações na preview."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.checks_transacoes.clear()
        
        self.label_preview.configure(
            text=f"📋 Transações encontradas: {len(self.transacoes)}"
        )
        
        for transacao in self.transacoes:
            frame = ctk.CTkFrame(self.scroll_frame)
            frame.pack(fill="x", pady=2, padx=2)
            
            var = ctk.BooleanVar(value=True)
            check = ctk.CTkCheckBox(
                frame, text="", variable=var, width=30,
                command=self._atualizar_btn_importar
            )
            check.pack(side="left", padx=5)
            self.checks_transacoes.append((transacao, var))
            
            # Descrição
            desc = transacao.descricao
            if transacao.eh_parcelada:
                parcelas_restantes = transacao.total_parcelas - transacao.parcela_atual + 1
                desc += f" ({transacao.parcela_atual}/{transacao.total_parcelas})"
                # Indicar quantas parcelas serão geradas se opção marcada
                if parcelas_restantes > 1:
                    desc += f" → +{parcelas_restantes - 1} próximas"
            
            ctk.CTkLabel(
                frame, text=desc, anchor="w", width=400
            ).pack(side="left", padx=5)
            
            # Data
            ctk.CTkLabel(
                frame, text=formatar_data(transacao.data), width=100
            ).pack(side="left", padx=10)
            
            # Valor
            ctk.CTkLabel(
                frame, text=formatar_moeda(transacao.valor),
                font=ctk.CTkFont(weight="bold"),
                text_color="#27ae60", width=100
            ).pack(side="right", padx=10)
        
        self._atualizar_btn_importar()
    
    def _atualizar_btn_importar(self):
        """Atualiza o estado do botão de importar."""
        if not self.btn_importar:
            return
        
        selecionadas = sum(1 for _, var in self.checks_transacoes if var.get())
        
        if selecionadas > 0:
            self.btn_importar.configure(state="normal")
            self.btn_importar.configure(text=f"✅ Importar ({selecionadas})")
        else:
            self.btn_importar.configure(state="disabled")
            self.btn_importar.configure(text="✅ Importar Selecionadas")
    
    def _selecionar_todas(self):
        """Seleciona ou desmarca todas as transações."""
        todas_selecionadas = all(var.get() for _, var in self.checks_transacoes)
        
        for _, var in self.checks_transacoes:
            var.set(not todas_selecionadas)
        
        self._atualizar_btn_importar()
    
    def _importar_selecionadas(self):
        """Importa as transações selecionadas."""
        selecionadas = [t for t, var in self.checks_transacoes if var.get()]
        
        if not selecionadas:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma transação!")
            return
        
        # Categoria
        cat_idx = 0
        try:
            cat_text = self.combo_categoria.get()
            cat_nomes = self._get_cat_nomes()
            cat_idx = cat_nomes.index(cat_text)
        except:
            pass
        
        if self.categorias:
            if isinstance(self.categorias[0], dict):
                categoria_id = self.categorias[cat_idx].get('id', 1)
            else:
                categoria_id = self.categorias[cat_idx].id
        else:
            categoria_id = 1
        
        # Divisões
        divisoes = []
        for pessoa_id, entry in self.divisoes_widgets:
            valor = entry.get().strip().replace('%', '')
            if valor:
                try:
                    percentual = float(valor)
                    if percentual > 0:
                        divisoes.append({
                            'pessoa_id': pessoa_id,
                            'percentual': percentual
                        })
                except:
                    pass
        
        # Importar
        resultado = self.importacao_service.salvar_transacoes(
            selecionadas,
            categoria_id,
            divisoes,
            self.var_gerar_parcelas.get()
        )
        
        if resultado.sucesso:
            messagebox.showinfo("Sucesso", resultado.mensagem)
            self.resultado = True
            self.destroy()
        else:
            messagebox.showerror("Erro", resultado.mensagem)
    
    def show(self) -> Optional[bool]:
        """Exibe o diálogo e retorna o resultado."""
        self.wait_window()
        return self.resultado
