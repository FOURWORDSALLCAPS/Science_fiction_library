import requests
import os
from pathlib import Path
from pathvalidate import sanitize_filename, sanitize_filepath
from bs4 import BeautifulSoup


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

        filepath = os.path.join(folder, f"{book_id}. {filename}.txt")

        book_text_url = f"{url}txt.php?id={book_id}"
        book_text_response = requests.get(book_text_url, allow_redirects=False)
        check_for_redirect(book_text_response)
        book_text_response.raise_for_status()
        book_text = book_text_response.text

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(book_text)

    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        return None, None


url = 'https://tululu.org/'
for book_id in range(11):
    download_txt(url, book_id=book_id)
