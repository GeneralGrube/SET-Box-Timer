import random
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from setbox_constants import *
from setbox_helpers import *
from setbox_connections import *
from setbox_texts import *

def initialize_session_state(conn: GSheetsConnection, localizer: Localizer):
    # Initialize session state

    # General Setup
    if "session_startup" not in st.session_state:
        st.session_state.session_startup = True    
    if "loc" not in st.session_state:
        st.session_state.loc = localizer

    # Current run variables
    if "running" not in st.session_state:
        st.session_state.running = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "last_elapsed" not in st.session_state:
        st.session_state.last_elapsed = 0.0
    if "run_timer_interval" not in st.session_state:
        st.session_state.run_timer_interval = None
    if "score_pending_flag" not in st.session_state:
        st.session_state.score_pending_flag = False
    if "superspeed" not in st.session_state:
        st.session_state.superspeed = False
    if "current_puzzle" not in st.session_state:
        st.session_state.current_puzzle = None
    if "current_entry" not in st.session_state:
        st.session_state.current_entry = None
    
    # Session Run variables
    if "session_scores" not in st.session_state:
        st.session_state.session_scores = pd.DataFrame(columns=SCORES_COLS)
    if "highscores" not in st.session_state:
        st.session_state.highscores = load_online_highscores(conn)
    if "player_dict" not in st.session_state:
        st.session_state.player_dict = {}  # dict of player index to (name, semester, study_id)

    # Misc
    if "error_msg" not in st.session_state:
        st.session_state.error_msg = ""

    #Setup flow control variables
    
    if "mode_setup_dialog_flag" not in st.session_state:
        st.session_state.mode_setup_dialog_flag = False
    if "player_info_dialog_flag" not in st.session_state:
        st.session_state.player_info_dialog_flag = False
    if "team_duel_dialog_flag" not in st.session_state:
        st.session_state.team_duel_dialog_flag = False

    #Setup variables
    if "num_players" not in st.session_state:
        st.session_state.num_players = 2

    # App & Game flow control variables
    if "active_game_flag" not in st.session_state:
        st.session_state.active_game_flag = False
    if "play_mode" not in st.session_state:
        st.session_state.play_mode = "Offenes Spiel"
    if "puzzle_sequence" not in st.session_state:
        st.session_state.puzzle_sequence = []
    if "game_counter" not in st.session_state:
        st.session_state.game_counter = 0
    if "game_timings" not in st.session_state:
        st.session_state.game_timings = {}


def reset_game():
    st.session_state.game_counter = 0
    st.session_state.game_timings = {}
    st.session_state.last_elapsed = 0.0
    st.session_state.puzzle_sequence = []
    st.session_state.active_game_flag = False

