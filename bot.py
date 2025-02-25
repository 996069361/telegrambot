import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import instaloader

# Logging sozlamalari
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Instagramdan video yuklab olish funksiyasi
def download_instagram_video(url):
    try:
        loader = instaloader.Instaloader()
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        # Faylni yuklash
        target_folder = f"{post.owner_username}_{shortcode}"
        loader.download_post(post, target=target_folder)
        
        # Videoning haqiqiy yo‘lini topish
        for file in os.listdir(target_folder):
            if file.endswith(".mp4"):
                return os.path.join(target_folder, file)
        
        return None  # Agar video topilmasa
    except Exception as e:
        logger.error(f"Instagramdan yuklashda xatolik: {e}")
        return None

# /start buyrug'i uchun handler
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Salom! Men Instagramdan video yuklab beruvchi botman.\n"
        "Video URL manzilini yuboring."
    )

# Video URL manzilini qabul qilish va yuklab olish
async def handle_message(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    await update.message.reply_text("Video yuklab olinmoqda. Bir oz kuting...")

    video_path = download_instagram_video(url)
    
    if video_path:
        try:
            with open(video_path, "rb") as video_file:
                await update.message.reply_video(video=video_file)
        except Exception as e:
            logger.error(f"Faylni jo‘natishda xatolik: {e}")
            await update.message.reply_text("Video jo‘natishda xatolik yuz berdi.")
    else:
        await update.message.reply_text(
            "Video yuklab olishda muammo yuz berdi.\n"
            "Iltimos, URL manzilni tekshirib qayta urinib ko‘ring."
        )

# Xatoliklarni qayta ishlash uchun handler
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

# Asosiy bot funksiyasi
def main() -> None:
    # Tokeningizni shu yerga kiriting
    TOKEN = "8019465723:AAG_XC0u98J15Jes9DGeR0c0sooaONWsYJk"

    # Telegram botni yaratish
    application = Application.builder().token(TOKEN).build()

    # Handlerlarni qo‘shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error)

    # Botni ishga tushirish
    application.run_polling()

if __name__ == "__main__":
    main()
