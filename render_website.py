import json
import argparse

from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from math import ceil
from urllib.parse import quote


def on_reload(books, env):
    books_per_page = 20

    num_pages = ceil(len(books) / books_per_page)
    for page_num, start_idx in enumerate(range(0, len(books), books_per_page), 1):
        end_idx = start_idx + books_per_page
        page_books = books[start_idx: end_idx]

        for book in page_books:
            book['image_url'] = quote(book['image_url'], safe='/:')
            book['book_path'] = quote(book['book_path'], safe='/:')

        template = env.get_template('template.html')
        rendered_page = template.render(books=page_books, page_num=page_num,
                                        num_pages=num_pages)

        with open(f'pages/index{page_num}.html', 'w', encoding='utf8') as file:
            file.write(rendered_page)


def main():
    parser = argparse.ArgumentParser(description='Данный код позволяет открыть локальную версию библиотеки книг',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dest_folder', type=str, default='json/book.json',
                        help='Путь к конфигурационному файлу .json')
    args = parser.parse_args()

    with open(args.dest_folder, 'r', encoding='utf-8') as file:
        books = json.load(file)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    on_reload(books, env)
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
