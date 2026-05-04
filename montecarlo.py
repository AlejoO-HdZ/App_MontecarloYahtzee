"""
montecarlo.py
Estrategia Montecarlo (1-step lookahead) para decidir qué dados mantener.
Contiene:
- all_keep_masks(): genera las 32 máscaras de bloqueo.
- simulate_expected_value_after_keeps(): estima EV por Montecarlo.
- choose_keep_mask_montecarlo(): selecciona la máscara con mayor EV.

Notas:
- Mantiene la aproximación 1-step (no reevalúa máscaras durante los rerolls).
"""