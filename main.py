import tkinter as tk
from tkinter import messagebox

def entrar():
    usuario = entry_usuario.get()
    senha = entry_senha.get()
    # Aqui você pode adicionar verificação com banco de dados
    messagebox.showinfo("Login", f"Usuário: {usuario}\nSenha: {senha}")

def cadastrar():
    messagebox.showinfo("Cadastro", "Redirecionar para cadastro...")

# Cria a janela principal
root = tk.Tk()
root.title("Login")
root.geometry("300x250")
root.resizable(False, False)

# Frame principal
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True, fill='both')

# Label Login
label_login = tk.Label(frame, text="Login", font=("Arial", 14))
label_login.pack(pady=(0, 10))

# Usuário
label_usuario = tk.Label(frame, text="Usuario")
label_usuario.pack(anchor='w')
entry_usuario = tk.Entry(frame, width=30)
entry_usuario.pack(pady=(0, 10))

# Senha
label_senha = tk.Label(frame, text="Senha")
label_senha.pack(anchor='w')
entry_senha = tk.Entry(frame, width=30, show="*")
entry_senha.pack(pady=(0, 10))

# Botão Entrar
btn_entrar = tk.Button(frame, text="Entrar", bg="#b2f2bb", width=20, command=entrar)
btn_entrar.pack(pady=(0, 10))

# Link Cadastre-se
btn_cadastrar = tk.Button(frame, text="Cadastre-se", fg="blue", bg="white", bd=0, command=cadastrar)
btn_cadastrar.pack()

# Inicia o loop da interface
root.mainloop()
