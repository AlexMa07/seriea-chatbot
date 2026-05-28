# Serie A 2024/25 Chatbot

Chatbot specializzato **esclusivamente** sul Campionato di Serie A italiana stagione **2024/25**.

Risponde a domande su classifica, risultati, marcatori, statistiche di giocatori e squadre, calendario delle partite.
Qualsiasi domanda che non riguardi la Serie A 2024/25 viene rifiutata con la risposta:
> *"Questo argomento non rientra nelle mie competenze"*

---

## Indice

1. [Requisiti di sistema](#requisiti-di-sistema)
2. [Struttura del progetto](#struttura-del-progetto)
3. [Installazione](#installazione)
4. [Avvio del server](#avvio-del-server)
5. [Arresto del server](#arresto-del-server)
6. [Utilizzo del chatbot](#utilizzo-del-chatbot)
7. [Dataset e dati reali](#dataset-e-dati-reali)
8. [Architettura tecnica](#architettura-tecnica)

---

## Requisiti di sistema

| Componente | Versione minima | Note |
|---|---|---|
| **Python** | 3.10+ | Testato su 3.12.3 |
| **pip** | qualsiasi | Incluso con Python |
| Sistema operativo | Linux / macOS / Windows | Su Windows usare PowerShell o WSL |

Nessun database esterno, nessun account cloud, nessuna connessione internet richiesta a runtime.

---

## Struttura del progetto

```
chatbot/
├── requirements.txt                  # Dipendenze Python
├── README.md                         # Questo file
│
├── backend/
│   ├── main.py                       # Applicazione FastAPI (entry point)
│   ├── chatbot.py                    # Logica principale del chatbot
│   ├── intent_detector.py            # Rilevamento intenti (rule-based)
│   ├── query_engine.py               # Query sui dati CSV
│   ├── data_loader.py                # Caricamento e cache dei CSV
│   │
│   └── data/
│       ├── generate_sample_data.py   # Script generatore dati campione
│       ├── matches.csv               # 380 partite (38 giornate × 10 match)
│       └── players.csv               # 89 giocatori con statistiche
│
└── frontend/
    ├── index.html                    # Interfaccia chat
    ├── style.css                     # Stile (tema scuro)
    └── script.js                     # Logica frontend
```

---

## Installazione

### 1. Copia il progetto sul PC

Copia la cartella `chatbot/` sul PC di destinazione (USB, rete, zip, ecc.).

### 2. Verifica Python

```bash
python3 --version
```

Se Python non è installato:

- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt update && sudo apt install python3 python3-pip -y
  ```
- **macOS:**
  ```bash
  brew install python
  ```
- **Windows:** scarica l'installer da [python.org](https://www.python.org/downloads/) e spunta *"Add Python to PATH"* durante l'installazione. Poi usa `python` al posto di `python3`.

### 3. Installa le dipendenze Python

Dalla cartella `chatbot/`:

```bash
pip3 install -r requirements.txt
```

> Su Windows: `pip install -r requirements.txt`

Le librerie installate sono:

| Libreria | Versione | Scopo |
|---|---|---|
| `fastapi` | 0.115.0 | Framework web per le API |
| `uvicorn[standard]` | 0.32.0 | Server ASGI ad alte prestazioni |
| `pandas` | 2.2.3 | Lettura e query dei file CSV |
| `python-multipart` | 0.0.12 | Parsing form data |

### 4. Genera i dati campione (solo al primo avvio)

Se i file `matches.csv` e `players.csv` non esistono già nella cartella `backend/data/`:

```bash
python3 backend/data/generate_sample_data.py
```

Output atteso:
```
✅ 380 partite scritte in .../backend/data/matches.csv
✅ 89 giocatori scritti in .../backend/data/players.csv
```

> ⚠️ I dati generati sono **campione/simulati**. Per dati reali vedi la sezione [Dataset e dati reali](#dataset-e-dati-reali).

---

## Avvio del server

Dalla cartella `chatbot/`:

### Linux / macOS

```bash
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Windows

```powershell
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Output atteso all'avvio

```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Accedi al chatbot

Apri il browser e vai su:

```
http://localhost:8000
```

Se vuoi accedere da un **altro PC sulla stessa rete**, usa l'indirizzo IP del PC che esegue il server:

```
http://<IP-DEL-SERVER>:8000
```

Per trovare l'IP del server:
- Linux/macOS: `ip a` oppure `hostname -I`
- Windows: `ipconfig`

### Avvio in background (Linux/macOS)

Per eseguire il server in background senza tenere aperto il terminale:

```bash
cd backend
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/chatbot.log 2>&1 &
echo "Server avviato con PID $!"
```

Verifica che sia attivo:

```bash
curl http://localhost:8000/api/health
# Risposta attesa: {"status":"ok","season":"Serie A 2024/25"}
```

---

## Arresto del server

### Se il server è in primo piano

Premi `CTRL + C` nel terminale.

### Se il server è in background (Linux/macOS)

Trova il PID del processo e terminalo:

```bash
# Trova il PID
pgrep -a uvicorn

# Termina il processo (sostituisci XXXX con il PID trovato)
kill XXXX
```

Oppure in un solo comando:

```bash
pkill -f "uvicorn main:app"
```

### Windows (background con start)

```powershell
# Trova il PID
Get-Process python

# Termina
Stop-Process -Id XXXX
```

---

## Utilizzo del chatbot

### Interfaccia web

Apri `http://localhost:8000` nel browser. Usa i pulsanti di suggerimento rapido oppure scrivi liberamente nel campo di testo.

### Esempi di domande supportate

| Domanda | Tipo di risposta |
|---|---|
| `Qual è la classifica attuale?` | Classifica completa (ultima giornata) |
| `Classifica alla 15ª giornata` | Classifica aggiornata a quella giornata |
| `Risultati della 10ª giornata` | Tutti i risultati della giornata |
| `Chi sono i migliori marcatori?` | Top 15 cannonieri della stagione |
| `Quanti gol ha segnato Lautaro Martinez?` | Statistiche complete del giocatore |
| `Quante presenze ha Moise Kean?` | Presenze, gol, assist, cartellini |
| `Statistiche del Napoli` | Record completo della squadra |
| `Come sta andando la Juventus?` | Statistiche e posizione in classifica |
| `Calendario Inter` | Tutte le partite dell'Inter con risultati |
| `Quando ha giocato l'Atalanta alla giornata 20?` | Partite filtrate |

### Domande fuori scope

Qualsiasi domanda non riguardante la Serie A 2024/25 riceve questa risposta fissa:

```
Questo argomento non rientra nelle mie competenze
```

Esempi di domande rifiutate: Champions League, Premier League, Serie B, Coppa Italia, altri sport, altre stagioni (es. 2023/24), previsioni future.

### API REST (uso programmatico)

Il chatbot espone un endpoint HTTP utilizzabile da qualsiasi client:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Chi sono i migliori marcatori?"}'
```

Risposta:
```json
{
  "response": "🥅 Classifica Marcatori — Serie A 2024/25\n\n   1. Mateo Retegui  (Atalanta)  24 gol\n..."
}
```

---

## Dataset e dati reali

### File CSV utilizzati

#### `backend/data/matches-v2.csv` — Partite

| Colonna | Tipo | Descrizione |
|---|---|---|
| `Date` | date (YYYY-MM-DD) | Data della partita |
| `HomeTeam` | string | Squadra di casa |
| `AwayTeam` | string | Squadra ospite |
| `FTHG` | integer | Gol casa (tempo regolamentare) |
| `FTAG` | integer | Gol ospite (tempo regolamentare) |
| `FTR` | string | Risultato finale: H=Casa, D=Pareggio, A=Ospite |
| `HTHG` | integer | Gol casa (primo tempo) |
| `HTAG` | integer | Gol ospite (primo tempo) |
| `HTR` | string | Risultato primo tempo |
| `Referee` | string | Arbitro (può essere vuoto) |
| `HS` / `AS` | integer | Tiri totali casa / ospite |
| `HST` / `AST` | integer | Tiri in porta casa / ospite |
| `HF` / `AF` | integer | Falli casa / ospite |
| `HC` / `AC` | integer | Corner casa / ospite |
| `HY` / `AY` | integer | Cartellini gialli casa / ospite |
| `HR` / `AR` | integer | Cartellini rossi casa / ospite |

> Il numero di giornata viene calcolato automaticamente ordinando le partite per data e raggruppandole in blocchi di 10 (38 giornate × 10 partite = 380 totali).

#### `backend/data/players.csv` — Giocatori

| Colonna | Tipo | Descrizione |
|---|---|---|
| `player_name` | string | Nome e cognome del giocatore |
| `team` | string | Squadra di appartenenza |
| `goals` | integer | Gol segnati |
| `assists` | integer | Assist |
| `appearances` | integer | Presenze |
| `yellow_cards` | integer | Cartellini gialli |
| `red_cards` | integer | Cartellini rossi |

### Squadre riconosciute

Atalanta, Bologna, Cagliari, Como, Empoli, Fiorentina, Genoa, Inter, Juventus, Lazio, Lecce, Milan, Monza, Napoli, Parma, Roma, Torino, Udinese, Venezia, Verona.

---

## Architettura tecnica

```
Browser  ──POST /api/chat──▶  FastAPI (main.py)
                                    │
                               Chatbot (chatbot.py)
                               ┌────┴────────────┐
                        Intent Detector      Query Engine
                        (intent_detector.py) (query_engine.py)
                                                  │
                                           Data Loader
                                           (data_loader.py)
                                                  │
                                      matches.csv / players.csv
```

- **Nessun LLM**: il rilevamento degli intenti è completamente rule-based (regex su testo italiano).
- **Nessun database**: tutti i dati sono letti da file CSV tramite pandas.
- **Frontend statico**: servito direttamente da FastAPI, nessun framework JS.
