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
    for element in soup.find_all(class_=['nisTitle', 'nisName', 'nisVal']):
        results.append(element.get_text(strip=True))
    
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
