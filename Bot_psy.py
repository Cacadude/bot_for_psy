import json
import requests
from bs4 import BeautifulSoup

def fetch_page(url, headers):
    response = requests.get(url, headers=headers, verify=False)
    response.encoding = 'windows-1251'
    return response

def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    # Отладочная информация: сохраняем весь HTML для проверки
    with open('debug_html.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    # Ищем все элементы с нужными классами
    elements = soup.find_all(class_=['nisTitle', 'nisName', 'nisVal'])
    print(f"Найдено элементов: {len(elements)}")  # Отладочный вывод
    
    # Формируем пары название-значение
    i = 0
    while i < len(elements):
        current = elements[i]
        current_classes = current.get('class', [])
        print(f"Элемент {i}: {current}")  # Отладочный вывод
        
        # Если текущий элемент - название (Title или Name)
        if 'nisTitle' in current_classes or 'nisName' in current_classes:
            name = current.get_text(strip=True)
            
            # Проверяем следующий элемент на значение
            if i+1 < len(elements) and 'nisVal' in elements[i+1].get('class', []):
                value = elements[i+1].get_text(strip=True)
                results.append(f"{name}: {value}")
                i += 2  # Пропускаем уже обработанное значение
            else:
                results.append(f"{name}: -")
                i += 1
        # Если текущий элемент - значение без названия
        elif 'nisVal' in current_classes:
            results.append(f"-: {current.get_text(strip=True)}")
            i += 1
    
    return results

def handle(data):
    try:
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return json.dumps({"error": "Неверный JSON"}, ensure_ascii=False)
        
        if not isinstance(data, dict):
            return json.dumps({"error": "Ожидается словарь"}, ensure_ascii=False)
            
        url = data.get('url')
        if not url:
            return json.dumps({"error": "Отсутствует URL"}, ensure_ascii=False)
        
        headers = {"User-Agent": "Mozilla/5.0"}
        response = fetch_page(url, headers)
        
        if response.status_code != 200:
            return json.dumps({"error": f"HTTP ошибка {response.status_code}"}, ensure_ascii=False)
        
        parsed_data = parse_page(response.text)
        return json.dumps(parsed_data, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"Ошибка: {str(e)}"}, ensure_ascii=False)
