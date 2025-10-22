import tkinter as tk
from tkinter import ttk
from ...services import produtos_criticos

class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FAFAFA")
        self.controller = controller

        # Header com logo + título
        header = tk.Frame(self, bg="#FAFAFA"); header.pack(fill='x')
        if self.controller.logo_img:
            ttk.Label(header, image=self.controller.logo_img).pack(side='left', padx=10, pady=8)
        ttk.Label(header, text='Bem-vindo!', style="H1.TLabel").pack(side='left', padx=8, pady=8)
        ttk.Button(header, text='Sair', style="Info.TButton",
                   command=lambda: self.controller.logout()).pack(side='right', padx=10, pady=8)
        self.alert_frame = tk.Frame(self, bg="#FFF3E0", bd=1, relief='solid')
        self.alert_title = ttk.Label(self.alert_frame, text="Alertas de Estoque Mínimo", style="H2.TLabel")
        self.alert_list = tk.Text(self.alert_frame, height=6, width=90, wrap='word', state='disabled', bg="#FFF8E1")

    def on_show(self):
        user = self.controller.get_user()
        criticos = produtos_criticos(user) if user else []

        # Limpa área de alerta
        for w in self.alert_frame.pack_slaves():
            w.forget()

        if criticos:
            lines = []
            for p in criticos:
                min_txt = p.minimo_estoque if p.minimo_estoque is not None else "-"
                lines.append(f"- {p.codigo} - {p.descricao}: estoque={p.estoque}, mínimo={min_txt}")
            txt = "\n".join(lines)

            self.alert_frame.pack(pady=8, padx=16, fill='x')
            self.alert_title.pack(anchor='w', padx=10, pady=(8, 4))
            self.alert_list.configure(state='normal')
            self.alert_list.delete('1.0', 'end')
            self.alert_list.insert('1.0', txt)
            self.alert_list.configure(state='disabled')
            self.alert_list.pack(padx=10, pady=(0, 10), fill='x')

            self.controller.set_status(f"{len(criticos)} produto(s) em nível crítico.", "error")
        else:
            self.alert_frame.forget()
            self.controller.set_status("Nenhum alerta de estoque mínimo.", "info")