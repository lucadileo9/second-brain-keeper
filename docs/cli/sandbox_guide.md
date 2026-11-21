# Guida alla Sandbox di VaultKeeper: Ambiente di Simulazione e Primi Passi

La modalità **Sandbox** di `second-brain-keeper` fornisce un ambiente di simulazione protetto, progettato per consentire a nuovi utenti, integratori di sistemi e agenti autonomi di sperimentare l'intero set di comandi e verificare le regole di governance senza toccare alcun file del Vault reale di produzione (`/srv/storage/Vault`).

---

## 1. Filosofia e Isolamento Ermetico

La gestione di un Second Brain articolato (strutturato su gerarchie Johnny.Decimal, MOC e migliaia di wikilink) richiede la massima cautela durante le operazioni mutative di massa.

La sandbox risponde a tre esigenze fondamentali:
1. **Onboarding Sicuro**: Esplorare le funzionalità di creazione, refactoring dei wikilink e normalizzazione prima di applicarle al proprio archivio reale.
2. **Collaudo di Script e Pipeline**: Validare script batch o integrazioni esterne contro un mock realistico e deterministico.
3. **Didattica e Dimostrazione**: Mostrare a colleghi o collaboratori il funzionamento del motore transazionale e dell'Health Score in un contesto riproducibile.

### Posizione Filesystem
Per impostazione predefinita, la sandbox viene allocata in uno spazio isolato nella home dell'utente:
```text
~/.sbk/sandbox
```
È possibile sovrascrivere tale percorso passando l'opzione `--target <cartella>` a tutti i comandi sandbox.

### Composizione del Vault Sandbox
All'inizializzazione, la sandbox crea un ambiente completo contenente:
- Un file di configurazione preconfigurato `vault.toml` (convenzione `Title_Case`, estensioni permesse, cartella inbox `00_Inbox`).
- La struttura ad aree Johnny.Decimal (`00-09_Meta`, `10-19_Progetti`, `20-29_Aree`, `90-99_Allegati`).
- Note dimostrative interconnesse da wikilink (ad es. `Progetto_Alpha.md`, `Nota_Beta.md`).
- File MOC di cartella (`00_Indice.md`).
- Il file di vocabolario controllato `00_Tassonomia_Tag.md`.
- Alcune violazioni intenzionali (come file orfani o convenzioni errate) ideate per mettere alla prova l'audit.

---

## 2. Comandi di Gestione della Sandbox

La famiglia di sottocomandi `sbk sandbox` comprende tre operazioni essenziali:

### `sbk sandbox init`
Inizializza un nuovo vault sandbox. Se la directory di destinazione esiste già e contiene dati, il comando rifiuta la sovrascrittura per sicurezza a meno di non specificare `--force`.
```bash
# Inizializzazione nella cartella standard ~/.sbk/sandbox
sbk sandbox init

# Inizializzazione in un percorso personalizzato
sbk sandbox init --target /tmp/test_vault --force
```

### `sbk sandbox path`
Restituisce il percorso assoluto canonico del vault sandbox attivo. È ideale per script di shell o per aprire direttamente la cartella come vault all'interno dell'applicazione desktop Obsidian.
```bash
sbk sandbox path
```

### `sbk sandbox reset`
Ripristina lo stato del vault sandbox alle condizioni iniziali di fabbrica. Tutte le modifiche, note create o file spostati durante i test vengono ripuliti e sostituiti con il set di dati iniziale.
```bash
sbk sandbox reset
```

---

## 3. Tutorial Guidato Interattivo (Walkthrough in 7 Passi)

Questo tutorial guida passo-passo attraverso un ciclo completo di familiarizzazione con il tool all'interno della sandbox.

### Passo 1: Inizializzare la Sandbox
Creare l'ambiente di simulazione con il comando:
```bash
sbk sandbox init --force
```
Il sistema genera l'albero completo e stampa a terminale il percorso assoluto in cui è stata allocata la sandbox.

### Passo 2: Ottenere il Percorso e Configurare la Shell
Per praticità operativa nei comandi successivi, è possibile salvare il percorso del vault sandbox in una variabile d'ambiente:
```bash
export SBK_VAULT=$(sbk sandbox path)
echo "Lavorando sulla sandbox in: $SBK_VAULT"
```
Da questo momento, sarà sufficiente passare `--root "$SBK_VAULT"` a qualsiasi comando `sbk` (oppure posizionarsi direttamente nella directory con `cd "$SBK_VAULT"`).

