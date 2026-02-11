# 🍽️ Food Diary Telegram Bot

Bot Telegram per tenere un diario alimentare con foto e export in Excel.

## ✨ Funzionalità

- 📝 Registra i pasti inviando semplici messaggi
- 📷 Allega foto ai tuoi pasti
- 💾 Database SQLite persistente
- 📊 Statistiche giornaliere e settimanali
- 📥 Export in Excel (completo, settimanale, mensile)
- 🐳 Deploy con Docker
- 🔄 CI/CD automatizzato con GitHub Actions

## 🚀 Quick Start con Docker

### Prerequisiti

1. Docker installato ([Install Docker](https://docs.docker.com/get-docker/))
2. Account Telegram e bot token

### Ottenere il Token del Bot Telegram

1. Apri Telegram e cerca `@BotFather`
2. Invia `/newbot` e segui le istruzioni
3. Copia il token che ricevi (simile a `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Esecuzione con Docker

```bash
# Pull l'immagine dal GitHub Container Registry
docker pull ghcr.io/YOUR_USERNAME/food-diary-bot:latest

# Esegui il container
docker run -d \
  --name food-diary-bot \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN=your_token_here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/photos:/app/photos \
  -v $(pwd)/exports:/app/exports \
  ghcr.io/YOUR_USERNAME/food-diary-bot:latest
```

### Oppure con Docker Compose

Crea un file `docker-compose.yml`:

```yaml
version: '3.8'

services:
  food-diary-bot:
    image: ghcr.io/YOUR_USERNAME/food-diary-bot:latest
    container_name: food-diary-bot
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    volumes:
      - ./data:/app/data
      - ./photos:/app/photos
      - ./exports:/app/exports
```

Poi esegui:

```bash
# Crea file .env con il tuo token
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env

# Avvia il bot
docker-compose up -d

# Vedi i log
docker-compose logs -f
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

### Comandi Disponibili

- `/start` - Messaggio di benvenuto
- `/help` - Lista dei comandi
- `/stats` - Visualizza statistiche
- `/export` - Esporta tutto il diario in Excel
- `/export_week` - Esporta ultima settimana
- `/export_month` - Esporta ultimo mese

### Registrare un Pasto

Basta inviare un messaggio al bot con quello che hai mangiato:

```
Pizza margherita con birra
```

### Registrare un Pasto con Foto

1. Seleziona una foto dalla galleria o scattane una
2. Aggiungi una caption con la descrizione
3. Invia al bot

La foto verrà salvata automaticamente!

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
├── requirements.txt            # Dipendenze Python
├── Dockerfile                  # Docker configuration
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

# Oppure con docker-compose
docker-compose logs -f

# Verifica che il container sia in esecuzione
docker ps
```

### Docker: Riavviare il bot

```bash
# Con Docker
docker restart food-diary-bot

# Oppure con docker-compose
docker-compose restart
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
