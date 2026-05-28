"""Query engine: interroga i dati CSV e restituisce strutture dati."""
import pandas as pd
from typing import Optional
from data_loader import DataLoader

TEAMS = [
    "Atalanta", "Bologna", "Cagliari", "Como", "Empoli",
    "Fiorentina", "Genoa", "Inter", "Juventus", "Lazio",
    "Lecce", "Milan", "Monza", "Napoli", "Parma",
    "Roma", "Torino", "Udinese", "Venezia", "Verona",
]


def _played(df: pd.DataFrame, up_to: Optional[int] = None) -> pd.DataFrame:
    mask = df["status"] == "played"
    if up_to is not None:
        mask &= df["matchday"] <= up_to
    return df[mask]


# ── Classifica ───────────────────────────────────────────────────────────────

def get_standings(matchday: Optional[int] = None) -> list[dict]:
    """Calcola la classifica fino alla giornata specificata (o l'ultima disputata)."""
    loader = DataLoader()
    matches = loader.matches
    max_md = loader.get_max_played_matchday()

    if matchday is None:
        matchday = max_md
    else:
        matchday = min(matchday, max_md)

    played = _played(matches, up_to=matchday)

    standings: dict[str, dict] = {
        t: {"G": 0, "V": 0, "P": 0, "S": 0, "GF": 0, "GS": 0, "Pt": 0}
        for t in TEAMS
    }

    for _, row in played.iterrows():
        home, away = row["home_team"], row["away_team"]
        hg, ag = int(row["home_goals"]), int(row["away_goals"])

        standings[home]["G"]  += 1;  standings[away]["G"]  += 1
        standings[home]["GF"] += hg; standings[away]["GF"] += ag
        standings[home]["GS"] += ag; standings[away]["GS"] += hg

        if hg > ag:
            standings[home]["V"] += 1; standings[home]["Pt"] += 3
            standings[away]["S"] += 1
        elif hg == ag:
            standings[home]["P"] += 1; standings[home]["Pt"] += 1
            standings[away]["P"] += 1; standings[away]["Pt"] += 1
        else:
            standings[away]["V"] += 1; standings[away]["Pt"] += 3
            standings[home]["S"] += 1

    result = [
        {
            "Squadra": t,
            **standings[t],
            "DR": standings[t]["GF"] - standings[t]["GS"],
        }
        for t in TEAMS
    ]
    result.sort(key=lambda x: (-x["Pt"], -x["DR"], -x["GF"]))
    for i, row in enumerate(result):
        row["Pos"] = i + 1

    return result, matchday


# ── Risultati ────────────────────────────────────────────────────────────────

def get_results(
    matchday: Optional[int] = None,
    team: Optional[str] = None,
) -> tuple[list[dict], Optional[int]]:
    """Restituisce i risultati per una giornata e/o una squadra."""
    loader = DataLoader()
    df = _played(loader.matches)

    if matchday is not None:
        df = df[df["matchday"] == matchday]
    if team is not None:
        df = df[(df["home_team"] == team) | (df["away_team"] == team)]

    rows = df.sort_values(["matchday", "home_team"]).to_dict("records")
    return rows, matchday


# ── Calendario ───────────────────────────────────────────────────────────────

def get_calendar(
    team: Optional[str] = None,
    matchday: Optional[int] = None,
) -> list[dict]:
    """Restituisce tutte le partite (giocate e programmate) filtrate per squadra/giornata."""
    loader = DataLoader()
    df = loader.matches.copy()

    if matchday is not None:
        df = df[df["matchday"] == matchday]
    if team is not None:
        df = df[(df["home_team"] == team) | (df["away_team"] == team)]

    return df.sort_values(["matchday"]).to_dict("records")


# ── Marcatori ────────────────────────────────────────────────────────────────

def get_top_scorers(n: int = 10) -> list[dict]:
    """Restituisce i migliori n marcatori della stagione."""
    loader = DataLoader()
    df = loader.players.copy()
    df = df[df["goals"] > 0].sort_values(
        ["goals", "assists"], ascending=[False, False]
    )
    return df.head(n).to_dict("records")


# ── Statistiche giocatore ────────────────────────────────────────────────────

def get_player_stats(player_name: str) -> Optional[dict]:
    """Restituisce le statistiche di un giocatore (ricerca case-insensitive)."""
    loader = DataLoader()
    df = loader.players
    mask = df["player_name"].str.lower() == player_name.lower()
    rows = df[mask]
    if rows.empty:
        return None
    return rows.iloc[0].to_dict()


# ── Statistiche squadra ──────────────────────────────────────────────────────

def get_team_stats(team: str) -> Optional[dict]:
    """Calcola le statistiche complete di una squadra per tutta la stagione."""
    loader = DataLoader()
    df = _played(loader.matches)
    df_team = df[(df["home_team"] == team) | (df["away_team"] == team)]

    if df_team.empty:
        return None

    stats = {"G": 0, "V": 0, "P": 0, "S": 0, "GF": 0, "GS": 0, "Pt": 0}

    for _, row in df_team.iterrows():
        home, away = row["home_team"], row["away_team"]
        hg, ag = int(row["home_goals"]), int(row["away_goals"])

        is_home = (home == team)
        gf, gs = (hg, ag) if is_home else (ag, hg)

        stats["G"]  += 1
        stats["GF"] += gf
        stats["GS"] += gs

        if gf > gs:
            stats["V"] += 1; stats["Pt"] += 3
        elif gf == gs:
            stats["P"] += 1; stats["Pt"] += 1
        else:
            stats["S"] += 1

    stats["DR"] = stats["GF"] - stats["GS"]

    # Posizione in classifica
    standings, _ = get_standings()
    pos = next((r["Pos"] for r in standings if r["Squadra"] == team), None)
    stats["Pos"] = pos

    # Media gol
    stats["MediaGF"] = round(stats["GF"] / stats["G"], 2) if stats["G"] else 0
    stats["MediaGS"] = round(stats["GS"] / stats["G"], 2) if stats["G"] else 0

    return stats
