# ═════════════════════════════════════════════════════════════════
# 🌿 PLANT RECOGNITION BOT - MODELS
# ═════════════════════════════════════════════════════════════════
# Модели данных для бота
# ═════════════════════════════════════════════════════════════════

from enum import Enum
from dataclasses import dataclass


class AnalysisMode(Enum):
    """Режимы анализа"""
    FREE = "free"      # Бесплатный: быстрый анализ
    PAID = "paid"      # Платный: расширенный анализ


@dataclass
class AnalysisResult:
    """Результат анализа растения/гриба"""
    
    common_name: str
    scientific_name: str
    organism_type: str
    confidence: float
    characteristics: list
    habitat: str
    edibility: str
    interesting_facts: list
    family: str = ""
    
    def to_message(self) -> str:
        """Форматирует результат для отправки в чат"""
        msg = f"""
🔍 *Идентификация*

*Название:* {self.common_name}
*Научное имя:* `{self.scientific_name}`
*Семейство:* {self.family}
*Тип:* {self.organism_type}

📊 *Уверенность:* {self.confidence * 100:.0f}%

🌱 *Характеристики:*
{chr(10).join(f"• {c}" for c in self.characteristics[:5])}

🏠 *Место обитания:* {self.habitat}

🍄 *Съедобность:* {self.edibility}

✨ *Интересные факты:*
{chr(10).join(f"• {f}" for f in self.interesting_facts[:3])}
"""
        return msg


@dataclass
class UserData:
    """Данные пользователя"""
    user_id: int
    mode: AnalysisMode = AnalysisMode.PAID
    total_images: int = 0
    total_tokens_used: int = 0
    
    def to_dict(self) -> dict:
        """Конвертирует в словарь"""
        return {
            "mode": self.mode,
            "total_images": self.total_images,
            "total_tokens_used": self.total_tokens_used
        }
