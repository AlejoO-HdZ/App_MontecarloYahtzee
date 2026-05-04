# 🎲 Yahtzee Simulator GUI (Python-TKinter)

Aplicación en Python que simula partidas del juego Yahtzee con interfaz gráfica (Tkinter). Aplicando Metodo Montecarlo y Distribuciones uniformes.
Permite Simular partidas, ejecutar lotes de simulaciones y visualizar estadísticas con gráficos (Histogramas,Botplox, COnvergencias y Validaciones de metodo Montecarlo de 0-100000).

---

## 📖 Descripción

Este proyecto fue desarrollado como práctica académica.  
El objetivo es mostrar cómo se pueden simular partidas de Yahtzee, acumular resultados y analizar la convergencia de los Yahtzees que aparecen en las tiradas frente a los que los jugadores anotan en la hoja de puntuación y Demostrar el metodo montecarlo, la ocvergencias entre probabilidades y vlaoes matematicos teoricos y simulados , para permitir el analisis de los metodos estaocsticos y de distribucion uniforme discreta.

---

## 🚀 Instalación:

### Requisitos previos
- Python 3.x instalado en tu sistema.
- Librerías necesarias: `tkinter`, `matplotlib` `Numpy` `math` `typing` `colections`.

### Pasos
1. Clona este repositorio
2. Ejecuta "Juego Yathzee/main.py"
3. Simula partidas con boton: "Start partida" o crea Batch o lote de simulaciones con boton: "Batch N"

3. ## 🔄 Flujo del juego

- Inicio de partida: se inicializan jugadores 1 y 2 (simulados) y hoja de puntuación.
- Cada turno: el jugador lanza dados, conserva algunos y vuelve a lanzar hasta 3 veces.
- Selección de categoría: se anota autmaticamente la jugada en el  tabler ode puntuaciones con las categorias.
- Cambio de turno: pasa al siguiente jugador.
- Fin de partida: cuando todas las categorías están llenas, se suman los puntos y se declara el ganador.
- Batch: se pueden simular muchas partidas automáticamente para obtener estadísticas.
- Gráficos: se muestran curvas de convergencia y comparación de Yahtzees aparecidos vs anotados.
- Validacion: Se puede validar el metodo montecarlo con 1000,10000 y 100000 lanzamientos


4. ## 📊 Funcionalidades principales
- Simulación de partidas individuales: permite jugar una partida completa de Yahtzee con tiradas, selección de categorías y cálculo de puntuaciones.
- Batch de simulaciones: ejecuta múltiples partidas de forma automática, acumula estadísticas y muestra un resumen final con victorias, lanzamientos y categorías.
- Estadísticas detalladas: incluye conteo de Yahtzees aparecidos en las tiradas y Yahtzees anotados en tablero de puntuacion simulado, además de distribución de caras de los dados.
- Gráficos de análisis: genera curvas de convergencia y comparaciones visuales entre los Yahtzees aparecidos y los anotados, usando Matplotlib.
- Interfaz gráfica amigable: botones claros para ejecutar cada modo de simulación sin necesidad de usar la terminal.

5. ## 📂 Organización del código

- Modulo gui.py → Contiene la interfaz gráfica con Tkinter. Maneja los botones de Jugar, Batch y Convergencia, y coordina la ejecución de las simulaciones.
- Modulo Montecarlo → Aplica los metodos y reglas de metodo montecarlo.
- Modulo juegoStart.py → Implementa la lógica principal del juego Yahtzee: turnos, tiradas de dados, selección de categorías y cálculo de puntuaciones.
- Modulo main.py.py → Arranque de la app
- Modulo analysis.py → Funciones de análisis y graficado con Matplotlib. Se encarga de mostrar curvas de convergencia y comparaciones de Yahtzees aparecidos vs anotados.
- Modulo utils.py.py → Utilidades generales, ui_log Tkinter. timeit decorator medir tiempos y helpers para convertir GameState a dict (export).
- README.md → Documento de referencia del proyecto. Explica instalación, uso, flujo del juego y organización del código.

