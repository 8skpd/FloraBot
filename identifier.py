# ═════════════════════════════════════════════════════════════════
# 🌿 PLANT RECOGNITION BOT - IDENTIFIER AGENT
# ═════════════════════════════════════════════════════════════════
# Агент для идентификации растений и грибов через Perplexity API
# ═════════════════════════════════════════════════════════════════

import os
import base64
import json
import re
from typing import Tuple

from models import AnalysisMode, AnalysisResult


class IdentifierAgent:
    """
    Агент идентификации с использованием Perplexity API
    """
    
    def __init__(self):
        """Инициализирует агент с проверкой API ключа"""
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key or self.api_key == "pplx-your_api_key_here":
            raise ValueError("❌ PERPLEXITY_API_KEY не установлен! Установите в .env файл")
        
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Инициализирует OpenAI клиент для Perplexity"""
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.perplexity.ai"
            )
        except ImportError:
            raise ImportError("❌ openai не установлен. Запустите: pip install openai")
        except Exception as e:
            raise Exception(f"❌ Ошибка инициализации Perplexity: {str(e)}")
    
    def identify(self, image_path: str, mode: AnalysisMode = AnalysisMode.PAID) -> Tuple[AnalysisResult, int]:
        """
        Идентифицирует вид на фото
        
        Args:
            image_path: Путь к изображению
            mode: Режим анализа (FREE или PAID)
        
        Returns:
            (AnalysisResult, количество токенов)
        """
        try:
            # Проверяем что файл существует
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Файл не найден: {image_path}")
            
            # Кодируем изображение в base64
            with open(image_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            
            # Определяем тип файла
            ext = os.path.splitext(image_path)[1].lower()
            media_type = self._get_media_type(ext)
            
            # Выбираем промпт в зависимости от режима
            prompt = self._get_prompt(mode)
            
            # Отправляем запрос к Perplexity
            print(f"📡 Отправляю запрос к Perplexity API (режим: {mode.value})...")
            response = self.client.chat.completions.create(
                model="sonar",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{encoded}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }],
                temperature=0.2 if mode == AnalysisMode.PAID else 0.1,
                max_tokens=1000 if mode == AnalysisMode.PAID else 600,
                top_p=0.9
            )
            
            # Извлекаем текст ответа
            text = response.choices[0].message.content
            tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0
            
            print(f"✅ Получен ответ ({tokens} токенов)")
            
            # Парсим JSON
            result = self._parse_response(text)
            
            return result, tokens
        
        except Exception as e:
            print(f"❌ Ошибка анализа: {str(e)}")
            error_result = AnalysisResult(
                common_name="Ошибка анализа",
                scientific_name="N/A",
                organism_type="unknown",
                confidence=0.0,
                characteristics=[str(e)[:100]],
                habitat="N/A",
                edibility="unknown",
                interesting_facts=[]
            )
            return error_result, 0
    
    @staticmethod
    def _get_media_type(ext: str) -> str:
        """Определяет MIME тип файла по расширению"""
        media_types = {
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        return media_types.get(ext, "image/jpeg")
    
    @staticmethod
    def _get_prompt(mode: AnalysisMode) -> str:
        """Возвращает промпт в зависимости от режима"""
        if mode == AnalysisMode.FREE:
            return """Проанализируй фото и верни ТОЛЬКО JSON:
{
    "common_name": "название",
    "scientific_name": "вид",
    "family": "семейство",
    "organism_type": "тип",
    "confidence": "высокий/средний/низкий",
    "characteristics": ["признак 1", "признак 2"],
    "habitat": "место",
    "edibility": "съедобность",
    "interesting_facts": ["факт 1"]
}"""
        else:
            return """Проанализируй фото растения, гриба или другого организма ОЧЕНЬ ТЩАТЕЛЬНО и дай результат в виде JSON.

ВАЖНО: Верни ТОЛЬКО валидный JSON без дополнительного текста!

{
    "common_name": "русское название (обязательно)",
    "scientific_name": "латинское название вида",
    "family": "название семейства",
    "organism_type": "гриб/растение/лишайник/мох и т.д.",
    "confidence": "высокий/средний/низкий",
    "characteristics": ["отличительный признак 1", "признак 2", "признак 3"],
    "habitat": "место произрастания и условия",
    "edibility": "съедобен/несъедобен/ядовит/неизвестно",
    "interesting_facts": ["интересный факт 1", "факт 2", "факт 3"]
}

Если не можешь определить объект - все равно верни JSON с best guess и низким confidence."""
    
    @staticmethod
    def _parse_response(text: str) -> AnalysisResult:
        """Парсит JSON ответ от модели"""
        try:
            print(f"📝 Парсирую ответ: {text[:100]}...")
            
            # Извлекаем JSON из текста
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if not json_match:
                print("⚠️  JSON не найден в ответе")
                return AnalysisResult(
                    common_name="Ошибка парсинга",
                    scientific_name="N/A",
                    organism_type="unknown",
                    confidence=0.0,
                    characteristics=["JSON не найден в ответе"],
                    habitat="N/A",
                    edibility="unknown",
                    interesting_facts=["Попробуйте отправить другое фото"]
                )
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # Конвертируем confidence в число
            confidence = IdentifierAgent._parse_confidence(data.get("confidence", "средний"))
            
            print("✅ JSON успешно спарсен")
            
            return AnalysisResult(
                common_name=data.get("common_name", "Unknown"),
                scientific_name=data.get("scientific_name", "unknown"),
                organism_type=data.get("organism_type", "unknown"),
                confidence=confidence,
                characteristics=data.get("characteristics", []),
                habitat=data.get("habitat", "Unknown"),
                edibility=data.get("edibility", "unknown"),
                interesting_facts=data.get("interesting_facts", []),
                family=data.get("family", "Unknown")
            )
        
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {str(e)}")
            return AnalysisResult(
                common_name="Ошибка парсинга JSON",
                scientific_name="N/A",
                organism_type="unknown",
                confidence=0.0,
                characteristics=[f"JSON ошибка: {str(e)[:80]}"],
                habitat="N/A",
                edibility="unknown",
                interesting_facts=[]
            )
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {str(e)}")
            return AnalysisResult(
                common_name="Ошибка обработки",
                scientific_name="N/A",
                organism_type="unknown",
                confidence=0.0,
                characteristics=[f"Ошибка: {str(e)[:80]}"],
                habitat="N/A",
                edibility="unknown",
                interesting_facts=[]
            )
    
    @staticmethod
    def _parse_confidence(confidence_str: str) -> float:
        """Конвертирует строку confidence в число"""
        confidence_map = {
            "высокий": 0.9,
            "средний": 0.6,
            "низкий": 0.3
        }
        return confidence_map.get(str(confidence_str).lower(), 0.6)
