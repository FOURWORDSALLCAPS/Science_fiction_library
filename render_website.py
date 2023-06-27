import json

from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from math import ceil


with open("json/book.json", "r", encoding="utf-8") as file:
    books_json = file.read()


books = json.loads(books_json)

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)


def on_reload():
    page_size = 20

    num_pages = ceil(len(books) / page_size)
    for page_num in range(1, num_pages + 1):
        start_idx = (page_num - 1) * page_size
        end_idx = start_idx + page_size
        page_books = books[start_idx: end_idx]

        template = env.get_template('template.html')

        rendered_page = template.render(books=page_books, page_num=page_num, num_pages=num_pages)

        with open(f'pages/index{page_num}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
