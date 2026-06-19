import requests
from bs4 import BeautifulSoup

KEYWORDS = ['дизайн', 'фото', 'web', 'python']
URL = 'https://habr.com/ru/articles/'
HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36')
}

def get_preview_data(article):
    """Получает все текстовые поля preview-информацию"""
    data = {}
    title_tag = article.find('a', class_='tm-title__link')
    data['title'] = title_tag.get_text(strip=True) if title_tag else ''
    data['link'] = title_tag.get('href', '') if title_tag else ''
    if data['link'] and not data['link'].startswith('http'):
        data['link'] = 'https://habr.com' + data['link']
    time_tag = article.find('time')
    data['date'] = time_tag.get('title', '') if time_tag else ''
    preview_tag = article.find('div', class_='article-formatted-body')
    data['preview'] = preview_tag.get_text(' ', strip=True).lower() if preview_tag else ''
    hubs = article.find_all('a', class_='tm-hub__title')
    data['hubs'] = ' '.join(h.get_text(strip=True).lower() for h in hubs)
    return data

def contains_keywords(text, keywords):
    """Проверяет текст на ключевое слово."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)

def parse_habr():
    """Парсит preview на хабр."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/120.0.0.0 Safari/537.36'}
    response = requests.get(URL, headers=HEADERS)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all('article', class_='tm-articles-list__item')

    for article in articles:
        data = get_preview_data(article)
        if not data['link']:
            continue

        if (contains_keywords(data['title'], KEYWORDS)
                or contains_keywords(data['preview'], KEYWORDS)
                or contains_keywords(data['hubs'], KEYWORDS)):
            print(f"{data['date']} – {data['title']} – {data['link']}")


if __name__ == '__main__':
    parse_habr()