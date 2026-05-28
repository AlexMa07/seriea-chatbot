#!/usr/bin/env python3
"""
Generatore di dati di esempio per la Serie A 2024/25.
Eseguire con: python backend/data/generate_sample_data.py
Sostituire i file CSV generati con dati reali per informazioni accurate.
"""
import csv
import math
import random
from datetime import date
from pathlib import Path

random.seed(42)

TEAMS = [
    "Atalanta", "Bologna", "Cagliari", "Como", "Empoli",
    "Fiorentina", "Genoa", "Inter", "Juventus", "Lazio",
    "Lecce", "Milan", "Monza", "Napoli", "Parma",
    "Roma", "Torino", "Udinese", "Venezia", "Verona",
]

# Profilo offensivo/difensivo di ogni squadra (media xG stimata)
TEAM_PROFILE = {
    "Inter":       {"att": 2.15, "def": 0.85},
    "Napoli":      {"att": 2.00, "def": 0.80},
    "Atalanta":    {"att": 2.05, "def": 1.05},
    "Juventus":    {"att": 1.70, "def": 0.90},
    "Milan":       {"att": 1.70, "def": 1.05},
    "Lazio":       {"att": 1.80, "def": 1.20},
    "Fiorentina":  {"att": 1.70, "def": 1.15},
    "Roma":        {"att": 1.65, "def": 1.20},
    "Bologna":     {"att": 1.50, "def": 1.25},
    "Torino":      {"att": 1.20, "def": 1.20},
    "Genoa":       {"att": 1.20, "def": 1.40},
    "Udinese":     {"att": 1.15, "def": 1.30},
    "Cagliari":    {"att": 1.10, "def": 1.45},
    "Lecce":       {"att": 1.00, "def": 1.50},
    "Verona":      {"att": 1.10, "def": 1.50},
    "Empoli":      {"att": 1.00, "def": 1.30},
    "Como":        {"att": 1.10, "def": 1.50},
    "Parma":       {"att": 1.00, "def": 1.55},
    "Monza":       {"att": 1.00, "def": 1.40},
    "Venezia":     {"att": 0.90, "def": 1.75},
}

HOME_ADVANTAGE = 0.25

# Date representative di ciascuna giornata
MATCHDAY_DATES = [
    date(2024,  8, 17), date(2024,  8, 24), date(2024,  8, 31),
    date(2024,  9, 14), date(2024,  9, 21), date(2024,  9, 28),
    date(2024, 10,  5), date(2024, 10, 19), date(2024, 10, 26),
    date(2024, 11,  2), date(2024, 11,  9), date(2024, 11, 23),
    date(2024, 11, 30), date(2024, 12,  7), date(2024, 12, 14),
    date(2024, 12, 21), date(2025,  1, 11), date(2025,  1, 18),
    date(2025,  1, 25), date(2025,  2,  1), date(2025,  2,  8),
    date(2025,  2, 15), date(2025,  2, 22), date(2025,  3,  1),
    date(2025,  3,  8), date(2025,  3, 15), date(2025,  3, 29),
    date(2025,  4,  5), date(2025,  4, 12), date(2025,  4, 19),
    date(2025,  4, 26), date(2025,  5,  3), date(2025,  5, 10),
    date(2025,  5, 17), date(2025,  5, 18), date(2025,  5, 19),
    date(2025,  5, 20), date(2025,  5, 25),
]

