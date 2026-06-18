import requests
from bs4 import BeautifulSoup
import time

KEYWORDS = ['дизайн', 'фото', 'web', 'python']

URL = 'https://habr.com/ru/articles/'


def get_article_full_text(url):
    """Получает полный текст статьи по ссылке."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://habr.com/ru/articles/'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"  Ошибка получения статьи: статус {response.status_code}")
            return ''

        soup = BeautifulSoup(response.text, 'html.parser')

        body = soup.find('div', class_='tm-article-body')
        if body:
            return body.get_text().lower()

        body = soup.find('div', class_='article-formatted-body')
        if body:
            return body.get_text().lower()

        for div in soup.find_all('div'):
            classes = div.get('class', [])
            if any('body' in cls.lower() or 'content' in cls.lower() for cls in classes):
                text = div.get_text().lower()
                if len(text) > 500:  # Если текст достаточно длинный, скорее всего это статья
                    return text

        article = soup.find('article')
        if article:
            return article.get_text().lower()

        return ''

    except Exception as e:
        print(f"  Ошибка при получении статьи {url}: {e}")
        return ''


def parse_habr_full():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    print("Загружаем главную страницу...")
    response = requests.get(URL, headers=headers, timeout=10)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        print(f"Ошибка загрузки главной страницы: статус {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []

    articles = soup.find_all('article', class_='tm-articles-list__item')

    if not articles:
        articles = soup.find_all('article')
        print(f"Найдено {len(articles)} статей через поиск всех article тегов")

    if not articles:
        articles = soup.find_all('div', class_=lambda x: x and 'article' in x.lower())
        print(f"Найдено {len(articles)} статей через поиск div с 'article' в классе")

    if not articles:
        print("Не удалось найти статьи на странице!")
        print("Попробуем вывести структуру страницы для отладки...")

        # Выводим все теги article для отладки
        all_articles = soup.find_all('article')
        print(f"Всего тегов <article>: {len(all_articles)}")

        # Выводим все div с классами, содержащими 'article'
        all_divs = soup.find_all('div', class_=lambda x: x and 'article' in x.lower())
        print(f"Всего div с 'article' в классе: {len(all_divs)}")

        return

    print(f"Найдено {len(articles)} статей для обработки\n")

    found_count = 0

    for idx, article in enumerate(articles, 1):
        print(f"Обработка статьи {idx}/{len(articles)}...")

        title_tag = None
        link = None

        title_tag = article.find('a', class_='tm-title__link')

        if not title_tag:
            for h_tag in ['h2', 'h3', 'h1']:
                h = article.find(h_tag)
                if h:
                    title_tag = h.find('a')
                    if title_tag:
                        break

        if not title_tag:
            for a in article.find_all('a'):
                href = a.get('href', '')
                if '/articles/' in href or '/post/' in href:
                    title_tag = a
                    break

        if not title_tag:
            print("  Не удалось найти заголовок/ссылку, пропускаем")
            continue

        title = title_tag.get_text().strip()
        link = title_tag.get('href')

        if link and not link.startswith('http'):
            link = 'https://habr.com' + link

        time_tag = article.find('time')
        date = time_tag.get('title', '') if time_tag else 'Дата неизвестна'

        if not time_tag:
            date_text = article.find(string=lambda s: s and any(month in s for month in ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']))
            if date_text:
                date = date_text.strip()

        print(f"  Заголовок: {title[:60]}...")
        print(f"  Ссылка: {link}")
        print(f"  Дата: {date}")

        print("  Получаем полный текст статьи...")
        full_text = get_article_full_text(link)

        if not full_text:
            print("  Не удалось получить текст статьи")
            continue

        print(f"  Длина текста: {len(full_text)} символов")

        found_keywords = [kw for kw in KEYWORDS if kw.lower() in full_text]

        if found_keywords:
            found_count += 1
            print(f"\n{date} – {title} – {link}")
            print(f"  Найдены ключевые слова: {', '.join(found_keywords)}\n")
        else:
            print("  Ключевые слова не найдены")

        time.sleep(1.5)

    print(f"\nОбработка завершена. Найдено {found_count} статей с ключевыми словами.")


if __name__ == '__main__':
    parse_habr_full()