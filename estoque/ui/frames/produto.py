import tkinter as tk
from tkinter import ttk, messagebox
from ...models import TipoUsuario
from ...services import criar_produto

class ProdutoFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FAFAFA")
        self.controller = controller

        # Header com logo + título + Home
        header = tk.Frame(self, bg="#FAFAFA"); header.pack(fill='x')
        if self.controller.logo_img:
            ttk.Label(header, image=self.controller.logo_img).pack(side='left', padx=10, pady=8)
        ttk.Label(header, text='Cadastro de Produto', style="H2.TLabel").pack(side='left', padx=8, pady=8)
        ttk.Button(header, text='← Home', style="Info.TButton",
                   command=lambda: self.controller.show_frame('HomeFrame')).pack(side='right', padx=10, pady=8)
        ttk.Button(header, text='Sair', style="Info.TButton",
                   command=lambda: self.controller.logout()).pack(side='right', padx=10, pady=8)
        form = tk.Frame(self, bg="#FAFAFA"); form.pack(pady=10)
        
        ttk.Label(form, text='Código').grid(row=0, column=0, sticky='e', padx=6, pady=6)
        self.e_cod = ttk.Entry(form, width=40); self.e_cod.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(form, text='Descrição').grid(row=1, column=0, sticky='e', padx=6, pady=6)
        self.e_desc = ttk.Entry(form, width=40); self.e_desc.grid(row=1, column=1, padx=6, pady=6)

        ttk.Label(form, text='Estoque mínimo (opcional)').grid(row=2, column=0, sticky='e', padx=6, pady=6)
        self.e_min = ttk.Entry(form, width=40); self.e_min.grid(row=2, column=1, padx=6, pady=6)

        ttk.Button(self, text='Salvar', style="Success.TButton", command=self._salvar).pack(pady=12)

    def on_show(self):
        user = self.controller.get_user()
        if not user or user.tipo != TipoUsuario.PADRAO:
            messagebox.showerror('Permissão', 'Apenas usuário Padrão acessa esta tela.')
            self.controller.show_frame('HomeFrame')

    def _salvar(self):
        try:
            u = self.controller.get_user()
            minimo = int(self.e_min.get()) if self.e_min.get().strip() else None
            p = criar_produto(u, u.empresa_id, self.e_cod.get().strip(), self.e_desc.get().strip(), minimo)
            messagebox.showinfo('OK', f'Produto criado (ID: {p.id})')
            self.controller.set_status(f"Produto '{p.codigo}' criado.", "success")

            if p.minimo_estoque is not None and p.minimo_estoque > 0 and p.estoque <= p.minimo_estoque:
                messagebox.showwarning('Estoque mínimo', f"O produto '{p.codigo} - {p.descricao}' já está abaixo/igual ao mínimo (0 <= {p.minimo_estoque}).")
                self.controller.set_status(f"[ALERTA] Produto '{p.codigo}' em nível crítico.", "error")

            self.e_cod.delete(0,'end'); self.e_desc.delete(0,'end'); self.e_min.delete(0,'end')
        except Exception as e:
            messagebox.showerror('Erro', str(e))
            self.controller.set_status(str(e), "error")