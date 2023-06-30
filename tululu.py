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
    filename = sanitize_filename(f'{title}')
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
    filepath = os.path.join(dest_folder, 'book.json')
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(books, file, ensure_ascii=False, indent=4)


def parse_book_page(soup, book_page_url):
    title_author = soup.select_one('h1').text
    title, author = title_author.split(' :: ')
    genre_tags = soup.select('span.d_book a')
    comments_tags = soup.select('div.texts')
    book_image_url = urljoin(book_page_url, soup.select_one('div.bookimage img')['src'])

    comments = [comment.select_one('span').get_text() for comment in comments_tags]

    genres = [genre_tag.text for genre_tag in genre_tags]

    title = sanitize_filename(title.strip())

    author = sanitize_filename(author.strip())

    book_path = f'books/{title}.txt'

    book = {
        'title': title,
        'author': author,
        'book_path': book_path,
        'genres': genres,
        'comments': comments,
        'image_url': book_image_url
    }

    return book


def get_last_page_number():
    url = 'https://tululu.org/l55/'
    try:
        response = requests.get(url)
        check_for_redirect(response)
        if not response.ok:
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        last_page_id = soup.select('.npage')[-1]['href'].split('/')[-2]

        return int(last_page_id) + 1
    except requests.exceptions.HTTPError as e:
        print(f'Error: Unable to load page: {e}', file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description='Данный код позволяет скачивать книги и обложки книг с сайта',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--start_id', type=int, nargs='?', default=1,
                        help='Страница, с которой начнется скачивание')
    parser.add_argument('--end_id', type=int, nargs='?', default=get_last_page_number(),
                        help='Страница, на которой закончится скачивание')
    parser.add_argument('--dest_folder', type=str, default='.',
                        help='Путь к каталогу с результатами парсинга: картинкам, книгам, JSON')
    parser.add_argument('--skip_imgs', action='store_true',
                        help='Не скачивать обложки для книг')
    parser.add_argument('--skip_txt', action='store_true',
                        help='Не скачивать текстовые файлы для книг')
    args = parser.parse_args()
    books = []
    for page_id in range(args.start_id, args.end_id):
        url = f'https://tululu.org/l55/{page_id}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            for book_id in soup.select('div.bookimage'):
                book_href = book_id.select_one('a')['href']
                trans_table = {ord('b'): None}
                book_unique_id = sanitize_filename(book_href).translate(trans_table)
                book_link = urljoin(url, book_href)
                try:
                    response = requests.get(book_link)
                    check_for_redirect(response)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'lxml')
                    book = parse_book_page(soup, book_link)
                    books.append(book)
                    if not args.skip_txt:
                        download_txt(book['title'], book_id=book_unique_id,
                                     dest_folder=os.path.join(args.dest_folder, 'media/books/'))
                    if not args.skip_imgs:
                        download_image(book['image_url'], dest_folder=os.path.join(args.dest_folder, 'media/images/'))
                    print('Название:', book['title'])
                    print('Автор:', book['author'])
                except requests.exceptions.HTTPError as e:
                    print(f'Error: Unable to download book {book_unique_id}: {e}', file=sys.stderr)
                except requests.exceptions.ConnectionError as e:
                    print(f'The request for book {book_unique_id} failed: {e}', file=sys.stderr)
                    time.sleep(3)
        except requests.exceptions.HTTPError as e:
            print(f'Error: Unable to load page {page_id}: {e}', file=sys.stderr)
        except requests.exceptions.ConnectionError as e:
            print(f'The request for page {page_id} failed: {e}', file=sys.stderr)
            time.sleep(3)
    save_to_json(books, dest_folder=os.path.join(args.dest_folder, 'json/'))


if __name__ == '__main__':
    main()
