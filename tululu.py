import requests
import os
import argparse

from pathvalidate import sanitize_filename, sanitize_filepath
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError('Page redirected')


def download_txt(url, book_id, folder='books/'):
    params = {'id': book_id}

        # Создание имени файла для сохранения книги
        filename = sanitize_filename(f"{book['title'][0]}")

        # Санитизация имени папки и получение ссылки на обложку книги
        folder = sanitize_filepath(folder)
        book_image_url = urljoin(url, soup.find('div', class_='bookimage').find('img')['src'])

        filepath = os.path.join(folder, f"{book_id}. {filename}.txt")

        # Загрузка текста книги
        book_text_url = f"{url}txt.php?id={book_id}"
        book_text_response = requests.get(book_text_url)
        check_for_redirect(book_text_response)
        book_text_response.raise_for_status()
        book_text = book_text_response.text

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(book_text)

        print('Название:', book['title'][0])

        print('Автор:', book['author'][0])

        return book_image_url

    except requests.exceptions.HTTPError:
        pass



def download_image(book_id, folder='images/'):
    book_page_url = f'https://tululu.org/b{book_id}'
    book_page_response = requests.get(book_page_url)
    soup = BeautifulSoup(book_page_response.text, 'lxml')
    book_image_url = urljoin(book_page_url, soup.find('div', class_='bookimage').find('img')['src'])
    os.makedirs(folder, exist_ok=True)
    response = requests.get(book_image_url)
    response.raise_for_status()
    check_for_redirect(response)
    filename = os.path.basename(urlparse(book_image_url).path)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def parse_book_page(soup):
    title_author = soup.find("h1").text
    title, author = title_author.split(" :: ")
    comments_tags = soup.find_all("div", {"class": "texts"})
    genre_tags = soup.find("span", class_="d_book").find_all("a")

    comments = []
    for comment in comments:
        comment_text = comment.find("span").get_text()
        comments_tags.append(comment_text)

    genres = []
    for genre_tag in genre_tags:
        genres.append(genre_tag.text)

    titles = []
    titles.append(sanitize_filename(title.strip()))

    authors = []
    authors.append(sanitize_filename(author.strip()))

    book = {
        'title': titles,
        'author': authors,
        'genre': genres,
        'comment': comments,
    }

    return book


def main():
    parser = argparse.ArgumentParser(description='Данный код позволяет скачивать книги и обложки книг с сайта')
    parser.add_argument('--start_id', type=int, default=10,
                        help='id книги, с которой начнется скачивание')
    parser.add_argument('--end_id', type=int, default=20,
                        help='id книги, на которой закончится скачивание')
    args = parser.parse_args()
    url = 'https://tululu.org/txt.php'
    try:
        for book_id in range(args.start_id, args.end_id):
            download_txt(url, book_id=book_id)
            download_image(book_id=book_id)
    except requests.exceptions.HTTPError as e:
        print(f"Error: Unable to download book: {e}")

    except requests.exceptions.RequestException as e:
        print(f"The request failed: {e}")


if __name__ == '__main__':
    main()
