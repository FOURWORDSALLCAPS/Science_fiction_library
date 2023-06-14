import requests
import os
import argparse
import sys
import time
import json
from pathvalidate import sanitize_filename, sanitize_filepath
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError('Page redirected')


def download_txt(title, book_id, dest_folder):
    params = {'id': book_id}
    url = 'https://tululu.org/txt.php'
    os.makedirs(dest_folder, exist_ok=True)
    filename = sanitize_filename(f"{title}")
    dest_folder = sanitize_filepath(dest_folder)
    filepath = os.path.join(dest_folder, f'{filename}.txt')
    book_text_response = requests.get(url, params=params)
    check_for_redirect(book_text_response)
    book_text_response.raise_for_status()
    book_text = book_text_response.text

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(book_text)


def download_image(image_url, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    response = requests.get(image_url)
    response.raise_for_status()
    check_for_redirect(response)
    filename = os.path.basename(urlparse(image_url).path)
    filepath = os.path.join(dest_folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def save_to_json(books, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    filepath = os.path.join(dest_folder)
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(books, file, ensure_ascii=False, indent=4)


def parse_book_page(soup, book_page_url):
    title_author = soup.select_one('h1').text
    title, author = title_author.split(" :: ")
    genre_tags = soup.select('d_book a')
    comments_tags = soup.select('div.texts')
    book_image_url = urljoin(book_page_url, soup.select_one('div.bookimage img')['src'])

    comments = [comment.select_one('span').get_text() for comment in comments_tags]

    genres = [genre_tag.text for genre_tag in genre_tags]

    title = sanitize_filename(title.strip())

    author = sanitize_filename(author.strip())

    book = {
        'title': title,
        'author': author,
        'genres': genres,
        'comments': comments,
        'image_url': book_image_url
    }

    return book


def main():
    parser = argparse.ArgumentParser(description='Данный код позволяет скачивать книги и обложки книг с сайта',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--start_id', type=int, nargs='?', default=10,
                        help='Страница, с которой начнется скачивание')
    parser.add_argument('--end_id', type=int, nargs='?', default=20,
                        help='Страница, на которой закончится скачивание')
    parser.add_argument('--dest_folder', type=str, default='.',
                        help='Путь к каталогу с результатами парсинга: картинкам, книгам, JSON')
    parser.add_argument('--skip_imgs', action='store_true',
                        help='Не скачивать обложки для книг')
    parser.add_argument('--skip_txt', action='store_true',
                        help='Не скачивать текстовые файлы для книг')
    parser.add_argument('--json_path', type=str, default='#',
                        help='Cвой путь к *.json файлу с результатами')
    args = parser.parse_args()
    books = []
    for page in range(args.start_id, args.end_id if args.end_id else args.start_id + 1):
        url = f"https://tululu.org/l55/{page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        for book in soup.select('div.bookimage'):
            book_href = book.select_one('a')['href']
            trans_table = {ord('b'): None}
            book_id = sanitize_filename(book_href).translate(trans_table)
            book_link = urljoin(url, book_href)
            url = f"{book_link}"
            try:
                response = requests.get(url)
                check_for_redirect(response)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')
                book = parse_book_page(soup, url)
                books.append(book)
                if not args.skip_txt:
                    download_txt(book['title'], book_id=book_id, dest_folder=os.path.join(args.dest_folder, 'books/'))
                if not args.skip_imgs:
                    download_image(book['image_url'], dest_folder=os.path.join(args.dest_folder, 'images/'))
                save_to_json(books, dest_folder=os.path.join(args.dest_folder, 'json/'))
                print('Название:', book['title'])
                print('Автор:', book['author'])
            except requests.exceptions.HTTPError as e:
                print(f'Error: Unable to download book {book_id}: {e}', file=sys.stderr)
            except requests.exceptions.ConnectionError as e:
                print(f'The request for book {book_id} failed: {e}', file=sys.stderr)
                time.sleep(3)


if __name__ == '__main__':
    main()
