"""
juegoStart.py

Lógica del juego Yahtzee (2 jugadores) y estructuras de estado.
Incluye:
- Generación de dados y utilidades (roll_single_die, roll_dice, has_sequence).
- Reglas de puntuación (score_hand, best_category_score).
- Clases de estado: PlayerState, GameStats, GameState.
- Flujo de juego: play_one_turn, play_game (sin prints; acepta logger opcional).
"""
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
# -------------------------------
# Constantes de categorías
# -------------------------------
CATEGORIES_ORDER = [
    "ones","twos","threes","fours","fives","sixes",
    "threeOfKind","fourOfKind","fullHouse","smallStraight",
    "largeStraight","yahtzee","chance"
]
# -------------------------------
# Utilidades de dados
# -------------------------------
def roll_single_die() -> int:
    """Devuelve un entero uniforme en [1,6]."""
    return random.randint(1, 6)

def roll_dice(values: List[int], locked: List[bool]) -> None:
    """Lanza dados no bloqueados, actualizando 'values' in place."""
    for i, is_locked in enumerate(locked):
        if not is_locked:
            values[i] = roll_single_die()

def has_sequence(values: List[int], needed_len: int) -> bool:
    """¿Existe una secuencia consecutiva de longitud 'needed_len'? (ignora duplicados)."""
    uniq = sorted(set(values))
    if not uniq:
        return False
    longest = curr = 1
    for i in range(1, len(uniq)):
        if uniq[i] == uniq[i-1] + 1:
            curr += 1
            longest = max(longest, curr)
        else:
            curr = 1
    return longest >= needed_len

# -------------------------------
# Puntuación
# -------------------------------
def score_hand(category: str, dice: List[int]) -> int:
    """Calcula la puntuación de una mano para una categoría dada."""
    counts = Counter(dice)
    freqs = list(counts.values())
    total = sum(dice)
    if category in ["ones","twos","threes","fours","fives","sixes"]:
        num = {"ones":1, "twos":2, "threes":3, "fours":4, "fives":5, "sixes":6}[category]
        return counts.get(num, 0) * num
    if category == "threeOfKind":
        return total if any(f >= 3 for f in freqs) else 0
    if category == "fourOfKind":
        return total if any(f >= 4 for f in freqs) else 0
    if category == "fullHouse":
        return 25 if (2 in freqs and 3 in freqs) else 0
    if category == "smallStraight":
        return 30 if has_sequence(dice, 4) else 0
    if category == "largeStraight":
        return 40 if has_sequence(dice, 5) else 0
    if category == "yahtzee":
        return 50 if 5 in freqs else 0
    if category == "chance":
        return total
    return 0

def best_category_score(dice: List[int], available: List[str]) -> Tuple[str, int]:
    """Devuelve (mejor_categoria, puntuación) para los dados dados."""
    best_cat, best = None, -1
    for cat in available:
        sc = score_hand(cat, dice)
        if sc > best:
            best = sc
            best_cat = cat
    return best_cat, best

# -------------------------------
# Estructuras de juego
# -------------------------------
@dataclass
class PlayerState:
    name: str
    scores: Dict[str, Optional[int]] = field(default_factory=lambda: {c: None for c in CATEGORIES_ORDER})
    total: int = 0

    def available_categories(self) -> List[str]:
        return [c for c,v in self.scores.items() if v is None]

    def set_score(self, category: str, points: int) -> None:
        self.scores[category] = points
        self.total = sum(v for v in self.scores.values() if v is not None)

@dataclass
class GameStats:
    total_rolls: int = 0
    face_hist: Counter = field(default_factory=Counter)
    category_hist: Counter = field(default_factory=Counter)
    scores_by_category: Dict[str, List[int]] = field(default_factory=lambda: defaultdict(list))

    def update_from_roll(self, values: List[int]) -> None:
        self.total_rolls += len(values)
        self.face_hist.update(values)

    def record_category(self, category: str, score: int) -> None:
        self.category_hist[category] += 1
        self.scores_by_category[category].append(score)

@dataclass
class GameState:
    players: List[PlayerState]
    current_player_idx: int = 0
    turn_in_round: int = 0  # 0..12 (13 turnos)
    dice_values: List[int] = field(default_factory=lambda: [0]*5)
    locked: List[bool] = field(default_factory=lambda: [False]*5)
    rolls_left: int = 3
    stats: GameStats = field(default_factory=GameStats)

    def reset_turn(self):
        self.dice_values = [0]*5
        self.locked = [False]*5
        self.rolls_left = 3

    @property
    def current_player(self) -> PlayerState:
        return self.players[self.current_player_idx]

    def advance_player(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        if self.current_player_idx == 0:
            self.turn_in_round += 1

# -------------------------------
# Flujo del juego (usa montecarlo.choose_keep_mask_montecarlo)
# -------------------------------
from montecarlo import choose_keep_mask_montecarlo

def play_one_turn(state: GameState, verbose: bool = True, logger=None, sims_per_mask: int = None):
    """
    Un turno completo para el jugador actual: hasta 3 tiradas + elección de categoría.
    - logger: función opcional para registrar texto (UI).
    - sims_per_mask: si se pasa, se transmite a la función Montecarlo.
    """
    player = state.current_player
    state.reset_turn()

    # Tirada inicial
    roll_dice(state.dice_values, state.locked)
    state.stats.update_from_roll(state.dice_values)
    state.rolls_left -= 1
    if verbose and logger:
        logger(f"\n{player.name} — Tirada 1: {state.dice_values}")

    # Hasta 2 rerolls con estrategia MC
    while state.rolls_left > 0:
        keep_mask = choose_keep_mask_montecarlo(
            state.dice_values, state.rolls_left, player.available_categories(),
            sims_per_mask=sims_per_mask
        )

        # Si la máscara "keep_mask" implica mantener todo tal cual (keep 5), plantarse:
        if all(keep_mask):
            if verbose and logger:
                logger(f"{player.name} decide plantarse con: {state.dice_values}")
            break

        # Bloquear según la máscara
        state.locked = keep_mask[:]
        # Reroll
        roll_dice(state.dice_values, state.locked)
        state.stats.update_from_roll(state.dice_values)
        state.rolls_left -= 1
        if verbose and logger:
            tirada_num = 3 - state.rolls_left
            logger(f"{player.name} — Tirada {tirada_num}: {state.dice_values} | keep: {keep_mask}")

    # Elegir mejor categoría disponible para la mano final
    cat, sc = best_category_score(state.dice_values, player.available_categories())
    player.set_score(cat, sc)
    state.stats.record_category(cat, sc)
    if verbose and logger:
        logger(f"→ {player.name} elige categoría '{cat}' y anota {sc} puntos. Total = {player.total}")

def play_game(verbose_each_turn: bool = True, logger=None, sims_per_mask: int = None) -> GameState:
    """
    Juega una partida completa entre 2 jugadores usando la estrategia Montecarlo.
    Devuelve el estado final del juego.
    """
    players = [PlayerState("Jugador 1"), PlayerState("Jugador 2")]
    state = GameState(players=players)

    # 13 turnos por jugador
    total_rounds = 13
    for r in range(total_rounds):
        for _p in range(len(players)):
            if verbose_each_turn and logger:
                logger(f"\n===== Ronda {r+1}/13 — Turno de {state.current_player.name} =====")
            play_one_turn(state, verbose=verbose_each_turn, logger=logger, sims_per_mask=sims_per_mask)
            state.advance_player()

    return state
