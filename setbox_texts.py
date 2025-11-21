from setbox_helpers import *
from setbox_constants import *

PLAY_MODE_TOOLTIP = """
Wähle den Spielmodus für deine Runde. Neben dem offenen Spiel gibt es verschiedene 	
:fire: Duell-Modi. In den Duell-Modi treten Spieler gegeneinander an, die Zeiten werden gestoppt und schließlich ein Gewinner ermittelt.
- **Offenes Spiel**: Jeder Spieler spielt für sich allein. Aufgaben können frei gewählt werden.
- :fire:**Einzel-Duell**: Zwei oder mehr Spieler treten gegeneinander an. Spieler spielen die gleiche Anzahl an Aufgaben.
- :fire:**Paar-Duell**: Spieler werden in Paare aufgeteilt und treten gegeneinander an. Jedes Paar spielt die gleiche Anzahl an Aufgaben.
- :fire:**Team-Duell**: Spieler werden in zwei Teams aufgeteilt und treten gegeneinander an. Jedes Team spielt die gleiche Anzahl an Aufgaben."""

NUM_PUZZLE_TOOLTIP = "Nicht jeder Spieler muss alle Aufgaben lösen. Die Anzahl der Aufgaben gibt nur an, wie abwechslungsreich das Spiel wird."

def puzzle_player_str(puzzle:str, player:str, team:str|None) -> str:
    puzzle = html_formatter(puzzle, 24, color=STDRED, span_only=True)
    player = html_formatter(player, 24, color=STDRED, span_only=True)
    if team:
        team = html_formatter(team, 24, color=STDRED, span_only=True)
        string = f"""Aufgabe: {puzzle}<br>Team:  {team}<br>Spieler:  {player}"""
    else:
        string = f"""Aufgabe: {puzzle}<br>Spieler:  {player}"""
    return string

def progress_text(counter: int, max_puzzles: int) -> str:
    return f"Runde {counter + 1} von {max_puzzles}"