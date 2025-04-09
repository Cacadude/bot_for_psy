import json
import requests
from bs4 import BeautifulSoup

def handle(data):
    try:
        # 1. Получаем URL
        if isinstance(data, str):
            data = json.loads(data)
        url = data.get('url')
        if not url:
            return json.dumps({"error": "URL не указан"}, ensure_ascii=False)

        # 2. Загружаем страницу
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "ru-RU,ru;q=0.9"
        }
        response = requests.get(url, headers=headers, verify=False)
        response.encoding = 'windows-1251'
        
        if response.status_code != 200:
            return json.dumps({"error": f"Ошибка загрузки: {response.status_code}"}, 
                            ensure_ascii=False)

        # 3. Парсим результаты
        soup = BeautifulSoup(response.text, 'html.parser')
        results = {}

        # Универсальный парсер для обоих типов тестов
        for item in soup.select('[class*="nis"], [class*="via"]'):
            classes = item.get('class', [])
            
            if 'nisTitle' in classes or 'viaTitle' in classes:
                current_title = item.get_text(strip=True)
                next_val = item.find_next(class_=['nisVal', 'viaVal'])
                if next_val:
                    results[current_title] = next_val.get_text(strip=True)
            
            elif 'nisName' in classes or 'viaName' in classes:
                name = item.get_text(strip=True)
                value = item.find_next(class_=['nisVal', 'viaVal'])
                if value:
                    results[name] = value.get_text(strip=True)

        return json.dumps(results, ensure_ascii=False) if results else json.dumps({"error": "Данные не найдены"}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"Ошибка: {str(e)}"}, ensure_ascii=False)
