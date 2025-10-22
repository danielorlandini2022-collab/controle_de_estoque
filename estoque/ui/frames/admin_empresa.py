import tkinter as tk
from tkinter import ttk, messagebox
from ...models import TipoUsuario
from ...services import criar_empresa

class AdminEmpresaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FAFAFA")
        self.controller = controller

        # Header com logo + título + Home
        header = tk.Frame(self, bg="#FAFAFA"); header.pack(fill='x')
        if self.controller.logo_img:
            ttk.Label(header, image=self.controller.logo_img).pack(side='left', padx=10, pady=8)
        ttk.Label(header, text='Cadastro de Empresa', style="H2.TLabel").pack(side='left', padx=8, pady=8)
        ttk.Button(header, text='← Home', style="Info.TButton",
                   command=lambda: self.controller.show_frame('HomeFrame')).pack(side='right', padx=10, pady=8)
        ttk.Button(header, text='Sair', style="Info.TButton",
                   command=lambda: self.controller.logout()).pack(side='right', padx=10, pady=8)
        form = tk.Frame(self, bg="#FAFAFA"); form.pack(pady=10)
        ttk.Label(form, text='Nome').grid(row=0, column=0, sticky='e', padx=6, pady=6)
        self.e_nome = ttk.Entry(form, width=40); self.e_nome.grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(form, text='CNPJ (apenas números)').grid(row=1, column=0, sticky='e', padx=6, pady=6)
        self.e_cnpj = ttk.Entry(form, width=40); self.e_cnpj.grid(row=1, column=1, padx=6, pady=6)
        ttk.Label(form, text='Telefone').grid(row=2, column=0, sticky='e', padx=6, pady=6)
        self.e_tel = ttk.Entry(form, width=40); self.e_tel.grid(row=2, column=1, padx=6, pady=6)
        ttk.Button(self, text='Salvar', style="Success.TButton", command=self._salvar).pack(pady=12)

    def on_show(self):
        user = self.controller.get_user()
        if not user or user.tipo != TipoUsuario.ADMIN:
            messagebox.showerror('Permissão', 'Apenas Admin acessa esta tela.')
            self.controller.show_frame('HomeFrame')

    def _salvar(self):
        try:
            u = self.controller.get_user()
            emp = criar_empresa(u, self.e_nome.get().strip(), self.e_cnpj.get().strip(), self.e_tel.get().strip() or None)
            messagebox.showinfo('OK', f'Empresa criada (ID: {emp.id})')
            self.controller.set_status(f"Empresa '{emp.nome}' criada.", "success")
            self.e_nome.delete(0,'end'); self.e_cnpj.delete(0,'end'); self.e_tel.delete(0,'end')
        except Exception as e:
            messagebox.showerror('Erro', str(e))
            self.controller.set_status(str(e), "error")