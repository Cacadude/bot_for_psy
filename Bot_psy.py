import json
import requests
from bs4 import BeautifulSoup

def get_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, verify=False)
    response.encoding = 'windows-1251'
    return response.text

def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    # Для всех типов ссылок собираем три класса
    items = soup.find_all(class_=['nisTitle', 'nisName', 'nisVal'])
    
    # Собираем пары название-значение
    for i in range(0, len(items)-1, 2):
        name = items[i].get_text(strip=True)
        value = items[i+1].get_text(strip=True) if i+1 < len(items) else 'N/A'
        results.append(f"{name}: {value}")
    
    return results

def handle(data):
    try:
        # Получаем URL из входных данных
        url = json.loads(data)['url'] if isinstance(data, str) else data['url']
        
        # Получаем HTML страницы
        html = get_page(url)
        
        # Парсим результаты
        results = parse_results(html)
        
        # Возвращаем в нужном формате
        return json.dumps(results, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
