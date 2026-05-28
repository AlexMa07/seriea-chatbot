"""Rilevamento intenti e riconoscimento entità per domande sulla Serie A 2024/25."""
import re
from typing import Optional, Tuple

SERIE_A_TEAMS: list[str] = [
    "Atalanta", "Bologna", "Cagliari", "Como", "Empoli",
    "Fiorentina", "Genoa", "Inter", "Juventus", "Lazio",
    "Lecce", "Milan", "Monza", "Napoli", "Parma",
    "Roma", "Torino", "Udinese", "Venezia", "Verona",
]

# Alias squadre → nome canonico
TEAM_ALIASES: dict[str, str] = {
    "inter milan": "Inter", "internazionale": "Inter", "nerazzurri": "Inter",
    "fc inter": "Inter", "f.c. inter": "Inter",
    "ac milan": "Milan", "a.c. milan": "Milan", "rossoneri": "Milan", "diavolo": "Milan",
    "juve": "Juventus", "bianconeri": "Juventus", "vecchia signora": "Juventus",
    "partenopei": "Napoli", "azzurri": "Napoli",
    "as roma": "Roma", "giallorossi": "Roma",
    "ss lazio": "Lazio", "biancocelesti": "Lazio",
    "dea": "Atalanta", "la dea": "Atalanta",
    "viola": "Fiorentina", "gigliati": "Fiorentina",
    "rossoblu": "Bologna", "rossoblù": "Bologna",
    "toro": "Torino", "granata": "Torino",
    "grifone": "Genoa",
    "hellas verona": "Verona", "hellas": "Verona", "gialloblu": "Verona",
    "crociati": "Parma",
    "lariani": "Como",
    "arancioneroverdi": "Venezia",
    "friulani": "Udinese",
}

# Pattern che indicano argomenti fuori scope
_OUT_OF_SCOPE: list[str] = [
    r"\bchampions\s*league\b", r"\buchampions\b",
    r"\beuropa\s*league\b", r"\bconference\s*league\b",
    r"\bpremier\s*league\b", r"\bepl\b",
    r"\bbundesliga\b", r"\bla\s*liga\b", r"\bligue\s*1\b",
    r"\bserie\s+[bc]\b",
    r"\bcoppa\s+italia\b", r"\bsupercoppa\b",
    r"\bworld\s+cup\b", r"\bcoppa\s+del\s+mondo\b", r"\bmondiali?\b",
    r"\beuropei?\b(?!\s+della\s+serie)",   # "europeo/europei" ma non "del campionato europeo della serie"
    r"\bnazionale\s+(italiana|di\s+calcio)\b",
    r"\bnba\b", r"\bnfl\b", r"\bformula\s*1\b", r"\bf1\b",
    r"\btennis\b", r"\bbasket(ball)?\b", r"\bciclismo\b",
    r"\bvolley(ball)?\b", r"\bnuoto\b", r"\batletismo\b", r"\brugby\b",
    r"\bgolf\b", r"\bcricket\b", r"\bbaseball\b",
    # Stagioni diverse
    r"\b202[012]/2[123]\b", r"\b2023[/-]24\b", r"\b2022[/-]23\b",
    r"\b2021[/-]22\b", r"\bstagione\s+scorsa\b", r"\banno\s+scorso\b",
    r"\bprossima\s+stagione\b",
]

_OUT_OF_SCOPE_RE = re.compile("|".join(_OUT_OF_SCOPE), re.IGNORECASE)

# Keyword di calcio che confermano il contesto Serie A (prefissi senza \b finale)
_FOOTBALL_KW = re.compile(
    r"\b(calcio|serie\s*a|campionato|giornata|partita|gara|classifica|"
    r"risultat|gol|marcator|assist|squadra|giocator|allenator|arbitr|"
    r"rigore|punteggio|calendario|presenze|cartellini|capocannoniere|"
    r"bomber|vittoria|pareggio|sconfitta|punti|statistiche|stagione)",
    re.IGNORECASE,
)

_GREETING_RE = re.compile(
    r"^\s*(ciao|salve|buongiorno|buonasera|buon\s*pomeriggio|hey|hi|hello)\b",
    re.IGNORECASE,
)

# ── Intent patterns ──────────────────────────────────────────────────────────

