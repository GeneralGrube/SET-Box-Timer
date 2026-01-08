import streamlit as st
from streamlit_gsheets import GSheetsConnection

from setbox_constants import *
from setbox_helpers import *
from setbox_texts import *
from setbox_mechanics import *
from setbox_connections import *

@st.dialog(title="Keine Aufgabenzeit vorhanden.", width="medium")
def forgot_record_dialog():
    st.warning("Es wurde keine Zeit für die Aufgabe aufgezeichnet.")
    if st.button("Verstanden", width="stretch"):
        st.rerun()

@st.dialog(title="Wie geht diese Aufgabe?", width="medium")
def puzzle_help_dialog(puzzle_number):
    if puzzle_number is None:
        st.pills("Aufgabe wählen", PUZZLES, key="puzzle_choice_video", default="1 Inversion", width="stretch")
        puzzle_number = PUZZLE_NUMBERS[st.session_state.get("puzzle_choice_video")]
    try:
        st.video(f"""{puzzle_number}.mp4""")
    except:
        st.info("Video nicht gefunden.")

@st.dialog(title="Spielmodus auswählen", width="medium", dismissible=False)
def play_mode_select_dialog():
    st.segmented_control("Spiel-Modus auswählen", options=PLAY_MODES.keys(), key="play_mode_dialog", help=PLAY_MODE_TOOLTIP, default="Offenes Spiel", width="stretch") #, args=(PLAY_MODES[st.session_state.play_mode],)
    try:
        st.session_state.play_mode = PLAY_MODES[st.session_state.get("play_mode_dialog", "Offenes Spiel")]
        play_mode = st.session_state.play_mode
        if play_mode == "pair_duel":
            st.error("Der 'Paar-Duell' Modus ist aktuell nicht verfügbar. Bitte wähle einen anderen Modus.")
        
        if st.button("Weiter zu den Einstellungen...", use_container_width=True): 
            mode_settings = MODE_SETTINGS[play_mode]
            st.session_state.min_players, st.session_state.max_players, st.session_state.player_step_size = mode_settings[0], mode_settings[1], mode_settings[2]
            st.session_state.mode_setup_dialog_flag = True
            st.rerun()
    except KeyError:
        pass

@st.dialog(title="Spielmodus Einstellungen", width="medium", dismissible=False)
def mode_setup_dialog():
    play_mode = st.session_state.play_mode
    
    if play_mode == "team_duel":
        col1, col2 = st.columns(2)
        with col1:
            name_team_a = st.text_input("Name Team A", value="🔥 Hot Docs 🌭")
        with col2:
            name_team_b = st.text_input("Name Team B", value="💨 Gas Busters 👻")

    num_players = st.slider("Anzahl Spieler", min_value=st.session_state.min_players, max_value=st.session_state.max_players, step=st.session_state.player_step_size, value=st.session_state.min_players)
    
    if play_mode in ["pair_duel", "team_duel"]:
        random_pairing = st.toggle("Zufällige Teameinteilung", value=False, help="Bei aktivierter Option werden die Spieler zufällig in Teams aufgeteilt.")
    else: random_pairing = False

    if play_mode != "open":
        num_puzzles = st.slider("Anzahl Aufgaben", min_value=2, max_value=5, step=1, value=2, help=NUM_PUZZLE_TOOLTIP)
    else: num_puzzles = 0

    if play_mode != "open":
        maximum_games = num_players * num_puzzles
        total_tasks = st.slider("Gesamtzahl Aufgaben", min_value=num_players, max_value=maximum_games, step=num_players, value=num_players, help=TOTAL_TASKS_TOOLTIP)
        st.info(f"Bei dieser Einstellung dauert die Runde etwa {total_tasks * 4} bis {total_tasks * 6} Minuten.")
    else: total_tasks = 0

    if st.button("Weiter zu den Spieler Informationen...", use_container_width=True):
        st.session_state.num_players = num_players
        st.session_state.num_puzzles = num_puzzles
        st.session_state.random_pairing = random_pairing
        st.session_state.total_tasks = total_tasks
        st.session_state.team_names = {
            0: name_team_a if play_mode == "team_duel" else "Team A",
            1: name_team_b if play_mode == "team_duel" else "Team B"
        }
        st.session_state.player_info_dialog_flag = True
        st.rerun()

