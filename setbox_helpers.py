import pandas as pd

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

def html_formatter(str: str, font_size: int = 48, align: str = "center", color: str ="black", font_weight: int = 700, span_only: bool = False) -> str:
    str = str.replace("\n","<br>")
    if span_only:
        return f'<span style="font-weight:{font_weight}; font-size:{font_size}px; color:{color}">{str}</span>'
    else:
        return f'<div style="text-align:{align};"><span style="font-weight:{font_weight}; font-size:{font_size}px; color:{color}">{str}</span></div>'

def update_session_scores_studyID(df: pd.DataFrame, player_dict: dict) -> pd.DataFrame:
    """
    Update the session scores DataFrame to include a 'study_id' column based on player_dict.
    If 'study_id' already exists, no changes are made.
    """
    if 'study_id' not in df.columns:
        try:
            study_ids = {v[0]: v[2] for k, v in player_dict.items()}
        except IndexError:
            study_ids = {}
        id_col = []
        for _, row in df.iterrows():
            player_name = row['player']
            if player_name in study_ids.keys():
                study_id = study_ids[player_name]
            else:
                study_id = 0
            id_col.append(study_id)
        df['study_id'] = id_col
    return df