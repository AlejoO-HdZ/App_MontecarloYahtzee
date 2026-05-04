"""
montecarlo.py

Estrategia Montecarlo (1-step lookahead) para decidir qué dados mantener.
Contiene:
- all_keep_masks(): genera las 32 máscaras de bloqueo.
- simulate_expected_value_after_keeps(): estima EV por Montecarlo.
- choose_keep_mask_montecarlo(): selecciona la máscara con mayor EV.
Notas:
- Mantiene la aproximación 1-step (no reevalúa máscaras durante los rerolls).
- Convención de rolls_remaining:(se resta 1 internamente).
"""

from typing import List
from collections import Counter
from juegoStart import best_category_score
from juegoStart import roll_single_die
from juegoStart import roll_dice  # no usado aquí pero disponible
import random

# -------------------------------
# Generación de máscaras
# -------------------------------
def all_keep_masks() -> List[List[bool]]:
    """Genera las 32 máscaras posibles de bloqueo para 5 dados."""
    masks = []
    for m in range(32):  # 0..31
        mask = [(m >> i) & 1 == 1 for i in range(5)]
        masks.append(mask)
    return masks

# -------------------------------
# Simulación EV
# -------------------------------
def simulate_expected_value_after_keeps(
        current_values: List[int],
        keep_mask: List[bool],
        rolls_remaining: int,
        available_categories: List[str],
        sims: int
) -> float:
    """
    Estima el valor esperado de la mejor categoría si:
    - conservas (keep_mask) algunos dados ahora,
    - y después solo rerolléas los no conservados el número de veces restante,
    - sin volver a cambiar la máscara (aprox. Montecarlo de 1 paso).
    """
    if rolls_remaining <= 0:
        _, sc = best_category_score(current_values, available_categories)
        return float(sc)

    kept = [v if keep_mask[i] else None for i, v in enumerate(current_values)]
    unlocked_idx = [i for i,b in enumerate(keep_mask) if not b]

    total_score = 0.0
    for _ in range(sims):
        # Copia de valores
        vals = kept[:]
        # Rerolls: tirar los no conservados 'rolls_remaining' veces, quedándose con la última
        temp = current_values[:]  # por si keep None
        for _r in range(rolls_remaining):
            for i in unlocked_idx:
                temp[i] = roll_single_die()
        # Construir resultado final
        for i in range(5):
            vals[i] = vals[i] if vals[i] is not None else temp[i]

        # Mejor categoría al final
        _, sc = best_category_score(vals, available_categories)
        total_score += sc

    return total_score / sims if sims > 0 else 0.0

def choose_keep_mask_montecarlo(
        current_values: List[int],
        rolls_remaining: int,
        available_categories: List[str],
        sims_per_mask: int = 300
) -> List[bool]:
    """
    Elige la máscara de bloqueo que maximiza el valor esperado estimado al final del turno.
    Nota: aproximación de 1 paso (no recalcula bloqueos tras la siguiente tirada durante la simulación).
    """
    best_mask = None
    best_ev = -1.0
    for mask in all_keep_masks():
        # Se mantiene la convención de rolls_remaining tal como en el código base.
        ev = simulate_expected_value_after_keeps(
            current_values, mask, rolls_remaining - 1, available_categories, sims_per_mask
        )
        if ev > best_ev:
            best_ev = ev
            best_mask = mask
    return best_mask
