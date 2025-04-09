import json
import requests
from bs4 import BeautifulSoup

def handle(data):
    try:
        # 1. Получаем URL из входных данных
        if isinstance(data, str):
            data = json.loads(data)
        url = data.get('url')
        if not url:
            return json.dumps({"error": "URL не указан"}, ensure_ascii=False)
        
        # 2. Загружаем страницу
        response = requests.get(url, 
                             headers={"User-Agent": "Mozilla/5.0"},
                             verify=False)
        response.encoding = 'windows-1251'
        
        if response.status_code != 200:
            return json.dumps({"error": f"Ошибка загрузки: {response.status_code}"}, 
                            ensure_ascii=False)
        
        # 3. Парсим результаты
        soup = BeautifulSoup(response.text, 'html.parser')
        results = {}
        
        # Собираем все элементы в порядке их появления
        items = soup.find_all(class_=['nisTitle', 'nisName', 'nisVal'])
        
        # Формируем пары название-значение
        for i in range(0, len(items)-1, 2):
            name = items[i].get_text(strip=True)
            value = items[i+1].get_text(strip=True)
            results[name] = value
        
        # 4. Возвращаем результат в JSON
        return json.dumps(results, ensure_ascii=False) if results else json.dumps({}, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"Ошибка: {str(e)}"}, ensure_ascii=False)
