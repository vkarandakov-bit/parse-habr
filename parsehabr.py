import requests
from bs4 import BeautifulSoup

KEYWORDS = ['дизайн', 'фото', 'web', 'python']

URL = 'https://habr.com/ru/articles/'

def parse_habr():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(URL, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all('article', class_='tm-articles-list__item')

    for article in articles:
        title_tag = article.find('a', class_='tm-title__link')
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link = title_tag.get('href')
        if link and not link.startswith('http'):
            link = 'https://habr.com' + link

        time_tag = article.find('time')
        date = time_tag.get('title', '') if time_tag else 'Дата неизвестна'

        preview_tag = article.find('div', class_='article-formatted-body')
        preview_text = preview_tag.get_text().lower() if preview_tag else ''

        found_keywords = [kw for kw in KEYWORDS if kw.lower() in preview_text]

        if found_keywords:
            print(f"{date} – {title} – {link}")
            print(f"  Найдены ключевые слова: {', '.join(found_keywords)}")


if __name__ == '__main__':
    parse_habr()