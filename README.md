# Second Brain Keeper (`sbk`)

> Motore universale di governance, refactoring atomico, diagnostica e manutenzione per Second Brain, Obsidian e archivi documentali Markdown.

[![CI](https://github.com/lucadileo9/second-brain-keeper/actions/workflows/ci.yml/badge.svg)](https://github.com/lucadileo9/second-brain-keeper/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/second-brain-keeper.svg)](https://pypi.org/project/second-brain-keeper/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://pypi.org/project/second-brain-keeper/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

---

## Panoramica

**`second-brain-keeper`** (distribuito tramite il binario da riga di comando **`sbk`** e come libreria Python **`sbk`**) è un sistema di livello enterprise progettato per presidiare, normalizzare e manutenere basi di conoscenza e archivi di note Markdown su larga scala.

Il sistema e ingegnerizzato secondo un'**architettura a doppia testa**:

1. **SDK Python Programmatico ([`Vault`](https://github.com/lucadileo9/second-brain-keeper/blob/main/docs/architecture/facade.md))**: API orientata agli oggetti, priva di effetti collaterali a terminale (senza stampe spurie o `sys.exit`), che scambia modelli di dominio immutabili ed e nativamente predisposta per script di automazione, pipeline dati e server MCP per agenti AI autonomi.
2. **Command Line Interface ([`sbk`](https://github.com/lucadileo9/second-brain-keeper/blob/main/docs/cli/overview.md))**: Interfaccia moderna a 20 comandi, arricchita con rendering Rich, simulazioni di sicurezza (`--dry-run`), formati serializzabili (`--format json|yaml|csv`) e codici di ritorno semantici POSIX (`ExitCode`).

Tutte le operazioni mutative sono incapsulate in un **Transaction Journal atomico con hashing crittografico SHA-256 e rollback LIFO**: qualsiasi creazione, rinomina, spostamento o cancellazione puo essere annullata all'istante tramite `sbk undo` e poi riapplicata tramite `sbk redo`.

---

## Installazione

### Tramite Pip (Ambiente Virtuale)
```bash
pip install second-brain-keeper
```
Il comando mette a disposizione immediatamente l'eseguibile `sbk` nel proprio ambiente di lavoro.

### Installazione per Sviluppo e Contributi
```bash
git clone https://github.com/lucadileo9/second-brain-keeper.git
cd second-brain-keeper
python3 -m venv .venv
source .venv/bin/activate
make install-dev
pre-commit install
```
L'installazione di sviluppo registra l'ambiente in modalita editable ed attiva i guardrail git locali tramite `pre-commit`.

---

## Primi Passi

> [!TIP] Ambiente di Prova Protetto - Sandbox
> Per familiarizzare con le funzionalita senza rischiare di alterare note reali, e disponibile la modalita sandbox isolata:
> ```bash
> sbk sandbox init
> export SBK_VAULT=$(sbk sandbox path)
> sbk --root "$SBK_VAULT" audit
> ```
> Per la guida completa ed esempi passo-passo, consultare la [**Guida alla Sandbox**](https://github.com/lucadileo9/second-brain-keeper/blob/main/docs/cli/sandbox_guide.md).

### 1. Inizializzare la Configurazione del Vault
```bash
sbk init --target /percorso/del/tuo/Vault
```
Genera il file guida `vault.toml` con le convenzioni di denominazione (`Title_Case`), i tag ammessi, le estensioni consentite e le soglie di archiviazione.

### 2. Eseguire l'Audit Diagnostico a 5 Fasi
```bash
sbk audit
```
Verifica filesystem, denominazione, conformita frontmatter YAML, tassonomia controllata dei tag e integrita dei wikilink (inclusi link rotti ed embed orfani), calcolando il **Vault Health Score** (da 0.0 a 100.0).

### 3. Creare una Nuova Nota Standardizzata
```bash
sbk create "Architettura a Microservizi" --type Appunto --tags "tech/architettura,tech/cloud"
```
Deposita la nota nell'area di staging (`00_Inbox/Architettura_A_Microservizi.md` o cartella specificata con `--folder`), inietta le variabili nel template e aggiorna il file indice MOC `00_Indice.md`.

### 4. Rinominare con Refactoring Globale dei Backlink
```bash
sbk rename 10-19_Progetti/vecchio_progetto.md Progetto_Nuovo
```
Rinomina il file e aggiorna simultaneamente tutti i collegamenti `[[...]]` che puntavano al vecchio nome all'interno dell'intero Vault.

### 5. Annullare o Riapplicare un'Operazione
```bash
# Annulla l'ultima transazione
sbk undo

# Riapplica l'operazione precedentemente annullata
sbk redo
```

---

## Tabella Sinottica dei 20 Comandi CLI

Per la consultazione dettagliata di argomenti, opzioni ed esempi d'uso per ciascun comando, consultare il [**Manuale di Riferimento dei Comandi CLI**](https://github.com/lucadileo9/second-brain-keeper/blob/main/docs/cli/commands_reference.md).

| Comando | Sintassi di Esempio | Descrizione Operativa |
| :--- | :--- | :--- |
| **`init`** | `sbk init [--force]` | Genera il file di configurazione predefinito `vault.toml`. |
| **`audit`** | `sbk audit [--target <path>] [--step 1..5] [-o report.md]` | Diagnostica a 5 fasi con calcolo del Vault Health Score. |
| **`clean-attachments`** | `sbk clean-attachments [--dry-run]` | Bonifica file orfani tramite soft-delete reversibile in `.trash/`. |
| **`normalize-names`** | `sbk normalize-names [--dry-run]` | Converte in `Title_Case` e riscrive contestualmente i backlink. |
| **`generate-indices`** | `sbk generate-indices [--all] [--dry-run]` | Genera o aggiorna i file MOC `00_Indice.md` di cartella. |
| **`frontmatter`** | `sbk frontmatter set-type --target n.md --type Appunto` | Ispeziona o modifica metadati YAML (`tipo`, tag). |
| **`history`** | `sbk history [--limit 20] [--format json] [-o FILE]` | Mostra lo storico delle transazioni atomiche del Journal. |
| **`undo`** | `sbk undo [--tx <id>] [--dry-run]` | Ripristina lo stato precedente. |
| **`redo`** | `sbk redo [--tx <id>] [--dry-run]` | Riapplica l'ultima transazione annullata tramite `undo`. |
| **`rename`** | `sbk rename vecchio.md Nuovo.md` | Rinomina una nota con sincronizzazione globale di backlink e MOC. |
| **`move`** | `sbk move nota.md 10-19_Progetti/` | Sposta file o cartelle aggiornando entrambi i MOC di area. |
| **`archive`** | `sbk archive Progetto_X/ [--no-tombstone]` | Trasferisce in cold storage e deposita scheda tombstone. |
| **`offload`** | `sbk offload [target] [--dry-run]` | Sposta allegati pesanti in cold storage rimpiazzando i link. |
| **`tags`** | `sbk tags add tech/rust [--section "Tecnologia"]` | Gestisce il vocabolario controllato `00_Tassonomia_Tag.md`. |
| **`config`** | `sbk config set naming_style Title_Case` | Ispeziona o modifica impostazioni a caldo in `vault.toml`. |
| **`search`** | `sbk search "query" [--tag t] [--type Appunto]` | Ricerca full-text e filtri combinatori multi-criterio. |
| **`graph-health`** | `sbk graph-health [--format md] [-o FILE]` | Analisi topologica del grafo (top hubs, dead-ends, orfani). |
| **`map`** | `sbk map [--output Mappa.md] [--format json]` | Cartografia strutturale delle sezioni del Vault. |
| **`create`** | `sbk create "Titolo" --type Appunto [--folder ...]` | Creazione standardizzata con staging inbox, template e MOC. |
| **`sandbox`** | `sbk sandbox {init,reset,path}` | Gestisce ambienti di test isolati per prove sicure. |

---

## Operazioni Massive da File JSON

Per migrazioni massive o riorganizzazioni rapide, `sbk` supporta l'opzione `--batch <file.json>` sui comandi di mutazione, applicando la strategia **Strict All-or-Nothing preflight** e raggruppando tutte le azioni in un'**unica transazione reversibile**:

```bash
# Spostamento batch di note verso cartelle di destinazione
sbk move --batch batch_move.json

# Rinomina batch con refactoring globale di tutti i wikilink
sbk rename --batch batch_rename.json

# Assegnazione massiva del tipo di nota (Frontmatter)
sbk frontmatter set-type --batch batch_types.json

# Iniezione massiva di tag tassonomici (Frontmatter)
sbk frontmatter add-tags --batch batch_tags.json
```

I file JSON adottano la sintassi dizionario `{sorgente: valore_target}`. I template pronti all'uso sono consultabili nella cartella [`examples/batch/`](https://github.com/lucadileo9/second-brain-keeper/tree/main/examples/batch).

---

## Utilizzo come Libreria Python (SDK)

La classe Facade [`Vault`](https://github.com/lucadileo9/second-brain-keeper/blob/main/docs/architecture/facade.md) espone un'interfaccia ad oggetti unificata per script di automazione o agenti intelligenti:

```python
from sbk import Vault

# Inizializzazione della Facade
vault = Vault(root_path="/percorso/del/tuo/Vault")

# 1. Diagnostica e referto di salute
report = vault.audit()
print(f"Health Score: {report.health_score}/100.0 (Problemi: {report.total_issues})")

# 2. Creazione standardizzata con auto-routing
result = vault.create(
    title="Strategie di Ottimizzazione Memoria",
    tipo="Appunto",
    tags=["tech/python", "architettura/performance"],
)
print(f"Nota creata in: {result.file_path} (Transazione: {result.tx_id})")

# 3. Rinomina sicura con refactoring globale dei wikilink
rename_res = vault.rename(
    old_path="Note/vecchio_appunto.md",
    new_name="Nuovo_Appunto",
)
print(f"Wikilink aggiornati: {rename_res.updated_links_count}")

# 4. Rollback immediato in caso di errore
undo_res = vault.undo()
print(f"Rollback completato: {undo_res.reverted_actions} azioni ripristinate")
```

---

## Mappa della Documentazione Tecnica

L'intero impianto documentale e organizzato nella cartella [`docs/`](https://github.com/lucadileo9/second-brain-keeper/tree/main/docs):

```text
docs/
├── architecture/
│   ├── facade.md              # Disamina completa della Facade (Vault), metodi e sequenze
│   ├── core_modules.md        # I moduli computazionali del core: classi, funzioni, I/O
│   ├── models.md              # Catalogo esaustivo dei Domain Models immutabili
│   └── transaction_journal.md # Meccanica dello stato, hashing SHA-256 e rollback LIFO
├── cli/
│   ├── overview.md            # Panoramica CLI, exit codes, opzioni globali e dry-run
│   ├── commands_reference.md  # Specifiche esaustive e parametri per tutti i 20 comandi
│   └── sandbox_guide.md       # Guida interattiva e walkthrough per testare nella sandbox
└── testing/
    └── test_suite.md          # Architettura dei test, fixture isolate e matrici CI
```

---

## Qualita del Codice e Strumenti di Sviluppo

Il repository adotta rigorosi standard di ingegneria del software con guardrail automatizzati:

- **Suite di Test**: Test automatizzati estesi a tutte le componenti core, CLI e modelli con fixture isolate e riproducibili.
- **Tipizzazione Statica**: 100% conforme a Mypy su tutti i moduli sorgente e CLI.
- **Stile & Linting**: Conforme agli standard di Ruff.
- **Analisi di Sicurezza**: Scanner AST Bandit privo di segnalazioni o vulnerabilita.
- **Automazione CI**: Matrice multipiattaforma su Linux, macOS e Windows con Python da 3.10 a 3.14.

### Comandi Make Disponibili

Il progetto include un `Makefile` pronto all'uso con rilevamento automatico del virtualenv:

```bash
make test          # Esegue la suite di test con report di copertura del codice
make lint          # Controlla lo stile del codice (Ruff check & format check)
make format        # Riformatta e corregge automaticamente il codice con Ruff
make typecheck     # Esegue il controllo statico dei tipi con Mypy
make pre-commit    # Esegue l'intera suite di hook pre-commit sui file modificati
make all           # Esegue in sequenza format, lint, typecheck e test
```

---

## Segnalazione Problemi e Contributi

I contributi sono benvenuti. Per segnalare anomalie o proporre miglioramenti, utilizzare i moduli dedicati:

- [**Segnala un Bug**](https://github.com/lucadileo9/second-brain-keeper/issues/new?template=bug_report.yml): per comportamenti inattesi, allegando ambiente, versione e log.
- [**Suggerisci una Funzionalita**](https://github.com/lucadileo9/second-brain-keeper/issues/new?template=feature_request.yml): per proporre estensioni CLI o nuove API dell'SDK.
- [**Migliora la Documentazione**](https://github.com/lucadileo9/second-brain-keeper/issues/new?template=documentation.yml): per segnalare parti poco chiare o proporre esempi aggiuntivi.

---

## Licenza

Questo progetto e rilasciato sotto licenza [GNU General Public License v3.0](https://github.com/lucadileo9/second-brain-keeper/blob/main/LICENSE).
