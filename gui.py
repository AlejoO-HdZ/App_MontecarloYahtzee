"""
gui.py

Interfaz Tkinter para controlar la simulación Yahtzee Montecarlo.

Actualizaciones en esta versión:
- Reordené botones: Start, Histograma, Torta categorías, Boxplot, Convergencia, Batch (verde), Descripción Probabilística (naranja tenue al final).
- El gráfico de torta (pie) se actualiza correctamente con los datos de la última partida o del batch agregado (usa category_hist o deriva de scores_by_category).
- Botón Batch colocado junto a Convergencia; botón Descripción Probabilística al final con estilo naranja ("Warning.TButton").
- tablero de puntuaciones en cuadrícula y estadísticas finales con porcentajes y explicación breve.
- Importaciones tardías y manejo de dependencias con mensajes claros.
"""