import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
try:
    ADMIN_ID = int(os.getenv("ADMIN_GROUP_ID").strip())
except:
    ADMIN_ID = None

# --- HANDLER START (SUDAH BERHASIL) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text("✅ Bot Aktif. Silakan kirim foto.")
    
    # Kirim info ke grup admin
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🚀 **USER START**\nNama: {user.first_name}\nID: `{user.id}`",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Gagal kirim start ke admin: {e}")

# --- HANDLER FOTO (UJI COBA DUAL-METHOD) ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id
    
    await update.message.reply_text("📥 Foto diterima, mencoba mengirim ke admin...")

    # METODE 1: Mencoba kirim sebagai FOTO
    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=f"📸 **METODE FOTO**\nUser: {user.first_name}",
            parse_mode='Markdown'
        )
        print("✅ Berhasil kirim menggunakan METODE FOTO")
        
    except Exception as e_photo:
        print(f"❌ Gagal METODE FOTO: {e_photo}")
        
        # METODE 2: Jika foto gagal, coba kirim sebagai DOKUMEN/FILE
        try:
            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=photo_id,
                caption=f"📄 **METODE DOKUMEN (Fallback)**\nUser: {user.first_name}",
                parse_mode='Markdown'
            )
            print("✅ Berhasil kirim menggunakan METODE DOKUMEN")
        except Exception as e_doc:
            print(f"❌ Gagal METODE DOKUMEN: {e_doc}")
            # Laporkan error terakhir ke chat user untuk diagnosa
            await update.message.reply_text(f"❌ Semua metode gagal.\nError Foto: {e_photo}\nError Dokumen: {e_doc}")
            return

    # Balasan hasil simulasi ke user
    await asyncio.sleep(2)
    await update.message.reply_text("HASIL: DATA TIDAK DITEMUKAN")

if __name__ == '__main__':
    if not TOKEN or not ADMIN_ID:
        print("❌ Cek .env!")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print(f"🚀 Bot Running... Target Admin: {ADMIN_ID}")
    app.run_polling(drop_pending_updates=True)
