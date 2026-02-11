# 🍽️ Food Diary Telegram Bot

Bot Telegram per tenere un diario alimentare con foto e export in Excel.

## ✨ Funzionalità

- 📝 Registra i pasti inviando semplici messaggi
- 📷 Allega foto ai tuoi pasti
- 💾 Database SQLite persistente
- 📊 Statistiche giornaliere e settimanali
- 📥 Export in Excel (completo, settimanale, mensile)
- 🔄 Funziona 24/7 sul Raspberry Pi

## 🚀 Setup su Raspberry Pi

### Prerequisiti

1. Raspberry Pi con Raspberry Pi OS installato
2. Python 3.9 o superiore
3. Account Telegram e bot token

### Ottenere il Token del Bot Telegram

1. Apri Telegram e cerca `@BotFather`
2. Invia `/newbot` e segui le istruzioni
3. Copia il token che ricevi (simile a `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Installazione

```bash
# Clona o copia il progetto sul Raspberry Pi
cd ~
# Assumendo che tu abbia già la cartella food_diary_bot

cd food_diary_bot

# Crea virtual environment
python3 -m venv venv

# Attiva virtual environment
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Crea file .env con il tuo token
cp .env.example .env
nano .env
# Inserisci il tuo token: TELEGRAM_BOT_TOKEN=il_tuo_token_qui
```

### Test del Bot

```bash
# Attiva virtual environment se non già fatto
source venv/bin/activate

# Avvia il bot
python bot.py
```

Se tutto funziona, vedrai "Bot started!" nel terminale. Prova a inviare un messaggio al tuo bot su Telegram!

### Configurazione come Servizio (Avvio Automatico)

Per far partire il bot automaticamente all'avvio del Raspberry Pi:

```bash
# Modifica il file service con il tuo token
nano food_diary_bot.service
# Sostituisci "your_token_here" con il tuo vero token

# Copia il file service
sudo cp food_diary_bot.service /etc/systemd/system/

# Ricarica systemd
sudo systemctl daemon-reload

# Abilita il servizio
sudo systemctl enable food_diary_bot.service

# Avvia il servizio
sudo systemctl start food_diary_bot.service

# Verifica lo stato
sudo systemctl status food_diary_bot.service
```

### Comandi Utili per Gestire il Servizio

```bash
# Vedere i log del bot
sudo journalctl -u food_diary_bot.service -f

# Fermare il bot
sudo systemctl stop food_diary_bot.service

# Riavviare il bot
sudo systemctl restart food_diary_bot.service

# Disabilitare l'avvio automatico
sudo systemctl disable food_diary_bot.service
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

## 📁 Struttura del Progetto

```
food_diary_bot/
├── bot.py                      # Bot principale
├── database.py                 # Gestione database SQLite
├── exporter.py                 # Export in Excel
├── requirements.txt            # Dipendenze Python
├── .env.example               # Template per variabili d'ambiente
├── .gitignore                 # File da ignorare in git
├── food_diary_bot.service     # File service per systemd
├── README.md                  # Questa guida
├── data/                      # Database (creata automaticamente)
│   └── food_diary.db
├── photos/                    # Foto salvate (creata automaticamente)
│   └── [user_id]_[timestamp].jpg
└── exports/                   # Export temporanei (creata automaticamente)
```

## 🔧 Troubleshooting

### Il bot non risponde

```bash
# Controlla i log
sudo journalctl -u food_diary_bot.service -n 50

# Verifica che il servizio sia attivo
sudo systemctl status food_diary_bot.service
```

### Errore "Token non trovato"

Assicurati di aver impostato correttamente il token:

```bash
# Nel file .env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Oppure nel file food_diary_bot.service
Environment="TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### Database bloccato

```bash
# Ferma il bot
sudo systemctl stop food_diary_bot.service

# Riavvia
sudo systemctl start food_diary_bot.service
```

### Spazio su disco

Le foto possono occupare spazio. Per controllare:

```bash
# Vedi quanto spazio occupa
du -sh ~/food_diary_bot/photos/

# Elimina foto vecchie se necessario (ATTENZIONE!)
# find ~/food_diary_bot/photos/ -mtime +90 -delete  # Elimina foto più vecchie di 90 giorni
```

## 🔒 Sicurezza

- **Non condividere mai il tuo bot token**
- Il file `.env` è in `.gitignore` per evitare di committarlo
- Solo tu puoi usare il bot (controlla con l'user_id se necessario)

## 📈 Backup

Per fare backup del database:

```bash
# Backup manuale
cp ~/food_diary_bot/data/food_diary.db ~/backup/food_diary_$(date +%Y%m%d).db

# Backup automatico giornaliero (aggiungi a crontab)
crontab -e
# Aggiungi questa riga:
# 0 2 * * * cp ~/food_diary_bot/data/food_diary.db ~/backup/food_diary_$(date +\%Y\%m\%d).db
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
