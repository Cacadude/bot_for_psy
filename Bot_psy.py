import json
import requests
from bs4 import BeautifulSoup

def fetch_page(url, headers):
    """Загружает HTML-страницу по указанному URL."""
    response = requests.get(url, headers=headers, verify=False)
    response.encoding = 'windows-1251'  # Указываем правильную кодировку
    return response

def parse_page(html, is_ipi=False):
    """Парсит HTML-страницу и извлекает данные."""
    soup = BeautifulSoup(html, 'html.parser')
    
    if is_ipi:
        # Для IPI тестов сначала пробуем найти nisTitle
        nis_titles = soup.find_all(class_='nisTitle')
        nis_values = soup.find_all(class_='nisVal')
        
        if nis_titles and nis_values:
            return nis_titles, nis_values
        else:
            # Если nisTitle не найдены, используем nisName как fallback
            nis_names = soup.find_all(class_='nisName')
            if nis_names and nis_values:
                return nis_names, nis_values
    else:
        # Для VIA тестов используем только nisName
        nis_names = soup.find_all(class_='nisName')
        nis_values = soup.find_all(class_='nisVal')
        
        if nis_names and nis_values:
            return nis_names, nis_values
    
    return None, None

def extract_data(names, values):
    """Извлекает текст из элементов и возвращает словарь с результатами."""
    results = {}
    for name, value in zip(names, values):
        name_text = name.get_text(strip=True)
        value_text = value.get_text(strip=True)
        results[name_text] = value_text
    return results

def handle(data):
    """
    Основная функция, которая принимает данные и возвращает JSON.
    :param data: Данные (строка или словарь), переданные в настройках блока.
    :return: JSON-строка с результатами.
    """
    # Если data передается как строка, преобразуем её в словарь
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return json.dumps({"error": "Неверный формат данных. Ожидается JSON-строка."}, ensure_ascii=False)
    
    # Проверяем, что data является словарем
    if not isinstance(data, dict):
        return json.dumps({"error": "Неверный формат данных. Ожидается словарь или JSON-строка."}, ensure_ascii=False)
    
    # Проверяем, что передан URL
    url = data.get('url')
    if not url:
        return json.dumps({"error": "URL не предоставлен"}, ensure_ascii=False)
    
    # Определяем тип теста по URL
    is_ipi = 'result?v=ipi' in url
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }
    
    # Загружаем страницу
    response = fetch_page(url, headers)
    if response.status_code == 200:
        names, values = parse_page(response.text, is_ipi)
        if names and values:
            results = extract_data(names, values)
            # Возвращаем результаты в формате JSON с поддержкой кириллицы
            return json.dumps(results, ensure_ascii=False)
        else:
            error_msg = "Не найдены элементы с классами nisTitle/nisVal или nisName/nisVal" if is_ipi else "Элементы с классами nisName/nisVal не найдены."
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    else:
        return json.dumps({"error": f"Ошибка при загрузке страницы: {response.status_code}"}, ensure_ascii=False)
