import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit import session_state as ss

from setbox_constants import *
from setbox_helpers import *
from setbox_texts import *
from setbox_mechanics import *
from setbox_connections import *

@st.dialog(title="Select Language", width="medium",dismissible=True)
def session_startup():
    #is in English, this dialog does not get localized. Localization based on language selection takes place after closing this dialog.
    st.info("This app accompanies the Simple Endoscopic Tasks Box (SET-Box) for training basic endoscopic skills. Please select your preferred language. You may watch the instruction videos for the puzzles.")
    
    lang_dict = {
        "DE": "de",
        "EN": "en"
    }
    st.pills("Select Language", ["DE", "EN"], key="language_picker", default="DE", width="stretch")
    st.session_state.loc = Localizer(lang_dict[st.session_state.get("language_picker", "DE")])
    
    #localize
    st.pills(ss.loc.translate("puzzle_help_dialog_picker"), PUZZLES, key="puzzle_choice_video", default="1 Inversion", width="stretch")
    puzzle_number = PUZZLE_NUMBERS[st.session_state.get("puzzle_choice_video")]
    try:
        st.video(f"""{puzzle_number}.mp4""")
    except:
        st.info(ss.loc.translate("puzzle_help_dialog_no_video"))

    if st.button("Okay!", width="stretch"):
        st.rerun()

@st.dialog(title=ss.loc.translate("play_mode_dialog_title"), width="medium", dismissible=False)
def play_mode_select_dialog():
    PLAY_MODES_LOCALIZED = ss.loc.translate("play_modes")
    st.segmented_control(ss.loc.translate("play_mode_dialog_label"), options=PLAY_MODES_LOCALIZED.keys(), key="play_mode_dialog", help=ss.loc.translate("play_mode_tooltip"), default=list(PLAY_MODES_LOCALIZED)[0], width="stretch") #, args=(PLAY_MODES[st.session_state.play_mode],)
    try:
        st.session_state.play_mode = PLAY_MODES_LOCALIZED[st.session_state["play_mode_dialog"]]
        play_mode = st.session_state.play_mode
        if play_mode == "pair_duel":
            st.error("Der 'Paar-Duell' Modus ist aktuell nicht verfügbar. Bitte wähle einen anderen Modus.")
        
        if st.button(ss.loc.translate("play_mode_dialog_continue"), use_container_width=True): 
            mode_settings = MODE_SETTINGS[play_mode]
            st.session_state.min_players, st.session_state.max_players, st.session_state.player_step_size = mode_settings[0], mode_settings[1], mode_settings[2]
            st.session_state.mode_setup_dialog_flag = True
            
            #catch wierd UI bug
            if st.session_state.previous_game_mode != play_mode:
                st.session_state.game_mode_changed_flag = True
                st.session_state.previous_game_mode = play_mode
            st.rerun()
    except KeyError:
        pass

