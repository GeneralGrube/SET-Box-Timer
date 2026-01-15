import streamlit as st
from streamlit_gsheets import GSheetsConnection
import time
import json
import os
from datetime import datetime
import pandas as pd

from setbox_texts import *
from setbox_mechanics import *
print("Checkpoint reached: start of setbox_main.py")
#Establish connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
localizer = Localizer("de")
initialize_session_state(conn, localizer)


from setbox_constants import *
from setbox_dialogs import *

# /c:/Users/Jakob/OneDrive/Programmieren/Anaconda/SET-Box/SET-Box_demo.py

st.set_page_config(page_title="SET-Box Game Timer", layout="centered")

#def save_highscores(hs):
#    try:
#        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
#            json.dump(hs, f, ensure_ascii=False, indent=2)
#    except Exception:
#        pass



def increment_game_counter():
    # check if time was recorded at all
    if st.session_state.last_elapsed == 0.0:
        forgot_record_dialog()
    else:
        if st.session_state.game_counter < len(st.session_state.puzzle_sequence):
            st.session_state.game_counter += 1
            st.session_state.last_elapsed = 0.0

@st.fragment(run_every=st.session_state.run_timer_interval)
def run_timer(ph):
    elapsed = time.time() - st.session_state.start_time
    ph.markdown(html_formatter(format_time(elapsed)), unsafe_allow_html=True)
    
print("Checkpoint reached: startstop")    
def startstop():
    st.session_state.superspeed = False
    play_mode = st.session_state.play_mode
    
    if play_mode == "open":
        st.session_state.error_msg = ""
        # Ensure puzzle selected
        try:
            puzzle = st.session_state.get("puzzle_choice") or ""
            st.session_state.current_puzzle = puzzle
        except:
            st.session_state.error_msg = "Bitte einen Spieler auswählen, bevor der Timer gestartet wird."
            return
        try:
            current_player = st.session_state.inv_player_dict[st.session_state.get("selected_player")]
        except:
            st.session_state.error_msg = "Bitte einen Spieler auswählen, bevor der Timer gestartet wird."
            return

        username = st.session_state.player_dict[current_player][0] or "Anonymous"
        semester = st.session_state.player_dict[current_player][1] or 0
    elif play_mode == "single_duel":
        puzzle = INV_PUZZLE_NUMBERS[st.session_state.puzzle_sequence[st.session_state.game_counter][1]]
        username = st.session_state.player_dict[st.session_state.puzzle_sequence[st.session_state.game_counter][0]][0]
        semester = st.session_state.player_dict[st.session_state.puzzle_sequence[st.session_state.game_counter][0]][1]
    elif play_mode == "team_duel":
        puzzle = INV_PUZZLE_NUMBERS[st.session_state.puzzle_sequence[st.session_state.game_counter][1]]
        username = st.session_state.player_dict[st.session_state.puzzle_sequence[st.session_state.game_counter][0]][0]
        semester = st.session_state.player_dict[st.session_state.puzzle_sequence[st.session_state.game_counter][0]][1]

    # Toggle behavior
    if not st.session_state.running:
        # Start timer
        st.session_state.start_time = time.time()
        st.session_state.running = True
        st.session_state.last_elapsed = 0.0
        st.session_state.run_timer_interval = 0.1
    else:
        # Stop timer and record
        elapsed = time.time() - (st.session_state.start_time or time.time())
        
        st.session_state.last_elapsed = elapsed
        st.session_state.running = False
        st.session_state.start_time = None
        st.session_state.run_timer_interval = None
        
        # Prepare entry with player and puzzle
        entry = {
            "player": username,
            "semester": semester,
            "puzzle": puzzle,
            "time_seconds": elapsed,
            "time_str": format_time(elapsed),
            "timestamp": datetime.now().isoformat() + "Z",
            "mode": play_mode
        }
        st.session_state.current_entry = entry
        st.session_state.score_pending_flag = True

### GUI Start
print("Checkpoint reached: GUI Start")
st.title("SET-Box Game Timer")

st.button("Neues Spiel beginnen...", key="new_game", on_click=play_mode_select_dialog, width="stretch")

#Setup flow control
if st.session_state.get("session_startup", False):
    st.session_state.session_startup = False
    session_startup()
if st.session_state.get("mode_setup_dialog_flag", False):
    st.session_state.mode_setup_dialog_flag = False
    reset_game()
    settings_dialog()
if st.session_state.get("player_info_dialog_flag", False):
    st.session_state.player_info_dialog_flag = False
    player_dialog()
if st.session_state.get("team_duel_dialog_flag", False):
    st.session_state.team_duel_dialog_flag = False
    team_dialog()

print("Checkpoint reached: GUI Main Area")

