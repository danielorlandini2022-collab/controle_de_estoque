import tkinter as tk
from tkinter import ttk, messagebox
from ...models import TipoUsuario
from ...services import criar_usuario, listar_empresas

class AdminUsuarioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FAFAFA")
        self.controller = controller

        # Header com logo + título + Home
        header = tk.Frame(self, bg="#FAFAFA"); header.pack(fill='x')
        if self.controller.logo_img:
            ttk.Label(header, image=self.controller.logo_img).pack(side='left', padx=10, pady=8)
        ttk.Label(header, text='Cadastro de Usuário', style="H2.TLabel").pack(side='left', padx=8, pady=8)
        ttk.Button(header, text='← Home', style="Info.TButton",
                   command=lambda: self.controller.show_frame('HomeFrame')).pack(side='right', padx=10, pady=8)
        ttk.Button(header, text='Sair', style="Info.TButton",
                   command=lambda: self.controller.logout()).pack(side='right', padx=10, pady=8)
        form = tk.Frame(self, bg="#FAFAFA"); form.pack(pady=10)
        # ... (restante do formulário igual ao que já está no seu arquivo)

        ttk.Label(form, text='Nome').grid(row=0, column=0, sticky='e', padx=6, pady=6)
        self.e_nome = ttk.Entry(form, width=44); self.e_nome.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(form, text='Email').grid(row=1, column=0, sticky='e', padx=6, pady=6)
        self.e_email = ttk.Entry(form, width=44); self.e_email.grid(row=1, column=1, padx=6, pady=6)

        ttk.Label(form, text='Senha').grid(row=2, column=0, sticky='e', padx=6, pady=6)
        self.e_senha = ttk.Entry(form, width=44, show='*'); self.e_senha.grid(row=2, column=1, padx=6, pady=6)

        ttk.Label(form, text='Tipo').grid(row=3, column=0, sticky='e', padx=6, pady=6)
        self.tipo_var = tk.StringVar(value='0')
        ttk.Radiobutton(form, text='Padrão', variable=self.tipo_var, value='0').grid(row=3, column=1, sticky='w', padx=6, pady=6)
        ttk.Radiobutton(form, text='Admin',  variable=self.tipo_var, value='1').grid(row=3, column=1, sticky='w', padx=120, pady=6)

        ttk.Label(form, text='Empresa').grid(row=4, column=0, sticky='e', padx=6, pady=6)
        self.cb_emp = ttk.Combobox(form, state='readonly', width=42)
        self.cb_emp.grid(row=4, column=1, padx=6, pady=6)
        self._emp_map = {}

        ttk.Button(self, text='Salvar', style="Success.TButton", command=self._salvar).pack(pady=12)

    def on_show(self):
        user = self.controller.get_user()
        if not user or user.tipo != TipoUsuario.ADMIN:
            messagebox.showerror('Permissão', 'Apenas Admin acessa esta tela.')
            self.controller.show_frame('HomeFrame')
            return
        emps = listar_empresas()
        self._emp_map = { f"{e.id} - {e.nome}": e.id for e in emps }
        self.cb_emp['values'] = list(self._emp_map.keys())
        if self._emp_map:
            self.cb_emp.current(0)

    def _salvar(self):
        try:
            tipo = TipoUsuario.ADMIN if self.tipo_var.get()=='1' else TipoUsuario.PADRAO
            emp_id = None
            if tipo == TipoUsuario.PADRAO:
                label = self.cb_emp.get()
                if not label:
                    raise ValueError("Selecione uma empresa para usuário Padrão.")
                emp_id = self._emp_map[label]

            u_admin = self.controller.get_user()
            u = criar_usuario(
                u_admin,
                self.e_nome.get().strip(),
                self.e_email.get().strip(),
                self.e_senha.get(),
                tipo,
                emp_id
            )
            messagebox.showinfo('OK', f'Usuário criado (ID: {u.id})')
            self.controller.set_status(f"Usuário '{u.nome}' criado.", "success")
            self.e_nome.delete(0,'end'); self.e_email.delete(0,'end'); self.e_senha.delete(0,'end')
        except Exception as e:
            messagebox.showerror('Erro', str(e))
            self.controller.set_status(str(e), "error")