def game_setup(play_mode: str, num_players: int, num_puzzles:int, random_pairing:bool, total_tasks: int):
    
    # Teams einteilen
    players = [p for p in range(0,num_players)]
    if random_pairing:
        random.shuffle(players)
    
    if play_mode == "team_duel":
        team_dict = {}   # dict of team index to list of player indices
        for i,player in enumerate(players):
            team_idx = i % 2
            if team_idx not in team_dict:
                team_dict[team_idx] = []
            team_dict[team_idx].append(player)   
        
        st.session_state["team_dict"] = team_dict
        
    # Aufgabenabfolge einstellen
    all_puzzles = list(PUZZLE_NUMBERS.values())[:5]
    selected_puzzles = random.sample(all_puzzles, num_puzzles)
    
    puzzle_sequence = [] #list of team/pair/player number and puzzle tuples
    shifter = 0
    player_puzzles = {} # keep track with player has done which puzzles
    for i in range(num_players):
        player_puzzles[i] = []
    
    if play_mode == "single_duel":
        starting = random.randint(0, num_players - 1)
        total = num_players
        for i in range(total_tasks):
            curr_puzzle = selected_puzzles[(i+shifter) % len(selected_puzzles)]
            curr_player = (starting + (i % total)) % total
            if (curr_puzzle not in player_puzzles[curr_player]) | (len(player_puzzles[curr_player]) >= len(selected_puzzles)):
                player_puzzles[curr_player].append(curr_puzzle)
                puzzle_sequence.append((curr_player, curr_puzzle))
            else:
                #find next available puzzle for this player
                for pz in selected_puzzles:
                    if pz not in player_puzzles[curr_player]:
                        player_puzzles[curr_player].append(pz)
                        puzzle_sequence.append((curr_player, pz))
                        break
            if (i + 1) % len(selected_puzzles) == 0:
                if len(selected_puzzles) >= num_players:
                    shifter += 1  # change starting puzzle after each full cycle
    
    elif play_mode == "team_duel":
        starting_team = random.randint(0, 1)    
        team_player_counters = {0:0, 1:0} # keep track of which player is next for each team
        team_puzzles = {0:[], 1:[]} # keep track of which puzzles have been assigned to each team
        
        for i in range(total_tasks):    
            # team & player selection                
            curr_team = (starting_team + (i % 2)) % 2
            curr_player_list = team_dict[curr_team]
            curr_player_idx = team_player_counters[curr_team] % len(curr_player_list)
            curr_player = curr_player_list[curr_player_idx]
            
            # puzzle selection
            # make sure every team sees every puzzle at least once if enough tasks (num_puzzles >= total_tasks/2)
            if (i // 2) == num_puzzles:
                played_puzzles = set(team_puzzles[curr_team])
                remaining_puzzle = set(selected_puzzles).difference(played_puzzles)
                curr_puzzle = list(remaining_puzzle)[0]
            # else just semi-randomly select a puzzle
            else:
                curr_puzzle = selected_puzzles[(i+shifter) % len(selected_puzzles)]
            # check if player has already done this puzzle
            inc = 1
            while curr_puzzle in player_puzzles[curr_player]:
                # increment puzzle counter to get next puzzle
                curr_puzzle = selected_puzzles[( (i + inc + shifter) % len(selected_puzzles))]
                inc += 1
            
            # keep track of assigned puzzles
            player_puzzles[curr_player].append(curr_puzzle)
            team_puzzles[curr_team].append(curr_puzzle)  
            puzzle_sequence.append((curr_player, curr_puzzle))
            
            team_player_counters[curr_team] += 1
            if (i + 1) % len(selected_puzzles) == 0:
                if len(selected_puzzles) >= len(curr_player_list):
                    shifter += 1  # change starting puzzle after each full cycle
            
    return puzzle_sequence

def set_highscores(current_highscores: dict, current_puzzle: str, entry: dict):
    # Append into puzzle-specific list
    hs_dict = current_highscores
    if current_puzzle not in hs_dict or not isinstance(hs_dict[current_puzzle], list):
        hs_dict[current_puzzle] = []
    hs_dict[current_puzzle].append(entry)
    # sort ascending (fastest first) for this puzzle
    hs_dict[current_puzzle].sort(key=lambda e: e["time_seconds"])
    hs_dict[current_puzzle] = hs_dict[current_puzzle][:MAX_HIGHSCORES]
    return hs_dict

def get_rankings(play_mode:str, puzzle_sequence: list, player_dict: dict, game_timings:dict, format_for_display: bool = False) -> pd.DataFrame | None:
    timings_df = pd.DataFrame(data=game_timings.values(), index=game_timings.keys(), columns=["player_id", "player", "puzzle", "time"])
    if play_mode == "single_duel":
        #Seperate timings for each player
        player_scores = {}
        for i, player in enumerate(player_dict.keys()):
            puzzle_list = list(timings_df[timings_df["player_id"] == player]["puzzle"])
            cum_time = timings_df[timings_df["player_id"] == player]["time"].sum()
            player_scores[i] = (player, player_dict[player][0], cum_time, puzzle_list)
        #sort to get rank
        player_scores = pd.DataFrame(data=player_scores.values(), index=player_scores.keys(), columns=["player_id", "player", "cum_time", "puzzles_solved"])
        player_scores.sort_values(by=["cum_time"], inplace=True)
        player_scores.reset_index(drop=True, inplace=True)
        if format_for_display:
            return format_rankings(player_scores)
        else:
            return player_scores
    if play_mode == "team_duel":
        # Seperate timings for each team
        team_dict = st.session_state.get("team_dict", {})
        team_scores = {}
        for team_idx, team_members in team_dict.items():
            puzzle_list = []
            cum_time = 0.0
            for player in team_members:
                player_timings = timings_df[timings_df["player_id"] == player]
                puzzle_list.extend(list(player_timings["puzzle"]))
                cum_time += player_timings["time"].sum()
            team_name = st.session_state.team_names.get(team_idx, f"Team {team_idx + 1}")
            team_scores[team_idx] = (team_idx, team_name, cum_time, puzzle_list)
        # sort to get rank
        team_scores = pd.DataFrame(data=team_scores.values(), index=team_scores.keys(), columns=["team_id", "team_name", "cum_time", "puzzles_solved"])
        team_scores.sort_values(by=["cum_time"], inplace=True)
        team_scores.reset_index(drop=True, inplace=True)
        if format_for_display:
            return format_rankings(team_scores)
        else:
            return team_scores
    return None