# Current Round Widgets
if st.session_state.get("active_game_flag", False):
    st.divider()
    if (st.session_state.game_counter == len(st.session_state.puzzle_sequence)) & (st.session_state.play_mode != "open"):
        st.balloons()
        rankings_formatted = get_rankings(st.session_state.play_mode, st.session_state.puzzle_sequence, st.session_state.player_dict, st.session_state.game_timings, format_for_display=True)
        st.markdown(html_formatter(f"And the winner is...\n🏆{rankings_formatted[0]["Spieler"]}🏆"), unsafe_allow_html=True)
        st.dataframe(rankings_formatted, hide_index=True, width="stretch")
        st.button("Scores online speichern", key="save_scores_end", on_click=upload_highscore_dialog, args=(conn,), width="stretch")
        reset_game()
    else:
        if st.session_state.play_mode != "open":
            st.progress((st.session_state.game_counter) / len(st.session_state.puzzle_sequence), text=progress_text(st.session_state.game_counter, len(st.session_state.puzzle_sequence)))
        col1, col2 = st.columns(2, vertical_alignment="center")
        # Player/Puzzle Widgets
        with col1:
            if st.session_state.play_mode == "open":
                st.pills("Spieler wählen", st.session_state.inv_player_dict.keys(), key="selected_player", width="stretch")
                st.pills("Aufgabe wählen", options=PUZZLES, key="puzzle_choice", width="stretch")
                st.button(":question: Wie geht diese Aufgaben?", key="help_task", on_click=puzzle_help_dialog, args=(None,), width="stretch")
            else:
                curr_puzzle = INV_PUZZLE_NUMBERS[st.session_state.puzzle_sequence[st.session_state.game_counter][1]]
                curr_player_id = st.session_state.puzzle_sequence[st.session_state.game_counter][0]
                curr_player = st.session_state.player_dict[curr_player_id][0]
                if st.session_state.play_mode == "team_duel":
                    #infer team from player id
                    if curr_player_id in st.session_state.team_dict[0]:
                        curr_team = st.session_state.team_names.get(0, 'Team A')
                    else:
                        curr_team = st.session_state.team_names.get(1, 'Team B')
                    st.pills("Team", options=[curr_team], default=curr_team, key="curr_team", width="stretch")
                st.pills("Spieler", options=[curr_player], default=curr_player, key="curr_player", width="stretch")
                st.pills("Aufgabe", options=[curr_puzzle], default=curr_puzzle, key="curr_puzzle", width="stretch")
                st.button(":question: Wie geht diese Aufgabe?", key="help_task", on_click=puzzle_help_dialog, args=(st.session_state.puzzle_sequence[st.session_state.game_counter][1],), width="stretch")

        # Time Widgets            
        with col2:
            st.button("⏱️ **Start/Stop**", key="startstop", on_click=startstop, width="stretch")
            #timer_placeholder = st.empty()
            if "timer_placeholder" not in st.session_state:
                st.session_state.timer_placeholder = st.empty()
                #st.session_state.timer_placeholder.markdown(html_formatter(format_time(0)), unsafe_allow_html=True)
            if st.session_state.get("running", False):
                run_timer(st.session_state.timer_placeholder)
            else:
                st.session_state.timer_placeholder.markdown(html_formatter(format_time(st.session_state.last_elapsed)), unsafe_allow_html=True)

        if st.session_state.play_mode != "open":
            st.button("Nächste Aufgabe", key="next_task", on_click=increment_game_counter, width="stretch")

    if st.session_state.error_msg:
        st.error(st.session_state.error_msg)

    # Catch unreasonable short runs before writing them to the highscores.
    if st.session_state.score_pending_flag == True:    
        if st.session_state.last_elapsed < 20:
            confirm_superspeed_dialog()

        if (st.session_state.superspeed == True) | (st.session_state.last_elapsed >= 20):
            st.session_state.superspeed = False
            st.session_state.score_pending_flag = False

            # Append to session scores
            if st.session_state.session_scores.empty:
                st.session_state.session_scores = pd.DataFrame([st.session_state.current_entry])
            else:
                st.session_state.session_scores = pd.concat([st.session_state.session_scores, pd.DataFrame([st.session_state.current_entry])], ignore_index=True)
            st.session_state.highscores = set_highscores(st.session_state.highscores, st.session_state.current_puzzle, st.session_state.current_entry)
            timings_entry = (st.session_state.inv_player_dict[st.session_state.current_entry["player"]], #player_id
                             st.session_state.current_entry["player"], #player
                             st.session_state.current_entry["puzzle"], #puzzle
                             st.session_state.current_entry["time_seconds"]) #timing
            st.session_state.game_timings[st.session_state.game_counter] = timings_entry
            st.rerun()
print("Checkpoint reached: GUI Highscore Area")

# Highscore Widgets
if st.session_state.get("active_game_flag", False):
    st.divider()
    # Current Round Scores
    if st.session_state.play_mode != "open":
        st.subheader("Rundenzeiten", width="stretch")

        if st.session_state.game_timings:
            rows = []
            for i, e in st.session_state.game_timings.items():
                rows.append({"Runde": i+1, "Spieler": e[1], "Aufgabe": e[2], "Zeit": format_time(e[3])})
            st.dataframe(rows, hide_index=True, width="stretch")
        else:
            st.info(f"Bisher liegen keine Zeiten vor.")

    # Highscore list
    if st.session_state.play_mode == "open":
        puzzle = st.session_state.get("puzzle_choice") or ""
    else:
        puzzle = INV_PUZZLE_NUMBERS[st.session_state.puzzle_sequence[st.session_state.game_counter][1]]
    st.subheader(f"Highscores für {puzzle}", width="stretch")
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

if st.session_state.play_mode == "open" and st.session_state.session_scores is not None and not st.session_state.session_scores.empty:
    st.divider()
    placeholder = st.empty()
    st.button("Scores online speichern", key="save_scores_end_open", on_click=upload_highscore_dialog, args=(conn,), width="stretch")
    #if st.button("Scores online speichern", width="stretch"):
        
        ## push all session scores to sheet
        #old_scores = load_online_for_update(conn)
        #success = push_score_to_sheet(st.session_state.session_scores.copy(deep=True), connection=conn, sheet_read_df=old_scores, puzzle_mapper=PUZZLE_NUMBERS)
        #if success:    
        #    #reset session scores after pushing
        #    st.session_state.session_scores = pd.DataFrame(columns=SCORES_COLS)
        #    with placeholder:
        #        st.success("Scores wurden online gespeichert.")
        #else:
        #    with placeholder:
        #        st.error("Fehler beim Speichern der Scores online. Bitte später erneut versuchen.")
    
