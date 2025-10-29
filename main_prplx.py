import os
import base64
from openai import OpenAI

from prompts1 import build_full_prompt


class ImageAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.images = {}
        self.token_usage = {}
        self.client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

    def add_image(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        self.images[file_path] = file_path
        self.token_usage[file_path] = 0

    def _get_media_type(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        media_types = {
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        return media_types.get(ext, "image/jpeg")

    def _encode_image(self, file_path: str) -> str:
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _process_image(self, file_path: str, prompt: str) -> str:
        if file_path not in self.images:
            raise KeyError(f"Изображение не добавлено: {file_path}")

        media_type = self._get_media_type(file_path)
        data_uri = f"data:{media_type};base64,{self._encode_image(file_path)}"
        try:
            response = self.client.chat.completions.create(
                model="sonar",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": data_uri}},
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )
            usage = response.usage.total_tokens if hasattr(response, "usage") else 0
            self.token_usage[file_path] += usage
            return response.choices[0].message.content
        except Exception as e:
            return f"Ошибка при анализе: {e}"

    def identify_object(self, file_path: str) -> str:
        prompt = build_full_prompt()
        return self._process_image(file_path, prompt)

    def print_token_usage(self):
        print("\n" + "=" * 50)
        for file_path, tokens in self.token_usage.items():
            print(f"{file_path}: использовано токенов {tokens}")
        print("=" * 50 + "\n")

if __name__ == "__main__":
    api_key = "api_key"
    analyzer = ImageAnalyzer(api_key)

    try:
        analyzer.add_image("m.jpg")
        result = analyzer.identify_object("m.jpg")
        print("Результат анализа:")
        print(result)
        analyzer.print_token_usage()
    except Exception as e:
        print(f"Ошибка: {e}")
