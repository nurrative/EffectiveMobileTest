import json
import sys
from datetime import datetime
from typing import List, Optional, Dict


# Класс для представления книги
class Book:
    def __init__(self, book_id: int, title: str, author: str, year: int):
        """Инициализация книги.

        Args:
            book_id (int): Уникальный идентификатор книги.
            title (str): Название книги.
            author (str): Автор книги.
            year (int): Год издания книги.
        """
        self.id = book_id
        self.title = title
        self.author = author
        self.year = year
        self.status = "в наличии"  # По умолчанию статус "в наличии"

    def to_dict(self) -> Dict:
        """Преобразование объекта книги в словарь."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "status": self.status
        }

    @staticmethod
    def from_dict(data: Dict) -> "Book":
        """Создание объекта книги из словаря."""
        book = Book(data["id"], data["title"], data["author"], data["year"])
        book.status = data["status"]
        return book

    def __str__(self) -> str:
        return f"ID: {self.id}, Title: {self.title}, Author: {self.author}, Year: {self.year}, Status: {self.status}"


# Класс для управления библиотекой
class Library:
    def __init__(self, storage_file: str = "library.json"):
        """Инициализация библиотеки.

        Args:
            storage_file (str): Имя файла для хранения данных о книгах.
        """
        self.storage_file = storage_file
        self.books: List[Book] = self.load_books()
        self.next_id = self.get_next_id()

    def load_books(self) -> List[Book]:
        """метод загрузки книг из файла."""
        try:
            with open(self.storage_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                return [Book.from_dict(book) for book in data]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("Ошибка чтения файла данных. Файл будет перезаписан.")
            return []

    def save_books(self):
        """метод сохранения списка книг в файл."""
        try:
            with open(self.storage_file, "w", encoding="utf-8") as file:
                json.dump([book.to_dict() for book in self.books], file, ensure_ascii=False, indent=4)
        except UnicodeEncodeError:
            print("Ошибка сохранения книги из-за некорректных символов в данных.")

    def get_next_id(self) -> int:
        """Получение следующего доступного ID книги."""
        if not self.books:
            return 1
        return max(book.id for book in self.books) + 1

    def validate_year(self, year: str):
        """метод проверки корректности года издания.

        Args:
            year (str): Год издания книги в виде строки.

        Raises:
            ValueError: Если год некорректен.
        """
        current_year = datetime.now().year
        if not year.isdigit() or not (0 < int(year) <= current_year):
            raise ValueError("Некорректный год. Укажите год в диапазоне от 1 до текущего года.")

    def add_book(self, title: str, author: str, year: str):
        """метод добавления книги в библиотеку."""
        try:
            self.validate_year(year)
            book = Book(self.next_id, title, author, int(year))
            self.books.append(book)
            self.next_id += 1
            self.save_books()
            print(f"Книга '{title}' успешно добавлена.")
        except ValueError as e:
            print(e)

    def remove_book(self, book_id: int):
        """метод удаления книги из библиотеки."""
        for book in self.books:
            if book.id == book_id:
                self.books.remove(book)
                self.save_books()
                print(f"Книга с ID {book_id} успешно удалена.")
                return
        print(f"Книга с ID {book_id} не найдена.")

    def search_books(self, **kwargs: Optional[str]):
        """метод поиска книги по заданным критериям."""
        results = []
        for book in self.books:
            if any(str(getattr(book, key)).lower() == str(value).lower() for key, value in kwargs.items()):
                results.append(book)
        if results:
            print("Найденные книги:")
            for book in results:
                print(book)
        else:
            print("Книги не найдены.")

    def display_books(self):
        """метод вывода списка всех книг."""
        if not self.books:
            print("Библиотека пуста.")
        else:
            print("Список всех книг:")
            for book in self.books:
                print(book)

    def update_status(self, book_id: int,  new_status: str):
        """метод обновления статуса книги."""
        for book in self.books:
            if book.id == book_id:
                if new_status in ["в наличии", "выдана"]:
                    book.status = new_status
                    self.save_books()
                    print(f"Статус книги '{book.title}' с ID {book_id} успешно обновлён на '{new_status}'.")
                else:
                    print("Недопустимый статус. Используйте 'в наличии' или 'выдана'.")
                return
        print(f"Книга с ID {book_id} не найдена.")


def main():
    """Главная функция приложения."""
    library = Library()
    running = True  # Флаг для управления циклом

    while running:
        print("\nМеню:")
        print("1. Добавить книгу")
        print("2. Удалить книгу")
        print("3. Найти книгу")
        print("4. Показать все книги")
        print("5. Изменить статус книги")
        print("6. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            title = input("Введите название книги: ")
            author = input("Введите автора книги: ")
            while True:
                year = input("Введите год издания: ")
                try:
                    library.validate_year(year)
                    break
                except ValueError as e:
                    print(e)
            library.add_book(title, author, year)
        elif choice == "2":
            try:
                book_id = int(input("Введите ID книги для удаления: "))
                library.remove_book(book_id)
            except ValueError:
                print("ID книги должно быть числом.")
        elif choice == "3":
            print("Введите критерии поиска (оставьте пустым, если не нужно):")
            title = input("Название: ")
            author = input("Автор: ")
            year = input("Год: ")
            criteria = {key: value for key, value in {"title": title, "author": author, "year": year}.items() if value}
            library.search_books(**criteria)
        elif choice == "4":
            library.display_books()
        elif choice == "5":
            try:
                book_id = int(input("Введите ID книги: "))
                print("\nВыберите новый статус книги:")
                print("1. В наличии")
                print("2. Выдана")

                status_choice = input("Введите номер статуса: ")

                if status_choice == "1":
                    new_status = "в наличии"
                elif status_choice == "2":
                    new_status = "выдана"
                else:
                    print("Неверный выбор статуса. Попробуйте снова.")
                    continue  # Если был неправильный выбор, возвращаемся к циклу
                library.update_status(book_id, new_status)

            except ValueError:
                print("ID книги должно быть числом.")
        elif choice == "6":
            print("Выход из программы.")
            running = False  # Устанавливаем флаг в False, чтобы выйти из цикла
            sys.exit(0)
        else:
            print("Неверный выбор. Попробуйте снова.")

    print("Программа завершена.")  # Печатаем сообщение о завершении программы


if __name__ == "__main__":
    main()



