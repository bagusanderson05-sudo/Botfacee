import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- SETUP LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

# --- LOAD VARIABEL ---
TOKEN = os.getenv("BOT_TOKEN")
try:
    ADMIN_ID = int(os.getenv("ADMIN_GROUP_ID").strip())
except:
    ADMIN_ID = None

# --- HANDLER START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = f"@{user.username}" if user.username else "Tanpa Username"
    
    # 1. Kirim pesan selamat datang ke User
    await update.message.reply_text(
        "✅ **BOT AKTIF**\nSilahkan kirim foto target untuk pengecekan FR.",
        parse_mode='Markdown'
    )

    # 2. KIRIM INFO KE GRUP ADMIN (LOG START)
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🚀 **USER MENEKAN START**\n\n"
                f"👤 Nama: {user.first_name}\n"
                f"🆔 ID: `{user.id}`\n"
                f"🌐 Username: {username}"
            ),
            parse_mode='Markdown'
        )
        print(f"✅ Notifikasi START terkirim ke admin: {ADMIN_ID}")
    except Exception as e:
        print(f"❌ Gagal kirim notifikasi START: {e}")

# --- HANDLER FOTO ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cek Jam Operasional
    now = datetime.now().hour
    if now < 6 or now > 21:
        await update.message.reply_text("⚠️ Server Offline (06.00 - 21.00 WIB).")
        return

    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id
    username = f"@{user.username}" if user.username else "Tanpa Username"

    await update.message.reply_text("📥 Foto diterima. Meneruskan ke admin...")

    # KIRIM FOTO KE ADMIN
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
        print(f"✅ Foto berhasil terkirim ke admin.")
    except Exception as e:
        print(f"❌ Gagal kirim foto ke admin: {e}")
        # Notifikasi error ke user chat agar kita tahu penyebabnya
        await update.message.reply_text(f"❌ Error kirim ke admin: {e}")
        return

    # Hasil Simulasi
    await asyncio.sleep(3)
    await update.message.reply_text(
        "**HASIL PENGECEKAN FR**\n\nNama : DATA TIDAK DITEMUKAN\nNIK : -\nSTATUS : TIDAK ADA DATA",
        parse_mode='Markdown'
    )

# --- RUNNER ---
if __name__ == '__main__':
    if not TOKEN or not ADMIN_ID:
        print("❌ Cek kembali file .env Anda!")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print(f"🚀 Bot berjalan... Target Admin: {ADMIN_ID}")
    
    # drop_pending_updates=True penting untuk membuang antrean lama yang bikin Conflict
    app.run_polling(drop_pending_updates=True)
