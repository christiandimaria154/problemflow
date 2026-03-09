# ProblemFlow GitHub Pages

Progetto statico per pubblicare automaticamente i **Problemi della settimana** per:

- **3C INFO — C**
- **4C INFO — Java**

Pubblicazione automatica:
- **lunedì**
- **giovedì**

## Struttura del repository

- `index.html` → pagina pubblica completa
- `widget.html` → widget da incorporare in Moodle tramite iframe
- `current.json` → problemi attualmente visibili
- `data/problems.json` → archivio dei problemi
- `data/state.json` → stato interno della rotazione
- `scripts/publish.py` → script che aggiorna `current.json`
- `.github/workflows/publish-problems.yml` → workflow GitHub Actions
- `CNAME` → custom domain per GitHub Pages
- `moodle_iframe_snippet.html` → snippet pronto per Moodle

## Passo passo

### 1. Crea un repository GitHub pubblico
Esempio: `problemflow`

### 2. Carica tutti i file
Carica nel repository il contenuto di questa cartella.

### 3. Attiva GitHub Pages
Vai in:

`Settings -> Pages`

Imposta:
- **Source**: `Deploy from a branch`
- **Branch**: `main`
- **Folder**: `/ (root)`

### 4. Controlla il sito
Dopo qualche minuto troverai:
- `https://TUO-USERNAME.github.io/problemflow/`
- `https://TUO-USERNAME.github.io/problemflow/widget.html`
- `https://TUO-USERNAME.github.io/problemflow/current.json`

### 5. Abilita la scrittura del workflow
Vai in:
`Settings -> Actions -> General -> Workflow permissions`

Seleziona:
- **Read and write permissions**

### 6. Pubblica manualmente la prima volta
Vai in:
`Actions -> Publish problems -> Run workflow`

Lancia:
- una volta con `lunedi`
- una volta con `giovedi`

### 7. Personalizza il sottodominio
Se vuoi usare `problems.dimariamoodle.it`:
- lascia il file `CNAME` con:
  `problems.dimariamoodle.it`
- configura il DNS del sottodominio verso GitHub Pages

### 8. Inserisci il widget in Moodle
Apri `moodle_iframe_snippet.html` e sostituisci l'URL con quello reale del sito.

## Come funziona la rotazione
- Lo script sceglie un problema per **3C** e uno per **4C**
- Tiene separati gli slot:
  - `lunedi`
  - `giovedi`
- Evita di ripetere lo stesso problema finché non esaurisce quelli disponibili per quello slot

## Archivio iniziale
Nel file `data/problems.json` trovi già:
- **20 problemi per 3C**
- **20 problemi per 4C**

## Nota pratica
I cron di GitHub Actions usano orario **UTC**.
