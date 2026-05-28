"""Core del chatbot: orchestrazione intent → query → risposta formattata."""
from intent_detector import (
    is_greeting, is_out_of_scope, detect_intent,
    extract_matchday, extract_team, extract_player,
)
from query_engine import (
    get_standings, get_results, get_calendar,
    get_top_scorers, get_player_stats, get_team_stats,
)
from data_loader import DataLoader

OUT_OF_SCOPE_MSG = "Questo argomento non rientra nelle mie competenze"
NO_DATA_MSG = "Non ho trovato dati per questa richiesta nel dataset disponibile."


# ── Formatter helpers ────────────────────────────────────────────────────────

def _fmt_standings(rows: list[dict], matchday: int) -> str:
    header = f"📊 Classifica Serie A 2024/25 — Giornata {matchday}\n\n"
    header += f"{'Pos':<4} {'Squadra':<16} {'G':>3} {'V':>3} {'P':>3} {'S':>3} " \
              f"{'GF':>3} {'GS':>3} {'DR':>4} {'Pt':>4}\n"
    header += "─" * 56 + "\n"
    lines = []
    for r in rows:
        dr = f"+{r['DR']}" if r["DR"] > 0 else str(r["DR"])
        lines.append(
            f"{r['Pos']:<4} {r['Squadra']:<16} {r['G']:>3} {r['V']:>3} "
            f"{r['P']:>3} {r['S']:>3} {r['GF']:>3} {r['GS']:>3} {dr:>4} {r['Pt']:>4}"
        )
    return header + "\n".join(lines)


def _fmt_results(rows: list[dict], matchday: int | None) -> str:
    if not rows:
        return NO_DATA_MSG
    if matchday:
        title = f"⚽ Risultati — {matchday}ª Giornata"
    else:
        title = "⚽ Risultati"
    lines = [title, ""]
    cur_md = None
    for r in rows:
        if matchday is None and r["matchday"] != cur_md:
            cur_md = r["matchday"]
            lines.append(f"  [{cur_md}ª Giornata — {r['date']}]")
        lines.append(
            f"  {r['home_team']:<16} {r['home_goals']:>2} - {r['away_goals']:<2}  {r['away_team']}"
        )
    return "\n".join(lines)


def _fmt_calendar(rows: list[dict], team: str | None) -> str:
    if not rows:
        return NO_DATA_MSG
    title = f"📅 Calendario — {team}" if team else "📅 Calendario Serie A 2024/25"
    lines = [title, ""]
    for r in rows:
        score = (
            f"{r['home_goals']} - {r['away_goals']}"
            if r["status"] == "played"
            else "da giocare"
        )
        lines.append(
            f"  GN {r['matchday']:>2}  {r['date']}  "
            f"{r['home_team']:<16} {score:^9} {r['away_team']}"
        )
    return "\n".join(lines)


def _fmt_top_scorers(rows: list[dict]) -> str:
    if not rows:
        return NO_DATA_MSG
    lines = ["🥅 Classifica Marcatori — Serie A 2024/25", ""]
    for i, r in enumerate(rows, 1):
        lines.append(f"  {i:>2}. {r['player_name']:<24} ({r['team']})  {r['goals']} gol")
    return "\n".join(lines)


def _fmt_player(r: dict) -> str:
    return (
        f"👤 {r['player_name']} — {r['team']} — Serie A 2024/25\n\n"
        f"  Presenze:            {r['appearances']}\n"
        f"  Gol:                 {r['goals']}\n"
        f"  Assist:              {r['assists']}\n"
        f"  Cartellini gialli:   {r['yellow_cards']}\n"
        f"  Cartellini rossi:    {r['red_cards']}"
    )


