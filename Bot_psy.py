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
    
    # Собираем все элементы в порядке их появления
    elements = soup.find_all(class_=['nisTitle', 'nisName', 'nisVal'])
    
    # Формируем пары название-значение
    i = 0
    while i < len(elements):
        current = elements[i]
        
        # Если текущий элемент - название (Title или Name)
        if 'nisTitle' in current['class'] or 'nisName' in current['class']:
            name = current.get_text(strip=True)
            
            # Проверяем следующий элемент на значение
            if i+1 < len(elements) and 'nisVal' in elements[i+1]['class']:
                value = elements[i+1].get_text(strip=True)
                results.append(f"{name}: {value}")
                i += 2  # Пропускаем уже обработанное значение
            else:
                results.append(f"{name}: -")  # Если значения нет
                i += 1
        # Если текущий элемент - значение без названия
        elif 'nisVal' in current['class']:
            results.append(f"-: {current.get_text(strip=True)}")
            i += 1
    
    return results

def handle(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)
        
        if not isinstance(data, dict) or not data.get('url'):
            return json.dumps({"error": "Требуется URL в формате JSON"}, ensure_ascii=False)
        
        headers = {"User-Agent": "Mozilla/5.0"}
        response = fetch_page(data['url'], headers)
        
        if response.status_code != 200:
            return json.dumps({"error": f"Ошибка {response.status_code}"}, ensure_ascii=False)
        
        parsed_data = parse_page(response.text)
        return json.dumps(parsed_data, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"Ошибка обработки: {str(e)}"}, ensure_ascii=False)
