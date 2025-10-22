import tkinter as tk
from tkinter import ttk, messagebox
from ...models import TipoUsuario
from ...services import listar_movimentos, get_nome_produto

class RelatoriosFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FAFAFA")
        self.controller = controller

        # Header com logo + título + Home
        header = tk.Frame(self, bg="#FAFAFA"); header.pack(fill='x')
        if self.controller.logo_img:
            ttk.Label(header, image=self.controller.logo_img).pack(side='left', padx=10, pady=8)
        ttk.Label(header, text='Relatório de Movimentos', style="H2.TLabel").pack(side='left', padx=8, pady=8)
        ttk.Button(header, text='← Home', style="Info.TButton",
                   command=lambda: self.controller.show_frame('HomeFrame')).pack(side='right', padx=10, pady=8)
        ttk.Button(header, text='Sair', style="Info.TButton",
                   command=lambda: self.controller.logout()).pack(side='right', padx=10, pady=8)
        cols = ('id','produto_id','tipo','quantidade','custo_unit', 'custo_total', 'criado_em','usuario')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

    def on_show(self):
        user = self.controller.get_user()
        if not user or user.tipo != TipoUsuario.PADRAO:
            messagebox.showerror('Permissão', 'Apenas usuário Padrão acessa esta tela.')
            self.controller.show_frame('HomeFrame')
            return
        for i in self.tree.get_children():
            self.tree.delete(i)
        for m in listar_movimentos(user):
            self.tree.insert('', 'end', values=(m.id, m.produto_id, m.tipo.value, m.quantidade, m.custo_unitario, m.criado_em, m.criado_por_id))

        cols = ('id','produto_id','tipo','quantidade','custo_unit', 'custo_total', 'criado_em','usuario')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

    def on_show(self):
        user = self.controller.get_user()
        if not user or user.tipo != TipoUsuario.PADRAO:
            messagebox.showerror('Permissão', 'Apenas usuário Padrão acessa esta tela.')
            self.controller.show_frame('HomeFrame')
            return
        for i in self.tree.get_children():
            self.tree.delete(i)
        for m in listar_movimentos(user):
            self.tree.insert('', 'end', values=(m.id, get_nome_produto(m.produto_id), m.tipo.value, m.quantidade, m.custo_unitario, (m.quantidade * m.custo_unitario), m.criado_em, m.criado_por_id))