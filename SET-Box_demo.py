import streamlit as st
from streamlit_gsheets import GSheetsConnection
import time
import json
import os
from datetime import datetime
import pandas as pd

# /c:/Users/Jakob/OneDrive/Programmieren/Anaconda/SET-Box/SET-Box_demo.py

# File to persist highscores
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

SCORES_COLS = ["player", "identifier", "puzzle", "time_seconds", "time_str", "timestamp", "duel_mode"]

st.set_page_config(page_title="SET-Box Timer", layout="centered")

def format_time(seconds: float) -> str:
    if seconds is None:
        return "00:00.00"
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds) % 60
    m = int(seconds) // 60
    # one digit after the decimal (tenths), rounded
    total_tenths = int(round(seconds * 10))
    m = total_tenths // 600
    s = (total_tenths // 10) % 60
    tenths = total_tenths % 10
    return f"{m:02d}:{s:02d}.{tenths}"

def _parse_time_seconds(t):
    # try numeric first, then mm:ss(.ms) style
    try:
        return float(t)
    except Exception:
        s = str(t or "").strip()
        if not s:
            return None
        if ":" in s:
            try:
                parts = s.split(":")
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            except Exception:
                return None
        try:
            return float(s)
        except Exception:
            return None

def load_local_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure structure is a dict mapping puzzle -> list
                if isinstance(data, dict):
                    return data
                # migrate old flat list to default puzzle key
                return {"default": data}
        except Exception:
            return {}
    return {}

def load_online_highscores(connection: GSheetsConnection, return_type: str = "dict"):
    try:
        df = conn.read()
    except Exception:
        st.error("Could not connect to Google Sheets for highscores. Falling back to local highscores.")
        load_local_highscores()

    if return_type == "df":
        df["Duel"] = df["Duel"].astype(bool, errors="ignore")
        return df

    rev_puzzle = {v: k for k, v in PUZZLE_NUMBERS.items()}
    hs_from_sheet = {}
    
    if df is not None and hasattr(df, "iterrows"):
        for _, row in df.iterrows():
            try:
                player = row.get("Player") if "Player" in row.index else row.get("player", "")
                identifier = row.get("Identifier") if "Identifier" in row.index else row.get("identifier", "")
                raw_time = row.get("Time") if "Time" in row.index else row.get("time", None)
                raw_puzzle = row.get("Puzzle") if "Puzzle" in row.index else row.get("puzzle", None)
                recorded = row.get("Recorded") if "Recorded" in row.index else row.get("recorded", "")
                duel_mode = row.get("Duel") if "Duel" in row.index else row.get("duel_mode", False)
    
                # parse puzzle number -> label
                try:
                    pnum = int(raw_puzzle)
                except Exception:
                    # maybe the sheet already contains the label
                    pnum = None
                puzzle_label = None
                if pnum is not None:
                    puzzle_label = rev_puzzle.get(pnum, str(pnum))
                else:
                    # use raw_puzzle as label if present
                    puzzle_label = str(raw_puzzle) if raw_puzzle is not None else None
    
                if not puzzle_label:
                    continue
                
                secs = _parse_time_seconds(raw_time)
                if secs is None:
                    continue
                
                player_display = str(player or "Anonymous")
    
                entry = {
                    "player": player_display,
                    "identifier": identifier,
                    "puzzle": puzzle_label,
                    "time_seconds": float(secs),
                    "time_str": format_time(float(secs)),
                    "timestamp": str(recorded),
                    "duel_mode": bool(duel_mode)
                }
                hs_from_sheet.setdefault(puzzle_label, []).append(entry)
            except Exception:
                # ignore malformed rows
                continue

    # sort and trim
    for k, v in hs_from_sheet.items():
        v.sort(key=lambda e: e["time_seconds"])
        hs_from_sheet[k] = v[:MAX_HIGHSCORES]

    return hs_from_sheet

def save_highscores(hs):
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(hs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def push_score_to_sheet(df: pd.DataFrame, connection: GSheetsConnection, sheet_read_df: pd.DataFrame, puzzle_mapper: dict) -> bool:
    """
    Append rows to the Google Sheet backing `connection`.
    Expects entry with keys: "player", "identifier", "puzzle", "time_seconds", "timestamp".
    Returns True on success, False on failure / no connection.
    """
    try:
        if connection is None:
            return False
        df.rename(columns={
            "player": "Player",
            "identifier": "Identifier",
            "puzzle": "Puzzle",
            "time_str": "Time",
            "timestamp": "Recorded",
            "duel_mode": "Duel"}, inplace=True)
        df.drop(columns=["time_seconds"], inplace=True, errors="ignore")
        df = df[["Player", "Identifier", "Time", "Puzzle", "Recorded", "Duel"]]
        df["Puzzle"] = df["Puzzle"].map(puzzle_mapper)

        df = pd.concat([sheet_read_df, df], ignore_index=True)
        with placeholder:
            st.info("Speichere Scores online...")
        connection.update(data=df)
        return True
    except Exception:
        return False

#Establish connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialize session state
if "running" not in st.session_state:
    st.session_state.running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "last_elapsed" not in st.session_state:
    st.session_state.last_elapsed = 0.0
if "highscores" not in st.session_state:
    st.session_state.highscores = load_online_highscores(conn)
if "session_scores" not in st.session_state:
    st.session_state.session_scores = pd.DataFrame(columns=SCORES_COLS)


### GUI Start
st.title("SET-Box Timer")

with st.expander("Aufgabenbeschreibung", expanded=False):
    st.pills("Aufgabe wählen", ["1 Inversion", "2 Schiebetür", "3 Falltür", "4 Ablage", "5 Schublade", "6 Guillotine", "7 Versteck"], key="puzzle_choice_video", default="1 Inversion", width="stretch")
    try:
        st.video(f"""{PUZZLE_NUMBERS[st.session_state.get("puzzle_choice_video")]}.mp4""")
    except:
        st.info("Video nicht gefunden.")

duel_mode = st.toggle("Aktiviere Duell-Modus (für 2 - 6 Spieler)", key="duel_mode", value=False)

if duel_mode:
    with st.expander("Duell-Modus Setup", expanded=True):
        st.slider("Anzahl Spieler", min_value=2, max_value=6, step=1, key="num_players", value=2)
        st.slider("Anzahl Aufgaben", min_value=1, max_value=6, step=1, key="num_puzzles", value=2)
        st.info("Nicht jeder Spieler muss alle Aufgaben lösen. Die Anzahl der Aufgaben gibt nur an, wie abwechslungsreich das Spiel wird.")
        maximum_games = st.session_state.num_players * st.session_state.num_puzzles
        st.slider("Gesamtzahl Aufgaben", min_value=st.session_state.num_players, max_value=maximum_games, step=st.session_state.num_players, key="total_tasks", value=st.session_state.num_players)
        st.info(f"Bei dieser Einstellung dauert die Runde etwa {st.session_state.total_tasks * 4} bis {st.session_state.total_tasks * 6} Minuten.")
        #if st.button("Spielernamen eingeben:"):
                
        st.button("Starte Duell")

with st.expander("Spieler Informationen", expanded=True):
    st.slider("Anzahl Spieler", min_value=1, max_value=10, step=1, key="num_players_simple", value=1)
    col1, col2 = st.columns(2)
    if st.session_state.num_players_simple:
        number_of_players = st.session_state.num_players_simple
    else:
        number_of_players = st.session_state.num_players
    with col1:
        for i in range(1, number_of_players + 1):
            st.text_input(f"Spieler {i} Namen eingeben:", key=f"username{i}")
    with col2:
        for i in range(1, number_of_players + 1):
            st.text_input(f"Spieler {i} Identifier (z.B. Matrikel, optional):", key=f"identifier{i}")

#st.text_input("Spieler Namen eingeben (optional):", key="username")
#st.text_input("Spieler Identifier (z.B. Matrikel, optional):", key="identifier")
player_dict = {}
for i in range(1, number_of_players + 1):
    player_dict[f"{st.session_state[f'username{i}']}"] = i
st.pills("Spieler wählen", player_dict.keys(), key="selected_player", width="stretch")
st.pills("Aufgabe wählen", ["1 Inversion", "2 Schiebetür", "3 Falltür", "4 Ablage", "5 Schublade", "6 Guillotine", "7 Versteck"], key="puzzle_choice", width="stretch")



if st.button("Start/Stop", width="stretch"):
    # Ensure puzzle selected
    puzzle = st.session_state.get("puzzle_choice") or ""
    current_player = st.session_state.get("selected_player") or ""
    if not puzzle:
        st.warning("Bitte ein Aufgabe auswählen, bevor der Timer gestartet wird.")
    elif not current_player:
        st.warning("Bitte einen Spieler auswählen, bevor der Timer gestartet wird.")
    else:
        username = current_player or "Anonymous"
        identifier = st.session_state[f"identifier{player_dict[username]}"] or 0
        # Toggle behavior
        if not st.session_state.running:
            # Start timer
            st.session_state.start_time = time.time()
            st.session_state.running = True
            st.session_state.last_elapsed = 0.0
        else:
            # Stop timer and record
            elapsed = time.time() - (st.session_state.start_time or time.time())
            st.session_state.last_elapsed = elapsed
            st.session_state.running = False
            st.session_state.start_time = None
            # Prepare entry with player and puzzle
            entry = {
                "player": username,
                "identifier": identifier,
                "puzzle": puzzle,
                "time_seconds": elapsed,
                "time_str": format_time(elapsed),
                "timestamp": datetime.now().isoformat() + "Z",
                "duel_mode": bool(duel_mode)
            }
            # Append to session scores
            st.session_state.session_scores = pd.concat([st.session_state.session_scores, pd.DataFrame([entry])], ignore_index=True)
            # Append into puzzle-specific list
            hs_dict = st.session_state.highscores
            if puzzle not in hs_dict or not isinstance(hs_dict[puzzle], list):
                hs_dict[puzzle] = []
            hs_dict[puzzle].append(entry)
            # sort ascending (fastest first) for this puzzle
            hs_dict[puzzle].sort(key=lambda e: e["time_seconds"])
            hs_dict[puzzle] = hs_dict[puzzle][:MAX_HIGHSCORES]
            st.session_state.highscores = hs_dict
            save_highscores(st.session_state.highscores)
        

# Display Timer
timer_placeholder = st.empty()
if st.session_state.running:
    # compute current elapsed and refresh app so the timer updates continuously
    elapsed = time.time() - st.session_state.start_time
    html = f'<div style="text-align:center;"><span style="font-weight:700; font-size:48px">{format_time(elapsed)}</span></div>'
    timer_placeholder.markdown(html, unsafe_allow_html=True)
    # short sleep to avoid a tight busy loop, then request a rerun to update UI
    time.sleep(0.1)
    st.rerun()
else:
    html = f'<div style="text-align:center;"><span style="font-weight:700; font-size:48px">{format_time(st.session_state.last_elapsed)}</span></div>'
    timer_placeholder.markdown(html, unsafe_allow_html=True)
    

# Highscore list
st.subheader("Highscores", width="stretch")
puzzle = st.session_state.get("puzzle_choice") or ""
if not puzzle:
    st.warning("Keine Aufgabe ausgewählt — Highscores sind pro Aufgabe. Bitte eine Aufgabe auswählen, um die zugehörigen Bestzeiten zu sehen.")
else:
    # Ensure highscores is a dict (migrate old flat list format or recover from corrupted state)
    hs = st.session_state.get("highscores", {})
    hs_for_puzzle = hs.get(puzzle, [])
    if hs_for_puzzle:
        rows = []
        for i, e in enumerate(hs_for_puzzle, start=1):
            rows.append({"Rang": i, "Spieler": e.get("player", "Anonymous"), "Zeit": e["time_str"], "Aufgezeichnet": e["timestamp"]})
        st.dataframe(rows, hide_index=True, width="stretch")
    else:
        st.info(f"No highscores yet for '{puzzle}'. Press Start/Stop to time something and record it.")

placeholder = st.empty()
if st.button("Scores online speichern", width="stretch"):
    # push all session scores to sheet
    if st.session_state.session_scores is not None and not st.session_state.session_scores.empty:
        old_scores = load_online_highscores(conn, "df")
        success = push_score_to_sheet(st.session_state.session_scores.copy(deep=True), connection=conn, sheet_read_df=old_scores, puzzle_mapper=PUZZLE_NUMBERS)
        if success:    
            #reset session scores after pushing
            st.session_state.session_scores = pd.DataFrame(columns=SCORES_COLS)
            with placeholder:
                st.success("Scores wurden online gespeichert.")
        else:
            with placeholder:
                st.error("Fehler beim Speichern der Scores online. Bitte später erneut versuchen.")
    else:
        with placeholder:
            st.info("Keine neuen Scores in dieser Sitzung zum Speichern.")
    
#st.session_state.session_scores
# expose function on session_state so it can be called from the UI code after recording an entry
#st.session_state["push_score_to_sheet"] = push_score_to_sheet(, connection=conn, sheet_read_df=df, puzzle_mapper=PUZZLE_NUMBERS)

