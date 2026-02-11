# 🍽️ Food Diary Telegram Bot

Bot Telegram per tenere un diario alimentare con foto e export in Excel.

## ✨ Funzionalità

- 📝 Registra i pasti inviando semplici messaggi
- 📷 Allega foto ai tuoi pasti
- 💾 Database SQLite persistente
- 📊 Statistiche giornaliere e settimanali
- 📥 Export in Excel (completo, settimanale, mensile)
- 🌐 **Pannello Admin Web** per gestire il database
- 🐳 Deploy con Docker
- 🔄 CI/CD automatizzato con GitHub Actions

## 🚀 Quick Start con Docker

### Prerequisiti

1. Docker installato ([Install Docker](https://docs.docker.com/get-docker/))
2. Account Telegram e bot token

## 🤖 Registrare il Bot su Telegram

### Passo 1: Creare il Bot con BotFather

1. Apri Telegram e cerca `@BotFather` (è il bot ufficiale di Telegram per creare bot)
2. Invia il comando `/newbot`
3. BotFather ti chiederà:
   - **Nome del bot**: Es. `Il Mio Diario Alimentare`
   - **Username del bot**: Deve finire con `bot`, es. `il_mio_diario_bot`
4. BotFather ti risponderà con il **token del bot** (simile a `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. **IMPORTANTE**: Copia e salva questo token in modo sicuro!

### Passo 2: Trovare il Tuo User ID

Per limitare l'accesso al bot solo a te, devi trovare il tuo Telegram User ID:

**Metodo 1 - Usando il bot (consigliato dopo il deploy):**
1. Avvia il bot (vedi sezione sotto) **SENZA** impostare `ALLOWED_USER_IDS`
2. Invia `/start` al tuo bot
3. Il bot ti risponderà con il tuo User ID nel formato: "Il tuo User ID è: `123456789`"
4. Ferma il bot, aggiungi il tuo User ID a `.env` e riavvia

**Metodo 2 - Usando @userinfobot:**
1. Cerca `@userinfobot` su Telegram
2. Invia `/start` al bot
3. Ti risponderà con il tuo User ID
4. Copia il numero

### Passo 3: Configurare il Bot

Crea il file `.env` con le tue credenziali:

```bash
# Crea il file .env
cat > .env << EOF
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_USER_IDS=987654321
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
ADMIN_SECRET_KEY=$(openssl rand -hex 32)
ADMIN_PORT=5000
EOF
```

Sostituisci:
- `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` con il token del tuo bot
- `987654321` con il tuo User ID
- `your_secure_password` con una password sicura per l'admin panel

**Per permettere più utenti**, separa gli ID con virgole:
```bash
ALLOWED_USER_IDS=123456789,987654321,555666777
```

**Per permettere a chiunque** (NON consigliato), lascia vuoto:
```bash
ALLOWED_USER_IDS=
```

### Esecuzione con Docker

#### Production (main branch - stable)

```bash
# Pull l'immagine dal GitHub Container Registry
docker pull ghcr.io/jurisacchetta/food-diary-bot:latest

# Esegui il container
docker run -d \
  --name food-diary-bot-prod \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN=your_token_here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/photos:/app/photos \
  -v $(pwd)/exports:/app/exports \
  ghcr.io/jurisacchetta/food-diary-bot:latest
```

#### Development (develop branch - latest features)

```bash
# Pull l'immagine development
docker pull ghcr.io/jurisacchetta/food-diary-bot:dev

# Esegui il container
docker run -d \
  --name food-diary-bot-dev \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN=your_token_here \
  -v $(pwd)/data-dev:/app/data \
  -v $(pwd)/photos-dev:/app/photos \
  -v $(pwd)/exports-dev:/app/exports \
  ghcr.io/jurisacchetta/food-diary-bot:dev
```

### Oppure con Docker Compose

#### Production Environment

```bash
# Crea file .env con il tuo token
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env

# Avvia il bot production
docker-compose -f docker-compose.prod.yml up -d

# Vedi i log
docker-compose -f docker-compose.prod.yml logs -f
```

#### Development Environment

```bash
# Crea file .env con il tuo token
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env

# Avvia il bot development
docker-compose -f docker-compose.dev.yml up -d

# Vedi i log
docker-compose -f docker-compose.dev.yml logs -f

# Update to latest dev version
docker-compose -f docker-compose.dev.yml pull
docker-compose -f docker-compose.dev.yml up -d
```

## 🔨 Build Locale

Se vuoi buildare l'immagine localmente:

```bash
# Clona il repository
git clone https://github.com/YOUR_USERNAME/Food-Diary-Bot.git
cd Food-Diary-Bot

# Build l'immagine
docker build -t food-diary-bot .

# Esegui
docker run -d \
  --name food-diary-bot \
  -e TELEGRAM_BOT_TOKEN=your_token_here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/photos:/app/photos \
  -v $(pwd)/exports:/app/exports \
  food-diary-bot
```

## 🐍 Setup Python Locale (Sviluppo)

```bash
# Clona il repository
git clone https://github.com/YOUR_USERNAME/Food-Diary-Bot.git
cd Food-Diary-Bot

# Crea virtual environment
python3 -m venv venv

# Attiva virtual environment
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt

# Crea file .env
cp .env.example .env
# Modifica .env e inserisci il tuo token

# Avvia il bot
python bot.py
```

## 📱 Come Usare il Bot

### Primi Passi

1. **Avvia il container** (vedi sezione sopra)
2. **Apri Telegram** e cerca il tuo bot usando lo username che hai scelto (es. `@il_mio_diario_bot`)
3. **Invia `/start`** al bot per iniziare

Se hai configurato correttamente `ALLOWED_USER_IDS`, il bot ti darà il benvenuto. Altrimenti, vedrai il tuo User ID per configurarlo.

### Comandi Disponibili

- `/start` - Messaggio di benvenuto e mostra il tuo User ID
- `/help` - Lista dei comandi disponibili
- `/stats` - Visualizza statistiche (pasti oggi, settimana, totale)
- `/export` - Esporta tutto il diario in Excel
- `/export_week` - Esporta l'ultima settimana
- `/export_month` - Esporta l'ultimo mese

### Registrare un Pasto

Basta inviare un messaggio al bot con quello che hai mangiato:

```
Pizza margherita con birra
```

Il bot risponderà con:
```
✅ Pasto registrato!

📝 Pizza margherita con birra
🕐 11/02/2026 13:45
```

### Registrare un Pasto con Foto

1. Seleziona una foto dalla galleria o scattane una
2. Aggiungi una **caption** (didascalia) con la descrizione del pasto
3. Invia al bot

**Esempio:**
- Foto: [immagine della pizza]
- Caption: `Pizza quattro formaggi al ristorante`

Il bot risponderà con:
```
✅ Pasto registrato!

📝 Pizza quattro formaggi al ristorante
🕐 11/02/2026 20:30
📷 Foto salvata
```

## 🌐 Pannello Admin Web

Oltre al bot Telegram, è disponibile un'interfaccia web per gestire il database.

### Caratteristiche

- ✅ Interfaccia web moderna con Bootstrap
- 🔍 Ricerca e filtri avanzati per i pasti
- ✏️ Modifica ed elimina pasti
- 📊 Visualizzazione dati con paginazione
- 📥 Export CSV/Excel direttamente dall'interfaccia
- 🔒 Autenticazione con username e password

### Accesso al Pannello Admin

#### Con Docker Compose (Consigliato)

Il pannello admin si avvia automaticamente insieme al bot:

```bash
# Assicurati che .env contenga le credenziali admin
docker-compose -f docker-compose.prod.yml up -d

# Verifica che entrambi i servizi siano attivi
docker-compose -f docker-compose.prod.yml ps
```

Accedi al pannello su: **http://localhost:5000**

Credenziali:
- **Username**: quello impostato in `ADMIN_USERNAME` (default: `admin`)
- **Password**: quella impostata in `ADMIN_PASSWORD`

#### Esecuzione Manuale (Python)

```bash
# Attiva virtual environment
source venv/bin/activate

# Imposta le variabili d'ambiente
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=your_password
export ADMIN_SECRET_KEY=$(openssl rand -hex 32)

# Avvia il pannello admin
python admin.py
```

Accedi su: **http://localhost:5000**

### Funzioni del Pannello Admin

1. **Dashboard Home**: Panoramica del sistema
2. **Gestione Pasti**:
   - Visualizza tutti i pasti con paginazione
   - Ricerca per username, user_id, o descrizione
   - Filtra per user_id, username, o data
   - Ordina per qualsiasi colonna
   - Modifica singoli pasti
   - Elimina pasti
3. **Export**:
   - Export in CSV
   - Export in Excel (.xlsx)
   - Export dei risultati filtrati

### Sicurezza

- ✅ Autenticazione HTTP Basic Auth
- ✅ Credenziali tramite variabili d'ambiente
- ✅ Secret key per sessioni Flask
- ⚠️ **IMPORTANTE**: Cambia sempre le password di default in produzione!
- 🔒 **Consiglio**: Usa un reverse proxy (nginx) con HTTPS in produzione

### Configurazione Avanzata

Nel file `.env`, puoi configurare:

```bash
# Admin Panel
ADMIN_USERNAME=admin                    # Username per login
ADMIN_PASSWORD=strong_password          # Password per login
ADMIN_SECRET_KEY=random_secret_key      # Chiave segreta Flask
ADMIN_PORT=5000                         # Porta su cui esporre l'admin
```

#### Cambiare Porta

```bash
# Nel file .env
ADMIN_PORT=8080

# Riavvia il servizio
docker-compose -f docker-compose.prod.yml restart food-diary-admin
```

#### Accesso Esterno (Produzione)

**⚠️ NON esporre direttamente su internet senza HTTPS!**

Usa un reverse proxy come nginx con SSL:

```nginx
server {
    listen 443 ssl;
    server_name admin.tuosito.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Visualizzare Statistiche

Invia `/stats` per vedere:
```
📊 Le tue statistiche:

🍽️ Pasti totali: 42
📅 Pasti oggi: 3
📆 Pasti questa settimana: 18
```

### Esportare i Dati

- `/export` - Scarica un file Excel con TUTTI i tuoi pasti
- `/export_week` - Scarica i pasti degli ultimi 7 giorni
- `/export_month` - Scarica i pasti degli ultimi 30 giorni

Il file Excel conterrà:
- ID pasto
- Data e ora
- Descrizione
- Percorso foto (se presente)

### 🔒 Sicurezza

Se qualcuno prova ad usare il bot senza essere nella whitelist, vedrà:
```
⛔ Accesso negato.

Il tuo User ID è: 123456789
Contatta l'amministratore del bot per ottenere l'accesso.
```

## 🔄 CI/CD e Versionamento

Questo progetto usa **GitHub Actions** per CI/CD automatizzato e **semantic-release** per il versionamento automatico.

### Commit Messages

I commit devono seguire la [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): subject

body (optional)

footer (optional)
```

**Tipi disponibili:**
- `feat`: Nuova funzionalità (genera MINOR version)
- `fix`: Bug fix (genera PATCH version)
- `docs`: Modifiche alla documentazione
- `style`: Cambiamenti di formattazione
- `refactor`: Refactoring del codice
- `perf`: Miglioramenti di performance
- `test`: Aggiunta/modifica test
- `build`: Modifiche al build system
- `ci`: Modifiche alla CI/CD
- `chore`: Altri cambiamenti

**Esempi:**
```bash
feat: add meal search functionality
fix: resolve database connection timeout
docs: update Docker setup instructions
ci: add automated testing workflow
```

**Breaking changes** (genera MAJOR version):
```bash
feat!: redesign database schema

BREAKING CHANGE: This changes the database structure
```

### Pipeline CI/CD

La pipeline si attiva automaticamente su push e pull request:

1. **Commit Lint** (PR): Valida i messaggi di commit
2. **Build & Push**: Build dell'immagine Docker e push su GitHub Container Registry
3. **Semantic Release** (main branch): Genera automaticamente:
   - Nuovo version tag
   - CHANGELOG.md aggiornato
   - GitHub Release con note

### GitHub Container Registry

Le immagini Docker vengono automaticamente pubblicate su:
```
ghcr.io/YOUR_USERNAME/food-diary-bot:latest
ghcr.io/YOUR_USERNAME/food-diary-bot:1.0.0
ghcr.io/YOUR_USERNAME/food-diary-bot:main
```

## 📁 Struttura del Progetto

```
food_diary_bot/
├── bot.py                      # Bot principale
├── database.py                 # Gestione database SQLite
├── exporter.py                 # Export in Excel
├── admin.py                    # Pannello admin Flask
├── requirements.txt            # Dipendenze Python
├── Dockerfile                  # Docker configuration
├── docker-compose.dev.yml     # Docker Compose development
├── docker-compose.prod.yml    # Docker Compose production
├── .dockerignore              # File da escludere dal build
├── .env.example               # Template per variabili d'ambiente
├── .gitignore                 # File da ignorare in git
├── commitlint.config.js       # Configurazione commit lint
├── .releaserc.json            # Configurazione semantic-release
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # Pipeline CI/CD
├── README.md                  # Questa guida
├── CHANGELOG.md               # Changelog generato automaticamente
├── data/                      # Database (creata automaticamente)
│   └── food_diary.db
├── photos/                    # Foto salvate (creata automaticamente)
│   └── [user_id]_[timestamp].jpg
└── exports/                   # Export temporanei (creata automaticamente)
```

## 🔧 Troubleshooting

### Docker: Il bot non risponde

```bash
# Controlla i log del container
docker logs food-diary-bot

# Controlla i log del pannello admin
docker logs food-diary-admin

# Oppure con docker-compose
docker-compose -f docker-compose.prod.yml logs -f

# Verifica che i container siano in esecuzione
docker ps
```

### Docker: Riavviare il bot

```bash
# Con Docker - Riavvia bot
docker restart food-diary-bot

# Con Docker - Riavvia admin panel
docker restart food-diary-admin

# Oppure con docker-compose - Riavvia tutto
docker-compose -f docker-compose.prod.yml restart

# Riavvia solo un servizio specifico
docker-compose -f docker-compose.prod.yml restart food-diary-bot
docker-compose -f docker-compose.prod.yml restart food-diary-admin
```

### Errore "Token non trovato"

Assicurati di aver impostato correttamente il token:

```bash
# Verifica la variabile d'ambiente
docker exec food-diary-bot env | grep TELEGRAM_BOT_TOKEN

# Oppure controlla il file .env
cat .env
```

### Spazio su disco

Le foto possono occupare spazio. Per controllare:

```bash
# Vedi quanto spazio occupa
du -sh ./photos/

# Con Docker
docker exec food-diary-bot du -sh /app/photos/

# Elimina foto vecchie se necessario (ATTENZIONE!)
# find ./photos/ -mtime +90 -delete  # Elimina foto più vecchie di 90 giorni
```

### Admin Panel: Non riesco ad accedere

```bash
# Verifica che il servizio sia attivo
docker ps | grep food-diary-admin

# Controlla i log per errori
docker logs food-diary-admin

# Verifica le credenziali in .env
cat .env | grep ADMIN_

# Testa la connessione
curl -u admin:password http://localhost:5000
```

### Admin Panel: Porta già in uso

```bash
# Cambia porta nel .env
echo "ADMIN_PORT=8080" >> .env

# Riavvia il servizio
docker-compose -f docker-compose.prod.yml restart food-diary-admin

# Accedi sulla nuova porta
# http://localhost:8080
```

### Database bloccato

```bash
# Ferma il container
docker stop food-diary-bot

# Riavvia
docker start food-diary-bot

# Oppure con docker-compose
docker-compose restart
```

## 🔒 Sicurezza

- **Non condividere mai il tuo bot token**
- Il file `.env` è in `.gitignore` per evitare di committarlo
- Solo tu puoi usare il bot (controlla con l'user_id se necessario)

## 📈 Backup

Per fare backup del database:

```bash
# Backup manuale
cp ./data/food_diary.db ./backup/food_diary_$(date +%Y%m%d).db

# Con Docker (se il volume è montato)
docker cp food-diary-bot:/app/data/food_diary.db ./backup/food_diary_$(date +%Y%m%d).db

# Backup automatico giornaliero (crontab)
crontab -e
# Aggiungi questa riga:
# 0 2 * * * docker cp food-diary-bot:/app/data/food_diary.db ~/backup/food_diary_$(date +\%Y\%m\%d).db
```

## 🆕 Aggiornamenti Futuri (Idee)

- [ ] Ricerca pasti per parola chiave
- [ ] Conteggio calorie (integrazione API)
- [ ] Grafici e trend
- [ ] Promemoria per registrare i pasti
- [ ] Export in PDF
- [ ] Multi-utente con permessi

## 📝 Licenza

Progetto personale - Usalo e modificalo come preferisci!

## 🤝 Supporto

Per problemi o domande, controlla i log del bot o verifica la configurazione seguendo questa guida.

Buon appetito! 🍕🍔🍣
