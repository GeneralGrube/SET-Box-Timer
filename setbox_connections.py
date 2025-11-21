import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import os
import json

from setbox_constants import *
from setbox_helpers import *

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

def load_online_raw_highscores(conn: GSheetsConnection):
    try:
        df = conn.read()
    except Exception:
        st.error("Could not connect to Google Sheets for highscores. Falling back to local highscores.")
        load_local_highscores()
    return df

def load_online_for_update(conn: GSheetsConnection):
    df = load_online_raw_highscores(conn)
    hs_list = []
    
    if df is not None and hasattr(df, "iterrows"):
        for _, row in df.iterrows():
            try:
                player = row.get("Player") if "Player" in row.index else row.get("player", "")
                semester = row.get("Semester") if "Semester" in row.index else row.get("semester", "")
                study_id = row.get("StudyID") if "StudyID" in row.index else row.get("study_id", "")
                raw_time = row.get("Time") if "Time" in row.index else row.get("time", None)
                raw_puzzle = row.get("Puzzle") if "Puzzle" in row.index else row.get("puzzle", None)
                recorded = row.get("Recorded") if "Recorded" in row.index else row.get("recorded", "")
                mode = row.get("Mode") if "Mode" in row.index else row.get("mode", False)

                entry = {
                        "Player": player,
                        "Semester": semester,
                        "StudyID": study_id,
                        "Puzzle": raw_puzzle,
                        "Time": raw_time,
                        "Recorded": str(recorded),
                        "Mode": str(mode)
                    }
                hs_list.append(entry)
            except Exception:
                # ignore malformed rows
                continue
    
    return pd.DataFrame(hs_list)  

def load_online_highscores(conn: GSheetsConnection, sort_trim: bool = True):
    df = load_online_raw_highscores(conn)

    rev_puzzle = {v: k for k, v in PUZZLE_NUMBERS.items()}
    hs_from_sheet = {}
    
    if df is not None and hasattr(df, "iterrows"):
        for _, row in df.iterrows():
            try:
                player = row.get("Player") if "Player" in row.index else row.get("player", "")
                semester = row.get("Semester") if "Semester" in row.index else row.get("semester", "")
                study_id = row.get("StudyID") if "StudyID" in row.index else row.get("study_id", "")
                raw_time = row.get("Time") if "Time" in row.index else row.get("time", None)
                raw_puzzle = row.get("Puzzle") if "Puzzle" in row.index else row.get("puzzle", None)
                recorded = row.get("Recorded") if "Recorded" in row.index else row.get("recorded", "")
                mode = row.get("Mode") if "Mode" in row.index else row.get("mode", False)
    
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
                    "semester": semester,
                    "study_id": study_id,
                    "puzzle": puzzle_label,
                    "time_seconds": float(secs),
                    "time_str": format_time(float(secs)),
                    "timestamp": str(recorded),
                    "mode": str(mode)
                }
                hs_from_sheet.setdefault(puzzle_label, []).append(entry)
                
            except Exception:
                # ignore malformed rows
                continue

    # sort and trim
    if sort_trim:
        for k, v in hs_from_sheet.items():
            v.sort(key=lambda e: e["time_seconds"])
            hs_from_sheet[k] = v[:MAX_HIGHSCORES]

    return hs_from_sheet

def push_score_to_sheet(df: pd.DataFrame, connection: GSheetsConnection, sheet_read_df: pd.DataFrame, puzzle_mapper: dict) -> bool:
    """
    Append rows to the Google Sheet backing `connection`.
    Expects entry with keys: "player", "identifier", "puzzle", "time_seconds", "timestamp".
    Returns True on success, False on failure / no connection.
    """
    df = update_session_scores_studyID(df, st.session_state.get("player_dict", {}))
    #try:
    if connection is None:
        return False
    df.rename(columns={
        "player": "Player",
        "semester": "Semester",
        "study_id": "StudyID",
        "puzzle": "Puzzle",
        "time_str": "Time",
        "timestamp": "Recorded",
        "mode": "Mode"}, inplace=True)
    df.drop(columns=["time_seconds"], inplace=True, errors="ignore")
    df = df[SHEET_COLS]
    df["Puzzle"] = df["Puzzle"].map(puzzle_mapper)
    df = pd.concat([sheet_read_df, df], ignore_index=True)
    connection.update(data=df)
    return True
    #except Exception:
    #    print(Exception)
    #    return False