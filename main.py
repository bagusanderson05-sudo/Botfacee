import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- KONFIGURASI LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Memuat variabel dari file .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
try:
    # Pastikan ID Grup Admin diawali dengan - (contoh: -100xxx)
    ADMIN_ID = int(os.getenv("ADMIN_GROUP_ID").strip())
except Exception as e:
    logger.error(f"Kesalahan konfigurasi ADMIN_GROUP_ID: {e}")
    ADMIN_ID = None

# --- HANDLER /START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    # Pesan sambutan sesuai permintaan
    welcome_text = (
        "SELAMAT DATANG\n\n"
        "BOT FR TESTING\n"
        "(KUOTA 10/DAY)\n\n"
        "CARA PENGGUNAAN BOT\n\n"
        "1. SILAHKAN MASUKKAN FOTO TARGET, UPAYAKAN FOTO TAMPAK DEPAN DAN TERLIHAT JELAS.\n\n\n"
        "2. SISTEM AKAN MELAKUKAN PENGECEKAN FR TARGET DALAM 10MENIT WAKTU TERCEPAT UNTUK MENDAPATKAN HASIL FR AKURASI TINGGI.\n\n"
        "3. BOT AKAN MENAMPILKAN HASIL NAMA, NIK, DAN PERSENTASE KEMIRIPAN DENGAN FOTO TARGET.\n\n\n"
        "4. BOT BERFUNGSI SAAT SERVER HIDUP DI PUKUL 06.00 WIB SAMPAI DENGAN PUKUL 21.00 WIB.\n\n"
        "5. GUNAKAN AKSES DENGAN BIJAK. TERIMAKASIH\n\n\n"
        "SELAMAT BERTUGAS, SEMOGA SUKSES SELALU"
    )
    
    await update.message.reply_text(welcome_text)
    
    # Kirim info User ke Grup Admin
    if ADMIN_ID:
        try:
            username = f"@{user.username}" if user.username else "Tidak ada username"
            info_admin = (
                "🚀 **USER BARU BERGABUNG**\n"
                "---------------------------\n"
                f"👤 **Nama:** {user.full_name}\n"
                f"🆔 **ID Telegram:** `{user.id}`\n"
                f"🔗 **Username:** {username}\n"
                f"📅 **Waktu:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                "---------------------------"
            )
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=info_admin,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Gagal kirim info start ke admin: {e}")

# --- HANDLER FOTO ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id
    
    # Notifikasi awal ke user
    await update.message.reply_text("📥 Foto diterima, mencoba mengirim ke admin...")

    # Logika pengiriman ke Admin (Forwarding)
    caption_admin = (
        f"📸 **PENGIRIMAN FOTO**\n"
        f"Dari: {user.full_name}\n"
        f"ID: `{user.id}`"
    )

    success = False
    # Coba kirim sebagai FOTO
    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=caption_admin,
            parse_mode='Markdown'
        )
        success = True
    except Exception as e_photo:
        logger.warning(f"Metode Foto gagal, mencoba Dokumen: {e_photo}")
        # Fallback ke DOKUMEN
        try:
            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=photo_id,
                caption=f"{caption_admin} (Format Dokumen)",
                parse_mode='Markdown'
            )
            success = True
        except Exception as e_doc:
            logger.error(f"Semua metode gagal: {e_doc}")
            await update.message.reply_text("❌ Gagal meneruskan foto ke server.")
            return

    # Jika berhasil terkirim ke admin
    if success:
        # Simulasi proses loading
        await asyncio.sleep(2)
        # Respon sesuai permintaan
        await update.message.reply_text("Sedang diproses...")

# --- MAIN RUNNER ---
if __name__ == '__main__':
    if not TOKEN or not ADMIN_ID:
        print("❌ ERROR: Harap isi BOT_TOKEN dan ADMIN_GROUP_ID di file .env!")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()

    # Menambahkan Handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print(f"✅ Bot telah berjalan... Monitoring Admin ID: {ADMIN_ID}")
    
    # Jalankan Bot
    app.run_polling(drop_pending_updates=True)
