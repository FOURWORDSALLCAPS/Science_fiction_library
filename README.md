# Библиотека научной фантастики

Данный код позволяет скачивать книги и обложки книг с сайта [tululu.org](https://tululu.org/). 

## Установка зависимостей

Запускаем CMD (можно через Win+R, дальше вводим`cmd`) и вписываем команду`cd /D <путь к папке со скриптами>`

```pip install -r requirements.txt```

## Хочу скачать библиотеку

1. Скачал проект
2. Перешел в каталог pages
3. Jткрыл файл index1.html
3. Нажав на `Читать` открылась страница с содержанием книги

## Запуск скрипта
Запуск скрипта осуществляется командой:

```python tululu.py```

По умолчанию скрипт будет скачивать книги и обложки из указанного интервала от первой до последней страницы. 

Дополнительные параметры запуска:
- `--start_id` - интервал от которого начнется скачивание.
- `--end_id` - интервал до которого пройдет скачивание.
- `--dest_folder` - Путь к каталогу с результатами парсинга: картинкам, книгам, JSON.
- `--skip_imgs` - Не скачивать обложки для книг.
- `--skip_txt` - Не скачивать текстовые файлы для книг.


```python tululu.py --start_id 5 --end_id 20 --dest_folder ./results/ --skip_imgs --skip_txt```

### Результат:
Получаете скрипт, который:
Скачивает книги и обложки по заданному интервалу и сохраняет в соответсвующее папки books и images, а так же сохраняет результат в .json файл

## Версия Python: 
Я использовал Python `3.8.3`, но он должен работать на любой более новой версии.

## Цель проекта:
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).

## Автор
(2023) Zaitsev Vladimir