from collections import UserDict
from datetime import datetime, timedelta
import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, name):
        super().__init__(name)
        if not name:
            raise ValueError("Name cannot be empty")

class Phone(Field):
    def __init__(self, phone):
        super().__init__(phone)
        if not phone.isdigit() or len(phone) != 10:
            raise ValueError("Invalid phone number format. Must contain 10 digits.")

class Birthday(Field):
    def __init__(self, value):
        try:
             self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if str(phone) == old_phone:
                phone.value = new_phone

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p.value
            
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(str(p) for p in self.phones)
        birthday_str = self.birthday.value.strftime("%d %m %Y") if self.birthday else "None"
        return f"Contact name: {self.name.value}, phones: {phones_str}, Birthday: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
    
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday and record.birthday.value:
                birthday_date = record.birthday.value
                birthday_this_year = birthday_date.replace(year=today.year).date()

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7:
                    if birthday_this_year.weekday() in [5, 6]:
                        days_until_birthday += (7 - birthday_this_year.weekday())

                    congratulation_date = today + timedelta(days=days_until_birthday)
                    congratulation_date_str = congratulation_date.strftime("%Y.%m.%d")

                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date_str
                    })

        return upcoming_birthdays

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "This name is not entered in the phone book."
    return wrapper

@handle_errors
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@handle_errors
def change_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    if record:
        record.phones = [Phone(p) for p in phone.split(',')]
        return "Contact changed."
    else:
        return "This name is not entered in the phone book."

@handle_errors
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return "; ".join(str(p) for p in record.phones)
    else:
        return "This name is not entered in the phone book."

@handle_errors
def show_all(book: AddressBook):
    return "\n".join(str(record) for record in book.data.values())

@handle_errors
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "This name is not entered in the phone book."

@handle_errors
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value.strftime("%d.%m.%Y")
    else:
        return "This name is not entered in the phone book or birthday is not set."

@handle_errors
def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join(f"Name: {b['name']}, Birthday: {b['congratulation_date']}" for b in upcoming_birthdays)
    else:
        return "No upcoming birthdays in the next week."


def main():
    # Завантаження даних з файлу
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            # Збереження даних у файл перед виходом
            save_data(book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")


main()