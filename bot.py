# ═════════════════════════════════════════════════════════════════
# 🌿 TELEGRAM BOT FOR PLANT & MUSHROOM RECOGNITION 🍄
# ═════════════════════════════════════════════════════════════════
# ВЕРСИЯ 5.0 - МУЛЬТИФАЙЛОВАЯ АРХИТЕКТУРА
# ═════════════════════════════════════════════════════════════════
# Главный файл для запуска бота
# ═════════════════════════════════════════════════════════════════

import os
from typing import Dict

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from dotenv import load_dotenv

from models import AnalysisMode
from identifier import IdentifierAgent
from handlers import BotHandlers

# Загружаем переменные окружения
load_dotenv()


class PlantRecognitionBot:
    """
    Основной класс бота для распознавания растений и грибов
    """
    
    def __init__(self):
        """Инициализирует бот"""
        # Проверяем Telegram токен
        self.tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.tg_token or self.tg_token == "your_telegram_bot_token_here":
            raise ValueError("❌ TELEGRAM_BOT_TOKEN не установлен! Установите в .env файл")
        
        print(f"✅ Telegram токен загружен")
        
        # Инициализируем агент идентификации
        try:
            self.identifier = IdentifierAgent()
            print(f"✅ Perplexity API готов")
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            raise
        
        # Данные пользователей
        self.user_data: Dict[int, dict] = {}
        
        # Инициализируем обработчики
        self.handlers = BotHandlers(self.identifier, self.user_data)
        
        # Создаём приложение
        self.app = Application.builder().token(self.tg_token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настраивает обработчики команд и сообщений"""
        
        # Команды
        self.app.add_handler(CommandHandler("start", self.handlers.start_handler))
        self.app.add_handler(CommandHandler("help", self.handlers.help_handler))
        self.app.add_handler(CommandHandler("mode", self.handlers.mode_handler))
        self.app.add_handler(CommandHandler("stats", self.handlers.stats_handler))
        
        # Callback обработчики для кнопок
        self.app.add_handler(CallbackQueryHandler(self.handlers.callback_mode_free, pattern="^mode_free$"))
        self.app.add_handler(CallbackQueryHandler(self.handlers.callback_mode_paid, pattern="^mode_paid$"))
        self.app.add_handler(CallbackQueryHandler(self.handlers.callback_set_mode_free, pattern="^set_mode_free$"))
        self.app.add_handler(CallbackQueryHandler(self.handlers.callback_set_mode_paid, pattern="^set_mode_paid$"))
        
        # Обработка фото
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handlers.photo_handler))
        
        # Обработка других сообщений
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handlers.text_handler
        ))
    
    def run(self):
        """Запускает бота"""
        print("\n" + "="*70)
        print("🚀 БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ!")
        print("="*70)
        print("\n📱 Инструкции:")
        print("   1. Откройте Telegram")
        print("   2. Найдите бота")
        print("   3. Отправьте /start")
        print("   4. Выберите режим (бесплатный или платный)")
        print("   5. Отправляйте фото растений/грибов")
        print("\n💡 Для остановки нажмите Ctrl+C\n")
        print("="*70 + "\n")
        
        self.app.run_polling()


# ═════════════════════════════════════════════════════════════════
# 🚀 ЗАПУСК БОТА
# ═════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        print("\n" + "="*70)
        print("🔧 ИНИЦИАЛИЗАЦИЯ БОТА")
        print("="*70)
        
        bot = PlantRecognitionBot()
        bot.run()
    
    except KeyboardInterrupt:
        print("\n\n⛔ Бот остановлен пользователем")
    
    except ValueError as e:
        print(f"\n❌ ОШИБКА КОНФИГУРАЦИИ: {e}")
        print("\n💡 РЕШЕНИЕ:")
        print("   1. Убедитесь что .env файл существует:")
        print("      ls -la .env")
        print("   2. Проверьте что .env содержит ключи:")
        print("      cat .env | head -5")
        print("   3. Если .env нет - создайте:")
        print("      cp .env.example .env")
        print("   4. Отредактируйте .env и добавьте реальные ключи")
    
    except Exception as e:
        print(f"\n❌ ОШИБКА ЗАПУСКА: {e}")
        print("\n💡 РЕШЕНИЕ:")
        print("   1. Установите зависимости:")
        print("      pip install -r requirements.txt")
        print("   2. Проверьте что установлены все пакеты:")
        print("      pip list | grep -E 'telegram|openai|python-dotenv'")
        print("   3. Если openai не установлен:")
        print("      pip install openai")
