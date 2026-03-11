import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Setup Logging agar kita tahu kalau ada error di terminal
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
# Gunakan default 0 jika ID tidak ditemukan agar tidak crash saat startup
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID") 

WELCOME_TEXT = """
SELAMAT DATANG BOT FR TESTING

1. Masukkan foto tampak depan & jelas.
2. Sistem akan mengecek dalam 10 menit.
3. Operasional: 06.00 - 21.00 WIB.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Cek Jam Operasional
    now = datetime.now().hour
    if now < 6 or now > 21:
        await update.message.reply_text("⚠️ Server sedang offline\nJam operasional 06.00 - 21.00 WIB")
        return

    # 2. Ambil Data User & Foto
    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id
    
    # Proteksi jika username kosong (None)
    username = f"@{user.username}" if user.username else "Tidak ada"
    first_name = user.first_name if user.first_name else "User"

    # 3. Kirim ke Admin (Penyebab utama biasanya di sini)
    try:
        await context.bot.send_photo(
            chat_id=int(ADMIN_GROUP_ID), # Pastikan diconvert ke int di sini
            photo=photo_id,
            caption=(
                f"📥 **FOTO MASUK**\n\n"
                f"👤 **User:** {first_name}\n"
                f"🆔 **Username:** {username}\n"
                f"🔢 **User ID:** `{user.id}`"
            ),
            parse_mode='Markdown' # Agar tampilan lebih rapi
        )
        logging.info(f"Foto dari {first_name} berhasil diteruskan ke Admin.")
    except Exception as e:
        logging.error(f"Gagal kirim ke admin: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan saat mengirim data ke server.")
        return

    # 4. Respon ke User
    await update.message.reply_text(
        "📥 Foto diterima\n\n⏳ Sistem sedang melakukan pengecekan FR..."
    )

    # Simulasi proses (5 detik)
    await asyncio.sleep(5)

    await update.message.reply_text(
        "**HASIL PENGECEKAN FR**\n\n"
        "Nama : DATA TIDAK DITEMUKAN\n"
        "NIK  : -\n"
        "Kemiripan : 0%\n\n"
        "STATUS : TIDAK ADA DATA",
        parse_mode='Markdown'
    )

# Inisialisasi Bot
if __name__ == '__main__':
    if not TOKEN or not ADMIN_GROUP_ID:
        print("ERROR: Token atau Admin Group ID belum diisi di .env!")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    # Filter PHOTO ditambahkan agar tidak merespon dokumen/file biasa
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot sedang berjalan...")
    app.run_polling()
