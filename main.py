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

TOKEN = os.getenv("BOT_TOKEN")
try:
    ADMIN_ID = int(os.getenv("ADMIN_GROUP_ID").strip())
except:
    ADMIN_ID = None

# --- HANDLER START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = f"@{user.username}" if user.username else "Tanpa Username"
    
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

    # LOG KE ADMIN (Dibuat seaman mungkin)
    if ADMIN_ID:
        async def send_admin_log():
            try:
                # 1. Kirim Teks Dulu (Supaya Cepat)
                log_msg = await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"👤 **USER START BOT**\nID: `{user.id}`\nNama: {user.full_name}\nUser: {username}",
                    parse_mode='Markdown'
                )
                
                # 2. Coba kirim foto profil secara terpisah
                user_photos = await context.bot.get_user_profile_photos(user.id, limit=1)
                if user_photos.total_count > 0:
                    await context.bot.send_photo(
                        chat_id=ADMIN_ID,
                        photo=user_photos.photos[0][-1].file_id,
                        caption=f"🖼 Foto Profil: {user.first_name}",
                        reply_to_message_id=log_msg.message_id
                    )
            except Exception as e:
                logger.error(f"Gagal kirim log admin: {e}")
        
        # Jalankan di background agar tidak menghambat respons ke user
        asyncio.create_task(send_admin_log())

# --- HANDLER FOTO ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().hour
    if now < 6 or now > 21:
        await update.message.reply_text("⚠️ Server Offline. Bot aktif 06.00 - 21.00 WIB.")
        return

    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id
    
    # Respons awal
    await update.message.reply_text("Sedang diproses...")

    # KIRIM KE ADMIN
    try:
        # Gunakan caption yang simpel agar tidak kena limit karakter
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=f"📥 **LAPORAN FOTO BARU**\nDari: {user.full_name}\nID: `{user.id}`",
            parse_mode='Markdown'
        )
        logger.info(f"Foto berhasil diteruskan ke admin {ADMIN_ID}")
    except Exception as e:
        logger.error(f"Metode foto gagal, mencoba dokumen: {e}")
        try:
            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=photo_id,
                caption=f"📥 **LAPORAN FOTO (DOC)**\nUser: {user.full_name}"
            )
        except Exception as e2:
            logger.error(f"Semua metode pengiriman ke admin gagal: {e2}")

    # Hasil Simulasi
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

    print(f"🚀 Bot Ready! Monitoring User Aktif.")
    app.run_polling(drop_pending_updates=True)
