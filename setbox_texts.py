from setbox_helpers import *
from setbox_constants import *

PLAY_MODE_TOOLTIP = """
Wähle den Spielmodus für deine Runde. Neben dem offenen Spiel gibt es verschiedene 	
:fire: Duell-Modi. In den Duell-Modi treten Spieler gegeneinander an, die Zeiten werden gestoppt und schließlich ein Gewinner ermittelt.
- **Offenes Spiel**: Jeder Spieler spielt für sich allein. Aufgaben können frei gewählt werden.
- :fire:**Einzel-Duell**: Zwei oder mehr Spieler treten gegeneinander an. Spieler spielen die gleiche Anzahl an Aufgaben.
- :fire:**Paar-Duell**: Spieler werden in Paare aufgeteilt und treten gegeneinander an. Jedes Paar spielt die gleiche Anzahl an Aufgaben.
- :fire:**Team-Duell**: Spieler werden in zwei Teams aufgeteilt und treten gegeneinander an. Jedes Team spielt die gleiche Anzahl an Aufgaben."""

NUM_PUZZLE_TOOLTIP = """
Verfügbare Aufgaben im Spiel. 
- Nicht alle Aufgaben stehen in diesem Modus zur Verfügung. 
- Nicht jeder Spieler muss alle Aufgaben lösen. 
- Die Anzahl der Aufgaben gibt an, wie abwechslungsreich das Spiel wird. """

TOTAL_TASKS_TOOLTIP = """
Gesamtzahl der Aufgaben, die in dieser Runde gespielt werden. 
- In Duell-Modi kommt jeder Spieler mindestens einmal an die Reihe.
- Im Team-Duell spielt jedes Team die Hälfte der Aufgaben."""

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

def format_rankings(rankings_table: pd.DataFrame) -> list:
    rows = []
    for i, e in rankings_table.iterrows():
        if i == 0:
            rows.append({"Platz": f"🥇 {i+1}", "Spieler": e.iloc[1], "Gesamtzeit": format_time(e.iloc[2]), "Aufgaben": e.iloc[3]})
        elif i == 1:
            rows.append({"Platz": f"🥈 {i+1}", "Spieler": e.iloc[1], "Gesamtzeit": format_time(e.iloc[2]), "Aufgaben": e.iloc[3]})
        elif i == 2:
            rows.append({"Platz": f"🥉 {i+1}", "Spieler": e.iloc[1], "Gesamtzeit": format_time(e.iloc[2]), "Aufgaben": e.iloc[3]})
        else:
            rows.append({"Platz": f"{i+1}", "Spieler": e.iloc[1], "Gesamtzeit": format_time(e.iloc[2]), "Aufgaben": e.iloc[3]})
    return rows