import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
try:
    ADMIN_ID = int(os.getenv("ADMIN_GROUP_ID").strip())
except:
    ADMIN_ID = None

# --- HANDLER START (REVISI PESAN SAMBUTAN) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
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
    
    # Kirim info ke grup admin
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🚀 **USER START**\nNama: {user.first_name}\nID: `{user.id}`",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Gagal kirim start ke admin: {e}")

# --- HANDLER FOTO ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id
    
    # Mengirim notifikasi awal ke user
    await update.message.reply_text("📥 Foto diterima, mencoba mengirim ke admin...")

    # METODE 1: Mencoba kirim sebagai FOTO
    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=f"📸 **METODE FOTO**\nUser: {user.first_name}\nID: `{user.id}`",
            parse_mode='Markdown'
        )
    except Exception as e_photo:
        logger.warning(f"Gagal METODE FOTO: {e_photo}")
        
        # METODE 2: Fallback ke Dokumen
        try:
            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=photo_id,
                caption=f"📄 **METODE DOKUMEN (Fallback)**\nUser: {user.first_name}",
                parse_mode='Markdown'
            )
        except Exception as e_doc:
            logger.error(f"Gagal METODE DOKUMEN: {e_doc}")
            await update.message.reply_text("❌ Terjadi kendala saat memproses foto.")
            return

    # Jeda simulasi sebelum memberikan hasil (Ubah sesuai kebutuhan)
    await asyncio.sleep(2)
    # REVISI: Mengubah balasan hasil menjadi "Sedang diproses..."
    await update.message.reply_text("Sedang diproses...")

if __name__ == '__main__':
    if not TOKEN or not ADMIN_ID:
        print("❌ Cek .env! BOT_TOKEN dan ADMIN_GROUP_ID wajib diisi.")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print(f"🚀 Bot Running... Target Admin: {ADMIN_ID}")
    app.run_polling(drop_pending_updates=True)
