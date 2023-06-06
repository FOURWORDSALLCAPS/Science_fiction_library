import requests
import os
import argparse
import sys
import time

from pathvalidate import sanitize_filename, sanitize_filepath
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError('Page redirected')


def download_txt(title, book_id, folder='books/'):
    params = {'id': book_id}
    url = 'https://tululu.org/txt.php'
    os.makedirs(folder, exist_ok=True)
    filename = sanitize_filename(f"{title}")
    folder = sanitize_filepath(folder)
    filepath = os.path.join(folder, f'{book_id}. {filename}.txt')
    book_text_response = requests.get(url, params=params)
    check_for_redirect(book_text_response)
    book_text_response.raise_for_status()
    book_text = book_text_response.text

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(book_text)


def download_image(image_url, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(image)
    response.raise_for_status()
    check_for_redirect(response)
    filename = os.path.basename(urlparse(image).path)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def parse_book_page(soup, book_page_url):
    title_author = soup.find('h1').text
    title, author = title_author.split(" :: ")
    genre_tags = soup.find('span', class_='d_book').find_all('a')
    comments_tags = soup.find_all('div', {'class': 'texts'})
    book_image_url = urljoin(book_page_url, soup.find('div', class_='bookimage').find('img')['src'])

    comments = [comment.find('span').get_text() for comment in comments_tags]

    genres = [genre_tag.text for genre_tag in genre_tags]

    title = sanitize_filename(title.strip())

    author = sanitize_filename(author.strip())

    book = {
        'title': title,
        'author': author,
        'genres': genres,
        'comments': comments,
        'image': book_image_url
    }

    return book


def main():
    parser = argparse.ArgumentParser(description='Данный код позволяет скачивать книги и обложки книг с сайта')
    parser.add_argument('--start_id', type=int, default=10,
                        help='id книги, с которой начнется скачивание')
    parser.add_argument('--end_id', type=int, default=20,
                        help='id книги, на которой закончится скачивание')
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id):
        book_page_url = f'https://tululu.org/b{book_id}'
        try:
            book_page_response = requests.get(book_page_url)
            check_for_redirect(book_page_response)
            book_page_response.raise_for_status()
            soup = BeautifulSoup(book_page_response.text, 'lxml')
            book = parse_book_page(soup, book_page_url)
            download_txt(book['title'], book_id=book_id)
            download_image(book['image_url'])
            print('Название:', book['title'])
            print('Автор:', book['author'])
        except requests.exceptions.HTTPError as e:
            print(f'Error: Unable to download book {book_id}: {e}', file=sys.stderr)
        except requests.exceptions.ConnectionError as e:
            print(f'The request for book {book_id} failed: {e}', file=sys.stderr)
            time.sleep(3)


if __name__ == '__main__':
    main()
