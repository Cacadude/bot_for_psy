import requests
from bs4 import BeautifulSoup

def fetch_page(url, headers):
    """Загружает HTML-страницу по указанному URL."""
    response = requests.get(url, headers=headers, verify=False)
    response.encoding = 'windows-1251'  # Указываем правильную кодировку
    return response

def parse_page(html):
    """Парсит HTML-страницу и извлекает данные."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Извлекаем названия и значения
    nis_names = soup.find_all(class_='nisName')
    nis_values = soup.find_all(class_='nisVal')
    
    # Проверяем, что элементы найдены
    if nis_names and nis_values:
        return nis_names, nis_values
    else:
        return None, None

def extract_data(nis_names, nis_values):
    """Извлекает текст из элементов и возвращает словарь с результатами."""
    results = {}
    for name, value in zip(nis_names, nis_values):
        name_text = name.get_text(strip=True)
        value_text = value.get_text(strip=True)
        results[name_text] = value_text
    return results

def main(url):
    """Основная функция для выполнения всех шагов."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }
    
    response = fetch_page(url, headers)
    if response.status_code == 200:
        nis_names, nis_values = parse_page(response.text)
        if nis_names and nis_values:
            results = extract_data(nis_names, nis_values)
            return results
    return None

url = "https://psytests.org/result?v=ipiOgMb4sotfh&b=51Bv5zdYvnari9"
results = main(url)

if results:
    print("Данные по результатам теста:")
    for name, value in results.items():
        print(f"{name}: {value}")
else:
    print("Элементы с классами nisName или nisVal не найдены.")