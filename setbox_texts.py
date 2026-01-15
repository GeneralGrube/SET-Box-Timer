from setbox_helpers import *
from setbox_constants import *
import json
import os

class Localizer:
    def __init__(self, language_code):
        self.language_code = language_code
        self.translations = self._load_translations()

    def _load_translations(self):
        file_path = f"translations/{self.language_code}.json"
        
        # Fallback to German if the requested language file doesn't exist
        if not os.path.exists(file_path):
            file_path = "translations/de.json"
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def translate(self, key, **kwargs):
        # Get the string, fallback to the key itself if not found
        text = self.translations.get(key, key)
        
        # Handle datatypes that are not strings
        if not isinstance(text, str):
            return text
        # Handle dynamic variables like {name}
        return text.format(**kwargs)

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