import json
import os
import requests

from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()


def get_page_data(url):
    """Получает данные о цитатах с одной страницы по-указанному URL, возвращает список"""
    try:
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')

        if req.status_code != 200:
            raise Exception(f'Ошибка! Код статуса {req.status_code}')

        next_btn = soup.find('li', class_='next')

        quotes = soup.find_all('span', class_='text')
        authors = soup.find_all('small', class_='author')
        authors_link = soup.find_all('a', string='(about)')

        quotes_data = []
        for quote, author, author_link in zip(quotes, authors, authors_link):
            tag_list = quote.find_next('div', class_='tags')
            tag_texts = [tag.get_text(strip=True) for tag in tag_list.find_all('a')] if tag_list else []

            quotes_data.append({
                'quote': quote.get_text(strip=True),
                'author': author.get_text(strip=True),
                'author_link': f'{os.getenv("BASE_URL").rstrip("/")}{author_link['href']}',
                'tags': tag_texts
            })

        if not next_btn:
            return None, quotes_data

        return req.text, quotes_data

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе страницы {url}: {e}")
        return None, []


def scrape_all_page():
    """
    Скрапит все страницы с цитатами, пока кнопка Next есть на странице, сохраняет результат в JSON-файл.
    """
    page_number = 1
    all_quotes = []

    while True:
        current_url = f'{os.getenv("BASE_URL")}page/{page_number}'

        page_content, page_quotes = get_page_data(current_url)

        if not page_content:
            print('Скраппинг завершён!')
            break

        all_quotes.extend(page_quotes)

        os.makedirs('output', exist_ok=True)
        with open('output/scrape_result.json', 'w', encoding='UTF-8') as json_file:
            json.dump(all_quotes, json_file, ensure_ascii=False, indent=4)

        page_number += 1


scrape_all_page()
