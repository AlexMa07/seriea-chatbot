"""Carica e mette in cache i dati CSV della Serie A 2024/25."""
import pandas as pd
from pathlib import Path
from typing import List

DATA_DIR = Path(__file__).parent / "data"

# Normalizzazione nomi squadra: valore nel CSV → nome canonico
_TEAM_NORMALIZE: dict[str, str] = {
    "Hellas Verona": "Verona",
}


def _parse_result(result_str) -> tuple[int, int]:
    """Converte la stringa 'X - Y' in (home_goals, away_goals)."""
    try:
        parts = str(result_str).split("-")
        return int(parts[0].strip()), int(parts[1].strip())
    except Exception:
        return 0, 0


def _load_matches(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Rinomina colonne
    df = df.rename(columns={
        "Match Number":  "match_number",
        "Round Number":  "matchday",
        "Date":          "date_raw",
        "Location":      "location",
        "Home Team":     "home_team",
        "Away Team":     "away_team",
        "Result":        "result_raw",
    })

    # Normalizza nomi squadra
    df["home_team"] = df["home_team"].replace(_TEAM_NORMALIZE)
    df["away_team"] = df["away_team"].replace(_TEAM_NORMALIZE)

    # Parsa data (formato DD/MM/YYYY HH:MM) → YYYY-MM-DD
    df["date"] = pd.to_datetime(df["date_raw"], format="%d/%m/%Y %H:%M", errors="coerce")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # Espandi il risultato in home_goals / away_goals
    goals = df["result_raw"].apply(_parse_result)
    df["home_goals"] = goals.apply(lambda x: x[0])
    df["away_goals"] = goals.apply(lambda x: x[1])

    # Tutte le righe presenti sono partite disputate
    df["status"] = "played"

    # Tipo giornata
    df["matchday"] = df["matchday"].astype(int)

    return df[[
        "match_number", "matchday", "date", "location",
        "home_team", "away_team", "home_goals", "away_goals", "status",
    ]]


class DataLoader:
    """Singleton che carica il CSV partite e players.csv una sola volta."""

    _instance: "DataLoader | None" = None

    def __new__(cls) -> "DataLoader":
        if cls._instance is None:
            obj = super().__new__(cls)
            obj._load()
            cls._instance = obj
        return cls._instance

    def _load(self) -> None:
        matches_path = DATA_DIR / "matches-serie-a-2024-UTC.csv"
        players_path = DATA_DIR / "league-players.CSV"

        if not matches_path.exists():
            raise FileNotFoundError(f"File non trovato: {matches_path}")
        if not players_path.exists():
            raise FileNotFoundError(f"File non trovato: {players_path}")

        self._matches: pd.DataFrame = _load_matches(matches_path)

        self._players: pd.DataFrame = pd.read_csv(players_path)
        for col in ("goals", "assists", "appearances", "yellow_cards", "red_cards"):
            if col in self._players.columns:
                self._players[col] = (
                    pd.to_numeric(self._players[col], errors="coerce").fillna(0).astype(int)
                )

    @property
    def matches(self) -> pd.DataFrame:
        return self._matches

    @property
    def players(self) -> pd.DataFrame:
        return self._players

    def get_teams(self) -> List[str]:
        teams = set(self._matches["home_team"].tolist() + self._matches["away_team"].tolist())
        return sorted(teams)

    def get_player_names(self) -> List[str]:
        return self._players["player_name"].tolist()

    def get_max_played_matchday(self) -> int:
        played = self._matches[self._matches["status"] == "played"]
        return int(played["matchday"].max()) if not played.empty else 0
