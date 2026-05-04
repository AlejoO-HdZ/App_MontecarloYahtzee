"""
gui.py

Interfaz Tkinter para controlar la simulación Yahtzee Montecarlo.

- botones: Start, Histograma, Boxplot, Convergencia, Batch (verde), Descripción Probabilística
- Botón Batch colocado junto a Convergencia; botón Descripción Probabilística al final con estilo naranja ("Warning.TButton").
- tablero de puntuaciones en cuadrícula y estadísticas finales con porcentajes y explicación breve.
- Importaciones tardías y manejo de dependencias con mensajes claros.
"""

import threading
import time
import re
from collections import Counter, defaultdict
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# Intentar importar matplotlib y numpy; si no están, avisar al usuario al intentar graficar
try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
except Exception:
    plt = None

try:
    import numpy as np
except Exception:
    np = None

# Categorías (coincide con juegoStart.CATEGORIES_ORDER)
CATEGORIES = [
    "ones","twos","threes","fours","fives","sixes",
    "threeOfKind","fourOfKind","fullHouse","smallStraight",
    "largeStraight","yahtzee","chance"
]

class YahtzeeApp:
    def __init__(self, root, sims_default: int = 300):
        self.root = root
        root.title("Yahtzee Montecarlo - Simulación")
        self.sims_default = sims_default
        self.sim_thread = None
        self.last_state = None
        self.totals_series = []  # Lista acumulada de puntajes totales por partida
        self.yahtzee_series = []

        # Paleta: azul tenue + verde tenue para Batch/Convergencia + naranja para descripción
        self.palette = {
            "bg": "#F4F7FB",        # fondo muy claro
            "panel_bg": "#FFFFFF",  # paneles blancos
            "accent": "#4A90E2",    # azul tenue (botones generales)
            "accent2": "#2F6FA8",   # azul secundario
            "muted": "#6B7280",     # gris para texto secundario
            "text": "#0F1724",      # gris muy oscuro para texto principal
            "success": "#4CAF50",   # verde tenue para Batch/Convergencia
            "success2": "#2E7D32",  # verde secundario
            "warn": "#F29C4A",      # naranja tenue para descripción probabilística
            "warn2": "#D97706"      # naranja secundario
        }

        self.create_widgets()
        self.apply_style()

    def apply_style(self):
        """Aplica estilo profesional usando ttk.Style, incluyendo estilos Success y Warning."""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            style.theme_use('default')

        style.configure("TFrame", background=self.palette["bg"])
        style.configure("TLabel", background=self.palette["bg"], foreground=self.palette["text"], font=("Segoe UI", 10))
        style.configure("TLabelFrame", background=self.palette["panel_bg"], foreground=self.palette["text"])
        style.configure("TButton",
                        background=self.palette["accent"],
                        foreground="white",
                        font=("Segoe UI", 10, "bold"),
                        padding=6)
        style.map("TButton",
                  background=[("active", self.palette["accent2"])],
                  foreground=[("disabled", "#A0A0A0")])

        # Estilo para botones de éxito (verde)
        style.configure("Success.TButton",
                        background=self.palette["success"],
                        foreground="white",
                        font=("Segoe UI", 10, "bold"),
                        padding=6)
        style.map("Success.TButton",
                  background=[("active", self.palette["success2"])])

        # Estilo para botón de advertencia/naranja (Descripción Probabilística)
        style.configure("Warning.TButton",
                        background=self.palette["warn"],
                        foreground="white",
                        font=("Segoe UI", 10, "bold"),
                        padding=6)
        style.map("Warning.TButton",
                  background=[("active", self.palette["warn2"])])

    def create_widgets(self):
        """Crea los widgets principales: controles, log y tablero de puntuaciones."""
        root = self.root
        root.configure(background=self.palette["bg"])
        frm = ttk.Frame(root, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        # Controles (arriba) - orden solicitado
        controls = ttk.LabelFrame(frm, text="Controles")
        controls.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        ttk.Label(controls, text="Sims por máscara:").grid(row=0, column=0, sticky="w")
        self.sims_var = tk.IntVar(value=self.sims_default)
        ttk.Entry(controls, textvariable=self.sims_var, width=8).grid(row=0, column=1, sticky="w")

        # Botones en el orden: Start, Histograma, Torta, Boxplot, Convergencia, Batch (verde), Descripción (naranja al final)
        ttk.Button(controls, text="Start partida (verbose)", command=self.play_one_game).grid(row=0, column=2, padx=6)
        ttk.Button(controls, text="Histograma caras", command=self.show_last_hist).grid(row=0, column=3, padx=6)
        ttk.Button(controls, text="Boxplot puntajes", command=self.show_last_boxplot).grid(row=0, column=4, padx=6)
        ttk.Button(controls, text="Convergencia", command=self.show_convergence, style="Success.TButton").grid(row=0, column=5, padx=6)

        ttk.Button(controls, text="Batch (N partidas)", command=self.open_batch_dialog, style="Success.TButton").grid(row=0, column=6, padx=6)
        ttk.Button(controls, text="Convergencia Yahtzee", command=self.plot_yahtzee_convergence, style="Success.TButton").grid(row=0, column=7, padx=6)
        ttk.Button(controls,text="Validación Montecarlo",command=self.validate_montecarlo,style="Warning.TButton").grid(row=0, column=8, padx=6)

        ttk.Button(controls, text="Descripción Probabilística", command=self.show_prob_description, style="Warning.TButton").grid(row=0, column=9, padx=6)


        # Panel izquierdo: salida (log)
        out_frame = ttk.LabelFrame(frm, text="Salida")
        out_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        frm.rowconfigure(1, weight=1)
        frm.columnconfigure(0, weight=3)
        out_frame.rowconfigure(0, weight=1)
        out_frame.columnconfigure(0, weight=1)

        self.output = scrolledtext.ScrolledText(out_frame, width=80, height=30, wrap=tk.WORD, bg="white")
        self.output.grid(row=0, column=0, sticky="nsew")

        # Panel derecho: tablero de puntuaciones (categorías x jugadores)
        board_frame = ttk.LabelFrame(frm, text="Tablero de puntuaciones")
        board_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        frm.columnconfigure(1, weight=1)
        board_frame.rowconfigure(0, weight=1)
        board_frame.columnconfigure(0, weight=1)

        # Treeview con columna de categoría + columnas por jugador
        columns = ("Categoria", "Jugador 1", "Jugador 2")
        self.score_table = ttk.Treeview(board_frame, columns=columns, show="headings", height=len(CATEGORIES)+2)
        self.score_table.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # Encabezados y anchuras
        self.score_table.heading("Categoria", text="Categoría")
        self.score_table.heading("Jugador 1", text="Jugador 1")
        self.score_table.heading("Jugador 2", text="Jugador 2")
        self.score_table.column("Categoria", width=160, anchor="w")
        self.score_table.column("Jugador 1", width=100, anchor="center")
        self.score_table.column("Jugador 2", width=100, anchor="center")

        # Insertar filas (una por categoría) con valores iniciales vacíos
        for cat in CATEGORIES:
            display_cat = self._pretty_category(cat)
            self.score_table.insert("", tk.END, iid=cat, values=(display_cat, "", ""))

        # Fila resumen de Totales por jugador (al final)
        self.score_table.insert("", tk.END, iid="__TOTALS__", values=("TOTAL", "0", "0"))

        # Barra de estado
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Regex para detectar la línea donde se informa la categoría elegida
        # Ejemplo: "→ Jugador 1 elige categoría 'ones' y anota 3 puntos. Total = 23"
        self._cat_line_re = re.compile(r"elige categoría '([^']+)' y anota (\d+) puntos.*Total = (\d+)")
        self._player_prefix_re = re.compile(r"→\s*(Jugador\s*\d+)")

    # -------------------------
    # Utilidades
    # -------------------------
    def _pretty_category(self, key: str) -> str:
        """Mapea claves técnicas a nombres más legibles para la tabla."""
        mapping = {
            "ones": "Ones",
            "twos": "Twos",
            "threes": "Threes",
            "fours": "Fours",
            "fives": "Fives",
            "sixes": "Sixes",
            "threeOfKind": "Three of a Kind",
            "fourOfKind": "Four of a Kind",
            "fullHouse": "Full House",
            "smallStraight": "Small Straight",
            "largeStraight": "Large Straight",
            "yahtzee": "Yahtzee",
            "chance": "Chance"
        }
        return mapping.get(key, key)

    # -------------------------
    # Logger y actualización de tablero
    # -------------------------
    def log(self, text: str):
        """
        Escribe texto en el panel de salida (thread-safe) y detecta líneas de puntuación
        para actualizar la tabla de puntuaciones en tiempo real.
        """
        def _append():
            self.output.insert(tk.END, text + "\n")
            self.output.see(tk.END)
            # Intentar detectar línea de categoría elegida y actualizar tabla
            try:
                m = self._cat_line_re.search(text)
                if m:
                    cat = m.group(1)
                    score = int(m.group(2))
                    total = int(m.group(3))
                    # Determinar jugador por prefijo de la línea
                    pm = self._player_prefix_re.search(text)
                    if pm:
                        player_name = pm.group(1).strip()
                    else:
                        # fallback
                        if "Jugador 1" in text:
                            player_name = "Jugador 1"
                        elif "Jugador 2" in text:
                            player_name = "Jugador 2"
                        else:
                            player_name = None

                    if player_name:
                        col = 1 if "1" in player_name else 2
                        # Actualizar la celda correspondiente en la tabla
                        current_vals = list(self.score_table.item(cat, "values"))
                        # current_vals = (Categoria, Jugador1, Jugador2)
                        current_vals[col] = str(score)
                        self.score_table.item(cat, values=current_vals)

                        # Recalcular sumas a partir de la tabla (más robusto)
                        total1 = 0
                        total2 = 0
                        for c in CATEGORIES:
                            v = self.score_table.item(c, "values")
                            try:
                                total1 += int(v[1]) if v[1] not in (None, "", "-") else 0
                            except Exception:
                                pass
                            try:
                                total2 += int(v[2]) if v[2] not in (None, "", "-") else 0
                            except Exception:
                                pass
                        self.score_table.item("__TOTALS__", values=("TOTAL", str(total1), str(total2)))
            except Exception:
                pass

        self.root.after(0, _append)

    # -------------------------
    # Ejecución de partidas
    # -------------------------
    def play_one_game(self):
        """Ejecuta una partida completa (verbose) en un hilo separado."""
        if self.sim_thread and self.sim_thread.is_alive():
            messagebox.showinfo("En ejecución", "Ya hay una simulación en ejecución. Espera a que termine.")
            return

        sims = int(self.sims_var.get())
        # Limpiar la tabla para nueva partida (mantener fila TOTAL)
        for cat in CATEGORIES:
            self.score_table.item(cat, values=(self._pretty_category(cat), "", ""))
        self.score_table.item("__TOTALS__", values=("TOTAL", "0", "0"))

        self.output.delete("1.0", tk.END)
        self.status_var.set("Jugando 1 partida...")

        def target():
            try:
                from juegoStart import play_game
                state = play_game(verbose_each_turn=True, logger=self.log, sims_per_mask=sims)
                self.last_state = state

                total_yahtzees_dados = 0
                self.yahtzee_series_dados = []

                # Guardar totales de la partida para convergencia
                for p in state.players:
                    self.totals_series.append(p.total)

                # Mostrar marcador final en formato solicitado
                self.log("\n===== MARCADOR FINAL =====")
                for p in state.players:
                    self.log(f"{p.name} : {p.total} puntos")
                    for cat in CATEGORIES:
                        val = getattr(p, "scores", {}).get(cat, None) if hasattr(p, "scores") else None
                        # fallback si la estructura es distinta
                        if val is None and hasattr(p, "score_by_category"):
                            val = p.score_by_category.get(cat, None)
                        val_str = str(val) if val is not None else "-"
                        self.log(f"  - {cat.ljust(13)}: {val_str}")

                    # Yahtzees que aparecieron en las tiradas (según category_hist)
                    yahtzees_dados = state.stats.category_hist.get("yahtzee", 0)
                    total_yahtzees_dados += yahtzees_dados
                    self.yahtzee_series_dados.append(yahtzees_dados)

                # Estadísticas de caras y ganador
                self._log_game_statistics(state)

                self.log(f"\nYahtzees que aparecieron en las simulaciones: {total_yahtzees_dados}")
                promedio_dados = total_yahtzees_dados / yahtzees_dados
                self.log(f"Promedio de Yahtzees por partida (simulación): {promedio_dados:.2f}")


            except Exception as e:
                self.log(f"Error durante la partida: {e}")
            finally:
                self.status_var.set("Listo")

        self.sim_thread = threading.Thread(target=target, daemon=True)
        self.sim_thread.start()

    def open_batch_dialog(self):
        """Abre diálogo para ejecutar un batch de partidas."""
        if self.sim_thread and self.sim_thread.is_alive():
            messagebox.showinfo("En ejecución", "Ya hay una simulación en ejecución. Espera a que termine.")
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("Ejecutar batch de simulaciones")
        ttk.Label(dlg, text="Número de partidas:").grid(row=0, column=0, padx=5, pady=5)
        nvar = tk.IntVar(value=100)
        ttk.Entry(dlg, textvariable=nvar, width=10).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(dlg, text="Sims por máscara:").grid(row=1, column=0, padx=5, pady=5)
        svar = tk.IntVar(value=self.sims_var.get())
        ttk.Entry(dlg, textvariable=svar, width=10).grid(row=1, column=1, padx=5, pady=5)

        def run_batch():
            n = int(nvar.get())
            sims = int(svar.get())
            dlg.destroy()
            self.run_batch(n, sims)

        ttk.Button(dlg, text="Iniciar", command=run_batch, style="Success.TButton").grid(row=2, column=0, columnspan=2, pady=10)

    def run_batch(self, n_games: int, sims_per_mask: int):
        """
        Ejecuta n partidas en lote, acumula estadísticas y guarda los puntajes totales
        en self.totals_series para análisis de convergencia.
        """
        self.output.delete("1.0", tk.END)
        self.status_var.set(f"Ejecutando {n_games} partidas (sims={sims_per_mask})...")
        self.log(f"Iniciando batch: {n_games} partidas, sims por máscara={sims_per_mask}")

        def target():
            try:
                from juegoStart import play_game, GameState, PlayerState
                wins = Counter()
                agg_face_hist = Counter()
                agg_category_hist = Counter()
                agg_scores_by_category = defaultdict(list)

                total_yahtzees_dados = 0
                self.yahtzee_series_dados = []

                start = time.time()
                for i in range(n_games):
                    state = play_game(verbose_each_turn=False, logger=None, sims_per_mask=sims_per_mask)

                    # Determinar ganador
                    if state.players[0].total > state.players[1].total:
                        wins[state.players[0].name] += 1
                    elif state.players[1].total > state.players[0].total:
                        wins[state.players[1].name] += 1
                    else:
                        wins["Empate"] += 1

                    # contar yahtzees en esta partida
                    yahtzee_count = 0
                    for p in state.players:
                        # si el jugador anotó algo en la categoría yahtzee
                        if hasattr(p, "scores") and p.scores.get("yahtzee", 0) > 0:
                            yahtzee_count += 1
                    self.yahtzee_series.append(yahtzee_count)


                    # Agregar estadísticas agregadas
                    agg_face_hist.update(state.stats.face_hist)
                    agg_category_hist.update(state.stats.category_hist)
                    for k, v in state.stats.scores_by_category.items():
                        agg_scores_by_category[k].extend(v)

                    # Guardar totales de la partida (ambos jugadores)
                    for p in state.players:
                        self.totals_series.append(p.total)

                    # Progreso cada 10%
                    if (i + 1) % max(1, n_games // 10) == 0:
                        self.log(f"  - Completadas {i+1}/{n_games} partidas")

                elapsed = time.time() - start

                # Construir last_state con agregados para graficar
                self.last_state = GameState(players=[PlayerState("Jugador 1"), PlayerState("Jugador 2")])
                self.last_state.stats.face_hist = agg_face_hist
                self.last_state.stats.category_hist = agg_category_hist
                self.last_state.stats.scores_by_category = agg_scores_by_category

                # Mostrar marcador final en formato solicitado
                self.log("\n===== MARCADOR FINAL =====")
                for p in state.players:
                    self.log(f"{p.name} : {p.total} puntos")
                    for cat in CATEGORIES:
                        val = getattr(p, "scores", {}).get(cat, None) if hasattr(p, "scores") else None
                        # fallback si la estructura es distinta
                        if val is None and hasattr(p, "score_by_category"):
                            val = p.score_by_category.get(cat, None)
                        val_str = str(val) if val is not None else "-"
                        self.log(f"  - {cat.ljust(13)}: {val_str}")

                # Resumen final
                self.log(f"\nBatch completado en {elapsed:.1f}s")
                self.log(f"Victorias: {dict(wins)}")
                total_rolls = sum(agg_face_hist.values())
                self.log(f"Total de lanzamientos (dados individuales): {total_rolls}")
                for face in range(1, 7):
                    c = agg_face_hist.get(face, 0)
                    pct = (c / total_rolls) * 100 if total_rolls else 0.0
                    expl = self._brief_explanation_for_pct(pct)
                    self.log(f" Cara {face}: {c} veces ({pct:.2f}%) — {expl}")

                    # Yahtzees que aparecieron en las tiradas (según category_hist)
                    yahtzees_dados = state.stats.category_hist.get("yahtzee", 0)
                    total_yahtzees_dados += yahtzees_dados
                self.yahtzee_series_dados.append(yahtzees_dados)


                # Mostrar ganador agregado (el que tenga más victorias)
                if wins:
                    winner = max(wins.items(), key=lambda x: x[1])[0]
                    self.log(f"\nGANADOR DEL BATCH: {winner.upper()}")

                self.log(f"\nSe guardaron {len(self.totals_series)} puntajes totales para análisis de convergencia.")

                self.log(f"\nYahtzees que aparecieron en las simulaciones: {total_yahtzees_dados}")
                promedio_dados = total_yahtzees_dados / n_games if n_games else 0
                self.log(f"Promedio de Yahtzees por partida (simulación): {promedio_dados:.2f}")


            except Exception as e:
                self.log(f"Error durante batch: {e}")
            finally:
                self.status_var.set("Listo")

        self.sim_thread = threading.Thread(target=target, daemon=True)
        self.sim_thread.start()

    def _brief_explanation_for_pct(self, pct: float) -> str:
        """
        Devuelve una explicación breve (2-3 palabras) según la desviación respecto a 16.6667%.
        - dentro ±2% -> "esperado"
        - > +2% -> "ligera sobre-rep"
        - < -2% -> "ligera sub-rep"
        """
        base = 100.0 / 6.0  # 16.666...
        diff = pct - base
        if abs(diff) <= 2.0:
            return "esperado"
        elif diff > 2.0:
            return "ligera sobre-rep"
        else:
            return "ligera sub-rep"

    # -------------------------
    # Estadísticas de partida
    # -------------------------
    def _log_game_statistics(self, state):
        """Imprime ganador (mayúsculas) y conteos de caras al finalizar una partida."""
        try:
            # Determinar ganador
            p0 = state.players[0].total
            p1 = state.players[1].total
            if p0 > p1:
                winner = state.players[0].name
            elif p1 > p0:
                winner = state.players[1].name
            else:
                winner = "EMPATE"
            self.log(f"\nGANADOR: {winner.upper()}")

            # Conteo de caras y total de lanzamientos
            total_faces = sum(state.stats.face_hist.values())
            self.log(f"\nTotal de lanzamientos (dados individuales): {total_faces}")
            for face in range(1, 7):
                c = state.stats.face_hist.get(face, 0)
                pct = (c / total_faces) * 100 if total_faces else 0.0
                expl = self._brief_explanation_for_pct(pct)
                self.log(f" Cara {face}: {c} veces ({pct:.2f}%) — {expl}")
        except Exception as e:
            self.log(f"Error al generar estadísticas de la partida: {e}")

    # -------------------------
    # Visualizaciones y análisis (con análisis embebido en cada gráfico)
    # -------------------------
    def show_last_hist(self):
        """Dibuja histograma de caras con estadísticas y análisis en un mismo cuadro."""
        if self.last_state is None:
            messagebox.showinfo("Sin datos", "No hay datos de simulación. Ejecuta una partida o batch primero.")
            return
        if plt is None:
            messagebox.showerror("Error", "matplotlib no está disponible. Instala matplotlib para graficar.")
            return

        try:
            import matplotlib.ticker as mtick

            face_hist = self.last_state.stats.face_hist
            faces = list(range(1, 7))
            counts = [face_hist.get(f, 0) for f in faces]
            total = sum(counts)
            freqs = [c / total if total > 0 else 0 for c in counts]

            probs_theo = [1/6] * 6
            # Estadísticas simuladas
            observations = []
            for f, c in zip(faces, counts):
                observations.extend([f] * c)
            if observations:
                E_sim = sum(observations) / len(observations)
                Var_sim = sum((x - E_sim) ** 2 for x in observations) / len(observations)
                sigma_sim = Var_sim ** 0.5
            else:
                E_sim = Var_sim = sigma_sim = 0.0

            # Plot
            plt.figure(figsize=(7, 4))
            bars = plt.bar(faces, freqs, color=self.palette["accent"], alpha=0.85,
                           label="Frecuencia simulada (%)")
            plt.plot(faces, probs_theo, marker='o', color="orange", linestyle='--',
                     linewidth=2, label="Prob. teórica (1/6)")

            plt.xlabel("Cara")
            plt.ylabel("Frecuencia (%)")
            plt.title("Histograma de caras (simulado vs teórico)")

            # Mostrar porcentaje encima de cada barra
            for bar, freq in zip(bars, freqs):
                porcentaje = freq * 100
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                         f"{porcentaje:.1f}%", ha='center', va='bottom', fontsize=9, color="black")

            # Formatear eje Y en porcentaje
            plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

            # Texto combinado: estadísticas + análisis en un mismo cuadro
            stats_text = (f"E_sim={E_sim:.6f}, Var_sim={Var_sim:.6f}, σ_sim={sigma_sim:.6f}\n"
                          f"E_theo=3.500000, Var_theo=2.916667, σ_theo=1.707825\n\n"
                          "Análisis: La distribución simulada debe aproximarse a la uniforme (1/6).\n"
                          "Desviaciones pequeñas son esperadas por azar; con más lanzamientos la frecuencia converge.")
            plt.gcf().text(0.02, 0.02, stats_text, fontsize=9, va='bottom',
                           bbox=dict(facecolor='white', alpha=0.8))

            plt.legend(loc="upper right")
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Error al graficar histograma", str(e))


    def show_category_pie(self):
        """
        Dibuja un diagrama de torta (pie) con la cantidad de anotaciones por categoría
        usando last_state.stats.category_hist (o scores_by_category counts).
        Actualiza con datos reales de la última partida o del batch agregado.
        """
        if self.last_state is None:
            messagebox.showinfo("Sin datos", "No hay datos de simulación. Ejecuta una partida o batch primero.")
            return
        if plt is None:
            messagebox.showerror("Error", "matplotlib no está disponible. Instala matplotlib para graficar.")
            return

        try:
            # Preferir category_hist si existe y tiene datos
            cat_hist = {}
            if hasattr(self.last_state.stats, "category_hist") and self.last_state.stats.category_hist:
                # Asegurar que sean enteros
                cat_hist = {k: int(v) for k, v in dict(self.last_state.stats.category_hist).items()}
            else:
                # Derivar: contar cuántas entradas hay por categoría en scores_by_category
                if hasattr(self.last_state.stats, "scores_by_category"):
                    cat_hist = {k: len(v) for k, v in self.last_state.stats.scores_by_category.items()}
                else:
                    # Si no hay datos, informar
                    messagebox.showinfo("Sin datos", "No hay registros por categoría para graficar.")
                    return

            # Filtrar categorías con cero para evitar slices vacíos
            cat_hist = {k: v for k, v in cat_hist.items() if v > 0}
            if not cat_hist:
                messagebox.showinfo("Sin datos", "No hay registros por categoría para graficar.")
                return

            labels = [self._pretty_category(k) for k in cat_hist.keys()]
            sizes = list(cat_hist.values())
            total = sum(sizes)
            # Colores agradables (usar colormap)
            colors = plt.cm.Paired(range(len(labels)))

            plt.figure(figsize=(7, 6))
            wedges, texts, autotexts = plt.pie(sizes, labels=labels, autopct=lambda pct: f"{pct:.1f}%\n({int(round(pct*total/100))})",
                                               colors=colors, startangle=90, textprops=dict(color="black"))
            plt.title("Distribución de anotaciones por categoría (porcentaje y conteo)")

            # Análisis embebido
            analysis_text = ("Análisis: El pie muestra la proporción de anotaciones por categoría.\n"
                             "Permite identificar categorías más frecuentes y menos frecuentes.")
            plt.gcf().text(0.02, 0.02, analysis_text, fontsize=9, va='bottom', bbox=dict(facecolor='white', alpha=0.8))

            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Error al graficar pie de categorías", str(e))

    def show_last_boxplot(self):
        """Dibuja boxplot de puntajes por categoría con análisis embebido en la figura."""
        if self.last_state is None:
            messagebox.showinfo("Sin datos", "No hay datos de simulación. Ejecuta una partida o batch primero.")
            return
        if plt is None:
            messagebox.showerror("Error", "matplotlib no está disponible. Instala matplotlib para graficar.")
            return

        try:
            scores_by_category = self.last_state.stats.scores_by_category
            cats = list(scores_by_category.keys())
            data = [scores_by_category[c] if scores_by_category[c] else [0] for c in cats]

            plt.figure(figsize=(10, 5))
            plt.boxplot(data, labels=[self._pretty_category(c) for c in cats], showfliers=False, patch_artist=True,
                        boxprops=dict(facecolor=self.palette["accent"], color=self.palette["text"]))
            plt.xticks(rotation=45)
            plt.title("Distribución de puntajes por categoría")

            # Análisis embebido
            analysis_text = ("Análisis: El boxplot muestra mediana y dispersión por categoría.\n"
                             "Categorías raras (ej. Yahtzee) tendrán pocos valores altos; otras muestran mayor variabilidad.")
            plt.gcf().text(0.02, 0.02, analysis_text, fontsize=9, va='bottom', bbox=dict(facecolor='white', alpha=0.8))

            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Error al graficar boxplot", str(e))

    def show_convergence(self):
        """
        Grafica la convergencia real usando self.totals_series (media acumulada).
        Incluye línea de tendencia (regresión lineal) y línea de media final.
        Inserta un análisis descriptivo dentro del mismo gráfico.
        Usa tonos verdes para indicar relación con Batch.
        """
        if not self.totals_series:
            messagebox.showinfo("Sin datos de convergencia",
                                "No hay puntajes guardados. Ejecuta partidas o un batch para generar datos de convergencia.")
            return
        if plt is None:
            messagebox.showerror("Error", "matplotlib no está disponible. Instala matplotlib para graficar.")
            return
        if np is None:
            messagebox.showerror("Error", "numpy no está disponible. Instala numpy para la regresión y graficado de convergencia.")
            return

        try:
            arr = np.array(self.totals_series, dtype=float)
            n = len(arr)
            cum_mean = np.cumsum(arr) / (np.arange(n) + 1)

            x = np.arange(n)
            coeffs = np.polyfit(x, cum_mean, 1)
            trend = np.polyval(coeffs, x)
            final_mean = cum_mean[-1]

            plt.figure(figsize=(9, 5))
            plt.plot(cum_mean, color=self.palette["success"], label="Media acumulada")
            plt.plot(trend, color=self.palette["success2"], linestyle="--", label=f"Línea de tendencia (slope={coeffs[0]:.6f})")
            plt.hlines(final_mean, 0, n-1, colors="#FF8A00", linestyles=':', label=f"Media final = {final_mean:.3f}")
            plt.xlabel("Número de observaciones (puntajes individuales)")
            plt.ylabel("Media acumulada del puntaje total")
            plt.title("Convergencia de la media acumulada (Ley de los grandes números)")
            plt.legend()

            # Análisis embebido
            analysis_text = (
                "Análisis: La curva verde muestra la media acumulada. La línea punteada es la tendencia estimada.\n"
                "Con suficientes observaciones la media tiende a estabilizarse; pendiente cercana a 0 indica convergencia."
            )
            plt.gcf().text(0.02, 0.02, analysis_text, fontsize=9, va='bottom', bbox=dict(facecolor='white', alpha=0.8))

            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Error al graficar convergencia", str(e))

    def show_prob_description(self):
        """
        Abre una ventana emergente con la Descripción Probabilística solicitada:
        - Distribución Uniforme: fracción, decimal y porcentaje
        - Valor Esperado
        - Varianza
        - Desviación Estándar
        Incluye un análisis descriptivo al final.
        """
        try:
            from analysis import probabilistic_description_with_results, theoretical_die_stats
            lines, block = probabilistic_description_with_results()
            probs, E, Var, sigma = theoretical_die_stats()

            # Construir la ventana emergente
            dlg = tk.Toplevel(self.root)
            dlg.title("Análisis Probabilístico")
            dlg.geometry("560x320")
            dlg.transient(self.root)

            txt = scrolledtext.ScrolledText(dlg, wrap=tk.WORD, width=70, height=16, bg="white")
            txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

            # Añadir las líneas exactas con fracción, decimal y porcentaje para la distribución
            frac = "1/6"
            dec = f"{probs[1]:.7f}"
            pct = f"{probs[1]*100:.2f}%"
            txt.insert(tk.END, "Análisis Probabilístico\n\n")
            txt.insert(tk.END, f"Distribución Uniforme: Cada cara del dado tiene probabilidad P(X=k) = {frac} ≈ {dec} ≈ {pct}\n")
            txt.insert(tk.END, f"Valor Esperado: E[X] = {E:.6f}\n")
            txt.insert(tk.END, f"Varianza: Var(X) = {Var:.6f}\n")
            txt.insert(tk.END, f"Desviación Estándar: σ = {sigma:.6f}\n\n")

            # Análisis descriptivo final
            analysis_paragraph = (
                "Análisis descriptivo:\n"
                "Los resultados anteriores corresponden a un dado justo de seis caras. "
                "La distribución uniforme indica que cada cara es igualmente probable. "
                "El valor esperado (3.5) es el promedio teórico de las caras 1..6. "
                "La varianza y la desviación estándar cuantifican la dispersión natural de los lanzamientos; "
                "valores más altos indican mayor variabilidad en los resultados individuales."
            )
            txt.insert(tk.END, analysis_paragraph)
            txt.configure(state=tk.DISABLED)

            # Botón para cerrar
            btn = ttk.Button(dlg, text="Cerrar", command=dlg.destroy)
            btn.pack(pady=6)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def plot_yahtzee_convergence(self):
        if not self.yahtzee_series:
            return

        cumulative_avg = []
        total = 0
        for i, count in enumerate(self.yahtzee_series, start=1):
            total += count
            cumulative_avg.append(total / i)

        plt.figure(figsize=(8,5))
        # Dispersión partida a partida
        plt.scatter(range(1, len(self.yahtzee_series)+1), self.yahtzee_series,
                    color="gray", alpha=0.4, label="Yahtzees por partida")
        # Promedio acumulado
        plt.plot(range(1, len(self.yahtzee_series)+1), cumulative_avg,
                 color="#4A90E2", linewidth=2, label="Promedio acumulado")
        plt.xlabel("Número de partidas")
        plt.ylabel("Yahtzees")
        plt.title("Convergencia de Yahtzees")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.show()


    def validate_montecarlo(self):
        """
        Simula N partidas de dados y valida Montecarlo mostrando un histograma.
        El usuario ingresa cuántos lanzamientos quiere simular.
        """
        import random
        import matplotlib.pyplot as plt
        from tkinter import simpledialog

        # Pedir número de lanzamientos
        n_lanzamientos = simpledialog.askinteger(
            "Número de partidas",
            "¿Cuántos lanzamientos quieres simular?",
            minvalue=100, maxvalue=100000
        )
        if not n_lanzamientos:
            return

        # Simulación
        face_hist = {i: 0 for i in range(1, 7)}
        for _ in range(n_lanzamientos):
            cara = random.randint(1, 6)
            face_hist[cara] += 1

        esperado = n_lanzamientos / 6
        margen = esperado * 0.05

        # Datos
        caras = list(range(1, 7))
        counts = [face_hist[c] for c in caras]

        # Gráfico
        fig = plt.figure(figsize=(9,6))
        bars = plt.bar(caras, counts, color="#A5D6A7", edgecolor="#388E3C", alpha=0.8)

        # Línea esperada en gris fuerte
        plt.axhline(esperado, color="gray", linestyle="--", linewidth=2)

        # Banda de tolerancia en naranja tenue
        plt.fill_between(caras, esperado-margen, esperado+margen, color="#FFA726", alpha=0.2)

        # Etiquetas encima de cada barra
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width()/2, count + 10,
                     str(count), ha='center', va='bottom', fontsize=9, color="black")

        # Leyendas explicativas al lado derecho
        plt.text(6.5, esperado, f"Esperado ≈ {esperado:.1f}", color="gray",
                 fontsize=10, fontweight="bold", va="center")
        plt.text(6.5, esperado+margen, "+5% tolerancia", color="#FFA726",
                 fontsize=9, fontweight="bold", va="bottom")
        plt.text(6.5, esperado-margen, "-5% tolerancia", color="#FFA726",
                 fontsize=9, fontweight="bold", va="top")

        plt.title(f"Validación Montecarlo - {n_lanzamientos} lanzamientos")
        plt.xlabel("Cara del dado")
        plt.ylabel("Frecuencia")
        plt.xticks(caras)

        plt.tight_layout()

        # Mostrar y traer al frente
        plt.show(block=False)
        mgr = plt.get_current_fig_manager()
        try:
            # Forzar que la ventana esté al frente
            mgr.window.attributes('-topmost', 1)
            mgr.window.focus_force()
            mgr.window.attributes('-topmost', 0)
        except Exception:
            pass
        plt.show()
# End of gui.py
