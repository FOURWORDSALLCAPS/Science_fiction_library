import requests
from pathlib import Path

url = "https://tululu.org/txt.php"
links = []

for id_book in range(11):
    params = {'id': id_book}
    response = requests.get(url, params=params)
    response.raise_for_status()
    links.append(response.url)

Path("books").mkdir(parents=True, exist_ok=True)


for link_number, link in enumerate(links):
    response = requests.get(link)
    response.raise_for_status()
    with open(f'books/book_{link_number}.txt', 'wb') as file:
        file.write(response.content)
