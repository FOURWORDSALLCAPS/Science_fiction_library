import json

from livereload import Server, shell
from jinja2 import Environment, FileSystemLoader, select_autoescape


with open("json/book.json", "r", encoding="utf-8") as file:
    books_json = file.read()


books = json.loads(books_json)

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)


def on_reload():
    template = env.get_template('template.html')

    rendered_page = template.render(
        books=json.loads(books_json)
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