@st.dialog(title=ss.loc.translate("settings_dialog_title"), width="medium", dismissible=False)
def settings_dialog():
    play_mode = st.session_state.play_mode
    
    if play_mode == "team_duel":
        col1, col2 = st.columns(2)
        with col1:
            name_team_a = st.text_input(ss.loc.translate("settings_dialog_team_name_a_label"), value=ss.loc.translate("settings_dialog_team_a_name_suggestion"))
        with col2:
            name_team_b = st.text_input(ss.loc.translate("settings_dialog_team_name_b_label"), value=ss.loc.translate("settings_dialog_team_b_name_suggestion"))

    if play_mode != "lndw":
        num_players = st.slider(ss.loc.translate("settings_dialog_num_players_label"), min_value=st.session_state.min_players, max_value=st.session_state.max_players, step=st.session_state.player_step_size, value=st.session_state.min_players)
    else:
        num_players = 1

    if play_mode in ["pair_duel", "team_duel"]:
        random_pairing = st.toggle(ss.loc.translate("settings_dialog_random_pairing_label"), value=False, help=ss.loc.translate("settings_dialog_random_pairing_tooltip"))
    else: random_pairing = False

    if play_mode not in ["open", "lndw"]:
        maximum_games = num_players * 5
        total_tasks = st.slider(ss.loc.translate("settings_dialog_total_tasks_label"), min_value=num_players, max_value=maximum_games, step=num_players, value=num_players, help=ss.loc.translate("settings_dialog_total_tasks_tooltip"))
        st.info(ss.loc.translate("settings_dialog_total_tasks_info", from_min=str(total_tasks * 4), to_min=str(total_tasks * 6)))
    else: total_tasks = 0

    if play_mode == "open":
        num_puzzles = 0
    elif play_mode == "single_duel":
        num_puzzles = total_tasks // num_players 
    elif play_mode == "team_duel":
        num_puzzles = total_tasks // 2
    elif play_mode == "lndw":
        num_puzzles = 0
        st.info(ss.loc.translate("settings_dialog_lndw_info"))

    if st.button(ss.loc.translate("settings_dialog_continue"), use_container_width=True):
        st.session_state.num_players = num_players
        # if number of 
        st.session_state.num_puzzles = num_puzzles
        st.session_state.random_pairing = random_pairing
        st.session_state.total_tasks = total_tasks
        st.session_state.team_names = {
            0: name_team_a if play_mode == "team_duel" else "Team A",
            1: name_team_b if play_mode == "team_duel" else "Team B"
        }
        st.session_state.player_info_dialog_flag = True
        st.rerun()

@st.dialog(title=ss.loc.translate("player_dialog_title"), width="medium", dismissible=False)
def player_dialog():
    number_of_players = st.session_state.get("num_players", 1)
    
    #prearrange playerdict if not existing
    if "player_dict" not in st.session_state:
        st.session_state.player_dict = {i: ("", 6) for i in range(0, number_of_players)}
    #append existing player dict if number of players increased
    if len(st.session_state.player_dict.keys()) < number_of_players:
        for i in range(len(st.session_state.player_dict.keys()), number_of_players):
            st.session_state.player_dict[i] = ("", 6)

    col1, col2 = st.columns(2)
    
    with col1:
        for i in range(0, number_of_players):
            if st.session_state.play_mode == "lndw":
                st.text_input(ss.loc.translate("player_dialog_name", idx=(str(i+1))), key=f"username{i}", value=st.session_state.player_dict[i][0], placeholder="begeisterter LNDW Teilnehmer")
            else:
                st.text_input(ss.loc.translate("player_dialog_name", idx=(str(i+1))), key=f"username{i}", value=st.session_state.player_dict[i][0])
    with col2:
        for i in range(0, number_of_players):
            if st.session_state.play_mode == "lndw":
                st.number_input(ss.loc.translate("player_dialog_semester_lndw", idx=(str(i+1))), key=f"semester{i}", min_value=0, max_value=100, value=st.session_state.player_dict[i][1], step=1)
            else:
                st.number_input(ss.loc.translate("player_dialog_semester", idx=(str(i+1))), key=f"semester{i}", min_value=1, max_value=20, value=st.session_state.player_dict[i][1], step=1)
    error_placeholder = st.empty()
    
    if st.button(ss.loc.translate("player_dialog_continue"), use_container_width=True):
        error_flag = False
        player_dict = {}
        checked_player_names = []
        for i in range(0, number_of_players):
            # check if name already exists, if so return with error message
            if st.session_state.get(f"username{i}") in checked_player_names:
                error_placeholder.error(ss.loc.translate("player_dialog_error_duplicate_name", name=st.session_state.get(f"username{i}")))
                error_flag = True
            else:
                if st.session_state.play_mode == "lndw":
                    if st.session_state[f'username{0}'] == "":
                        player_dict[i] = (f"LNDW-Teilnehmer", st.session_state.get(f"semester{i}", ""))
                    else:
                        player_dict[i] = (f"{st.session_state[f'username{i}']}", st.session_state.get(f"semester{i}", ""))
                else:
                    player_dict[i] = (f"{st.session_state[f'username{i}']}", st.session_state.get(f"semester{i}", ""))
                checked_player_names.append(f"{st.session_state[f'username{i}']}")
        if not error_flag:
            st.session_state.player_dict = player_dict
            st.session_state.inv_player_dict = {v[0]: k for k, v in player_dict.items()}
            st.session_state.active_game_flag = True
            if st.session_state.play_mode not in ["open", "lndw"]:
                st.session_state.puzzle_sequence = game_setup(st.session_state.play_mode, st.session_state.num_players, st.session_state.num_puzzles, st.session_state.random_pairing, st.session_state.total_tasks)
            if st.session_state.play_mode == "team_duel":
                st.session_state.team_duel_dialog_flag = True
            st.rerun()

