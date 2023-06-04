import requests
import os
from pathvalidate import sanitize_filename, sanitize_filepath
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError('Page redirected')


def download_txt(url, book_id, folder='books/'):
    try:
        params = {'id': book_id}

        os.makedirs(folder, exist_ok=True)

        response = requests.get(url, params=params)
        check_for_redirect(response)  # Проверка на редирект
        response.raise_for_status()

        book_page_url = f'https://tululu.org/b{book_id}'
        book_page_response = requests.get(book_page_url)
        check_for_redirect(book_page_response)
        book_page_response.raise_for_status()
        soup = BeautifulSoup(book_page_response.text, 'lxml')
        title_author = soup.find("h1").text
        title, author = title_author.split(" :: ")
        filename = sanitize_filename(f"{title.strip()}")
        folder = sanitize_filepath(folder)
        book_image_url = urljoin(url, soup.find('div', class_='bookimage').find('img')['src'])
        filepath = os.path.join(folder, f"{book_id}. {filename}.txt")
        book_text_url = f"{url}txt.php?id={book_id}"
        book_text_response = requests.get(book_text_url, allow_redirects=False)
        check_for_redirect(book_text_response)
        book_text_response.raise_for_status()
        book_text = book_text_response.text

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(book_text)

        return book_image_url
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")


def download_image(url, folder='images/'):
    try:
        os.makedirs(folder, exist_ok=True)
        response = requests.get(url)
        response.raise_for_status()

        filename = os.path.basename(urlparse(url).path)
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as file:
            file.write(response.content)

    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")


url = 'https://tululu.org/'
for book_id in range(11):
    download_image(download_txt(url, book_id=book_id))
