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
    
    # Находим ВСЕ элементы в порядке их появления
    for element in soup.find_all(class_=['nisTitle', 'nisName', 'nisVal']):
        if 'nisTitle' in element['class']:
            results.append(('title', element.get_text(strip=True)))
        elif 'nisName' in element['class']:
            results.append(('name', element.get_text(strip=True)))
        elif 'nisVal' in element['class']:
            results.append(('value', element.get_text(strip=True)))
    
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
        
        # Формируем плоский список в порядке появления
        output = []
        current_item = {}
        
        for item_type, text in parsed_data:
            if item_type == 'title':
                if current_item:
                    output.append(current_item)
                current_item = {'title': text, 'items': []}
            elif item_type == 'name':
                current_item['items'].append({'name': text, 'value': None})
            elif item_type == 'value' and current_item.get('items'):
                if current_item['items'] and current_item['items'][-1]['value'] is None:
                    current_item['items'][-1]['value'] = text
                else:
                    current_item['items'].append({'name': None, 'value': text})
        
        if current_item:
            output.append(current_item)
            
        return json.dumps(output, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": f"Ошибка обработки: {str(e)}"}, ensure_ascii=False)
