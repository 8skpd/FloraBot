import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)
from main_giga import ImageAnalyzer as GigaAnalyzer
from main_prplx import ImageAnalyzer as PrplxAnalyzer

# Словарь для хранения состояния пользователей: user_id -> 'giga' or 'prplx'
USER_STATES = {}

# Настройки для GigaChat
GIGA_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS", "api_key")
GIGA_SCOPE = "GIGACHAT_API_PERS"
GIGA_MODEL = "GigaChat-Max"

# Настройки для Perplexity
PRPLX_APIKEY = os.getenv("PRPLX_API_KEY", "api_key")

# Инициализация анализаторов
giga_analyzer = GigaAnalyzer(GIGA_CREDENTIALS, GIGA_SCOPE, GIGA_MODEL)
prplx_analyzer = PrplxAnalyzer(PRPLX_APIKEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - приветствие и установка начальной нейросети"""
    user_id = update.effective_user.id
    USER_STATES[user_id] = "giga"  # По умолчанию GigaChat

    await update.message.reply_text(
        "🌿 Добро пожаловать!\n\n"
        "Отправьте png или jpg файл с растением или грибом, "
        "а я отвечу что это и дам полезную информацию.\n\n"
        "🤖 Текущая нейросеть: GigaChat\n"
        "📝 /switch — переключить на Perplexity\n"
        "❓ /help — справка"
    )


async def switch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /switch - переключение между нейросетями"""
    user_id = update.effective_user.id
    current = USER_STATES.get(user_id, "giga")

    # Переключаем
    USER_STATES[user_id] = "prplx" if current == "giga" else "giga"

    model_name = "Perplexity" if USER_STATES[user_id] == "prplx" else "GigaChat"

    await update.message.reply_text(
        f"✅ Нейросеть изменена!\n\n"
        f"🤖 Теперь анализ изображений ведется через: {model_name}\n\n"
        f"Отправьте png или jpg файл с растением или грибом!"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help - справка по использованию бота"""
    await update.message.reply_text(
        "📖 Как пользоваться ботом:\n\n"
        "1. Отправьте фотографию растения или гриба в формате PNG/JPG\n"
        "2. Бот проанализирует изображение и выдаст информацию:\n"
        "   • Название (русское и латинское)\n"
        "   • Семейство\n"
        "   • Ключевые признаки\n"
        "   • Среду обитания\n"
        "   • Интересные факты\n\n"
        "🔄 /switch — переключить нейросеть (GigaChat ⇄ Perplexity)\n"
        "🏠 /start — перезапустить бота"
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фотографий - основная логика анализа"""
    user_id = update.effective_user.id

    # Получаем фото
    photos = update.message.photo
    if not photos:
        await update.message.reply_text(
            "⚠️ Отправьте, пожалуйста, фотографию растения или гриба в формате PNG/JPG."
        )
        return

    # Уведомление о начале обработки
    processing_msg = await update.message.reply_text("🔍 Анализирую изображение...")

    try:
        # Скачиваем файл
        file_id = photos[-1].file_id
        photo_file = await context.bot.get_file(file_id)
        filename = f"temp_{user_id}_{int(update.message.date.timestamp())}.jpg"
        await photo_file.download_to_drive(filename)

        # Определяем выбранную модель
        model = USER_STATES.get(user_id, "giga")

        # Анализируем через выбранную нейросеть
        if model == "giga":
            giga_analyzer.add_image(filename)
            result = giga_analyzer.identify_object(filename)
        else:  # prplx
            prplx_analyzer.add_image(filename)
            result = prplx_analyzer.identify_object(filename)

        # Удаляем сообщение о обработке
        await processing_msg.delete()

        # Отправляем результат
        await update.message.reply_text(
            f"📊 Результат анализа:\n\n{result}\n\n"
            f"🔄 Отправьте новое изображение для продолжения анализа!"
        )

        # Удаляем временный файл
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await processing_msg.delete()
        await update.message.reply_text(
            f"❌ Произошла ошибка при анализе изображения:\n{str(e)}\n\n"
            f"Попробуйте отправить другое изображение."
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик документов (если пользователь отправит файл как документ)"""
    await update.message.reply_text(
        "⚠️ Пожалуйста, отправьте изображение как фото, а не как файл/документ.\n"
        "Просто прикрепите изображение в чат."
    )


def main():
    """Запуск бота"""
    # ИСПРАВЛЕНО: Правильное использование os.getenv()
    # Вариант 1: Получить из переменной окружения
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    # Вариант 2: Если переменной нет, использовать токен напрямую
    if not token:
        token = "8481248627:AAFEez1gAQwI_unfiEacnyRqrYqcpJRTq-I"

    # Проверка наличия токена
    if not token:
        print("❌ Ошибка: не установлена переменная окружения TELEGRAM_BOT_TOKEN")
        return

    # Создаем приложение
    app = ApplicationBuilder().token(token).build()

    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("switch", switch))
    app.add_handler(CommandHandler("help", help_cmd))

    # Регистрируем обработчики сообщений
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

    # Запускаем бота
    print("🤖 Бот запущен и готов к работе!")
    app.run_polling()


if __name__ == "__main__":
    main()