# Giocatori chiave con statistiche approssimative per la stagione 2024/25
KEY_PLAYERS = [
    # Atalanta
    {"player_name": "Mateo Retegui",        "team": "Atalanta",   "goals": 24, "assists": 6,  "appearances": 37, "yellow_cards": 5, "red_cards": 0},
    {"player_name": "Ademola Lookman",       "team": "Atalanta",   "goals":  9, "assists": 6,  "appearances": 34, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Charles De Ketelaere", "team": "Atalanta",   "goals":  7, "assists": 8,  "appearances": 33, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Mario Pašalić",         "team": "Atalanta",   "goals":  5, "assists": 7,  "appearances": 32, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Ederson",               "team": "Atalanta",   "goals":  3, "assists": 5,  "appearances": 30, "yellow_cards": 6, "red_cards": 0},
    # Bologna
    {"player_name": "Riccardo Orsolini",     "team": "Bologna",    "goals": 10, "assists": 6,  "appearances": 34, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Santiago Castro",       "team": "Bologna",    "goals":  8, "assists": 3,  "appearances": 30, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Dan Ndoye",             "team": "Bologna",    "goals":  6, "assists": 7,  "appearances": 33, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Giovanni Fabbian",      "team": "Bologna",    "goals":  5, "assists": 3,  "appearances": 28, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Remo Freuler",          "team": "Bologna",    "goals":  2, "assists": 4,  "appearances": 31, "yellow_cards": 5, "red_cards": 0},
    # Cagliari
    {"player_name": "Roberto Piccoli",       "team": "Cagliari",   "goals":  9, "assists": 2,  "appearances": 33, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Gianluca Lapadula",     "team": "Cagliari",   "goals":  5, "assists": 1,  "appearances": 25, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Zito Luvumbo",          "team": "Cagliari",   "goals":  4, "assists": 5,  "appearances": 30, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Razvan Marin",          "team": "Cagliari",   "goals":  3, "assists": 4,  "appearances": 32, "yellow_cards": 6, "red_cards": 1},
    # Como
    {"player_name": "Nico Paz",              "team": "Como",       "goals":  7, "assists": 6,  "appearances": 36, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Patrick Cutrone",       "team": "Como",       "goals":  6, "assists": 2,  "appearances": 28, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Assane Diao",           "team": "Como",       "goals":  4, "assists": 4,  "appearances": 30, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Sergi Roberto",         "team": "Como",       "goals":  1, "assists": 5,  "appearances": 25, "yellow_cards": 4, "red_cards": 0},
    # Empoli
    {"player_name": "Sebastiano Esposito",   "team": "Empoli",     "goals":  8, "assists": 3,  "appearances": 35, "yellow_cards": 5, "red_cards": 0},
    {"player_name": "Lorenzo Colombo",       "team": "Empoli",     "goals":  5, "assists": 1,  "appearances": 27, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Jacopo Fazzini",        "team": "Empoli",     "goals":  4, "assists": 4,  "appearances": 30, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Youssef Maleh",         "team": "Empoli",     "goals":  2, "assists": 3,  "appearances": 28, "yellow_cards": 4, "red_cards": 0},
    # Fiorentina
    {"player_name": "Moise Kean",            "team": "Fiorentina", "goals": 13, "assists": 3,  "appearances": 34, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Albert Guðmundsson",    "team": "Fiorentina", "goals":  8, "assists": 4,  "appearances": 26, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Lucas Beltrán",         "team": "Fiorentina", "goals":  4, "assists": 3,  "appearances": 28, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Nicolás González",      "team": "Fiorentina", "goals":  3, "assists": 5,  "appearances": 22, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Edoardo Bove",          "team": "Fiorentina", "goals":  2, "assists": 3,  "appearances": 16, "yellow_cards": 2, "red_cards": 0},
    # Genoa
    {"player_name": "Andrea Pinamonti",      "team": "Genoa",      "goals":  8, "assists": 2,  "appearances": 32, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Vitinha",               "team": "Genoa",      "goals":  5, "assists": 2,  "appearances": 28, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Morten Frendrup",       "team": "Genoa",      "goals":  2, "assists": 4,  "appearances": 30, "yellow_cards": 5, "red_cards": 0},
    {"player_name": "Aaron Martin",          "team": "Genoa",      "goals":  1, "assists": 4,  "appearances": 29, "yellow_cards": 4, "red_cards": 0},
    # Inter
    {"player_name": "Lautaro Martinez",      "team": "Inter",      "goals": 17, "assists": 7,  "appearances": 36, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Marcus Thuram",         "team": "Inter",      "goals": 14, "assists": 5,  "appearances": 35, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Hakan Çalhanoğlu",      "team": "Inter",      "goals":  7, "assists": 8,  "appearances": 31, "yellow_cards": 5, "red_cards": 0},
    {"player_name": "Nicolò Barella",        "team": "Inter",      "goals":  5, "assists": 10, "appearances": 33, "yellow_cards": 7, "red_cards": 0},
    {"player_name": "Federico Dimarco",      "team": "Inter",      "goals":  4, "assists": 9,  "appearances": 32, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Piotr Zieliński",       "team": "Inter",      "goals":  4, "assists": 5,  "appearances": 29, "yellow_cards": 3, "red_cards": 0},
    # Juventus
    {"player_name": "Dušan Vlahović",        "team": "Juventus",   "goals": 12, "assists": 2,  "appearances": 31, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Kenan Yıldız",          "team": "Juventus",   "goals":  8, "assists": 6,  "appearances": 35, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Teun Koopmeiners",      "team": "Juventus",   "goals":  6, "assists": 6,  "appearances": 28, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Francisco Conceição",   "team": "Juventus",   "goals":  5, "assists": 4,  "appearances": 25, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Manuel Locatelli",      "team": "Juventus",   "goals":  2, "assists": 5,  "appearances": 30, "yellow_cards": 6, "red_cards": 0},
    # Lazio
    {"player_name": "Mattia Zaccagni",       "team": "Lazio",      "goals":  9, "assists": 8,  "appearances": 35, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Taty Castellanos",      "team": "Lazio",      "goals":  8, "assists": 3,  "appearances": 29, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Pedro",                 "team": "Lazio",      "goals":  7, "assists": 5,  "appearances": 30, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Nicolò Rovella",        "team": "Lazio",      "goals":  3, "assists": 5,  "appearances": 33, "yellow_cards": 7, "red_cards": 0},
    {"player_name": "Gustav Isaksen",        "team": "Lazio",      "goals":  4, "assists": 4,  "appearances": 28, "yellow_cards": 2, "red_cards": 0},
    # Lecce
    {"player_name": "Nikola Krstović",       "team": "Lecce",      "goals":  7, "assists": 1,  "appearances": 30, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Lameck Banda",          "team": "Lecce",      "goals":  4, "assists": 3,  "appearances": 28, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Patrick Dorgu",         "team": "Lecce",      "goals":  3, "assists": 4,  "appearances": 32, "yellow_cards": 4, "red_cards": 0},
    # Milan
    {"player_name": "Rafael Leão",           "team": "Milan",      "goals": 11, "assists": 9,  "appearances": 34, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Alvaro Morata",         "team": "Milan",      "goals":  9, "assists": 4,  "appearances": 30, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Christian Pulisic",     "team": "Milan",      "goals":  8, "assists": 7,  "appearances": 32, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Tijjani Reijnders",     "team": "Milan",      "goals":  7, "assists": 6,  "appearances": 34, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Ruben Loftus-Cheek",    "team": "Milan",      "goals":  3, "assists": 4,  "appearances": 25, "yellow_cards": 3, "red_cards": 0},
    # Monza
    {"player_name": "Dany Mota",             "team": "Monza",      "goals":  6, "assists": 2,  "appearances": 30, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Daniel Maldini",        "team": "Monza",      "goals":  4, "assists": 4,  "appearances": 28, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Milan Djuric",          "team": "Monza",      "goals":  4, "assists": 1,  "appearances": 26, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Gianluca Caprari",      "team": "Monza",      "goals":  3, "assists": 3,  "appearances": 24, "yellow_cards": 2, "red_cards": 0},
    # Napoli
    {"player_name": "Romelu Lukaku",         "team": "Napoli",     "goals": 11, "assists": 5,  "appearances": 34, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Scott McTominay",       "team": "Napoli",     "goals":  8, "assists": 4,  "appearances": 35, "yellow_cards": 5, "red_cards": 0},
    {"player_name": "David Neres",           "team": "Napoli",     "goals":  7, "assists": 6,  "appearances": 33, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Matteo Politano",       "team": "Napoli",     "goals":  5, "assists": 6,  "appearances": 31, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Khvicha Kvaratskhelia", "team": "Napoli",     "goals":  5, "assists": 7,  "appearances": 18, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Giacomo Raspadori",     "team": "Napoli",     "goals":  4, "assists": 3,  "appearances": 28, "yellow_cards": 2, "red_cards": 0},
    # Parma
    {"player_name": "Dennis Man",            "team": "Parma",      "goals":  6, "assists": 4,  "appearances": 33, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Valentin Mihăilă",      "team": "Parma",      "goals":  5, "assists": 3,  "appearances": 30, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Adrián Bernabé",        "team": "Parma",      "goals":  3, "assists": 5,  "appearances": 32, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Enrico Del Prato",      "team": "Parma",      "goals":  1, "assists": 1,  "appearances": 30, "yellow_cards": 5, "red_cards": 0},
    # Roma
    {"player_name": "Artem Dovbyk",          "team": "Roma",       "goals": 10, "assists": 3,  "appearances": 31, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Paulo Dybala",          "team": "Roma",       "goals":  6, "assists": 5,  "appearances": 22, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Lorenzo Pellegrini",    "team": "Roma",       "goals":  4, "assists": 6,  "appearances": 30, "yellow_cards": 5, "red_cards": 0},
    {"player_name": "Stephan El Shaarawy",   "team": "Roma",       "goals":  4, "assists": 3,  "appearances": 28, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Bryan Cristante",       "team": "Roma",       "goals":  3, "assists": 4,  "appearances": 32, "yellow_cards": 7, "red_cards": 1},
    # Torino
    {"player_name": "Che Adams",             "team": "Torino",     "goals":  7, "assists": 3,  "appearances": 32, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Antonio Sanabria",      "team": "Torino",     "goals":  5, "assists": 2,  "appearances": 28, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Samuele Ricci",         "team": "Torino",     "goals":  2, "assists": 5,  "appearances": 34, "yellow_cards": 6, "red_cards": 0},
    {"player_name": "Borna Sosa",            "team": "Torino",     "goals":  2, "assists": 4,  "appearances": 28, "yellow_cards": 3, "red_cards": 0},
    # Udinese
    {"player_name": "Lorenzo Lucca",         "team": "Udinese",    "goals": 10, "assists": 3,  "appearances": 34, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Florian Thauvin",       "team": "Udinese",    "goals":  5, "assists": 7,  "appearances": 31, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Alexis Sánchez",        "team": "Udinese",    "goals":  3, "assists": 3,  "appearances": 20, "yellow_cards": 2, "red_cards": 0},
    {"player_name": "Hassane Kamara",        "team": "Udinese",    "goals":  1, "assists": 4,  "appearances": 28, "yellow_cards": 5, "red_cards": 0},
    # Venezia
    {"player_name": "Joel Pohjanpalo",       "team": "Venezia",    "goals":  9, "assists": 2,  "appearances": 34, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Gaetano Oristanio",     "team": "Venezia",    "goals":  4, "assists": 4,  "appearances": 30, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Hans Nicolussi Caviglia","team": "Venezia",   "goals":  2, "assists": 3,  "appearances": 29, "yellow_cards": 4, "red_cards": 0},
    # Verona
    {"player_name": "Casper Tengstedt",      "team": "Verona",     "goals":  5, "assists": 1,  "appearances": 25, "yellow_cards": 3, "red_cards": 0},
    {"player_name": "Tijani Noslin",         "team": "Verona",     "goals":  4, "assists": 3,  "appearances": 28, "yellow_cards": 4, "red_cards": 0},
    {"player_name": "Dani Silva",            "team": "Verona",     "goals":  3, "assists": 2,  "appearances": 26, "yellow_cards": 5, "red_cards": 0},
    {"player_name": "Santiago Magnani",      "team": "Verona",     "goals":  2, "assists": 1,  "appearances": 30, "yellow_cards": 6, "red_cards": 0},
]


def poisson(lam: float) -> int:
    """Variabile casuale di Poisson tramite algoritmo di Knuth."""
    L = math.exp(-max(0.01, lam))
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def generate_score(home: str, away: str) -> tuple[int, int]:
    """Genera un risultato realistico basato sui profili delle squadre."""
    h, a = TEAM_PROFILE[home], TEAM_PROFILE[away]
    home_xg = (h["att"] + (2.0 - a["def"])) / 2 + HOME_ADVANTAGE
    away_xg = (a["att"] + (2.0 - h["def"])) / 2
    home_xg = max(0.3, min(4.0, home_xg))
    away_xg = max(0.3, min(4.0, away_xg))
    return poisson(home_xg), poisson(away_xg)


def generate_schedule(teams: list) -> list:
    """Genera il calendario completo andata/ritorno con algoritmo round-robin."""
    n = len(teams)
    assert n % 2 == 0
    first_leg = []
    fixed = teams[0]
    rotatable = list(teams[1:])
    for _ in range(n - 1):
        current = [fixed] + rotatable
        pairs = [(current[j], current[n - 1 - j]) for j in range(n // 2)]
        first_leg.append(pairs)
        rotatable = [rotatable[-1]] + rotatable[:-1]
    second_leg = [[(away, home) for home, away in rnd] for rnd in first_leg]
    return first_leg + second_leg


def main():
    out_dir = Path(__file__).parent
    schedule = generate_schedule(TEAMS)

    matches = []
    for md_idx, round_pairs in enumerate(schedule):
        matchday = md_idx + 1
        match_date = MATCHDAY_DATES[md_idx]
        for home, away in round_pairs:
            hg, ag = generate_score(home, away)
            matches.append({
                "matchday":    matchday,
                "date":        match_date.strftime("%Y-%m-%d"),
                "home_team":   home,
                "away_team":   away,
                "home_goals":  hg,
                "away_goals":  ag,
                "status":      "played",
            })

    matches_path = out_dir / "matches.csv"
    with open(matches_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["matchday", "date", "home_team", "away_team",
                                               "home_goals", "away_goals", "status"])
        writer.writeheader()
        writer.writerows(matches)
    print(f"✅ {len(matches)} partite scritte in {matches_path}")

    players_path = out_dir / "players.csv"
    with open(players_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["player_name", "team", "goals", "assists",
                                               "appearances", "yellow_cards", "red_cards"])
        writer.writeheader()
        writer.writerows(KEY_PLAYERS)
    print(f"✅ {len(KEY_PLAYERS)} giocatori scritti in {players_path}")


if __name__ == "__main__":
    main()
