import tkinter as tk
from tkinter import ttk, messagebox
from ...services import autenticar

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FAFAFA")
        self.controller = controller

        # Header com logo + título (sem botão Home)
        header = tk.Frame(self, bg="#FAFAFA"); header.pack(fill='x')
        if self.controller.logo_img:
            ttk.Label(header, image=self.controller.logo_img).pack(side='left', padx=10, pady=8)
        ttk.Label(header, text='Login', style="H1.TLabel").pack(side='left', padx=8, pady=8)

        # Formulário
        form = tk.Frame(self, bg="#FAFAFA"); form.pack(pady=10)
        ttk.Label(form, text='Email').grid(row=0, column=0, sticky='e', padx=6, pady=6)
        self.e_email = ttk.Entry(form, width=40)
        self.e_email.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(form, text='Senha').grid(row=1, column=0, sticky='e', padx=6, pady=6)
        self.e_senha = ttk.Entry(form, width=40, show='*')
        self.e_senha.grid(row=1, column=1, padx=6, pady=6)

        ttk.Button(self, text='Entrar', style="Primary.TButton", command=self._login).pack(pady=16)

    def _login(self):
        email = self.e_email.get().strip()
        senha = self.e_senha.get()
        user = autenticar(email, senha)
        if user:
            messagebox.showinfo('Login', f'Bem-vindo, {user.nome}!')
            self.controller.set_user(user)
        else:
            messagebox.showerror('Erro', 'Credenciais inválidas')
            self.controller.set_status("Falha ao autenticar.", "error")

    def on_show(self):
        self.e_email.delete(0, 'end')
        self.e_senha.delete(0, 'end')

    def on_call(self):
        self.controller.logout()

    