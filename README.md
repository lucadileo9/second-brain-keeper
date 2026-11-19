# Second Brain Keeper (`sbk`)

> Motore universale di governance, refactoring atomico, diagnostica e manutenzione per Second Brain, Obsidian e archivi documentali.

[![CI](https://github.com/lucadileo9/second-brain-keeper/actions/workflows/ci.yml/badge.svg)](https://github.com/lucadileo9/second-brain-keeper/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)]()
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

---

## Panoramica

**`obsidian-vaultkeeper`** (distribuito tramite il binario da riga di comando **`vk`** e come libreria Python `vaultkeeper`) è un sistema di livello enterprise progettato per presidiare, normalizzare e manutenere archivi di appunti Markdown complessi (oltre 3.900 note su architettura Johnny.Decimal).

Il sistema è ingegnerizzato secondo un'**architettura a doppia testa**:
1. **SDK Python Programmatico ([`Vault`](docs/architecture/facade.md))**: API orientata agli oggetti, priva di effetti collaterali a terminale (zero `print` o `sys.exit`), che scambia modelli di dominio immutabili ed è nativamente predisposta per script di automazione e server MCP per agenti AI autonomi.
2. **Command Line Interface ([`vk`](docs/cli/overview.md))**: Interfaccia moderna a 20 comandi, arricchita con rendering `Rich`, simulazioni di sicurezza pre-volo (`--dry-run`), formati serializzabili (`--format json|yaml|csv`) e codici di ritorno semantici POSIX (`ExitCode`).

Tutte le operazioni mutative sono incapsulate in un **Transaction Journal atomico con hashing crittografico SHA-256 e rollback LIFO**: qualsiasi creazione, rinomina, spostamento o cancellazione può essere annullata all'istante tramite `sbk undo`.

---

## Installazione

### Tramite Pip (Ambiente Virtuale)
```bash
pip install second-brain-keeper
```

### Installazione per Sviluppo e Contributi
```bash
git clone https://github.com/lucadileo9/second-brain-keeper.git
cd second-brain-keeper
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## Primi Passi (Quickstart)

> [!TIP] Ambiente di Prova Protetto (Sandbox)
> Per familiarizzare con VaultKeeper senza toccare il Vault reale, è disponibile la modalità sandbox:
> ```bash
> sbk sandbox init
> export SBK_VAULT=$(sbk sandbox path)
> sbk --root "$SBK_VAULT" audit
> ```
> Per la guida completa ed esempi passo-passo, consultare la [**Guida alla Sandbox**](docs/cli/sandbox_guide.md).

### 1. Inizializzare la Configurazione del Vault
```bash
sbk init --target /srv/storage/Vault
```
Genera il file guida `vault.toml` con le convenzioni di denominazione (`Title_Case`), i tag ammessi, le estensioni consentite e le soglie di archiviazione.

### 2. Eseguire l'Audit Diagnostico a 5 Fasi
```bash
sbk audit
```
Verifica filesystem, denominazione, conformità frontmatter YAML, tassonomia controllata dei tag e integrità dei wikilink (inclusi link rotti ed embed orfani), calcolando il **Vault Health Score** (da 0.0 a 100.0).

### 3. Creare una Nuova Nota Standardizzata
```bash
sbk create "Architettura a Microservizi" --type Appunto --tags "tech/architettura,tech/cloud"
```
Deposita la nota nell'area di staging (`00_Inbox/Architettura_A_Microservizi.md` o cartella specificata con `--folder`), inietta le variabili nel template e aggiorna il MOC `00_Indice.md`.

### 4. Rinominare con Refactoring Globale dei Backlink
```bash
sbk rename 10-19_Progetti/vecchio_progetto.md Progetto_Varys
```
Rinomina il file e aggiorna simultaneamente tutti i collegamenti `[[...]]` che puntavano al vecchio nome all'interno dell'intero Vault.

### 5. Annullare o Riapplicare un'Operazione
```bash
# Annulla l'ultima transazione con verifica di sicurezza crittografica SHA-256
sbk undo

# Riapplica l'operazione annullata
sbk redo
```

---

## Tabella Sinottica dei 20 Comandi CLI

Per la consultazione dettagliata di argomenti, opzioni ed esempi d'uso per ciascun comando, consultare il [**Manuale di Riferimento dei Comandi CLI**](docs/cli/commands_reference.md).

| Comando | Sintassi di Esempio | Descrizione Operativa | Reversibile con `undo` |
| :--- | :--- | :--- | :---: |
| **`init`** | `sbk init [--force]` | Genera il file di configurazione predefinito `vault.toml`. | No |
| **`audit`** | `sbk audit [--target <path>] [--step 1..5] [-o report.md]` | Diagnostica a 5 fasi con calcolo del Vault Health Score. | No (Read-Only) |
| **`clean-attachments`** | `sbk clean-attachments [--dry-run]` | Bonifica file orfani tramite soft-delete reversibile in `.trash/`. | **Sì** |
| **`normalize-names`** | `sbk normalize-names [--dry-run]` | Converte in `Title_Case` e riscrive contestualmente i backlink. | **Sì** |
| **`generate-indices`** | `sbk generate-indices [--all] [--dry-run]` | Genera o aggiorna i file MOC `00_Indice.md` di cartella. | No (Idempotente) |
| **`frontmatter`** | `sbk frontmatter set-type --target n.md --type Appunto` | Ispeziona o modifica metadati YAML (`tipo`, tag). | **Sì** |
| **`history`** | `sbk history [--limit 20] [--format json] [-o FILE]` | Mostra lo storico delle transazioni atomiche del Journal. | No (Read-Only) |
| **`undo`** | `sbk undo [--tx <id>] [--dry-run]` | Ripristina lo stato del filesystem precedente con verifica SHA-256. | **Sì** (Rollback) |
| **`redo`** | `sbk redo [--tx <id>] [--dry-run]` | Riapplica l'ultima transazione annullata tramite `undo`. | **Sì** (Reapply) |
| **`rename`** | `sbk rename vecchio.md Nuovo.md` | Rinomina una nota con sincronizzazione globale di backlink e MOC. | **Sì** |
| **`move`** | `sbk move nota.md 10-19_Progetti/` | Sposta file o cartelle aggiornando entrambi i MOC di area. | **Sì** |
| **`archive`** | `sbk archive Progetto_X/ [--no-tombstone]` | Trasferisce in cold storage e deposita scheda tombstone. | **Sì** |
| **`offload`** | `sbk offload [target] [--dry-run]` | Sposta allegati pesanti (>50MB) in cold storage rimpiazzando i link. | **Sì** |
| **`tags`** | `sbk tags add tech/rust [--section "Tecnologia"]` | Gestisce il vocabolario controllato `00_Tassonomia_Tag.md`. | **Sì** |
| **`config`** | `sbk config set naming_style Title_Case` | Ispeziona o modifica impostazioni a caldo in `vault.toml`. | **Sì** |
| **`search`** | `sbk search "query" [--tag t] [--type Appunto]` | Ricerca full-text e filtri combinatori multi-criterio. | No (Read-Only) |
| **`graph-health`** | `sbk graph-health [--format md] [-o FILE]` | Analisi topologica del grafo (top hubs, dead-ends, orfani). | No (Read-Only) |
| **`map`** | `sbk map [--output Mappa.md] [--format json]` | Cartografia strutturale Johnny.Decimal e volumi del Vault. | No (Read-Only) |
| **`create`** | `sbk create "Titolo" --type Appunto [--folder ...]` | Creazione standardizzata con staging inbox, template e MOC. | **Sì** |
| **`sandbox`** | `sbk sandbox {init,reset,path}` | Gestisce ambienti di test isolati (v. [guida](docs/cli/sandbox_guide.md)). | No (Isolato) |

---

## Operazioni Batch da File JSON

Per migrazioni massive o riorganizzazioni rapide, `vk` supporta l'opzione `--batch <file.json>` sui comandi di mutazione, applicando la strategia **Strict All-or-Nothing preflight** e raggruppando tutte le azioni in un'**unica transazione reversibile**:

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

I file JSON adottano la sintassi dizionario `{sorgente: valore_target}`. I template pronti all'uso sono consultabili nella cartella [`examples/batch/`](examples/batch/).

---

## Utilizzo come Libreria Python (SDK)

La classe Facade [`Vault`](docs/architecture/facade.md) espone un'interfaccia unificata per script di automazione o agenti intelligenti:

```python
from sbk import Vault

# Inizializzazione della Facade
vault = Vault(root_path="/srv/storage/Vault")

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
    old_path="20-29_Istruzione/Informatica/vecchio_appunto.md",
    new_name="Nuovo_Appunto",
)
print(f"Wikilink aggiornati: {rename_res.updated_links_count}")

# 4. Rollback immediato in caso di errore
undo_res = vault.undo()
print(f"Rollback completato: {undo_res.reverted_actions} azioni ripristinate")
```

---

## Mappa della Documentazione Tecnica

L'intero impianto documentale è organizzato nella cartella [`docs/`](docs):

```text
docs/
├── architecture/
│   ├── facade.md              # Disamina completa della Facade (Vault), metodi e sequenze
│   ├── core_modules.md        # I 15 moduli computazionali del core: classi, funzioni, I/O
│   ├── models.md              # Catalogo esaustivo dei 23 Domain Models immutabili
│   └── transaction_journal.md # Meccanica dello stato, hashing SHA-256 e rollback LIFO
├── cli/
│   ├── overview.md            # Panoramica CLI, exit codes, opzioni globali e dry-run
│   ├── commands_reference.md  # Specifiche esaustive e parametri per tutti i 20 comandi
│   └── sandbox_guide.md       # Guida interattiva e walkthrough per testare nella sandbox
└── testing/
    └── test_suite.md          # 184 test, copertura >=90%, fixture isolate e matrici CI
```

---

## Qualità e Suite di Test

- **Test Suite**: 184 test automatizzati eseguiti in meno di 0.8s.
- **Copertura del Codice**: $\ge 90\%$ complessivo misurato con `pytest-cov`.
- **Controllo Tipi Statico**: 100% conforme a `mypy --strict` su 79 file sorgente.
- **Stile & Linting**: 100% conforme alle regole di `ruff check` e `ruff format`.
- **Sicurezza**: Zero vulnerabilità o avvisi rilevati tramite scanner AST `bandit`.

Per eseguire localmente la suite di test e le verifiche di qualità:
```bash
.venv/bin/pytest --cov=sbk --cov-report=term-missing
.venv/bin/mypy src/ tests/
.venv/bin/ruff check src/ tests/
.venv/bin/bandit -r src/ -ll
```

---

## Licenza

Questo progetto è rilasciato sotto licenza [GNU General Public License v3.0](LICENSE).
