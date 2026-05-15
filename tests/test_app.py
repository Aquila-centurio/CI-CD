import json, os, tempfile

os.environ["DATA_FILE"] = tempfile.mktemp(suffix=".json")
os.environ["REDIS_HOST"] = ""  # отключаем redis в тестах

from app import load_books, save_book  # было save_books

def test_load_когда_файла_нет():
    assert load_books() == []

def test_сохранить_и_прочитать():
    save_book({"title": "Clean Code", "author": "Martin"})  # было save_books
    books = load_books()
    assert len(books) == 1
    assert books[0]["title"] == "Clean Code"

def test_несколько_книг():
    save_book({"title": "A"})  # было save_books
    save_book({"title": "B"})
    assert len(load_books()) >= 2