@st.dialog(title="Spieler Informationen", width="medium", dismissible=False)
def player_info_dialog():
    number_of_players = st.session_state.get("num_players", 1)
    
    col1, col2 = st.columns(2)
    with col1:
        for i in range(0, number_of_players):
            st.text_input(f"Spieler {i+1} Namen eingeben:", key=f"username{i}")
    with col2:
        for i in range(0, number_of_players):
            st.number_input(f"Spieler {i+1} Semster:", key=f"semster{i}", min_value=1, max_value=20, value=6, step=1)
    error_placeholder = st.empty()
    
    if st.button("Spieler Informationen speichern", use_container_width=True):
        error_flag = False
        player_dict = {}
        checked_player_names = []
        for i in range(0, number_of_players):
            # check if name already exists, if so return with error message
            if st.session_state.get(f"username{i}") in checked_player_names:
                error_placeholder.error(f"Der Name '{st.session_state.get(f'username{i}')}' wurde mehrfach eingegeben. Bitte eindeutige Spielernamen verwenden.")
                error_flag = True
            else:
                player_dict[i] = (f"{st.session_state[f'username{i}']}", st.session_state.get(f"semster{i}", ""))
                checked_player_names.append(f"{st.session_state[f'username{i}']}")
        if not error_flag:
            st.session_state.player_dict = player_dict
            st.session_state.inv_player_dict = {v[0]: k for k, v in player_dict.items()}
            st.session_state.active_game_flag = True
            if st.session_state.play_mode != "open":
                st.session_state.puzzle_sequence = game_setup(st.session_state.play_mode, st.session_state.num_players, st.session_state.num_puzzles, st.session_state.random_pairing, st.session_state.total_tasks)
            if st.session_state.play_mode == "team_duel":
                st.session_state.team_duel_dialog_flag = True
            st.rerun()

@st.dialog("Team Übersicht", width="medium", dismissible=True)
def team_overview_dialog():
    team_dict = st.session_state.get("team_dict", {})
    team_names = st.session_state.get("team_names", {})
    col1, col2 = st.columns(2)
    with col1:
        team_name = team_names.get(0, 'Team A')
        player_name_list = []
        for player_id in team_dict[0]:
            player_name_list.append(st.session_state.player_dict[player_id][0])
        st.pills(team_name, player_name_list, key="team_a_player_list", width="stretch")
    with col2:
        team_name = team_names.get(1, 'Team B')
        player_name_list = []
        for player_id in team_dict[1]:
            player_name_list.append(st.session_state.player_dict[player_id][0])
        st.pills(team_name, player_name_list, key="team_b_player_list", width="stretch")
    if st.button("Okay, los gehts!", width="stretch"):
        st.rerun()

@st.dialog("Runde wirklich unter 20 Sekunden?", dismissible=False)
def confirm_superspeed_dialog():
    st.warning("Eine Runde unter 20 Sekunden ist sehr unwahrscheinlich. Warst du wirklich so schnell?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ja, klar!", width="stretch"):
            st.session_state.superspeed = True
            st.rerun()
    with col2:
        if st.button("Ne, verklickt...", width="stretch"):
            st.session_state.superspeed = False
            st.session_state.score_pending_flag = False
            st.session_state.last_elapsed = 0.0
            st.rerun()

@st.dialog("Upload Highscores")
def upload_highscore_dialog(connection: GSheetsConnection):
    number_of_players = st.session_state.get("num_players", 1)
    st.info("Bitte Studien IDs der Spieler eingeben, damit die Zeiten zugeordnet werden können.")
    col1, col2 = st.columns(2)
    with col1:
        for i in range(0, number_of_players):
            st.text_input(f"Spieler {i+1} Namen:", key=f"username{i}", value=st.session_state.player_dict[i][0], disabled=True)
            #st.write(f"{st.session_state.player_dict[i][0]}")
    with col2:
        for i in range(0, number_of_players):
            st.number_input(f"Spieler {i+1} Studien ID:", key=f"study_id{i}", min_value=1, max_value=500, value=1, step=1)
    if st.button("Highscores hochladen", use_container_width=True):
        for i in range(0, number_of_players):
            st.session_state.player_dict[i] = (st.session_state.player_dict[i][0], st.session_state.player_dict[i][1], st.session_state.get(f"study_id{i}", ""))
        old_scores = load_online_for_update(connection)
        success_flag = push_score_to_sheet(st.session_state.session_scores.copy(deep=True), connection=connection, sheet_read_df=old_scores, puzzle_mapper=PUZZLE_NUMBERS)
        if success_flag:
            st.session_state.session_scores = pd.DataFrame(columns=SCORES_COLS)
        st.rerun()
