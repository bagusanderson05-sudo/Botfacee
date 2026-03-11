import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURATION & LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
RAW_ADMIN_ID = os.getenv("ADMIN_GROUP_ID")

# Pastikan ID Admin dikonversi ke Integer dengan benar
try:
    ADMIN_GROUP_ID = int(RAW_ADMIN_ID.strip()) if RAW_ADMIN_ID else None
except ValueError:
    logger.error("Format ADMIN_GROUP_ID di .env salah! Harus berupa angka.")
    ADMIN_GROUP_ID = None

# --- 2. HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "*SELAMAT DATANG BOT FR TESTING*\n\n"
        "1. Kirim foto tampak depan jelas.\n"
        "2. Sistem akan mengecek otomatis.\n"
        "3. Jam operasional: 06.00 - 21.00 WIB."
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cek Jam Operasional
    now = datetime.now().hour
    if now < 6 or now > 21:
        await update.message.reply_text("⚠️ Server Offline. Jam operasional 06.00 - 21.00 WIB.")
        return

    user = update.message.from_user
    photo_file_id = update.message.photo[-1].file_id
    username = f"@{user.username}" if user.username else "Tidak ada"

    # A. Respon ke User
    await update.message.reply_text("📥 Foto diterima. Sedang diteruskan ke Admin...")

    # B. Kirim ke Admin
    try:
        if ADMIN_GROUP_ID is None:
            raise ValueError("ADMIN_GROUP_ID tidak terkonfigurasi dengan benar.")

        await context.bot.send_photo(
            chat_id=ADMIN_GROUP_ID,
            photo=photo_file_id,
            caption=(
                f"📥 *LAPORAN FOTO BARU*\n\n"
                f"👤 *Nama:* {user.first_name}\n"
                f"🆔 *User ID:* `{user.id}`\n"
                f"🌐 *Username:* {username}"
            ),
            parse_mode='Markdown'
        )
        logger.info(f"Berhasil meneruskan foto dari {user.id} ke grup {ADMIN_GROUP_ID}")

    except Exception as e:
        logger.error(f"Gagal kirim ke admin: {e}")
        await update.message.reply_text(f"❌ Gagal lapor ke admin: {e}")
        return

    # C. Simulasi Proses FR
    await asyncio.sleep(3)
    await update.message.reply_text(
        "*HASIL PENGECEKAN FR*\n\n"
        "Nama : DATA TIDAK DITEMUKAN\n"
        "NIK  : -\n"
        "STATUS : TIDAK ADA DATA",
        parse_mode='Markdown'
    )

# --- 3. MAIN RUNNER ---

if __name__ == '__main__':
    if not TOKEN or not ADMIN_GROUP_ID:
        print("❌ ERROR: TOKEN atau ADMIN_GROUP_ID belum diatur di .env!")
    else:
        # Build Application
        app = ApplicationBuilder().token(TOKEN).build()

        # Add Handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

        print(f"🚀 Bot Running...")
        print(f"Target Admin ID: {ADMIN_GROUP_ID}")

        # drop_pending_updates=True adalah kunci untuk mengatasi 'Conflict'
        # Ini akan menghapus antrean pesan lama yang nyangkut di server
        app.run_polling(drop_pending_updates=True)
