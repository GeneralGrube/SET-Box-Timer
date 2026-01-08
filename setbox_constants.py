HIGHSCORE_FILE = "highscores.json"
MAX_HIGHSCORES = 20  # keep top N

PUZZLE_NUMBERS = {
    "1 Inversion": 1,
    "2 Schiebetür": 2,
    "3 Falltür": 3,
    "4 Ablage": 4,
    "5 Schublade": 5,
    "6 Guillotine": 6,
    "7 Versteck": 7,        
}

INV_PUZZLE_NUMBERS = {v: k for k, v in PUZZLE_NUMBERS.items()}

SCORES_COLS = ["player", "semester", "puzzle", "time_seconds", "time_str", "timestamp", "duel_mode"]

SHEET_COLS = ["Player", "Semester", "StudyID", "Time", "Puzzle", "Recorded", "Mode"]

PLAY_MODES = {
    "Offenes Spiel": "open",
    "Duell-Modus": "single_duel",
    #"Paar-Duell": "pair_duel",
    "Team-Duell": "team_duel",
}

MODE_SETTINGS = {
    "open": (1, 10, 1), #min_players, max_players, player_step_size
    "pair_duel" : (4, 8, 2),
    "team_duel" : (4, 8, 2),
    "single_duel": (2, 8, 1)
}

PUZZLES = ["1 Inversion", "2 Schiebetür", "3 Falltür", "4 Ablage", "5 Schublade", "6 Guillotine", "7 Versteck"]

STDRED = "firebrick"
