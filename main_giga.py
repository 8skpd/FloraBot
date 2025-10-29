import os
from gigachat import GigaChat

from prompts1 import build_full_prompt


class ImageAnalyzer:
    def __init__(self, credentials: str, scope: str = "GIGACHAT_API_PERS", model: str = "GigaChat-Max"):
        self.GIGACHAT_CREDENTIALS = credentials
        self.scope = scope
        self.model = model
        self.images = {}
        self.total_tokens_used = 0

        self.giga = GigaChat(
            credentials=self.GIGACHAT_CREDENTIALS,
            scope=self.scope,
            model=self.model,
            verify_ssl_certs=False
        )

    def add_image(self, file_path: str):
        """Загружает изображение"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        try:
            with open(file_path, "rb") as f:
                upload_resp = self.giga.upload_file(f)

            self.images[file_path] = upload_resp
            print(f"Файл {file_path} успешно загружен")

        except Exception as e:
            raise Exception(f"Ошибка при загрузке файла: {str(e)}")

    def analyze_image(
            self,
            file_path: str,
            prompt: str = "Определи, что изображено на снимке. Опиши объект и его особенности."
    ) -> str:
        """Анализирует изображение"""
        if file_path not in self.images:
            raise KeyError(f"Изображение не добавлено: {file_path}")

        try:
            upload_resp = self.images[file_path]
            file_id = upload_resp.id_

            chat_resp = self.giga.chat({
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                        "attachments": [file_id]
                    }
                ]
            })

            # Сохраняем информацию о токенах
            if hasattr(chat_resp, 'usage'):
                self.total_tokens_used += chat_resp.usage.total_tokens

            return chat_resp.choices[0].message.content

        except Exception as e:
            return f"Ошибка при анализе: {str(e)}"

    def analyze_all(self, prompt: str = None) -> list[dict]:
        """Анализирует все добавленные изображения"""
        prompt = prompt or "Определи, что изображено на снимке. Опиши объект и его особенности."
        results = []

        for file_path in self.images.keys():
            text = self.analyze_image(file_path, prompt)
            results.append({"image": file_path, "analysis": text})

        return results

    def get_image_count(self) -> int:
        return len(self.images)

    def get_remaining_tokens(self) -> dict:
        """Получает остаток токенов на аккаунте"""
        try:
            balance = self.giga.get_balance()
            return balance
        except Exception as e:
            return {"error": str(e)}

    def print_token_usage(self):
        """Выводит информацию об использованных и оставшихся токенах"""
        remaining = self.get_remaining_tokens()

        print(f"\n{'=' * 50}")
        print(f"Статистика токенов:")
        print(f"  Использовано в текущей сессии: {self.total_tokens_used}")

        if "error" not in remaining:
            print(f"  Остаток токенов на аккаунте:")
            for model, tokens in remaining.items():
                print(f"    {model}: {tokens}")
        else:
            print(f"  Остаток: {remaining['error']}")

        print(f"{'=' * 50}\n")

    def reset_token_counter(self):
        """Обнуляет счётчик токенов текущей сессии"""
        self.total_tokens_used = 0

    def clear_images(self):
        self.images = {}


    def identify_object(self, file_path: str) -> str:
        promted = build_full_prompt()
        return self.analyze_image(file_path, promted)

    def close(self):
        if hasattr(self.giga, "close"):
            self.giga.close()


if __name__ == "__main__":
    credentials = "api_key"
    analyzer = ImageAnalyzer(credentials)

    try:
        analyzer.add_image("лис.jpg")

        print(analyzer.identify_object("лис.jpg"))
        analyzer.print_token_usage()


    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        analyzer.close()