### Passo 3: Eseguire la Diagnostica Preliminare (`audit`)
Lanciare l'audit a 5 fasi per analizzare lo stato iniziale della sandbox:
```bash
sbk --root "$SBK_VAULT" audit
```
Verranno analizzate le 5 dimensioni di governance:
1. **Fase 1**: Filesystem & Storage (nomi lunghi, allegati pesanti, estensioni).
2. **Fase 2**: Naming Conventions (controllo stile `Title_Case`).
3. **Fase 3**: Frontmatter & Metadata (presenza campo `tipo`, blocchi YAML validi).
4. **Fase 4**: Tag Taxonomy (controllo conformità con `00_Tassonomia_Tag.md`).
5. **Fase 5**: Referential Integrity (rilevamento wikilink orfani ed embed mancanti).

Al termine, verrà stampato il **Vault Health Score** (da 0.0 a 100.0) con il dettaglio delle eventuali anomalie.

### Passo 4: Creare una Nuova Nota Standardizzata (`create`)
Creare un nuovo appunto documentale:
```bash
sbk --root "$SBK_VAULT" create "Architettura a Code RabbitMQ" --type Appunto --tags "tech/backend,architettura/messaging"
```
Cosa accade internamente:
- La nota viene depositata automaticamente nell'area di staging (`00_Inbox/Architettura_A_Code_RabbitMQ.md`).
- Viene iniettato il frontmatter YAML conforme con timestamp ISO e tag.
- Il file indice `00_Indice.md` della cartella viene aggiornato con l'inserimento della nuova voce.
- L'intera operazione viene registrata nel Transaction Journal per garantire la reversibilità.

Se si desidera specificare una cartella di destinazione diversa:
```bash
sbk --root "$SBK_VAULT" create "Integrazione API" --type Progetto --folder "10-19_Progetti"
```

### Passo 5: Eseguire un Refactoring di Naming con Sincronizzazione (`rename`)
Rinominare una nota esistente e osservare l'aggiornamento automatico dei wikilink:
```bash
sbk --root "$SBK_VAULT" rename "$SBK_VAULT/20-29_Aree/Nota_Beta.md" "Nota_Beta_Avanzata"
```
VaultKeeper:
- Rinomina il file su filesystem applicando lo standard `Title_Case` (`Nota_Beta_Avanzata.md`).
- Scansiona tutte le altre note del vault e aggiorna ogni occorrenza `[[Nota_Beta]]` in `[[Nota_Beta_Avanzata]]`.
- Aggiorna l'indice `00_Indice.md` della cartella `20-29_Aree`.

### Passo 6: Sperimentare la Simulazione Pre-Volo (`--dry-run`)
Prima di applicare comandi che alterano il filesystem, è buona norma effettuare una simulazione:
```bash
sbk --root "$SBK_VAULT" clean-attachments --dry-run
```
Il flag `--dry-run` esegue l'intero ciclo di parsing e calcolo senza scrivere su disco né aprire transazioni nel journal, mostrando a terminale l'elenco esatto delle modifiche previste.

### Passo 7: Viaggio nel Tempo (`undo` e `redo`)
Tutte le modifiche mutative possono essere annullate all'istante:
```bash
# Annulla l'ultima operazione (ad esempio la rinomina della Nota Beta)
sbk --root "$SBK_VAULT" undo
```
Il motore calcola l'impronta crittografica SHA-256 dei file coinvolti per certificare che non siano stati alterati da terzi e ripristina la situazione precedente in ordine inverso (LIFO).

Se si desidera riapplicare l'operazione annullata:
```bash
sbk --root "$SBK_VAULT" redo
```

---

## 4. Conclusione della Sessione di Test

Al termine delle prove, è possibile azzerare la sandbox e riportarla allo stato vergine in un solo passaggio:
```bash
sbk sandbox reset
```
In alternativa, per eliminare completamente la directory dal disco:
```bash
rm -rf "$(sbk sandbox path)"
```
In questo modo il sistema resta pulito e pronto per la prossima sessione di verifica o formazione.
