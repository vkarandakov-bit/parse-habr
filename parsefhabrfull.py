import requests
from bs4 import BeautifulSoup
import time

from parsehabr import get_preview_data, contains_keywords, KEYWORDS, URL, HEADERS


def get_article_full_text(url):
    """Получает полный текст статьи по ссылке."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        if response.status_code != 200:
            return ''

        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.find('div', class_='article-formatted-body')
        if not body:
            body = soup.find('div', class_='tm-article-body')
        if not body:
            body = soup.find('article')

        return body.get_text(' ', strip=True).lower() if body else ''

    except Exception:
        return ''


def parse_habr_full():
    "Парсит статью на habr."
    response = requests.get(URL, headers=HEADERS)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all('article', class_='tm-articles-list__item')

    for article in articles:
        data = get_preview_data(article)
        if not data['link']:
            continue

        # Шаг 1: проверяем preview (как в базовом сценарии)
        preview_has_keywords = (
                contains_keywords(data['title'], KEYWORDS)
                or contains_keywords(data['preview'], KEYWORDS)
                or contains_keywords(data['hubs'], KEYWORDS)
        )

        if not preview_has_keywords:
            continue
        full_text = get_article_full_text(data['link'])
        if contains_keywords(full_text, KEYWORDS):
            print(f"{data['date']} – {data['title']} – {data['link']}")
        time.sleep(1.5)


if __name__ == '__main__':
    parse_habr_full()