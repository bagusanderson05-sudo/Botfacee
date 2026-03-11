import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- LOGGING SETUP ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

# --- VARIABEL ---
TOKEN = os.getenv("BOT_TOKEN")
try:
    # Membersihkan karakter aneh jika ada
    ADMIN_ID = int(os.getenv("ADMIN_GROUP_ID").strip())
except Exception as e:
    logger.error(f"Gagal membaca ADMIN_GROUP_ID: {e}")
    ADMIN_ID = None

# --- FUNGSI UTAMA ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ **BOT FR TESTING AKTIF**\n\nSilahkan kirim foto target Anda.",
        parse_mode='Markdown'
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cek Jam Operasional (06.00 - 21.00)
    now = datetime.now().hour
    if now < 6 or now > 21:
        await update.message.reply_text("⚠️ Server Offline. Jam operasional 06.00 - 21.00 WIB.")
        return

    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id
    username = f"@{user.username}" if user.username else "Tidak ada"

    # 1. Notifikasi ke User
    await update.message.reply_text("📥 Foto diterima. Sedang memproses ke admin...")

    # 2. Teruskan ke Grup Admin
    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=(
                f"📥 **LAPORAN FOTO BARU**\n\n"
                f"👤 Nama: {user.first_name}\n"
                f"🆔 ID: `{user.id}`\n"
                f"🌐 Username: {username}"
            ),
            parse_mode='Markdown'
        )
        logger.info(f"✅ Berhasil lapor ke grup {ADMIN_ID}")
    except Exception as e:
        logger.error(f"❌ Gagal lapor admin: {e}")
        # Kirim error ke user agar kita tahu penyebabnya (misal: Chat not found)
        await update.message.reply_text(f"❌ Gagal kirim ke admin: {e}")
        return

    # 3. Simulasi FR
    await asyncio.sleep(3)
    await update.message.reply_text(
        "**HASIL PENGECEKAN FR**\n\nNama : DATA TIDAK DITEMUKAN\nNIK : -\nSTATUS : TIDAK ADA DATA",
        parse_mode='Markdown'
    )

# --- RUNNER ---
if __name__ == '__main__':
    if not TOKEN or not ADMIN_ID:
        print("❌ Konfigurasi .env salah!")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print(f"🚀 Bot Running... Admin ID: {ADMIN_ID}")
    
    # drop_pending_updates=True akan menghapus sesi lama yang bikin Conflict
    app.run_polling(drop_pending_updates=True)
