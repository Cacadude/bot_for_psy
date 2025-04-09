import json
import requests
from bs4 import BeautifulSoup

def get_test_results(url):
    # Загружаем страницу
    response = requests.get(url, verify=False, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ru-RU,ru;q=0.9"
    })
    response.encoding = 'windows-1251'
    
    # Парсим HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Собираем все элементы результатов
    elements = soup.find_all(class_=['nisTitle', 'nisName', 'nisVal'])
    
    # Формируем пары "название: значение"
    results = {}
    for i in range(0, len(elements), 2):
        if i+1 < len(elements):
            name = elements[i].get_text(strip=True)
            value = elements[i+1].get_text(strip=True)
            results[name] = value
    
    return json.dumps(results, ensure_ascii=False)

def handle(data):
    try:
        # Получаем URL из входных данных
        if isinstance(data, str):
            data = json.loads(data)
        url = data['url']
        
        # Получаем и возвращаем результаты
        return get_test_results(url)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