def _fmt_team_stats(team: str, s: dict) -> str:
    dr = f"+{s['DR']}" if s["DR"] > 0 else str(s["DR"])
    pos = s["Pos"] if s["Pos"] else "N/D"
    g = s["G"] or 1  # evita divisione per zero

    lines = [
        f"🏟️  {team} — Stagione 2024/25",
        "",
        f"  Posizione in classifica: {pos}ª",
        f"  Partite giocate:  {s['G']}",
        f"  Vittorie:         {s['V']}",
        f"  Pareggi:          {s['P']}",
        f"  Sconfitte:        {s['S']}",
        f"  Gol fatti:        {s['GF']}  (media {s['MediaGF']} a partita)",
        f"  Gol subiti:       {s['GS']}  (media {s['MediaGS']} a partita)",
        f"  Differenza reti:  {dr}",
        f"  Punti:            {s['Pt']}",
    ]

    # Statistiche aggiuntive (presenti solo con il nuovo schema)
    if s.get("Tiri", 0) > 0:
        lines += [
            "",
            f"  Tiri totali:      {s['Tiri']}  (media {round(s['Tiri']/g,1)} a partita)",
            f"  Tiri in porta:    {s['TiriPorta']}  (media {round(s['TiriPorta']/g,1)} a partita)",
            f"  Corner:           {s['Corner']}",
            f"  Falli commessi:   {s['Falli']}",
            f"  Cartellini gialli:{s['Gialli']}",
            f"  Cartellini rossi: {s['Rossi']}",
        ]

    return "\n".join(lines)


# ── Chatbot ──────────────────────────────────────────────────────────────────

class Chatbot:
    def __init__(self) -> None:
        self._loader = DataLoader()

    def respond(self, message: str) -> str:
        message = message.strip()
        if not message:
            return "Inserisci una domanda sulla Serie A 2024/25."

        # 1. Saluto
        if is_greeting(message):
            return (
                "Ciao! Sono il chatbot della Serie A 2024/25. 🏆\n"
                "Posso rispondere a domande su classifica, risultati, "
                "statistiche di giocatori e squadre, calendario e marcatori.\n"
                "Come posso aiutarti?"
            )

        # 2. Fuori scope
        if is_out_of_scope(message):
            return OUT_OF_SCOPE_MSG

        # 3. Entità
        matchday = extract_matchday(message)
        team = extract_team(message)
        player = extract_player(message, self._loader.get_player_names())

        # 4. Intent
        intent = detect_intent(message)

        # 5. Esegui query e formatta risposta
        try:
            return self._dispatch(intent, message, matchday, team, player)
        except Exception as exc:
            return f"Errore nel recupero dei dati: {exc}"

    def _dispatch(
        self,
        intent: str,
        message: str,
        matchday: int | None,
        team: str | None,
        player: str | None,
    ) -> str:
        # ── classifica ────────────────────────────────────────────────────
        if intent == "classifica":
            rows, md = get_standings(matchday)
            return _fmt_standings(rows, md)

        # ── risultati ─────────────────────────────────────────────────────
        if intent == "risultati":
            rows, md = get_results(matchday=matchday, team=team)
            return _fmt_results(rows, md)

        # ── marcatori ─────────────────────────────────────────────────────
        if intent == "marcatori":
            # Se è chiesto di uno specifico giocatore, mostra le sue stat
            if player:
                stats = get_player_stats(player)
                if stats:
                    return _fmt_player(stats)
            return _fmt_top_scorers(get_top_scorers(15))

        # ── statistiche giocatore ─────────────────────────────────────────
        if intent == "statistiche_giocatore":
            if player:
                stats = get_player_stats(player)
                if stats:
                    return _fmt_player(stats)
                return f"Non ho trovato dati per il giocatore '{player}'."
            return "Per quale giocatore vuoi le statistiche? Specifica il nome."

        # ── statistiche squadra ───────────────────────────────────────────
        if intent == "statistiche_squadra":
            if team:
                stats = get_team_stats(team)
                if stats:
                    return _fmt_team_stats(team, stats)
                return f"Non ho trovato dati per la squadra '{team}'."
            return "Per quale squadra vuoi le statistiche? Specifica il nome."

        # ── calendario ────────────────────────────────────────────────────
        if intent == "calendario":
            rows = get_calendar(team=team, matchday=matchday)
            return _fmt_calendar(rows, team)

        # ── intent sconosciuto ────────────────────────────────────────────
        # Tenta di rispondere con ciò che è stato estratto
        if player:
            stats = get_player_stats(player)
            if stats:
                return _fmt_player(stats)
        if team:
            stats = get_team_stats(team)
            if stats:
                return _fmt_team_stats(team, stats)
        if matchday:
            rows, _ = get_standings(matchday)
            return _fmt_standings(rows, matchday)

        return (
            "Non ho capito la domanda. Puoi chiedermi ad esempio:\n"
            "• Classifica alla 20ª giornata\n"
            "• Risultati della 5ª giornata\n"
            "• Quanti gol ha segnato Lautaro Martinez?\n"
            "• Statistiche del Napoli\n"
            "• Chi sono i migliori marcatori?"
        )
