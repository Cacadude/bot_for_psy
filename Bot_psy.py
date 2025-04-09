import json
import requests
from bs4 import BeautifulSoup

def fetch_page(url, headers):
    """Загружает HTML-страницу по указанному URL."""
    response = requests.get(url, headers=headers, verify=False)
    response.encoding = 'windows-1251'
    return response

def parse_page(html, is_ipi=False):
    """Парсит HTML-страницу с учетом типа теста."""
    soup = BeautifulSoup(html, 'html.parser')
    
    if is_ipi:
        # Для IPI: собираем иерархическую структуру
        results = {}
        titles = soup.find_all(class_='nisTitle')
        names = soup.find_all(class_='nisName')
        values = soup.find_all(class_='nisVal')
        
        if titles and values:
            # Группируем значения по блокам
            value_groups = []
            temp_group = []
            for val in values:
                temp_group.append(val.get_text(strip=True))
                if len(temp_group) == 4:  # 4 значения на блок (как на скриншоте)
                    value_groups.append(temp_group)
                    temp_group = []
            
            # Собираем результаты
            for title, name_block, val_group in zip(titles, names, value_groups):
                title_text = title.get_text(strip=True)
                results[title_text] = {
                    "total": val_group[0],  # Общий процент (первое значение)
                    "subscales": {
                        name.get_text(strip=True): val 
                        for name, val in zip(
                            name_block.find_all(class_='nisName'), 
                            val_group[1:]  # Остальные значения для подшкал
                        )
                    }
                }
            return results
    else:
        # Для VIA: плоская структура
        names = soup.find_all(class_='nisName')
        values = soup.find_all(class_='nisVal')
        if names and values:
            return {
                name.get_text(strip=True): value.get_text(strip=True)
                for name, value in zip(names, values)
            }
    
    return None

def handle(data):
    """Обработчик запроса с автоматическим определением типа теста."""
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON input"}, ensure_ascii=False)
    
    if not isinstance(data, dict) or not data.get('url'):
        return json.dumps({"error": "Missing URL"}, ensure_ascii=False)
    
    is_ipi = 'result?v=ipi' in data['url'].lower()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = fetch_page(data['url'], headers)
    if response.status_code != 200:
        return json.dumps({"error": f"HTTP {response.status_code}"}, ensure_ascii=False)
    
    results = parse_page(response.text, is_ipi)
    if not results:
        return json.dumps({"error": "No test data found"}, ensure_ascii=False)
    
    return json.dumps(results, ensure_ascii=False)
