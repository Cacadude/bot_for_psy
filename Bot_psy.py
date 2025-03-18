import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def fetch_page(url, headers):
    """Загружает HTML-страницу по указанному URL."""
    response = requests.get(url, headers=headers, verify=False)
    response.encoding = 'windows-1251'
    return response

def parse_page(html, url):
    """Парсит HTML-страницу и извлекает данные."""
    soup = BeautifulSoup(html, 'html.parser')
    
    if 'result?v=ipi' in url:
        nis_names = soup.find_all(class_=['nisName', 'nisTitle'])
        nis_values = soup.find_all(class_='nisVal')
    else:
        nis_names = soup.find_all(class_='nisName')
        nis_values = soup.find_all(class_='nisVal')
    
    return nis_names, nis_values if nis_names and nis_values else (None, None)

def extract_data(nis_names, nis_values):
    """Извлекает текст из элементов и возвращает словарь с результатами."""
    return {name.get_text(strip=True): value.get_text(strip=True) 
            for name, value in zip(nis_names, nis_values)}

def handle(data):
    try:
        data = json.loads(data) if isinstance(data, str) else data
        
        if not isinstance(data, dict) or not data.get('url'):
            return json.dumps({"error": "Invalid input"}, ensure_ascii=False)
        
        # Генерация случайного User-Agent
        try:
            ua = UserAgent()
            user_agent = ua.random  
        except:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
        headers = {
            "User-Agent": user_agent,
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/"
        }
        
        response = fetch_page(data['url'], headers)
        
        if response.status_code == 200:
            nis_names, nis_values = parse_page(response.text, data['url'])
            return json.dumps(extract_data(nis_names, nis_values), ensure_ascii=False) if nis_names else json.dumps({"error": "Elements not found"}, ensure_ascii=False)
        
        return json.dumps({"error": f"HTTP Error {response.status_code}"}, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
