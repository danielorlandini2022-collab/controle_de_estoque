# estoque/ui/frames/movimento.py
import tkinter as tk
from tkinter import ttk, messagebox
from ...models import TipoUsuario, TipoMov
from ...services import listar_produtos, lancar_movimento, produto_em_alerta, obter_produto

PADY = 6  # espaçamento vertical padrão entre linhas

class MovimentoFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FAFAFA")
        self.controller = controller

        # ===== Header: logo + título + Home =====
        header = tk.Frame(self, bg="#FAFAFA")
        header.pack(fill='x')
        if self.controller.logo_img:
            ttk.Label(header, image=self.controller.logo_img).pack(side='left', padx=10, pady=8)
        ttk.Label(header, text='Lançar Entrada/Saída', style="H2.TLabel").pack(side='left', padx=8, pady=8)
        ttk.Button(header, text='← Home', style="Info.TButton",
                   command=lambda: self.controller.show_frame('HomeFrame')).pack(side='right', padx=10, pady=8)
        ttk.Button(header, text='Sair', style="Info.TButton",
                   command=lambda: self.controller.logout()).pack(side='right', padx=10, pady=8)
        # ===== Form: 2 colunas (labels e inputs) =====
        form = ttk.Frame(self, padding=(12, 8, 12, 8))
        form.pack(fill='x', expand=False)

        # coluna 0 = labels (fixa), coluna 1 = campos (expansível)
        form.columnconfigure(0, weight=0, minsize=180)
        form.columnconfigure(1, weight=1)

        # Produto
        ttk.Label(form, text='Produto').grid(row=0, column=0, sticky='e', padx=(0, 12), pady=PADY)
        self.cb_prod = ttk.Combobox(form, state='readonly')
        self.cb_prod.grid(row=0, column=1, sticky='ew', pady=PADY)

        # Tipo
        ttk.Label(form, text='Tipo').grid(row=1, column=0, sticky='e', padx=(0, 12), pady=PADY)
        self.tipo_var = tk.StringVar(value=TipoMov.ENTRADA.value)
        self.cb_tipo = ttk.Combobox(form, state='readonly',
                                    values=[m.value for m in TipoMov],
                                    textvariable=self.tipo_var)
        self.cb_tipo.grid(row=1, column=1, sticky='w', pady=PADY)

        # Quantidade
        ttk.Label(form, text='Quantidade').grid(row=2, column=0, sticky='e', padx=(0, 12), pady=PADY)
        self.e_qtd = ttk.Entry(form, width=20)
        self.e_qtd.grid(row=2, column=1, sticky='w', pady=PADY)

        # Custo unitário
        ttk.Label(form, text='Custo unitário (opcional)').grid(row=3, column=0, sticky='e', padx=(0, 12), pady=PADY)
        self.e_custo = ttk.Entry(form, width=20)
        self.e_custo.grid(row=3, column=1, sticky='w', pady=PADY)

        # Observação
        ttk.Label(form, text='Observação (opcional)').grid(row=4, column=0, sticky='e', padx=(0, 12), pady=PADY)
        self.e_obs = ttk.Entry(form)
        self.e_obs.grid(row=4, column=1, sticky='ew', pady=PADY)

        # Barra de botões (alinhado à direita)
        btnbar = ttk.Frame(self)
        btnbar.pack(fill='x', pady=(8, 0))
        ttk.Button(btnbar, text='Lançar', style='Primary.TButton',
                   command=self._lancar).pack(side='right', padx=12)

    def on_show(self):
        user = self.controller.get_user()
        if not user or user.tipo != TipoUsuario.PADRAO:
            messagebox.showerror('Permissão', 'Apenas usuário Padrão acessa esta tela.')
            self.controller.show_frame('HomeFrame')
            return

        prods = listar_produtos(user)

        # Mostra estoque e mínimo (melhor leitura; sem “saltar” largura)
        self._map = {}
        items = []
        for p in prods:
            min_txt = p.minimo_estoque if p.minimo_estoque is not None else "-"
            label = f"{p.codigo} - {p.descricao} (id={p.id}) [estoque={p.estoque}, min={min_txt}]"
            items.append(label)
            self._map[label] = p.id
        self.cb_prod['values'] = items
        if items:
            self.cb_prod.current(0)

    def _lancar(self):
        try:
            u = self.controller.get_user()
            key = self.cb_prod.get()
            if not key:
                raise ValueError('Selecione um produto.')

            pid = self._map[key]
            qtd = int(self.e_qtd.get())
            if qtd <= 0:
                raise ValueError('Quantidade deve ser um inteiro positivo.')

            custo = float(self.e_custo.get()) if self.e_custo.get().strip() else None
            tipo = TipoMov(self.tipo_var.get())

            mov = lancar_movimento(u, pid, tipo, qtd, custo, self.e_obs.get().strip() or None)
            messagebox.showinfo('OK', f'{tipo.value} registrada (Mov. #{mov.id})')
            self.controller.set_status(f"{tipo.value} registrada para o produto id={pid}.", "success")

            # Aviso de estoque mínimo pós-operação
            if produto_em_alerta(pid):
                p = obter_produto(pid)
                min_txt = p.minimo_estoque if p and p.minimo_estoque is not None else "-"
                msg = (f"O produto '{p.codigo} - {p.descricao}' atingiu o estoque mínimo.\n"
                       f"Estoque atual: {p.estoque} (mínimo: {min_txt})")
                messagebox.showwarning("Estoque mínimo", msg)
                try:
                    self.controller.bell()
                except Exception:
                    pass
                self.controller.set_status(f"[ALERTA] Produto '{p.codigo}' em nível crítico.", "error")

            # Limpa campos e recarrega para refletir novos estoques
            self.e_qtd.delete(0, 'end')
            self.e_custo.delete(0, 'end')
            self.e_obs.delete(0, 'end')
            self.on_show()

        except Exception as e:
            messagebox.showerror('Erro', str(e))
            self.controller.set_status(str(e), "error")