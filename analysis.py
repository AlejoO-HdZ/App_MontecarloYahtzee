"""
analysis.py

Funciones de análisis y visualización para la actividad Montecarlo Yahtzee.

Incluye:
- Estadística teórica para un dado justo (1..6).
- Funciones de graficado:
    * Histograma de caras con línea teórica y anotación de E, Var, σ.
    * Boxplot de puntajes por categoría.
    * Gráfico de convergencia (media acumulada).
- Función que devuelve la descripción probabilística
  junto con los resultados numéricos para mostrar en la GUI o en el informe.
"""

from collections import Counter
import math
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

# -------------------------------
# Estadística teórica para un dado justo
# -------------------------------
def theoretical_die_stats() -> Tuple[Dict[int, float], float, float, float]:
    """
    Devuelve la distribución teórica y estadísticas para un dado justo 1..6.
    Retorna:
      - probs: dict cara -> probabilidad
      - E: valor esperado
      - Var: varianza
      - sigma: desviación estándar
    """
    probs = {k: 1/6 for k in range(1,7)}
    # E[X] = (1+2+3+4+5+6)/6 = 3.5
    E = 3.5
    # E[X^2] = (1^2+...+6^2)/6 = 91/6
    EX2 = 91.0/6.0
    Var = EX2 - E*E  # 91/6 - 12.25 = 35/12
    sigma = math.sqrt(Var)
    return probs, E, Var, sigma

# -------------------------------
# Descripción probabilística exacta solicitada
# -------------------------------
def probabilistic_description_with_results() -> Tuple[List[str], str]:
    """
    Devuelve una lista de líneas con la descripción textual exacta solicitada,
    seguida de los resultados numéricos calculados para un dado justo (1..6).

    Las líneas devueltas contienen exactamente el texto pedido y el valor numérico:
      - Distribución Uniforme: Cada cara del dado tiene probabilidad P(X=k)
      - Valor Esperado: E[X] =
      - Varianza: Var(X)
      - Desviación Estándar: σ =
    """
    probs, E, Var, sigma = theoretical_die_stats()

    # Formateo numérico con precisión razonable para el informe
    E_str = f"{E:.6f}"
    Var_str = f"{Var:.6f}"
    sigma_str = f"{sigma:.6f}"
    p_str = "1/6 ≈ 0.1666667"

    lines = [
        f"Distribución Uniforme: Cada cara del dado tiene probabilidad P(X=k) = {p_str}",
        f"Valor Esperado: E[X] = {E_str}",
        f"Varianza: Var(X) = {Var_str}",
        f"Desviación Estándar: σ = {sigma_str}"
    ]
    block = "\n".join(lines)
    return lines, block

# -------------------------------
# Funciones de graficado
# -------------------------------
def plot_face_histogram(face_hist: Counter, show_theoretical: bool = True):
    """
    Histograma de frecuencias de caras (1..6) con línea teórica P=1/6.
    También muestra E, Var y sigma simulados y teóricos en la leyenda y en la figura.
    """
    faces = list(range(1,7))
    counts = [face_hist.get(f, 0) for f in faces]
    total = sum(counts)
    freqs = [c/total if total>0 else 0 for c in counts]

    probs_theo, E_theo, Var_theo, sigma_theo = theoretical_die_stats()

    # Estadísticas simuladas
    observations = []
    for f,c in zip(faces, counts):
        observations.extend([f]*c)
    if observations:
        E_sim = sum(observations)/len(observations)
        Var_sim = sum((x - E_sim)**2 for x in observations)/len(observations)
        sigma_sim = math.sqrt(Var_sim)
    else:
        E_sim = Var_sim = sigma_sim = 0.0

    plt.figure(figsize=(7,4))
    plt.bar(faces, freqs, color="#1F6FEB", alpha=0.85, label="Frecuencia simulada (relativa)")
    if show_theoretical:
        theo_vals = [probs_theo[f] for f in faces]
        plt.plot(faces, theo_vals, marker='o', color="#FF8A00", linestyle='--', label="Prob. teórica (1/6)")

    plt.xlabel("Cara")
    plt.ylabel("Frecuencia relativa")
    plt.title("Histograma de caras (simulado vs teórico)")

    # Anotar estadísticas simuladas vs teóricas
    stats_text = (f"E_sim={E_sim:.6f}, Var_sim={Var_sim:.6f}, σ_sim={sigma_sim:.6f}\n"
                  f"E_theo={E_theo:.6f}, Var_theo={Var_theo:.6f}, σ_theo={sigma_theo:.6f}")
    plt.gca().text(0.02, 0.95, stats_text, transform=plt.gca().transAxes,
                   fontsize=9, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))

    # Añadir la descripción probabilística exacta en la figura (texto solicitado)
    try:
        lines, _ = probabilistic_description_with_results()
        text_block = "\n".join(lines)
        plt.gcf().text(0.02, 0.02, text_block, fontsize=9, va='bottom', bbox=dict(facecolor='white', alpha=0.8))
    except Exception:
        pass

    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_scores_by_category(scores_by_category: Dict[str, List[int]]):
    """Boxplot por categoría para visualizar la distribución de puntajes."""
    cats = list(scores_by_category.keys())
    data = [scores_by_category[c] if scores_by_category[c] else [0] for c in cats]
    plt.figure(figsize=(10,5))
    plt.boxplot(data, labels=cats, showfliers=False, patch_artist=True,
                boxprops=dict(facecolor="#1F6FEB", color="#0F1724"))
    plt.xticks(rotation=45)
    plt.title("Distribución de puntajes por categoría")
    plt.tight_layout()
    plt.show()

def plot_convergence(metric_series: List[float], theoretical: float = None, label: str = "Media acumulada"):
    """
    Grafica la media acumulada de una serie de métricas (por ejemplo puntaje total por partida)
    para mostrar convergencia hacia un valor teórico (si se proporciona).
    """
    try:
        import numpy as np
    except Exception:
        raise RuntimeError("numpy es requerido para plot_convergence. Instala numpy e inténtalo de nuevo.")

    arr = np.array(metric_series, dtype=float)
    cum_mean = np.cumsum(arr) / (np.arange(len(arr)) + 1)
    plt.figure(figsize=(8,4))
    plt.plot(cum_mean, color="#1F6FEB", label=label)
    if theoretical is not None:
        plt.hlines(theoretical, 0, len(arr)-1, colors="#FF8A00", linestyles='--', label="Valor teórico")
    plt.xlabel("Número de partidas")
    plt.ylabel("Media acumulada")
    plt.title("Convergencia de la media (Ley de los grandes números)")
    plt.legend()
    plt.tight_layout()
    plt.show()


