"""
Componentes base da interface gráfica.
"""

import customtkinter as ctk
from typing import Optional, Callable
from tkinter import colorchooser


class BaseFrame(ctk.CTkFrame):
    """Frame base com funcionalidades comuns."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent


class Card(ctk.CTkFrame):
    """Componente de card para exibição de informações."""
    
    def __init__(self, parent, titulo: str, valor: str, 
                 cor: str = "#3498db", **kwargs):
        super().__init__(parent, **kwargs)
        
        ctk.CTkLabel(
            self,
            text=titulo,
            font=ctk.CTkFont(size=14),
            text_color="gray"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            self,
            text=valor,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=cor
        ).pack(pady=(5, 15))


class ColorButton(ctk.CTkButton):
    """Botão para seleção de cor."""
    
    def __init__(self, parent, cor_inicial: str = "#3498db", 
                 on_color_change: Callable = None, **kwargs):
        self.cor_atual = cor_inicial
        self.on_color_change = on_color_change
        
        super().__init__(
            parent,
            text="",
            width=50,
            height=40,
            fg_color=cor_inicial,
            hover_color=cor_inicial,
            command=self._escolher_cor,
            **kwargs
        )
    
    def _escolher_cor(self):
        cor = colorchooser.askcolor(color=self.cor_atual, title="Escolher Cor")
        if cor[1]:
            self.cor_atual = cor[1]
            self.configure(fg_color=self.cor_atual, hover_color=self.cor_atual)
            if self.on_color_change:
                self.on_color_change(self.cor_atual)
    
    def get_cor(self) -> str:
        return self.cor_atual
    
    def set_cor(self, cor: str):
        self.cor_atual = cor
        self.configure(fg_color=cor, hover_color=cor)


class LabeledEntry(ctk.CTkFrame):
    """Entry com label integrado."""
    
    def __init__(self, parent, label: str, placeholder: str = "", 
                 width: int = 300, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry = ctk.CTkEntry(
            self,
            width=width,
            height=40,
            font=ctk.CTkFont(size=14),
            placeholder_text=placeholder
        )
        self.entry.pack(fill="x")
    
    def get(self) -> str:
        return self.entry.get()
    
    def set(self, valor: str):
        self.entry.delete(0, "end")
        self.entry.insert(0, valor)
    
    def clear(self):
        self.entry.delete(0, "end")


class ActionButton(ctk.CTkButton):
    """Botão de ação estilizado."""
    
    STYLES = {
        'primary': {'fg_color': '#3498db', 'hover_color': '#2980b9'},
        'success': {'fg_color': '#27ae60', 'hover_color': '#219a52'},
        'danger': {'fg_color': '#e74c3c', 'hover_color': '#c0392b'},
        'warning': {'fg_color': '#f39c12', 'hover_color': '#d68910'},
        'secondary': {'fg_color': '#6c757d', 'hover_color': '#5a6268'},
        'info': {'fg_color': '#17a2b8', 'hover_color': '#138496'},
    }
    
    def __init__(self, parent, text: str, style: str = 'primary', 
                 icon: str = "", **kwargs):
        style_config = self.STYLES.get(style, self.STYLES['primary'])
        
        display_text = f"{icon} {text}".strip() if icon else text
        
        super().__init__(
            parent,
            text=display_text,
            **style_config,
            **kwargs
        )


class ConfirmDialog(ctk.CTkToplevel):
    """Diálogo de confirmação."""
    
    def __init__(self, parent, titulo: str, mensagem: str):
        super().__init__(parent)
        
        self.title(titulo)
        self.geometry("400x180")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Centralizar
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 180) // 2
        self.geometry(f"400x180+{x}+{y}")
        
        self.result = False
        
        # Conteúdo
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            main_frame,
            text=mensagem,
            font=ctk.CTkFont(size=14),
            wraplength=350
        ).pack(pady=20)
        
        # Botões
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ActionButton(
            btn_frame,
            text="Não",
            style="secondary",
            width=100,
            command=self._nao
        ).pack(side="right", padx=(10, 0))
        
        ActionButton(
            btn_frame,
            text="Sim",
            style="danger",
            width=100,
            command=self._sim
        ).pack(side="right")
    
    def _sim(self):
        self.result = True
        self.destroy()
    
    def _nao(self):
        self.result = False
        self.destroy()
    
    def show(self) -> bool:
        self.wait_window()
        return self.result


class MessageDialog(ctk.CTkToplevel):
    """Diálogo de mensagem."""
    
    def __init__(self, parent, titulo: str, mensagem: str, 
                 tipo: str = "info"):
        super().__init__(parent)
        
        self.title(titulo)
        self.geometry("400x160")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Centralizar
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 160) // 2
        self.geometry(f"400x160+{x}+{y}")
        
        # Ícones por tipo
        icones = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        icone = icones.get(tipo, 'ℹ️')
        
        # Conteúdo
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            main_frame,
            text=f"{icone} {mensagem}",
            font=ctk.CTkFont(size=14),
            wraplength=350
        ).pack(pady=20)
        
        ActionButton(
            main_frame,
            text="OK",
            style="primary",
            width=100,
            command=self.destroy
        ).pack()
    
    def show(self):
        self.wait_window()