@st.dialog(ss.loc.translate("team_dialog_title"), width="medium", dismissible=True)
def team_dialog():
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
    if st.button(ss.loc.translate("team_dialog_continue"), width="stretch"):
        st.rerun()

@st.dialog(title=ss.loc.translate("forgot_record_dialog_title"), width="medium")
def forgot_record_dialog():
    st.warning(ss.loc.translate("forgot_record_dialog_warning"))
    if st.button(ss.loc.translate("forgot_record_dialog_continue"), width="stretch"):
        st.rerun()

@st.dialog(title=ss.loc.translate("puzzle_help_dialog_title"), width="medium")
def puzzle_help_dialog(puzzle_number: int|None=None):
    if puzzle_number is None:
        #localize
        st.pills(ss.loc.translate("puzzle_help_dialog_picker"), PUZZLES, key="puzzle_choice_video", default="1 Inversion", width="stretch")
        puzzle_number = PUZZLE_NUMBERS[st.session_state.get("puzzle_choice_video")]
    try:
        st.video(f"""{puzzle_number}.mp4""")
    except:
        st.info(ss.loc.translate("puzzle_help_dialog_no_video"))

@st.dialog(ss.loc.translate("conform_superspeed_dialog_title"), dismissible=False)
def confirm_superspeed_dialog():
    st.warning(ss.loc.translate("confirm_superspeed_dialog_warning"))
    col1, col2 = st.columns(2)
    with col1:
        if st.button(ss.loc.translate("confirm_superspeed_true"), width="stretch"):
            st.session_state.superspeed = True
            st.rerun()
    with col2:
        if st.button(ss.loc.translate("confirm_superspeed_false"), width="stretch"):
            st.session_state.superspeed = False
            st.session_state.score_pending_flag = False
            st.session_state.last_elapsed = 0.0
            st.rerun()

@st.dialog(ss.loc.translate("upload_highscore_dialog_title"), width="medium", dismissible=False)
def upload_highscore_dialog(connection: GSheetsConnection):
    number_of_players = st.session_state.get("num_players", 1)
    st.info(ss.loc.translate("upload_highscore_dialog_info"))
    st.image("survey_QR.svg", width=800)
    st.info(ss.loc.translate("upload_highscore_dialog_instruction"))
    col1, col2 = st.columns(2)
    with col1:
        for i in range(0, number_of_players):
            st.text_input(ss.loc.translate("upload_highscore_dialog_name", idx=(str(i+1))), key=f"username{i}", value=st.session_state.player_dict[i][0], disabled=True)
            #st.write(f"{st.session_state.player_dict[i][0]}")
    with col2:
        for i in range(0, number_of_players):
            st.number_input(ss.loc.translate("upload_highscore_dialog_studyid", idx=(str(i+1))), key=f"study_id{i}", min_value=1, max_value=500, value=1, step=1)
    if st.button(ss.loc.translate("upload_highscores_continue"), use_container_width=True):
        for i in range(0, number_of_players):
            st.session_state.player_dict[i] = (st.session_state.player_dict[i][0], st.session_state.player_dict[i][1], st.session_state.get(f"study_id{i}", ""))
        old_scores = load_online_for_update(connection)
        success_flag = push_score_to_sheet(st.session_state.session_scores.copy(deep=True), connection=connection, sheet_read_df=old_scores, puzzle_mapper=PUZZLE_NUMBERS)
        if success_flag:
            st.session_state.session_scores = pd.DataFrame(columns=SCORES_COLS)
        st.rerun()
