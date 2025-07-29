from typing import List


class Book:

    def __init__(self, title: str, author: str, isbn: int, available_copies: int):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.available_copies = available_copies

    def display_info(self):
        return f"Title: {self.title}, Author: {self.author}, ISBN: {self.isbn}, Available Copies: {self.available_copies}"

    def borrow_copy(self):
        if self.available_copies > 0:
            self.available_copies -= 1
            return "Success"
        return "Not enough copies in Library"

    def return_copy(self):
        self.available_copies += 1
        return "Success"


class Member:

    def __init__(self, member_id: int, name: str):
        self.member_id = member_id
        self.name = name
        self.borrowed_books: List[Book] = []

    def borrow_book(self, book: Book):
        result = book.borrow_copy()
        if result == "Success":
            self.borrowed_books.append(book)
        return result

    def return_book(self, book: Book):
        if book in self.borrowed_books:
            result = book.return_copy()
            if result == "Success":
                self.borrowed_books.remove(book)
            return result
        return "Book not in borrowed list"

    def list_borrowed_books(self):
        for book in self.borrowed_books:
            print(
                f"Title: {book.title}, Author: {book.author}, ISBN: {book.isbn}, Available Copies: {book.available_copies}"
            )


class Library:

    def __init__(self):
        self.books: List[Book] = []
        self.members: List[Member] = []

    def add_book(self, book: Book):
        self.books.append(book)
        return "Success"

    def register_member(self, member: Member):
        self.members.append(member)
        return "Success"

    def find_book_by_title(self, title: str) -> Book | None:
        for book in self.books:
            if book.title == title:
                return book
        return "Book not found"

    def find_member_by_id(self, member_id: str) -> Member | None:
        for member in self.members:
            if member.member_id == member_id:
                return member
        return "Member not found"

    def display_all_books(self):
        for book in self.books:
            book.display_info()

    def display_all_members(self):
        for member in self.members:
            print(
                f"Member ID: {member.member_id}, Name: {member.name}, Borrowed Books: {member.borrowed_books}"
            )
