import streamlit as st
import time
import json
import os
from datetime import datetime

# /c:/Users/Jakob/OneDrive/Programmieren/Anaconda/SET-Box/SET-Box_demo.py

# File to persist highscores
HIGHSCORE_FILE = "highscores.json"
MAX_HIGHSCORES = 20  # keep top N

st.set_page_config(page_title="SET-Box Timer", layout="centered")

def format_time(seconds: float) -> str:
    if seconds is None:
        return "00:00.00"
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds) % 60
    m = int(seconds) // 60
    return f"{m:02d}:{s:02d}.{ms:02d}"

def load_highscores():
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

def save_highscores(hs):
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(hs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# Initialize session state
if "running" not in st.session_state:
    st.session_state.running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "last_elapsed" not in st.session_state:
    st.session_state.last_elapsed = 0.0
if "highscores" not in st.session_state:
    st.session_state.highscores = load_highscores()

puzzle_numbers = {
    "1 Inversion": 1,
    "2 Schiebetür": 2,
    "3 Falltür": 3,
    "4 Ablage": 4,
    "5 Schublade": 5,
    "6 Guillotine": 6,
    "7 Versteck": 7,        
}

st.title("SET-Box Timer")

with st.expander("Aufgabenbeschreibung", expanded=False):
    st.pills("Rätsel wählen", ["1 Inversion", "2 Schiebetür", "3 Falltür", "4 Ablage", "5 Schublade", "6 Guillotine", "7 Versteck"], key="puzzle_choice_video", default="1 Inversion", width="stretch")
    try:
        st.video(f"{puzzle_numbers[st.session_state.get("puzzle_choice_video")]}.mp4")
    except:
        st.info("Video nicht gefunden.")

duel_mode = st.toggle("Aktiviere Duell-Modus (für 2 - 6 Spieler)", key="duel_mode", value=False)

if duel_mode:
    st.info("Im Duell-Modus werden die Zeiten für bis zu 6 Spieler erfasst. Jeder Spieler kann seinen Namen eingeben, und die Zeiten werden getrennt aufgezeichnet.")
    st.text_input("Spieler 1 Namen eingeben:", key="username1")
    st.text_input("Spieler 2 Namen eingeben:", key="username2")
    st.text_input("Spieler 3 Namen eingeben:", key="username3")
    st.text_input("Spieler 4 Namen eingeben:", key="username4")
    st.text_input("Spieler 5 Namen eingeben:", key="username5")
    st.text_input("Spieler 6 Namen eingeben:", key="username6")
    st.warning("Duell-Modus bisher nicht implementiert.")

st.text_input("Spieler Namen eingeben (optional):", key="username")
st.pills("Rätsel wählen", ["1 Inversion", "2 Schiebetür", "3 Falltür", "4 Ablage", "5 Schublade", "6 Guillotine", "7 Versteck"], key="puzzle_choice", width="stretch")



if st.button("Start/Stop", use_container_width=True):
    # Ensure puzzle selected
    puzzle = st.session_state.get("puzzle_choice") or ""
    if not puzzle:
        st.warning("Bitte ein Rätsel auswählen, bevor der Timer gestartet wird.")
    else:
        username = st.session_state.get("username") or "Anonymous"
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
                "puzzle": puzzle,
                "time_seconds": elapsed,
                "time_str": format_time(elapsed),
                "timestamp": datetime.now().isoformat() + "Z",
            }
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
    st.warning("Kein Rätsel ausgewählt — Highscores sind pro Rätsel. Bitte ein Rätsel auswählen, um die zugehörigen Bestzeiten zu sehen.")
else:
    # Ensure highscores is a dict (migrate old flat list format or recover from corrupted state)
    hs = st.session_state.get("highscores", {})
    if not isinstance(hs, dict):
        if isinstance(hs, list):
            # migrate legacy flat list into a default puzzle key
            hs = {"default": hs}
        else:
            # fallback to an empty mapping
            hs = {}
        st.session_state.highscores = hs

    hs_for_puzzle = hs.get(puzzle, [])
    if hs_for_puzzle:
        rows = []
        for i, e in enumerate(hs_for_puzzle, start=1):
            rows.append({"Rank": i, "Player": e.get("player", "Anonymous"), "Time": e["time_str"], "Recorded (UTC)": e["timestamp"]})
        st.table(rows)
    else:
        st.info(f"No highscores yet for '{puzzle}'. Press Start/Stop to time something and record it.")

if st.button("Reset Highscores", use_container_width=True):
    # Reset only the currently selected puzzle's highscores if a puzzle selected,
    # otherwise reset all.
    puzzle = st.session_state.get("puzzle_choice") or ""
    if puzzle:
        st.session_state.highscores[puzzle] = []
    else:
        st.session_state.highscores = {}
    save_highscores(st.session_state.highscores)