import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Setup Logging yang lebih ketat
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
# Pastikan ADMIN_GROUP_ID di .env sudah benar (Contoh: -1003805823946)
try:
    ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID").strip())
except:
    ADMIN_GROUP_ID = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Aktif. Silahkan kirim foto target.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cek Jam Operasional
    now = datetime.now().hour
    if now < 6 or now > 21:
        await update.message.reply_text("⚠️ Server offline (06.00 - 21.00 WIB)")
        return

    user = update.message.from_user
    username = f"@{user.username}" if user.username else "Tidak ada"
    
    # Ambil foto kualitas tertinggi
    photo_file = await update.message.photo[-1].get_file()
    
    # Respon awal ke user
    await update.message.reply_text("📥 Foto diterima, sedang diteruskan ke Admin...")

    # --- PROSES KIRIM KE ADMIN ---
    try:
        # Kita gunakan file_id langsung, tapi jika gagal, bot akan memberikan error spesifik
        await context.bot.send_photo(
            chat_id=ADMIN_GROUP_ID,
            photo=photo_file.file_id,
            caption=(
                f"📥 *FOTO MASUK*\n\n"
                f"👤 User: {user.first_name}\n"
                f"🆔 ID: `{user.id}`\n"
                f"🌐 Username: {username}"
            ),
            parse_mode='Markdown'
        )
        print(f"✅ SUKSES: Foto dari {user.first_name} terkirim ke grup {ADMIN_GROUP_ID}")

    except Exception as e:
        print(f"❌ GAGAL KIRIM KE ADMIN: {e}")
        # Jika error 'Chat not found', berarti ID Grup salah
        # Jika error 'Forbidden', berarti bot bukan admin/dikeluarkan
        await update.message.reply_text(f"Terjadi error saat kirim ke admin: {e}")
        return

    # --- SIMULASI HASIL FR ---
    await asyncio.sleep(3)
    await update.message.reply_text(
        "HASIL PENGECEKAN FR\n\nNama : DATA TIDAK DITEMUKAN\nNIK : -\nSTATUS : TIDAK ADA DATA"
    )

if __name__ == '__main__':
    if not TOKEN or not ADMIN_GROUP_ID:
        print("❌ ERROR: TOKEN atau ADMIN_GROUP_ID kosong di .env")
        exit()

    # drop_pending_updates=True untuk membersihkan 'Conflict' dari sesi sebelumnya
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print(f"Bot berjalan. Target Admin ID: {ADMIN_GROUP_ID}")
    app.run_polling(drop_pending_updates=True)
