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
    
    # Находим все блоки с результатами
    result_blocks = soup.find_all('div', class_='nisResBlock')
    
    for block in result_blocks:
        # Извлекаем основной заголовок и значение
        title = block.find('div', class_='nisTitle')
        if title:
            title_text = title.get_text(strip=True)
            value = title.find_next('div', class_='nisVal')
            if value:
                results.append(f"{title_text}: {value.get_text(strip=True)}")
        
        # Извлекаем подпункты
        items = block.find_all('div', class_='nisItem')
        for item in items:
            name = item.find('div', class_='nisName')
            value = item.find('div', class_='nisVal')
            if name and value:
                results.append(f"{name.get_text(strip=True)}: {value.get_text(strip=True)}")
    
    return results

def handle(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)
        
        if not isinstance(data, dict) or not data.get('url'):
            return json.dumps({"error": "Требуется URL в формате JSON"}, ensure_ascii=False)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9"
        }
        
        response = fetch_page(data['url'], headers)
        
        if response.status_code != 200:
            return json.dumps({"error": f"Ошибка {response.status_code}"}, ensure_ascii=False)
        
        parsed_data = parse_page(response.text)
        return json.dumps(parsed_data, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"Ошибка обработки: {str(e)}"}, ensure_ascii=False)