_STANDINGS_RE = re.compile(
    r"\b(classifica|classifiche|graduatoria|posizione\s+in\s+tabella|"
    r"chi\s+[èe]\s+primo|chi\s+[èe]\s+in\s+testa|chi\s+guida|"
    r"chi\s+comanda|chi\s+[èe]\s+in\s+vetta|testa\s+alla)",
    re.IGNORECASE,
)
_RESULTS_RE = re.compile(
    r"\b(risultat|punteggio|come\s+[èe]\s+andat|come\s+ha\s+finito|"
    r"ha\s+vinto|ha\s+pareggiato|ha\s+perso|[èe]\s+finita|finita)",
    re.IGNORECASE,
)
_SCORERS_RE = re.compile(
    r"\b(marcator|capocannoniere|chi\s+segna|chi\s+ha\s+segnato|"
    r"migliori?\s+(marcator|bomber)|classifica\s+marcator|più\s+gol|bomber)",
    re.IGNORECASE,
)
_PLAYER_RE = re.compile(
    r"\b(quanti\s+gol|quanti\s+assist|quante\s+presenze|quanti\s+cartellini|"
    r"statistiche\s+d[i']|rendimento\s+d[i'])",
    re.IGNORECASE,
)
_TEAM_STATS_RE = re.compile(
    r"\b(statistiche\s+(dell[a']|del)|come\s+sta\s+andando|"
    r"rendimento\s+(della|del)|record\s+della|stagione\s+(della|del))",
    re.IGNORECASE,
)
_CALENDAR_RE = re.compile(
    r"\b(calendario|quando\s+gioca|quando\s+si\s+gioca|prossima\s+partita|"
    r"prossimo\s+turno|partite\s+d[i']|tutte\s+le\s+partite)",
    re.IGNORECASE,
)


def is_greeting(message: str) -> bool:
    return bool(_GREETING_RE.match(message))


def is_out_of_scope(message: str) -> bool:
    if _OUT_OF_SCOPE_RE.search(message):
        return True
    # Se non ci sono keyword calcistiche NÉ nomi di squadre → fuori scope
    has_football = bool(_FOOTBALL_KW.search(message))
    has_team = bool(extract_team(message))
    if not has_football and not has_team:
        return True
    return False


def extract_matchday(text: str) -> Optional[int]:
    """Estrae il numero di giornata dal testo."""
    patterns = [
        r"(\d+)[aª°]?\s*giornata",
        r"giornata\s+(?:numero\s+)?(\d+)",
        r"turno\s+(?:numero\s+)?(\d+)",
        r"(\d+)[aª°]?\s*turno",
        r"giornata\s+n[°.]?\s*(\d+)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 38:
                return val
    return None


def extract_team(text: str) -> Optional[str]:
    """Estrae il nome canonico della squadra dal testo."""
    lower = text.lower()
    # Prima controlla alias multi-parola (più lunghi prima)
    for alias in sorted(TEAM_ALIASES, key=len, reverse=True):
        if alias in lower:
            return TEAM_ALIASES[alias]
    # Poi i nomi ufficiali
    for team in SERIE_A_TEAMS:
        if re.search(r"\b" + re.escape(team) + r"\b", text, re.IGNORECASE):
            return team
    return None


def extract_player(text: str, known_players: list[str]) -> Optional[str]:
    """Estrae il nome di un giocatore dal testo cercando cognome o nome completo."""
    lower = text.lower()
    best: Optional[str] = None
    best_len = 0
    for name in known_players:
        parts = name.lower().split()
        # Cerca cognome (ultimo token) o nome completo
        for part in [name.lower(), parts[-1]]:
            if re.search(r"\b" + re.escape(part) + r"\b", lower):
                if len(part) > best_len:
                    best = name
                    best_len = len(part)
    return best


def detect_intent(message: str) -> str:
    """
    Ritorna uno dei seguenti intent:
    greeting | classifica | risultati | marcatori | statistiche_giocatore
    | statistiche_squadra | calendario | unknown
    """
    if is_greeting(message):
        return "greeting"

    scores: dict[str, int] = {
        "classifica":             0,
        "risultati":              0,
        "marcatori":              0,
        "statistiche_giocatore":  0,
        "statistiche_squadra":    0,
        "calendario":             0,
    }

    if _STANDINGS_RE.search(message):
        scores["classifica"] += 3
    if _RESULTS_RE.search(message):
        scores["risultati"] += 3
    if _SCORERS_RE.search(message):
        scores["marcatori"] += 3
    if _PLAYER_RE.search(message):
        scores["statistiche_giocatore"] += 3
    if _TEAM_STATS_RE.search(message):
        scores["statistiche_squadra"] += 2
    if _CALENDAR_RE.search(message):
        scores["calendario"] += 3

    # Keyword aggiuntive di rinforzo
    msg_lower = message.lower()

    if re.search(r"\bgol\b", msg_lower) and re.search(r"\b(segnato|segna|reti)\b", msg_lower):
        scores["statistiche_giocatore"] += 2
        scores["marcatori"] += 1

    if re.search(r"\bassist", msg_lower):
        scores["statistiche_giocatore"] += 2

    if re.search(r"\bpresenz", msg_lower):
        scores["statistiche_giocatore"] += 2

    if re.search(r"\bcartellini?", msg_lower):
        scores["statistiche_giocatore"] += 2

    if re.search(r"\b(risultato|punteggio)\b", msg_lower):
        scores["risultati"] += 2

    if re.search(r"\b(quando|prossim|calendari)", msg_lower):
        scores["calendario"] += 1

    best_intent = max(scores, key=lambda k: scores[k])
    return best_intent if scores[best_intent] > 0 else "unknown"
