# estoque/ui/controller.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk   # ➕ PIL para redimensionar
from pathlib import Path

from ..config import LOGO_PATH, LOGO_MAX_HEIGHT
from ..models import Usuario, TipoUsuario
from .frames.login import LoginFrame
from .frames.home import HomeFrame
from .frames.admin_empresa import AdminEmpresaFrame
from .frames.admin_usuario import AdminUsuarioFrame
from .frames.produto import ProdutoFrame
from .frames.movimento import MovimentoFrame
from .frames.relatorios import RelatoriosFrame
from .theme import apply_theme

# no topo do controller.py
from PIL import Image, ImageTk
from pathlib import Path
import os



class AppController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Estoque (SQLAlchemy)')
        self.geometry('1000x650')
        self.resizable(True, True)
        self._user: Usuario | None = None

        apply_theme(self)

        # ➕ Carrega logo 1x para todo o app
        self.logo_img = self._load_logo()

        # Container central
        self.container = tk.Frame(self, bg="#FAFAFA")
        self.container.pack(fill='both', expand=True)

        # Frames
        self.frames = {}
        for F in (LoginFrame, HomeFrame, AdminEmpresaFrame, AdminUsuarioFrame, ProdutoFrame, MovimentoFrame, RelatoriosFrame):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Status bar
        self.status_var = tk.StringVar(value="Aguardando login...")
        status = tk.Frame(self, bg="#EEEEEE")
        status.pack(fill='x', side='bottom')
        ttk.Label(status, textvariable=self.status_var).pack(side='left', padx=8, pady=3)

        # Menus base + por papel
        self._build_menu_base()
        self._rebuild_role_menus()
        self.show_frame('LoginFrame')

        # Encerramento e atalhos
        self.protocol('WM_DELETE_WINDOW', self.on_exit)
        self.bind_all('<Alt-h>', lambda e: self.show_frame('HomeFrame'))
        self.bind_all('<F1>',    lambda e: self.show_frame('HomeFrame'))

# dentro da classe AppController
    def _load_logo(self):
        
        """
        Carrega o logo a partir de LOGO_PATH ou de locais comuns.
        Redimensiona para altura LOGO_MAX_HEIGHT, mantendo proporção.
        Retorna PhotoImage ou None.
        """
        from ..config import LOGO_PATH, LOGO_MAX_HEIGHT

        # Base do projeto (raiz)
        # controller.py está em estoque/ui/controller.py → 2 níveis acima é a raiz do projeto
        project_root = Path(__file__).resolve().parents[2]

        # Candidatos de caminho (ordem de tentativa)
        candidates = [
            Path(LOGO_PATH),
            Path.cwd() / LOGO_PATH,
            project_root / LOGO_PATH,
            project_root / "assets" / "logo.png",
            project_root / "logo.png",
        ]

        chosen = None
        for p in candidates:
            try:
                if p.exists() and p.is_file():
                    chosen = p
                    break
            except Exception:
                pass

        if not chosen:
            # você pode exibir no status bar também:
            try:
                self.set_status("Logo não encontrado. Coloque 'logo.png' na raiz ou em assets/logo.png.", "info")
            except Exception:
                pass
            return None

        try:
            img = Image.open(chosen).convert("RGBA")
            w, h = img.size
            target_h = int(os.getenv("ESTOQUE_LOGO_H", LOGO_MAX_HEIGHT))
            if h != target_h and target_h > 0:
                ratio = target_h / float(h)
                new_size = (max(1, int(w * ratio)), target_h)
                img = img.resize(new_size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            # Log opcional no status bar para sabermos de onde veio
            try:
                self.set_status(f"Logo carregado de: {chosen}", "info")
            except Exception:
                pass
            return photo
        except Exception as e:
            try:
                self.set_status(f"Falha ao carregar logo: {e}", "error")
            except Exception:
                pass
            return None
        # ... restante do controller (sem mudanças) ...

    def _build_menu_base(self):
        self.menu_bar = tk.Menu(self)
        # Sessão (sempre existe)
        self.menu_sessao = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_sessao.add_command(label='Home', command=lambda: self.show_frame('HomeFrame'))
        self.menu_sessao.add_separator()
        self.menu_sessao.add_command(label='Logout', command=self.logout)
        self.menu_sessao.add_command(label='Sair', command=self.on_exit)
        self.menu_bar.add_cascade(label='Sessão', menu=self.menu_sessao)
        self.config(menu=self.menu_bar)

    def _clear_role_menus(self):
        # Remove cascatas além de 'Sessão'
        end = self.menu_bar.index('end')
        if end is not None:
            for i in reversed(range(1, end + 1)):
                self.menu_bar.delete(i)

    def _rebuild_role_menus(self):
        self._clear_role_menus()
        user = self._user
        if not user:
            # sem usuário logado -> nenhum menu funcional
            return

        if user.tipo == TipoUsuario.ADMIN:
            # Somente Admin
            menu_admin = tk.Menu(self.menu_bar, tearoff=0)
            menu_admin.add_command(label='Empresas', command=lambda: self.show_frame('AdminEmpresaFrame'))
            menu_admin.add_command(label='Usuários', command=lambda: self.show_frame('AdminUsuarioFrame'))
            self.menu_bar.add_cascade(label='Admin', menu=menu_admin)
        else:
            # Usuário Padrão
            menu_est = tk.Menu(self.menu_bar, tearoff=0)
            menu_est.add_command(label='Produtos', command=lambda: self.show_frame('ProdutoFrame'))
            menu_est.add_command(label='Entradas/Saídas', command=lambda: self.show_frame('MovimentoFrame'))
            self.menu_bar.add_cascade(label='Estoque', menu=menu_est)

            menu_rel = tk.Menu(self.menu_bar, tearoff=0)
            menu_rel.add_command(label='Relatórios', command=lambda: self.show_frame('RelatoriosFrame'))
            self.menu_bar.add_cascade(label='Relatórios', menu=menu_rel)

    def set_status(self, msg: str, kind: str = "info"):
        self.status_var.set(msg)
        # você pode colorir por tipo se quiser; aqui mantemos simples

    def show_frame(self, name: str):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            try:
                frame.on_show()
            except Exception as e:
                messagebox.showerror('Erro', str(e))
                self.set_status(str(e), "error")

    def set_user(self, user: Usuario):
        self._user = user
        self._rebuild_role_menus()
        self.set_status(f"Logado como: {user.nome}", "success")
        self.show_frame('HomeFrame')

    def get_user(self) -> Usuario | None:
        return self._user

    def logout(self):
        self._user = None
        self._rebuild_role_menus()
        self.set_status("Sessão encerrada.", "info")
        self.show_frame('LoginFrame')

    def on_exit(self):
        self.destroy()