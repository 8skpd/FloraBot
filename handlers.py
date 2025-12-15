# ═════════════════════════════════════════════════════════════════
# 🌿 PLANT RECOGNITION BOT - HANDLERS
# ═════════════════════════════════════════════════════════════════
# Обработчики команд и сообщений для Telegram бота
# ═════════════════════════════════════════════════════════════════

import os
import tempfile
from typing import Dict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ParseMode

from models import AnalysisMode, AnalysisResult
from identifier import IdentifierAgent


class BotHandlers:
    """Обработчики команд и сообщений"""
    
    def __init__(self, identifier: IdentifierAgent, user_data: Dict[int, dict]):
        self.identifier = identifier
        self.user_data = user_data
    
    # ═════════════════════════════════════════════════════════════════
    # 🔧 КОМАНДЫ
    # ═════════════════════════════════════════════════════════════════
    
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        
        # Инициализируем данные пользователя
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "mode": AnalysisMode.PAID,
                "total_images": 0,
                "total_tokens_used": 0
            }
        
        keyboard = [
            [
                InlineKeyboardButton("🆓 Бесплатный режим", callback_data="mode_free"),
                InlineKeyboardButton("💎 Платный режим", callback_data="mode_paid")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """
👋 *Добро пожаловать!*

Это бот для распознавания растений и грибов! 🌿🍄

🎯 *Что я умею:*
• Распознавать растения и грибы по фото
• Выдавать научное латинское название
• Рассказывать интересные факты
• Проверять съедобность

📊 *Два режима работы:*

🆓 *Бесплатный режим*
   • Быстрый анализ (~5-7 сек)
   • Базовая точность
   • Меньше токенов

💎 *Платный режим*
   • Расширенный анализ (~10-15 сек)
   • Высокая точность
   • Больше интересных фактов

📸 *Как начать:*
1. Выберите режим ниже
2. Отправьте фото растения или гриба
3. Получите результат!
"""
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        message = """
📖 *ИНСТРУКЦИЯ*

1️⃣ *Выберите режим* (/mode)
   🆓 Бесплатный - быстро
   💎 Платный - точнее

2️⃣ *Отправьте фото*
   • Растения или грибы
   • Хорошее качество 📸
   • Видны характерные признаки

3️⃣ *Дождитесь анализа*
   • Бесплатный: 5-7 сек
   • Платный: 10-15 сек

4️⃣ *Получите результат*
   • Русское название
   • Латинское научное название
   • Семейство
   • Характеристики
   • Место обитания
   • Съедобность
   • Интересные факты

💡 *Советы:*
• Фотируйте с разных углов
• Включайте естественное освещение
• Показывайте характерные признаки

⚙️ *Команды:*
/start - начало
/help - справка
/mode - переключить режим
/stats - статистика
"""
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def mode_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /mode"""
        user_id = update.effective_user.id
        current_mode = self.user_data.get(user_id, {}).get("mode", AnalysisMode.PAID)
        
        keyboard = [
            [
                InlineKeyboardButton("🆓 Бесплатный (5-7 сек)", callback_data="set_mode_free"),
                InlineKeyboardButton("💎 Платный (10-15 сек)", callback_data="set_mode_paid")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        current = "🆓 БЕСПЛАТНЫЙ" if current_mode == AnalysisMode.FREE else "💎 ПЛАТНЫЙ"
        
        message = f"""
*Выберите режим анализа:*

Текущий режим: *{current}*

🆓 *Бесплатный режим*
   ✓ Быстрый (~5-7 сек)
   ✓ Базовая точность
   ✓ Минимальные затраты
   
💎 *Платный режим*
   ✓ Расширенный анализ
   ✓ Высокая точность
   ✓ Больше информации
   ⏱️ Медленнее (~10-15 сек)
"""
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def stats_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats"""
        user_id = update.effective_user.id
        user_stats = self.user_data.get(user_id, {})
        
        mode = user_stats.get("mode", AnalysisMode.PAID).value
        images = user_stats.get("total_images", 0)
        tokens = user_stats.get("total_tokens_used", 0)
        
        mode_emoji = "🆓" if mode == "free" else "💎"
        mode_name = "Бесплатный" if mode == "free" else "Платный"
        
        message = f"""
📊 *Ваша статистика*

{mode_emoji} *Режим:* {mode_name}
📸 *Обработано фото:* {images}
🔢 *Использовано токенов:* {tokens}

💡 Используйте /mode для переключения режима
"""
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    # ═════════════════════════════════════════════════════════════════
    # 🔘 CALLBACK ОБРАБОТЧИКИ
    # ═════════════════════════════════════════════════════════════════
    
    async def callback_mode_free(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback для выбора бесплатного режима на /start"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "mode": AnalysisMode.FREE,
                "total_images": 0,
                "total_tokens_used": 0
            }
        else:
            self.user_data[user_id]["mode"] = AnalysisMode.FREE
        
        await query.answer("✅ Выбран бесплатный режим", show_alert=False)
        
        message = """
✅ *Вы выбрали бесплатный режим*

🆓 *Параметры:*
• Скорость: Быстрый (~5-7 сек)
• Точность: Базовая
• Токены: Минимальные затраты

📸 Теперь отправляйте фото растений и грибов!
"""
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def callback_mode_paid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback для выбора платного режима на /start"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "mode": AnalysisMode.PAID,
                "total_images": 0,
                "total_tokens_used": 0
            }
        else:
            self.user_data[user_id]["mode"] = AnalysisMode.PAID
        
        await query.answer("✅ Выбран платный режим", show_alert=False)
        
        message = """
✅ *Вы выбрали платный режим*

💎 *Параметры:*
• Скорость: Средняя (~10-15 сек)
• Точность: Высокая
• Токены: Расширенная обработка

📸 Теперь отправляйте фото растений и грибов!
"""
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def callback_set_mode_free(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback для переключения на бесплатный режим из /mode"""
        query = update.callback_query
        user_id = query.from_user.id
        
        self.user_data[user_id]["mode"] = AnalysisMode.FREE
        
        await query.answer("✅ Перешли на бесплатный режим", show_alert=False)
        
        message = """
✅ *Текущий режим: БЕСПЛАТНЫЙ (🆓)*

Параметры анализа:
• Скорость: ~5-7 сек
• Точность: Базовая
• Модель: Быстрый анализ

Отправляйте фото! 📸
"""
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def callback_set_mode_paid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Callback для переключения на платный режим из /mode"""
        query = update.callback_query
        user_id = query.from_user.id
        
        self.user_data[user_id]["mode"] = AnalysisMode.PAID
        
        await query.answer("✅ Перешли на платный режим", show_alert=False)
        
        message = """
✅ *Текущий режим: ПЛАТНЫЙ (💎)*

Параметры анализа:
• Скорость: ~10-15 сек
• Точность: Высокая
• Модель: Perplexity (расширенный)

Отправляйте фото! 📸
"""
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    # ═════════════════════════════════════════════════════════════════
    # 📸 ОБРАБОТКА МЕДИА И ТЕКСТА
    # ═════════════════════════════════════════════════════════════════
    
    async def photo_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик загрузки фото"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Инициализируем данные пользователя если нужно
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "mode": AnalysisMode.PAID,
                "total_images": 0,
                "total_tokens_used": 0
            }
        
        user_mode = self.user_data[user_id]["mode"]
        mode_emoji = "🆓" if user_mode == AnalysisMode.FREE else "💎"
        
        # Отправляем "печатает..." индикатор
        await context.bot.send_chat_action(
            chat_id=chat_id,
            action=ChatAction.TYPING
        )
        
        try:
            # Отправляем сообщение о начале анализа
            time_est = "5-7 сек" if user_mode == AnalysisMode.FREE else "10-15 сек"
            await update.message.reply_text(
                f"{mode_emoji} *Анализирую фото...*\n\n⏳ Это займет {time_est}",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Скачиваем и сохраняем изображение
            photo_file = await update.message.photo[-1].get_file()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                image_path = tmp.name
            
            await photo_file.download_to_drive(image_path)
            print(f"📥 Фото сохранено: {image_path}")
            
            # Анализируем с выбранным режимом
            result, tokens_used = self.identifier.identify(image_path, user_mode)
            
            # Обновляем статистику
            self.user_data[user_id]["total_images"] += 1
            self.user_data[user_id]["total_tokens_used"] += tokens_used
            
            # Форматируем ответ
            response_msg = result.to_message()
            response_msg += f"\n\n{mode_emoji} *Режим:* {'Бесплатный' if user_mode == AnalysisMode.FREE else 'Платный'}\n• Токенов: {tokens_used}"
            
            # Отправляем результат
            await update.message.reply_text(
                response_msg,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Удаляем временный файл
            try:
                os.remove(image_path)
                print(f"🗑️  Временный файл удален")
            except:
                pass
        
        except Exception as e:
            error_msg = f"❌ *Ошибка анализа:*\n\n`{str(e)[:200]}`"
            print(f"Error: {str(e)}")
            await update.message.reply_text(
                error_msg,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        message = """
📸 *Пожалуйста, отправьте фото растения или гриба!*

Используйте команды:
/start - начало
/help - справка
/mode - переключить режим
/stats - статистика
"""
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
