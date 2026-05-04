"""
utils.py

Utilidades generales:
- ui_log: logger thread-safe para la interfaz Tkinter.
- timeit decorator para medir tiempos.
- helpers para convertir GameState a dict (export).
"""

import time
from functools import wraps
from typing import Callable, Any, Dict

def timeit(func: Callable) -> Callable:
    """Decorador simple para medir tiempo de ejecución de funciones."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.time()
        res = func(*args, **kwargs)
        t1 = time.time()
        print(f"[timeit] {func.__name__} ejecutado en {t1-t0:.3f}s")
        return res
    return wrapper

def game_state_to_dict(state) -> Dict:
    """Convierte un GameState a un dict serializable (resumen)."""
    players = []
    for p in state.players:
        players.append({
            "name": p.name,
            "total": p.total,
            "scores": p.scores
        })
    return {
        "players": players,
        "face_hist": dict(state.stats.face_hist),
        "category_hist": dict(state.stats.category_hist),
        "scores_by_category": {k:list(v) for k,v in state.stats.scores_by_category.items()}
    }

# Logger thread-safe para UI: la GUI define su propia función; aquí dejamos un fallback
def ui_log(logger_func, text: str):
    """Llama a logger_func(text) si está disponible, sino imprime en consola."""
    if logger_func:
        try:
            logger_func(text)
        except Exception:
            print(text)
    else:
        print(text)
