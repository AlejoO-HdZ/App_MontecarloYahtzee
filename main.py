"""
main.py
Punto de arranque de la aplicación Yahtzee Montecarlo.
"""
import random
import sys
# Parámetros globales
SIMS_PER_MASK = 300
SEED = 42

# Inicializar semilla global
if SEED is not None:
    random.seed(SEED)

def run_app():
    """
    Inicia la GUI. Importaciones que dependen de otros módulos se hacen aquí
    para evitar importaciones circulares.
    """
    try:
        import tkinter as tk
    except Exception as e:
        print("Error: tkinter no está disponible en este entorno.", e)
        sys.exit(1)

    # Importaciones tardías
    try:
        from gui import YahtzeeApp
    except Exception as e:
        print("Error al importar gui.py:", e)
        raise

    root = tk.Tk()
    app = YahtzeeApp(root, sims_default=SIMS_PER_MASK)
    root.mainloop()

if __name__ == "__main__":
    run_app()
