"""
Interfaz Gráfica - Agentes Inteligentes
Othello & TicTacToe 3D (4x4x4) vs IA Minimax Alfa-Beta
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os

# Agregar el directorio raíz al path para importar módulos del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from juegos.othello import JuegoOthello
from juegos.tictactoe3d import JuegoTicTacToe3D
from algoritmos.minimax import AgenteMinimaxAlfaBeta
from heuristicas.othello_heuristics import get_evaluador_othello
from heuristicas.ttt3d_heuristics import get_evaluador_ttt3d

# ─── Paleta de Colores ──────────────────────────────────────────────────────
BG_DARK     = "#0d0f14"
BG_PANEL    = "#141720"
BG_CARD     = "#1a1f2e"
BG_HOVER    = "#222840"
ACCENT      = "#6c63ff"
ACCENT2     = "#ff6584"
ACCENT3     = "#43e97b"
TEXT_PRIMARY   = "#f0f0f8"
TEXT_SECONDARY = "#8888aa"
CELL_EMPTY  = "#1e2438"
CELL_HOVER  = "#2a3050"
BORDER      = "#2d3255"

# Colores de fichas
COL_BLACK   = "#1a1a2e"     # Jugador 1 (Oscuro/Negro)
COL_WHITE   = "#e8e8f0"     # Jugador -1 (Claro/Blanco)
COL_IA      = "#6c63ff"     # IA highlight
VALID_COL   = "#43e97b"     # Movimiento válido

# ─── Pesos por defecto ───────────────────────────────────────────────────────
PESOS_OTHELLO_DEFAULT = (0.40401033647179574, 0.9562255176191674,-0.5810995767711737,-0.5608392529830415)
PESOS_TTT3D_DEFAULT   = (0.7533482793088735,-0.7018771573432969, 0.8615901366527485, 0.8437413291129652)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎮 Agentes Inteligentes — IA Búsquedas")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.minsize(900, 650)

        # Centrar ventana
        self.update_idletasks()
        w, h = 1100, 720
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        """Construye la estructura principal de la UI."""
        # Título principal
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", padx=24, pady=(20, 8))

        tk.Label(
            header, text="🤖  Agentes Inteligentes", font=("Segoe UI", 22, "bold"),
            bg=BG_DARK, fg=TEXT_PRIMARY
        ).pack(side="left")

        tk.Label(
            header, text="Minimax con Poda Alfa-Beta",
            font=("Segoe UI", 11), bg=BG_DARK, fg=TEXT_SECONDARY
        ).pack(side="left", padx=(14, 0), pady=(8, 0))

        # Separador decorativo
        sep = tk.Frame(self, bg=ACCENT, height=2)
        sep.pack(fill="x", padx=24, pady=(0, 16))

        # Notebook (pestañas)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Custom.TNotebook", background=BG_DARK, borderwidth=0, tabmargins=[0, 0, 0, 0])
        style.configure("Custom.TNotebook.Tab",
            background=BG_PANEL, foreground=TEXT_SECONDARY,
            padding=[18, 8], font=("Segoe UI", 11, "bold"), borderwidth=0
        )
        style.map("Custom.TNotebook.Tab",
            background=[("selected", ACCENT)],
            foreground=[("selected", TEXT_PRIMARY)]
        )

        self.notebook = ttk.Notebook(self, style="Custom.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Pestaña Othello
        self.tab_othello = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_othello, text="  ⚫ Othello  ")

        # Pestaña TicTacToe 3D
        self.tab_ttt = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_ttt, text="  🎯 TicTacToe 3D (4×4×4)  ")

        # Construir cada juego
        self.othello_ui = OthelloUI(self.tab_othello)
        self.ttt_ui = TicTacToe3DUI(self.tab_ttt)


# ─── Panel lateral reutilizable ─────────────────────────────────────────────
def make_side_panel(parent):
    """Devuelve un frame de panel lateral con scroll."""
    frame = tk.Frame(parent, bg=BG_PANEL, width=240)
    frame.pack_propagate(False)
    return frame


def section_label(parent, text):
    tk.Label(parent, text=text, font=("Segoe UI", 10, "bold"),
             bg=BG_PANEL, fg=ACCENT).pack(anchor="w", padx=14, pady=(14, 2))


def info_label(parent, textvariable=None, text="", fg=TEXT_SECONDARY):
    if textvariable:
        lbl = tk.Label(parent, textvariable=textvariable,
                       font=("Segoe UI", 10), bg=BG_PANEL, fg=fg,
                       wraplength=210, justify="left")
    else:
        lbl = tk.Label(parent, text=text,
                       font=("Segoe UI", 10), bg=BG_PANEL, fg=fg,
                       wraplength=210, justify="left")
    lbl.pack(anchor="w", padx=14, pady=2)
    return lbl


def action_button(parent, text, command, color=ACCENT):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg=TEXT_PRIMARY, relief="flat",
        font=("Segoe UI", 10, "bold"),
        activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY,
        cursor="hand2", padx=10, pady=6
    )
    btn.pack(fill="x", padx=14, pady=4)

    def on_enter(e): btn.config(bg=BG_HOVER)
    def on_leave(e): btn.config(bg=color)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def separator(parent):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=10, pady=8)


# ════════════════════════════════════════════════════════════════════════════
#  OTHELLO UI
# ════════════════════════════════════════════════════════════════════════════
class OthelloUI:
    CELL = 60
    PAD  = 4

    def __init__(self, parent):
        self.parent = parent
        self.juego = JuegoOthello()
        self.estado = None
        self.jugador_humano = 1     # El humano juega como Negras (1)
        self.profundidad = tk.IntVar(value=3)
        self.ia_thinking = False
        self.hover_cell = None

        self._build(parent)
        self.nueva_partida()

    # ── Construcción de UI ─────────────────────────────────────────────────
    def _build(self, parent):
        main = tk.Frame(parent, bg=BG_DARK)
        main.pack(fill="both", expand=True)

        # Panel izquierdo
        side = make_side_panel(main)
        side.pack(side="left", fill="y", padx=(0, 2))

        section_label(side, "⚙  Configuración")
        tk.Label(side, text="🔍 Profundidad IA:", font=("Segoe UI", 10, "bold"),
                 bg=BG_PANEL, fg=TEXT_PRIMARY).pack(anchor="w", padx=14)

        self.depth_scale = tk.Scale(
            side, variable=self.profundidad, from_=1, to=6, orient="horizontal",
            bg=BG_PANEL, fg=TEXT_PRIMARY, troughcolor=BG_CARD,
            highlightthickness=0, font=("Segoe UI", 10), length=200,
            activebackground=ACCENT, sliderrelief="flat", bd=0,
            tickinterval=1
        )
        self.depth_scale.pack(fill="x", padx=14, pady=4)

        tk.Label(side, text="🎨 Jugar como:", font=("Segoe UI", 10, "bold"),
                 bg=BG_PANEL, fg=TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(8, 2))

        self.lado_var = tk.StringVar(value="negro")
        side_frame = tk.Frame(side, bg=BG_PANEL)
        side_frame.pack(fill="x", padx=14, pady=4)
        for txt, val in [("⚫ Negras", "negro"), ("⚪ Blancas", "blanco")]:
            rb = tk.Radiobutton(
                side_frame, text=txt, variable=self.lado_var, value=val,
                bg=BG_CARD, fg=TEXT_SECONDARY, selectcolor=ACCENT,
                activebackground=ACCENT, activeforeground=TEXT_PRIMARY,
                font=("Segoe UI", 11, "bold"), cursor="hand2",
                indicatoron=0, padx=12, pady=6, relief="flat",
                bd=0, highlightthickness=0
            )
            rb.pack(side="left", expand=True, fill="x", padx=2)

        separator(side)
        action_button(side, "▶  Nueva Partida", self.nueva_partida, ACCENT)
        action_button(side, "⏩  IA Juega Ahora", self.forzar_ia, ACCENT2)

        separator(side)
        section_label(side, "📊  Marcador")

        self.lbl_negro = tk.StringVar(value="⚫ Negras: 2")
        self.lbl_blanco = tk.StringVar(value="⚪ Blancas: 2")
        info_label(side, self.lbl_negro, fg=TEXT_PRIMARY)
        info_label(side, self.lbl_blanco, fg=TEXT_PRIMARY)

        separator(side)
        section_label(side, "📝  Estado")
        self.lbl_turno = tk.StringVar(value="Tu turno")
        self.lbl_estado = tk.StringVar(value="")
        info_label(side, self.lbl_turno, fg=ACCENT3)
        self.lbl_nodos_var = tk.StringVar(value="")
        info_label(side, self.lbl_nodos_var, fg=TEXT_SECONDARY)
        self.lbl_podas_var = tk.StringVar(value="")
        info_label(side, self.lbl_podas_var, fg=TEXT_SECONDARY)

        separator(side)
        section_label(side, "ℹ  Leyenda")
        self._legend(side)

        # Área del tablero
        board_area = tk.Frame(main, bg=BG_DARK)
        board_area.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(board_area, text="Othello — 8×8", font=("Segoe UI", 14, "bold"),
                 bg=BG_DARK, fg=TEXT_PRIMARY).pack(pady=(0, 8))

        canvas_frame = tk.Frame(board_area, bg=BORDER, padx=3, pady=3)
        canvas_frame.pack()

        size = self.CELL * 8
        self.canvas = tk.Canvas(canvas_frame, width=size, height=size,
                                bg="#1a4a2e", highlightthickness=0, cursor="hand2")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>", self._on_hover)
        self.canvas.bind("<Leave>", self._on_leave)

    def _legend(self, parent):
        items = [
            ("⚫", "Ficha Negra (Jugador 1)", COL_BLACK),
            ("⚪", "Ficha Blanca (Jugador 2)", "#aaaacc"),
            ("🟢", "Jugada válida", VALID_COL),
        ]
        for icon, text, col in items:
            row = tk.Frame(parent, bg=BG_PANEL)
            row.pack(anchor="w", padx=14, pady=1)
            tk.Label(row, text=icon, font=("Segoe UI", 10), bg=BG_PANEL).pack(side="left")
            tk.Label(row, text=text, font=("Segoe UI", 9), bg=BG_PANEL, fg=col).pack(side="left", padx=4)

    # ── Lógica de juego ────────────────────────────────────────────────────
    def nueva_partida(self):
        self.ia_thinking = False
        self.jugador_humano = 1 if self.lado_var.get() == "negro" else -1
        self.estado = self.juego.estado_inicial()
        self.hover_cell = None
        self.lbl_nodos_var.set("")
        self.lbl_podas_var.set("")
        self._actualizar_ui()

        # Si la IA empieza primero
        if self.juego.jugador_actual(self.estado) != self.jugador_humano:
            self.parent.after(400, self._turno_ia)

    def _get_ia(self):
        pesos = PESOS_OTHELLO_DEFAULT
        evaluador = get_evaluador_othello(pesos)
        return AgenteMinimaxAlfaBeta(
            profundidad_maxima=self.profundidad.get(),
            evaluador=evaluador
        )

    def forzar_ia(self):
        if not self.ia_thinking and self.estado and not self.juego.es_terminal(self.estado):
            self._turno_ia()

    def _turno_ia(self):
        if self.ia_thinking:
            return
        self.ia_thinking = True
        self.lbl_turno.set("🤖 IA pensando...")

        def run():
            ia = self._get_ia()
            jugada = ia.seleccionar_movimiento(self.juego, self.estado)
            self.parent.after(0, lambda: self._aplicar_ia(jugada, ia))

        threading.Thread(target=run, daemon=True).start()

    def _aplicar_ia(self, jugada, ia):
        self.ia_thinking = False
        if jugada is not None or self.juego.jugadas_legales(self.estado) == [None]:
            self.estado = self.juego.aplicar_jugada(self.estado, jugada)

        self.lbl_nodos_var.set(f"Nodos explorados: {ia.nodos_explorados:,}")
        self.lbl_podas_var.set(f"Podas: {ia.nodos_podados:,}")
        self._actualizar_ui()
        self._verificar_fin()

    def _on_click(self, event):
        if self.ia_thinking:
            return
        if self.juego.es_terminal(self.estado):
            return
        if self.juego.jugador_actual(self.estado) != self.jugador_humano:
            return

        col = event.x // self.CELL
        row = event.y // self.CELL
        pos = row * 8 + col

        jugadas = self.juego.jugadas_legales(self.estado)
        if jugadas == [None]:
            # Paso de turno
            self.estado = self.juego.aplicar_jugada(self.estado, None)
            self._actualizar_ui()
            self._verificar_fin_y_turno_ia()
            return

        movimiento = next((j for j in jugadas if j[0] == pos), None)
        if movimiento:
            self.estado = self.juego.aplicar_jugada(self.estado, movimiento)
            self._actualizar_ui()
            self._verificar_fin_y_turno_ia()

    def _on_hover(self, event):
        col = event.x // self.CELL
        row = event.y // self.CELL
        new_hover = (row, col)
        if new_hover != self.hover_cell:
            self.hover_cell = new_hover
            self._dibujar_tablero()

    def _on_leave(self, event):
        self.hover_cell = None
        self._dibujar_tablero()

    def _verificar_fin_y_turno_ia(self):
        if self.juego.es_terminal(self.estado):
            self._verificar_fin()
            return
        actual = self.juego.jugador_actual(self.estado)
        if actual != self.jugador_humano:
            self.parent.after(300, self._turno_ia)

    def _verificar_fin(self):
        if self.juego.es_terminal(self.estado):
            black, white, _, _ = self.estado
            b = bin(black).count("1")
            w = bin(white).count("1")
            if b > w:
                msg = f"🎉 ¡Ganan las NEGRAS!\n⚫ {b}  vs  ⚪ {w}"
            elif w > b:
                msg = f"🎉 ¡Ganan las BLANCAS!\n⚫ {b}  vs  ⚪ {w}"
            else:
                msg = f"🤝 ¡EMPATE!\n⚫ {b}  vs  ⚪ {w}"
            self.lbl_turno.set("Partida terminada")
            messagebox.showinfo("Fin de partida", msg)

    def _actualizar_ui(self):
        black, white, turn, _ = self.estado
        b_count = bin(black).count("1")
        w_count = bin(white).count("1")
        self.lbl_negro.set(f"⚫ Negras: {b_count}")
        self.lbl_blanco.set(f"⚪ Blancas: {w_count}")

        if not self.juego.es_terminal(self.estado):
            if turn == self.jugador_humano:
                self.lbl_turno.set("🟢 Tu turno")
            else:
                self.lbl_turno.set("🤖 IA pensando...")

        self._dibujar_tablero()

    def _dibujar_tablero(self):
        self.canvas.delete("all")
        black, white, turn, _ = self.estado
        CELL = self.CELL

        jugadas = self.juego.jugadas_legales(self.estado)
        valid_pos = set()
        if jugadas and jugadas != [None] and turn == self.jugador_humano:
            valid_pos = {j[0] for j in jugadas}

        for row in range(8):
            for col in range(8):
                x1 = col * CELL
                y1 = row * CELL
                x2 = x1 + CELL
                y2 = y1 + CELL
                pos = row * 8 + col
                bit = 1 << pos

                # Color de celda
                is_hover = self.hover_cell == (row, col)
                if is_hover and pos in valid_pos:
                    fill = "#2d5c3f"
                elif is_hover:
                    fill = "#1e4030"
                else:
                    fill = "#1a4a2e"

                self.canvas.create_rectangle(x1, y1, x2, y2,
                    fill=fill, outline="#0d2e1c", width=1)

                # Resaltar movimientos válidos
                if pos in valid_pos:
                    pad = CELL // 2 - 8
                    cx, cy = x1 + CELL // 2, y1 + CELL // 2
                    self.canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                        fill=VALID_COL, outline="", stipple="gray50")

                # Dibujar fichas
                if bit & black:
                    self._draw_piece(x1, y1, CELL, "#1a1a2e", "#3a3a6e")
                elif bit & white:
                    self._draw_piece(x1, y1, CELL, "#e8e8f0", "#aaaacc")

        # Líneas de cuadrícula
        for i in range(9):
            self.canvas.create_line(i * CELL, 0, i * CELL, 8 * CELL, fill="#0d2e1c", width=1)
            self.canvas.create_line(0, i * CELL, 8 * CELL, i * CELL, fill="#0d2e1c", width=1)

        # Coordenadas del tablero
        cols_lbl = "ABCDEFGH"
        for i in range(8):
            self.canvas.create_text(i * CELL + CELL // 2, 8 * CELL - 6,
                text=cols_lbl[i], font=("Segoe UI", 7), fill="#4a6a54")
            self.canvas.create_text(6, i * CELL + CELL // 2,
                text=str(i + 1), font=("Segoe UI", 7), fill="#4a6a54")

    def _draw_piece(self, x1, y1, cell, color, highlight):
        pad = 6
        cx = x1 + cell // 2
        cy = y1 + cell // 2
        r = cell // 2 - pad
        # Sombra
        self.canvas.create_oval(cx - r + 2, cy - r + 2, cx + r + 2, cy + r + 2,
            fill="#050a08", outline="")
        # Ficha
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
            fill=color, outline=highlight, width=2)
        # Brillo
        self.canvas.create_oval(cx - r + 4, cy - r + 4, cx - 2, cy - 2,
            fill=highlight, outline="", stipple="gray50")


# ════════════════════════════════════════════════════════════════════════════
#  TICTACTOE 3D UI
# ════════════════════════════════════════════════════════════════════════════
class TicTacToe3DUI:
    CELL = 72
    GAP  = 18   # Espacio entre capas

    def __init__(self, parent):
        self.parent = parent
        self.juego = JuegoTicTacToe3D()
        self.estado = None
        self.jugador_humano = 1
        self.profundidad = tk.IntVar(value=2)
        self.ia_thinking = False
        self.hover_cell = None  # (capa, fila, col)

        self._build(parent)
        self.nueva_partida()

    def _build(self, parent):
        main = tk.Frame(parent, bg=BG_DARK)
        main.pack(fill="both", expand=True)

        # Panel lateral
        side = make_side_panel(main)
        side.pack(side="left", fill="y", padx=(0, 2))

        section_label(side, "⚙  Configuración")
        tk.Label(side, text="🔍 Profundidad IA:", font=("Segoe UI", 10, "bold"),
                 bg=BG_PANEL, fg=TEXT_PRIMARY).pack(anchor="w", padx=14)

        self.depth_scale = tk.Scale(
            side, variable=self.profundidad, from_=1, to=4, orient="horizontal",
            bg=BG_PANEL, fg=TEXT_PRIMARY, troughcolor=BG_CARD,
            highlightthickness=0, font=("Segoe UI", 10), length=200,
            activebackground=ACCENT, sliderrelief="flat", bd=0,
            tickinterval=1
        )
        self.depth_scale.pack(fill="x", padx=14, pady=4)

        tk.Label(side, text="🎨 Jugar como:", font=("Segoe UI", 10, "bold"),
                 bg=BG_PANEL, fg=TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(8, 2))

        self.lado_var = tk.StringVar(value="x")
        side_frame = tk.Frame(side, bg=BG_PANEL)
        side_frame.pack(fill="x", padx=14, pady=4)
        for txt, val in [("❌ Jugador X", "x"), ("⭕ Jugador O", "o")]:
            rb = tk.Radiobutton(
                side_frame, text=txt, variable=self.lado_var, value=val,
                bg=BG_CARD, fg=TEXT_SECONDARY, selectcolor=ACCENT,
                activebackground=ACCENT, activeforeground=TEXT_PRIMARY,
                font=("Segoe UI", 11, "bold"), cursor="hand2",
                indicatoron=0, padx=12, pady=6, relief="flat",
                bd=0, highlightthickness=0
            )
            rb.pack(side="left", expand=True, fill="x", padx=2)

        separator(side)
        action_button(side, "▶  Nueva Partida", self.nueva_partida, ACCENT)
        action_button(side, "⏩  IA Juega Ahora", self.forzar_ia, ACCENT2)

        separator(side)
        section_label(side, "📊  Progreso")
        self.lbl_fichas_x = tk.StringVar(value="❌ X: 0 fichas")
        self.lbl_fichas_o = tk.StringVar(value="⭕ O: 0 fichas")
        info_label(side, self.lbl_fichas_x, fg=TEXT_PRIMARY)
        info_label(side, self.lbl_fichas_o, fg=TEXT_PRIMARY)

        separator(side)
        section_label(side, "📝  Estado")
        self.lbl_turno = tk.StringVar(value="Tu turno")
        info_label(side, self.lbl_turno, fg=ACCENT3)
        self.lbl_nodos_var = tk.StringVar(value="")
        self.lbl_podas_var = tk.StringVar(value="")
        info_label(side, self.lbl_nodos_var, fg=TEXT_SECONDARY)
        info_label(side, self.lbl_podas_var, fg=TEXT_SECONDARY)

        separator(side)
        section_label(side, "ℹ  Capas del tablero")
        for i in range(4):
            tk.Label(side, text=f"  Capa Z={i}  →  Posiciones {i*16} a {i*16+15}",
                     font=("Segoe UI", 8), bg=BG_PANEL, fg=TEXT_SECONDARY).pack(anchor="w", padx=14)

        separator(side)
        section_label(side, "📖  Leyenda")
        items = [("❌", "Jugador X (1)", "#ff6b6b"), ("⭕", "Jugador O (-1)", "#6bc5ff")]
        for icon, text, col in items:
            row = tk.Frame(side, bg=BG_PANEL)
            row.pack(anchor="w", padx=14, pady=1)
            tk.Label(row, text=icon, font=("Segoe UI", 10), bg=BG_PANEL).pack(side="left")
            tk.Label(row, text=text, font=("Segoe UI", 9), bg=BG_PANEL, fg=col).pack(side="left", padx=4)

        # Área del tablero
        board_area = tk.Frame(main, bg=BG_DARK)
        board_area.pack(side="left", fill="both", expand=True)

        tk.Label(board_area, text="TicTacToe 3D — 4×4×4",
                 font=("Segoe UI", 14, "bold"), bg=BG_DARK, fg=TEXT_PRIMARY).pack(pady=(10, 4))

        sub = tk.Label(board_area,
            text="Haz clic en una celda vacía para colocar tu ficha. ¡Forma una línea de 4 en cualquier dirección!",
            font=("Segoe UI", 9), bg=BG_DARK, fg=TEXT_SECONDARY, wraplength=620)
        sub.pack(pady=(0, 10))

        # Canvas con scroll si es necesario
        self.canvas_frame = tk.Frame(board_area, bg=BG_DARK)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Calcular tamaño del canvas
        cw = self.CELL * 4 * 4 + self.GAP * 3 + 20
        ch = self.CELL * 4 + 70

        canvas_wrap = tk.Frame(self.canvas_frame, bg=BORDER, padx=2, pady=2)
        canvas_wrap.pack()

        self.canvas = tk.Canvas(canvas_wrap, width=cw, height=ch,
                                bg=BG_CARD, highlightthickness=0, cursor="hand2")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>", self._on_hover)
        self.canvas.bind("<Leave>", self._on_leave)

    # ── Lógica de juego ────────────────────────────────────────────────────
    def nueva_partida(self):
        self.ia_thinking = False
        self.jugador_humano = 1 if self.lado_var.get() == "x" else -1
        self.estado = self.juego.estado_inicial()
        self.hover_cell = None
        self.lbl_nodos_var.set("")
        self.lbl_podas_var.set("")
        self._actualizar_ui()

        if self.juego.jugador_actual(self.estado) != self.jugador_humano:
            self.parent.after(400, self._turno_ia)

    def _get_ia(self):
        pesos = PESOS_TTT3D_DEFAULT
        evaluador = get_evaluador_ttt3d(pesos)
        return AgenteMinimaxAlfaBeta(
            profundidad_maxima=self.profundidad.get(),
            evaluador=evaluador
        )

    def forzar_ia(self):
        if not self.ia_thinking and self.estado and not self.juego.es_terminal(self.estado):
            self._turno_ia()

    def _turno_ia(self):
        if self.ia_thinking:
            return
        self.ia_thinking = True
        self.lbl_turno.set("🤖 IA pensando...")

        def run():
            ia = self._get_ia()
            jugada = ia.seleccionar_movimiento(self.juego, self.estado)
            self.parent.after(0, lambda: self._aplicar_ia(jugada, ia))

        threading.Thread(target=run, daemon=True).start()

    def _aplicar_ia(self, jugada, ia):
        self.ia_thinking = False
        if jugada is not None:
            self.estado = self.juego.aplicar_jugada(self.estado, jugada)

        self.lbl_nodos_var.set(f"Nodos explorados: {ia.nodos_explorados:,}")
        self.lbl_podas_var.set(f"Podas: {ia.nodos_podados:,}")
        self._actualizar_ui()
        self._verificar_fin()

    def _pos_to_coords(self, pos):
        z = pos // 16
        rem = pos % 16
        y = rem // 4
        x = rem % 4
        return z, y, x

    def _coords_to_canvas(self, z, row, col):
        """Convierte coordenadas 3D a posición en canvas."""
        CELL = self.CELL
        GAP = self.GAP
        offset_x = z * (CELL * 4 + GAP) + 10
        offset_y = 50
        cx = offset_x + col * CELL
        cy = offset_y + row * CELL
        return cx, cy

    def _canvas_to_pos(self, x, y):
        """Convierte posición canvas a índice del tablero (o None)."""
        CELL = self.CELL
        GAP = self.GAP
        for z in range(4):
            ox = z * (CELL * 4 + GAP) + 10
            oy = 50
            if ox <= x < ox + CELL * 4 and oy <= y < oy + CELL * 4:
                col = (x - ox) // CELL
                row = (y - oy) // CELL
                return row * 4 + z * 16 + col
        return None

    def _canvas_to_cell(self, x, y):
        """Devuelve (z, row, col) o None."""
        CELL = self.CELL
        GAP = self.GAP
        for z in range(4):
            ox = z * (CELL * 4 + GAP) + 10
            oy = 50
            if ox <= x < ox + CELL * 4 and oy <= y < oy + CELL * 4:
                col = (x - ox) // CELL
                row = (y - oy) // CELL
                return (z, row, col)
        return None

    def _on_click(self, event):
        if self.ia_thinking or self.juego.es_terminal(self.estado):
            return
        if self.juego.jugador_actual(self.estado) != self.jugador_humano:
            return

        pos = self._canvas_to_pos(event.x, event.y)
        if pos is None:
            return

        tablero, _ = self.estado
        if tablero[pos] != 0:
            return  # Celda ocupada

        jugadas = self.juego.jugadas_legales(self.estado)
        if pos in jugadas:
            self.estado = self.juego.aplicar_jugada(self.estado, pos)
            self._actualizar_ui()
            if not self.juego.es_terminal(self.estado):
                if self.juego.jugador_actual(self.estado) != self.jugador_humano:
                    self.parent.after(200, self._turno_ia)
            else:
                self._verificar_fin()

    def _on_hover(self, event):
        cell = self._canvas_to_cell(event.x, event.y)
        if cell != self.hover_cell:
            self.hover_cell = cell
            self._dibujar_tablero()

    def _on_leave(self, event):
        if self.hover_cell is not None:
            self.hover_cell = None
            self._dibujar_tablero()

    def _verificar_fin(self):
        if self.juego.es_terminal(self.estado):
            tablero, _ = self.estado
            ganador = self.juego._comprobar_ganador(tablero)
            if ganador == 1:
                msg = "🎉 ¡Gana el Jugador X!"
            elif ganador == -1:
                msg = "🎉 ¡Gana el Jugador O!"
            else:
                msg = "🤝 ¡EMPATE! El tablero está lleno."
            self.lbl_turno.set("Partida terminada")
            messagebox.showinfo("Fin de partida", msg)

    def _actualizar_ui(self):
        tablero, turn = self.estado
        x_count = tablero.count(1)
        o_count = tablero.count(-1)
        self.lbl_fichas_x.set(f"❌ X: {x_count} fichas")
        self.lbl_fichas_o.set(f"⭕ O: {o_count} fichas")

        if not self.juego.es_terminal(self.estado):
            if turn == self.jugador_humano:
                sym = "❌" if turn == 1 else "⭕"
                self.lbl_turno.set(f"🟢 Tu turno  ({sym})")
            else:
                self.lbl_turno.set("🤖 IA pensando...")

        self._dibujar_tablero()

    def _dibujar_tablero(self):
        self.canvas.delete("all")
        tablero, turn = self.estado
        CELL = self.CELL

        jugadas = set()
        if not self.juego.es_terminal(self.estado) and turn == self.jugador_humano:
            jugadas = set(self.juego.jugadas_legales(self.estado))

        # Colores por capa (gradiente sutil)
        layer_colors = ["#181e30", "#1a2035", "#1c223a", "#1e2540"]
        layer_labels = ["Z=0  (Base)", "Z=1", "Z=2", "Z=3  (Tope)"]

        for z in range(4):
            ox, oy = self._coords_to_canvas(z, 0, 0)

            # Título de capa
            self.canvas.create_text(
                ox + CELL * 2, oy - 22,
                text=layer_labels[z],
                font=("Segoe UI", 9, "bold"),
                fill=ACCENT if z == 0 else TEXT_SECONDARY
            )

            for row in range(4):
                for col in range(4):
                    x1 = ox + col * CELL
                    y1 = oy + row * CELL
                    x2 = x1 + CELL
                    y2 = y1 + CELL
                    pos = row * 4 + z * 16 + col

                    is_hover = self.hover_cell == (z, row, col)
                    is_valid = pos in jugadas

                    # Fondo de celda
                    if is_hover and is_valid:
                        bg = "#2a3460"
                    elif is_hover:
                        bg = "#232842"
                    elif is_valid:
                        bg = "#1e2c40"
                    else:
                        bg = layer_colors[z]

                    self.canvas.create_rectangle(x1, y1, x2, y2,
                        fill=bg, outline=BORDER, width=1)

                    # Movimiento válido: punto verde sutil
                    if is_valid:
                        cx, cy = x1 + CELL // 2, y1 + CELL // 2
                        self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                            fill="#43e97b", outline="", stipple="gray50")

                    val = tablero[pos]
                    if val == 1:
                        self._draw_x(x1, y1, CELL)
                    elif val == -1:
                        self._draw_o(x1, y1, CELL)

            # Borde de capa
            self.canvas.create_rectangle(
                ox, oy, ox + CELL * 4, oy + CELL * 4,
                outline=ACCENT if z == 0 else BORDER, width=2, fill=""
            )

    def _draw_x(self, x1, y1, cell):
        pad = 14
        x2, y2 = x1 + cell, y1 + cell
        # Sombra
        self.canvas.create_line(x1+pad+2, y1+pad+2, x2-pad+2, y2-pad+2,
            fill="#200000", width=4, capstyle="round")
        self.canvas.create_line(x2-pad+2, y1+pad+2, x1+pad+2, y2-pad+2,
            fill="#200000", width=4, capstyle="round")
        # X
        self.canvas.create_line(x1+pad, y1+pad, x2-pad, y2-pad,
            fill="#ff6b6b", width=4, capstyle="round")
        self.canvas.create_line(x2-pad, y1+pad, x1+pad, y2-pad,
            fill="#ff6b6b", width=4, capstyle="round")

    def _draw_o(self, x1, y1, cell):
        pad = 12
        cx = x1 + cell // 2
        cy = y1 + cell // 2
        r = cell // 2 - pad
        # Sombra
        self.canvas.create_oval(cx - r + 2, cy - r + 2, cx + r + 2, cy + r + 2,
            outline="#001a33", width=5)
        # O
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
            outline="#6bc5ff", width=4, fill="")
        # Brillo interno
        self.canvas.create_oval(cx - r + 6, cy - r + 6, cx - r//2, cy - r//2,
            outline="#aaddff", width=1, fill="")


# ─── Punto de entrada ────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
