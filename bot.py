"""
Telegram bot for food diary
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from database import DatabaseManager
from exporter import ExcelExporter


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class FoodDiaryBot:
    def __init__(self, token: str, allowed_user_ids: Optional[list] = None):
        self.token = token
        self.allowed_user_ids = allowed_user_ids or []
        self.db = DatabaseManager()
        self.exporter = ExcelExporter(self.db)
        self.photos_dir = Path("photos")
        self.photos_dir.mkdir(exist_ok=True)
    
    def is_user_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to use the bot"""
        if not self.allowed_user_ids:
            # If no whitelist is set, allow everyone
            return True
        return user_id in self.allowed_user_ids
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Check if user is allowed
        if not self.is_user_allowed(user.id):
            await update.message.reply_text(
                f"⛔ Accesso negato.\n\n"
                f"Il tuo User ID è: `{user.id}`\n"
                f"Contatta l'amministratore del bot per ottenere l'accesso."
            )
            logger.warning(f"Unauthorized access attempt by user {user.id} (@{user.username})")
            return
        
        welcome_message = f"""
👋 Ciao {user.first_name}!

Benvenuto nel tuo Diario Alimentare! 🍽️

**Come usarlo:**
📝 Invia un messaggio qualsiasi per registrare un pasto
📷 Puoi allegare una foto al messaggio
📊 /stats - Visualizza le tue statistiche
📥 /export - Scarica il tuo diario in Excel
🗑️ /help - Mostra tutti i comandi

Inizia subito inviando quello che hai mangiato!
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_id = update.effective_user.id
        
        if not self.is_user_allowed(user_id):
            await update.message.reply_text("⛔ Accesso negato.")
            return
        
        help_text = """
📋 **Comandi disponibili:**

/start - Messaggio di benvenuto
/help - Mostra questo messaggio
/stats - Statistiche del tuo diario
/export - Esporta tutto in Excel
/export_week - Esporta ultima settimana
/export_month - Esporta ultimo mese

**Per registrare un pasto:**
Invia semplicemente un messaggio con quello che hai mangiato.
Puoi aggiungere una foto per avere un ricordo visivo! 📷
        """
        await update.message.reply_text(help_text)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user_id = update.effective_user.id
        
        if not self.is_user_allowed(user_id):
            await update.message.reply_text("⛔ Accesso negato.")
            return
        
        stats = self.db.get_stats(user_id)
        
        stats_message = f"""
📊 **Le tue statistiche:**

🍽️ Pasti totali: {stats['total_meals']}
📅 Pasti oggi: {stats['meals_today']}
📆 Pasti questa settimana: {stats['meals_this_week']}
        """
        await update.message.reply_text(stats_message)
    
    async def export_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /export command - export all meals"""
        user_id = update.effective_user.id
        
        if not self.is_user_allowed(user_id):
            await update.message.reply_text("⛔ Accesso negato.")
            return
        
        await update.message.reply_text("⏳ Sto preparando il tuo export...")
        
        try:
            filename = self.exporter.export_to_excel(user_id)
            
            with open(filename, 'rb') as file:
                await update.message.reply_document(
                    document=file,
                    filename=f"diario_alimentare.xlsx",
                    caption="📥 Ecco il tuo diario alimentare completo!"
                )
            
            # Clean up file
            os.remove(filename)
            
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Export error: {e}")
            await update.message.reply_text("❌ Errore durante l'export. Riprova più tardi.")
    
    async def export_week_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export last week's meals"""
        user_id = update.effective_user.id
        
        if not self.is_user_allowed(user_id):
            await update.message.reply_text("⛔ Accesso negato.")
            return
        
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        await update.message.reply_text("⏳ Sto preparando l'export dell'ultima settimana...")
        
        try:
            filename = self.exporter.export_date_range_to_excel(
                user_id,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            with open(filename, 'rb') as file:
                await update.message.reply_document(
                    document=file,
                    filename=f"diario_settimana.xlsx",
                    caption="📥 Ecco i tuoi pasti dell'ultima settimana!"
                )
            
            os.remove(filename)
            
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Export week error: {e}")
            await update.message.reply_text("❌ Errore durante l'export. Riprova più tardi.")
    
    async def export_month_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export last month's meals"""
        user_id = update.effective_user.id
        
        if not self.is_user_allowed(user_id):
            await update.message.reply_text("⛔ Accesso negato.")
            return
        
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        await update.message.reply_text("⏳ Sto preparando l'export dell'ultimo mese...")
        
        try:
            filename = self.exporter.export_date_range_to_excel(
                user_id,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            with open(filename, 'rb') as file:
                await update.message.reply_document(
                    document=file,
                    filename=f"diario_mese.xlsx",
                    caption="📥 Ecco i tuoi pasti dell'ultimo mese!"
                )
            
            os.remove(filename)
            
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Export month error: {e}")
            await update.message.reply_text("❌ Errore durante l'export. Riprova più tardi.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages and photos"""
        user = update.effective_user
        
        if not self.is_user_allowed(user.id):
            await update.message.reply_text("⛔ Accesso negato.")
            return
        
        message_text = update.message.caption if update.message.caption else update.message.text
        
        if not message_text:
            message_text = "Pasto senza descrizione"
        
        photo_path = None
        
        # Handle photo if present
        if update.message.photo:
            photo_path = await self.save_photo(update, context)
        
        # Save to database
        meal_id = self.db.add_meal(
            user_id=user.id,
            username=user.username,
            message=message_text,
            photo_path=photo_path
        )
        
        # Send confirmation
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        confirmation = f"✅ Pasto registrato!\n\n📝 {message_text}\n🕐 {timestamp}"
        
        if photo_path:
            confirmation += "\n📷 Foto salvata"
        
        await update.message.reply_text(confirmation)
    
    async def save_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """Save photo from message"""
        try:
            photo = update.message.photo[-1]  # Get highest resolution
            file = await context.bot.get_file(photo.file_id)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            user_id = update.effective_user.id
            filename = f"photos/{user_id}_{timestamp}.jpg"
            
            # Download photo
            await file.download_to_drive(filename)
            
            return filename
            
        except Exception as e:
            logger.error(f"Error saving photo: {e}")
            return None
    
    def run(self):
        """Start the bot"""
        application = Application.builder().token(self.token).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("export", self.export_command))
        application.add_handler(CommandHandler("export_week", self.export_week_command))
        application.add_handler(CommandHandler("export_month", self.export_month_command))
        
        # Add message handler (for text and photos)
        application.add_handler(MessageHandler(
            filters.TEXT | filters.PHOTO,
            self.handle_message
        ))
        
        logger.info("Bot started!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    # Get token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        raise ValueError(
            "Token non trovato! Imposta la variabile d'ambiente TELEGRAM_BOT_TOKEN"
        )
    
    # Get allowed user IDs from environment variable
    allowed_user_ids = []
    allowed_ids_str = os.getenv("ALLOWED_USER_IDS", "")
    if allowed_ids_str:
        try:
            allowed_user_ids = [int(uid.strip()) for uid in allowed_ids_str.split(",") if uid.strip()]
            logger.info(f"Whitelist enabled: {len(allowed_user_ids)} authorized user(s)")
        except ValueError:
            logger.error("Invalid ALLOWED_USER_IDS format. Use comma-separated integers.")
    else:
        logger.warning("No ALLOWED_USER_IDS set. Bot is accessible to everyone!")
    
    bot = FoodDiaryBot(token, allowed_user_ids)
    bot.run()


if __name__ == "__main__":
    main()
