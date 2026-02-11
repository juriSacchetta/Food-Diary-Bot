"""
Telegram bot for food diary
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)

from database import DatabaseManager
from exporter import ExcelExporter


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
MEAL_TYPE, INGREDIENTS, PHOTO, NOTES = range(4)


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
🍽️ /new_meal - Registra un nuovo pasto (interattivo)
📊 /stats - Visualizza le tue statistiche
📥 /export - Scarica il tuo diario in Excel
❓ /help - Mostra tutti i comandi

Inizia subito registrando il tuo primo pasto con /new_meal!
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
/new_meal - Registra un nuovo pasto (guidato)
/stats - Statistiche del tuo diario
/export - Esporta tutto in Excel
/export_week - Esporta ultima settimana
/export_month - Esporta ultimo mese

**Per registrare un pasto:**
Usa il comando /new_meal e segui la procedura guidata:
1️⃣ Scegli il tipo (Pasto principale o Snack)
2️⃣ Inserisci gli ingredienti
3️⃣ Aggiungi una foto (opzionale)
4️⃣ Aggiungi note extra (opzionale)
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
    
    async def new_meal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the interactive meal registration process"""
        user_id = update.effective_user.id
        
        if not self.is_user_allowed(user_id):
            await update.message.reply_text("⛔ Accesso negato.")
            return ConversationHandler.END
        
        # Create inline keyboard for meal type selection
        keyboard = [
            [
                InlineKeyboardButton("🍽️ Pasto Principale", callback_data="meal_main"),
                InlineKeyboardButton("🍪 Snack", callback_data="meal_snack")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🍽️ **Registrazione Nuovo Pasto**\n\n"
            "Scegli il tipo di pasto:",
            reply_markup=reply_markup
        )
        
        return MEAL_TYPE
    
    async def meal_type_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle meal type selection"""
        query = update.callback_query
        await query.answer()
        
        # Store meal type in context
        meal_type = "Pasto Principale" if query.data == "meal_main" else "Snack"
        context.user_data['meal_type'] = query.data.replace("meal_", "")
        
        await query.edit_message_text(
            f"✅ Tipo: **{meal_type}**\n\n"
            "📝 Ora inserisci gli **ingredienti** del pasto:\n"
            "(es: Pasta al pomodoro, parmigiano, basilico)"
        )
        
        return INGREDIENTS
    
    async def ingredients_received(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle ingredients input"""
        user_id = update.effective_user.id
        
        if not self.is_user_allowed(user_id):
            await update.message.reply_text("⛔ Accesso negato.")
            return ConversationHandler.END
        
        # Store ingredients
        context.user_data['ingredients'] = update.message.text
        
        # Ask for photo
        keyboard = [
            [InlineKeyboardButton("⏭️ Salta foto", callback_data="skip_photo")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📷 Ottimo! Ora invia una **foto** del pasto\n"
            "(oppure premi 'Salta foto' per continuare)",
            reply_markup=reply_markup
        )
        
        return PHOTO
    
    async def photo_received(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo upload"""
        user_id = update.effective_user.id
        
        if not self.is_user_allowed(user_id):
            await update.message.reply_text("⛔ Accesso negato.")
            return ConversationHandler.END
        
        # Save photo
        photo_path = await self.save_photo(update, context)
        context.user_data['photo_path'] = photo_path
        
        # Ask for notes
        keyboard = [
            [InlineKeyboardButton("✅ Termina registrazione", callback_data="skip_notes")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ Foto salvata!\n\n"
            "📝 Vuoi aggiungere altre **note**?\n"
            "(es: Pasto cucinato a casa, molto buono)\n\n"
            "Oppure premi 'Termina registrazione'",
            reply_markup=reply_markup
        )
        
        return NOTES
    
    async def skip_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Skip photo step"""
        query = update.callback_query
        await query.answer()
        
        context.user_data['photo_path'] = None
        
        keyboard = [
            [InlineKeyboardButton("✅ Termina registrazione", callback_data="skip_notes")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⏭️ Foto saltata\n\n"
            "📝 Vuoi aggiungere altre **note**?\n"
            "(es: Pasto cucinato a casa, molto buono)\n\n"
            "Oppure premi 'Termina registrazione'"
        )
        await query.message.reply_text(
            "Inserisci le note o premi il pulsante per terminare:",
            reply_markup=reply_markup
        )
        
        return NOTES
    
    async def notes_received(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle notes and save meal"""
        user_id = update.effective_user.id
        
        if not self.is_user_allowed(user_id):
            await update.message.reply_text("⛔ Accesso negato.")
            return ConversationHandler.END
        
        # Store notes
        notes = update.message.text
        
        # Save to database
        await self.save_meal_to_db(update, context, notes)
        
        return ConversationHandler.END
    
    async def skip_notes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Skip notes and save meal"""
        query = update.callback_query
        await query.answer()
        
        # Save to database without notes
        await self.save_meal_to_db(update, context, message=None)
        
        return ConversationHandler.END
    
    async def save_meal_to_db(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: Optional[str] = None):
        """Save the completed meal to database"""
        user = update.effective_user if update.effective_user else update.callback_query.from_user
        
        meal_type = context.user_data.get('meal_type', 'meal')
        ingredients = context.user_data.get('ingredients', 'Non specificato')
        photo_path = context.user_data.get('photo_path', None)
        
        # Create message text
        if message:
            full_message = f"{ingredients}\n\nNote: {message}"
        else:
            full_message = ingredients
        
        # Save to database
        meal_id = self.db.add_meal(
            user_id=user.id,
            username=user.username,
            message=full_message,
            photo_path=photo_path,
            meal_type=meal_type,
            ingredients=ingredients
        )
        
        # Send confirmation
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        meal_type_emoji = "🍽️" if meal_type == "main" else "🍪"
        meal_type_label = "Pasto Principale" if meal_type == "main" else "Snack"
        
        confirmation = (
            f"✅ **Pasto registrato con successo!**\n\n"
            f"{meal_type_emoji} Tipo: {meal_type_label}\n"
            f"📝 Ingredienti: {ingredients}\n"
            f"🕐 {timestamp}"
        )
        
        if photo_path:
            confirmation += "\n📷 Foto salvata"
        
        if message:
            confirmation += f"\n💭 Note: {message}"
        
        # Clear user data
        context.user_data.clear()
        
        # Send confirmation
        if update.message:
            await update.message.reply_text(confirmation)
        else:
            await update.callback_query.message.reply_text(confirmation)
    
    async def cancel_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the meal registration"""
        context.user_data.clear()
        await update.message.reply_text(
            "❌ Registrazione annullata.\n\n"
            "Usa /new_meal per iniziare una nuova registrazione."
        )
        return ConversationHandler.END
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages and photos - inform about new registration method"""
        user = update.effective_user
        
        if not self.is_user_allowed(user.id):
            await update.message.reply_text("⛔ Accesso negato.")
            return
        
        # Inform user about the new interactive registration
        await update.message.reply_text(
            "ℹ️ **Nuovo Sistema di Registrazione!**\n\n"
            "Ora puoi registrare i pasti in modo guidato con più dettagli!\n\n"
            "🍽️ Usa il comando **/new_meal** per iniziare la registrazione interattiva.\n\n"
            "Potrai scegliere:\n"
            "• Tipo di pasto (Principale o Snack)\n"
            "• Ingredienti\n"
            "• Foto (opzionale)\n"
            "• Note aggiuntive (opzionale)"
        )
    
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
        
        # Conversation handler for meal registration
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("new_meal", self.new_meal_command)],
            states={
                MEAL_TYPE: [CallbackQueryHandler(self.meal_type_selected)],
                INGREDIENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.ingredients_received)],
                PHOTO: [
                    MessageHandler(filters.PHOTO, self.photo_received),
                    CallbackQueryHandler(self.skip_photo, pattern="^skip_photo$")
                ],
                NOTES: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.notes_received),
                    CallbackQueryHandler(self.skip_notes, pattern="^skip_notes$")
                ]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_registration)]
        )
        
        # Add conversation handler
        application.add_handler(conv_handler)
        
        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("export", self.export_command))
        application.add_handler(CommandHandler("export_week", self.export_week_command))
        application.add_handler(CommandHandler("export_month", self.export_month_command))
        
        # Add message handler (for text and photos) - this now only triggers outside conversation
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
