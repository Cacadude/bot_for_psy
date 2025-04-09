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
        
        # 2. Определяем тип теста
        is_via = 'result?v=via' in url.lower()
        
        # 3. Загружаем страницу
        response = requests.get(url,
                             headers={"User-Agent": "Mozilla/5.0"},
                             verify=False)
        response.encoding = 'windows-1251'
        
        if response.status_code != 200:
            return json.dumps({"error": f"Ошибка загрузки: {response.status_code}"},
                            ensure_ascii=False)
        
        # 4. Парсим результаты
        soup = BeautifulSoup(response.text, 'html.parser')
        results = {}
        
        if is_via:
            # Обработка VIA теста
            for row in soup.select('.viaRow'):
                name = row.select_one('.viaName').get_text(strip=True)
                value = row.select_one('.viaVal').get_text(strip=True)
                results[name] = value
        else:
            # Обработка IPI теста
            titles = soup.find_all(class_='nisTitle')
            names = soup.find_all(class_='nisName')
            values = soup.find_all(class_='nisVal')
            
            # Собираем данные в правильном порядке
            all_items = []
            for title in titles:
                all_items.append(('title', title.get_text(strip=True)))
            
            for name in names:
                all_items.append(('name', name.get_text(strip=True)))
            
            for i, value in enumerate(values):
                if i < len(all_items):
                    item_type, name = all_items[i]
                    results[name] = value.get_text(strip=True)
        
        return json.dumps(results, ensure_ascii=False) if results else json.dumps({}, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"Ошибка: {str(e)}"}, ensure_ascii=False)
