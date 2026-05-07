

class LoggerInterface:

    @staticmethod
    def log(message: str):
        pass

class PythonCMDLogger(LoggerInterface):

    def __init__(self):
        self.messages = []

    def log(self, message: str):
        self.messages.append(f"[LOG] {message}")

class Book:

    def __init__(self, title: str, author: str, isbn: int, available_copies: int):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.available_copies = available_copies

    def borrow(self) -> bool:
        if self.available_copies > 0:
            self.available_copies -= 1
            return True
        else:
            return False

    def return_book(self):
        self.available_copies += 1

class Member:

    def __init__(self, name: str, member_id: int):
        self.name = name
        self.member_id = member_id
        self.borrowed_books: list[Book] = []

    def borrow_book(self, book: Book):
        if book.borrow():
            self.borrowed_books.append(book)
            return "Successfully borrowed a book"
        else:
            return "Not enough book in Library"

    def return_book(self, book: Book):
        if book in self.borrowed_books:
            self.borrowed_books.remove(book)
            book.return_book()
            return "Successfully returned a book"
        else:
            return "Member doesn't have this book"

class Student(Member):

    def __init__(self, name, member_id):
        super().__init__(name, member_id)

    def borrow_book(self, book: Book):
        if len(self.borrowed_books) < 3:
            return super().borrow_book(book)
        else:
            return "Students can borrow only 3 books at a time"

    def return_book(self, book):
        return super().return_book(book)

class Teacher(Member):

    def __init__(self, name, member_id):
        super().__init__(name, member_id)

    def borrow_book(self, book: Book):
        if len(self.borrowed_books) < 5:
            return super().borrow_book(book)
        else:
            return "Teachers can borrow only 5 books at a time"

    def return_book(self, book):
        return super().return_book(book)

class Library:

    def __init__(self, logger: LoggerInterface):
        self.books: list[Book] = []
        self.members: list[Member] = []
        self.logger = logger

    def add_book(self, book: Book):
        self.books.append(book)
        self.logger.log(f'Added new book: {book.title}')

    def add_member(self, member: Member):
        self.members.append(member)
        self.logger.log(f'Added new member: {member.name}')

    def find_book_by_title(self, title):
        for book in self.books:
            if book.title == title:
                return book
        return None

    def find_member_by_member_id(self, member_id):
        for member in self.members:
            if member.member_id == member_id:
                return member
        return None

    def borrow_book(self, member_id, title):
        book = self.find_book_by_title(title)
        member = self.find_member_by_member_id(member_id)

        if book==None or member==None:
            self.logger.log(f'member or book could not be found and borrowed')
            return "Member or book not found"

        self.logger.log(f'member: {member.name} borrowed a book: {book.title}')
        return member.borrow_book(book)

    def return_book(self, member_id, title):
        book = self.find_book_by_title(title)
        member = self.find_member_by_member_id(member_id)

        if book==None or member==None:
            return "Member or book not found"

        return member.return_book(book)

class MemberFactory:

    @staticmethod
    def create_member(name, member_id, role):
        match role:
            case "teacher":
                return Teacher(name, member_id)
            case "student":
                return Student(name, member_id)
            case _:
                return None


logger = PythonCMDLogger()
library = Library(logger)

book1 = Book("1984", "George Orwell", "123456", 15)
book2 = Book("The Hobbit", "J.R.R. Tolkien", "654321", 15)
library.add_book(book1)
library.add_book(book2)

student = MemberFactory.create_member("Alice", 101, "student")
teacher = MemberFactory.create_member("Mr. Brown", 201, "teacher")
library.add_member(student)
library.add_member(teacher)

print(library.borrow_book(101, "1984"))
print(library.borrow_book(101, "1984"))
print(library.borrow_book(101, "1984"))
print(library.borrow_book(101, "1984"))
library.borrow_book(201, "The Hobbit")
print(library.return_book(101, "1984"))
print(library.return_book(101, "1984"))
print(library.return_book(101, "1984"))
print(library.return_book(101, "1984"))

print(library.borrow_book(101, "1984"))
print(library.borrow_book(101, "1984"))
print(library.borrow_book(101, "1984"))
print(library.borrow_book(101, "1984"))