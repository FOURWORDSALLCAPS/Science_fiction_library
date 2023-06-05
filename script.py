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
    try:
        params = {'id': book_id}

        os.makedirs(folder, exist_ok=True)

        response = requests.get(url, params=params)
        check_for_redirect(response)
        response.raise_for_status()
        book_page_url = f'https://tululu.org/b{book_id}'
        book_page_response = requests.get(book_page_url)
        check_for_redirect(book_page_response)
        book_page_response.raise_for_status()
        soup = BeautifulSoup(book_page_response.text, 'lxml')
        book = parse_book_page(soup)
        filename = sanitize_filename(f"{book['title'][0]}")
        folder = sanitize_filepath(folder)
        book_image_url = urljoin(url, soup.find('div', class_='bookimage').find('img')['src'])
        filepath = os.path.join(folder, f"{book_id}. {filename}.txt")
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


def download_image(url, folder='images/'):
    try:
        os.makedirs(folder, exist_ok=True)
        response = requests.get(url)
        response.raise_for_status()

        filename = os.path.basename(urlparse(url).path)
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as file:
            file.write(response.content)

    except requests.exceptions.HTTPError:
        pass

    except requests.exceptions.RequestException as e:
        pass


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
    parser = argparse.ArgumentParser(description='Telegram-бот для публикации фотографий')
    parser.add_argument('start_id', type=int, default=10,
                        help='id книги, с которой начнется скачивание')
    parser.add_argument('end_id', type=int, default=20,
                        help='id книги, на котором закончится скачивание')
    args = parser.parse_args()
    url = 'https://tululu.org/'
    for book_id in range(args.start_id, args.end_id):
        download_image(download_txt(url, book_id=book_id))


if __name__ == '__main__':
    main()
