import os
import mysql.connector
import random
from decimal import Decimal
import string

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="0612049471",
        database="library"
    )

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_library_card_no(cursor):
    while True:
        number = 'D0' + ''.join(random.choices('0123456789', k=8))
        cursor.execute("SELECT library_card_no FROM Account WHERE library_card_no = %s", (number,))
        if cursor.fetchone() is None:
            return number
        
def generate_book_id(cursor):
    while True:
        book_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
        cursor.execute("SELECT book_id FROM Books WHERE book_id = %s", (book_id,))
        if not cursor.fetchone():
            return book_id


def create_account():
    Library = connect_to_database()
    cursor = Library.cursor()
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    is_admin_input = input("Is the user an admin? (yes/no): ")
    is_admin = is_admin_input.lower() == 'yes'
    balance = Decimal(input("Initial Balance (numeric value): "))
    library_card_no = generate_library_card_no(cursor)
    query = """
    INSERT INTO Account (library_card_no, first_name, last_name, is_admin, balance)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (library_card_no, first_name, last_name, is_admin, balance))
    Library.commit()
    print(f"Account created successfully! Your library card number is {library_card_no}")
    cursor.close()
    Library.close()

def see_account_information():
    Library = connect_to_database()
    cursor = Library.cursor()
    print(" ")
    library_card_no = input("Enter Library Card Number: ")
    cursor.execute("SELECT * FROM Account WHERE library_card_no = %s", (library_card_no,))
    account = cursor.fetchone()
    if account:
        clear_screen()
        print("\nAccount Information:")
        print("Library Card No:", account[0])
        print("First Name:", account[1])
        print("Last Name:", account[2])
        print("Is Admin:", "Yes" if account[3] else "No")
        print(" ")
        print("Balance: $",account[4])
        cursor.execute("""
        SELECT b.book_id, b.title, cl.checked_out_date 
        FROM Books b 
        JOIN checking_log cl ON b.book_id = cl.book_id 
        WHERE cl.library_card_no = %s""", (library_card_no,))
        books = cursor.fetchall()
        if books:
            print("\nBooks Rented Out:")
            for book in books:
                print(f"Book ID: {book[0]}, Title: {book[1]}, Date Checked Out: {book[2]}")
        else:
            print(" ")
            print("No books currently checked out.")
    else:
        print("No account found with that library card number.")
    cursor.close()
    Library.close()

def edit_balance(library_card_no):
    Library = connect_to_database()
    cursor = Library.cursor()
    cursor.execute("SELECT first_name, last_name, balance FROM Account WHERE library_card_no = %s", (library_card_no,))
    account = cursor.fetchone()
    if account:
        print(f"Account for {account[0]} {account[1]} with current balance: ${account[2]}")
        change = Decimal(input("Enter amount to add/subtract from balance: "))
        new_balance = account[2] + change
        cursor.execute("UPDATE Account SET balance = %s WHERE library_card_no = %s", (new_balance, library_card_no))
        Library.commit()
        print(f"Account balance updated. New Balance: ${new_balance}")
    cursor.close()
    Library.close()

def main_menu():
    while True:
        clear_screen()
        print("\nMain Menu:")
        print("1. Account Information")
        print("2. Inventory")
        print("3. Exit")
        choice = input("Enter choice: ")
        if choice == '1':
            see_account_information()
        elif choice == '2':
            inventory_menu()
        elif choice == '3':
            break
        input("\nPress Enter to continue...")

def inventory_menu():
    while True:
        clear_screen()
        print("\nInventory Menu:")
        print("1. See Books")
        print("2. Add Books")
        print("3. Edit Book Status")
        print("4. Return to Main Menu")
        choice = input("Enter choice: ")
        if choice == '1':
            see_books()
        elif choice == '2':
            add_books()
        elif choice == '3':
            edit_book_status()
        elif choice == '4':
            break
        input("\nPress Enter to continue...")


#BOOK EDITING/MANIPULATION

def see_books():
    Library = connect_to_database()
    cursor = Library.cursor()
    try:
        cursor.execute("SELECT book_id, title, author, genre, release_date, checked_out FROM Books")
        books = cursor.fetchall()
        if books:
            print("\nList of Books:")
            for book in books:
                checked_out_status = "Yes" if book[5] else "No"
                print(f"Book ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Genre: {book[3]}, Release Date: {book[4]}, Checked Out: {checked_out_status}")
        else:
            print("No books found.")
    except mysql.connector.Error as error:
        print(f"Error retrieving books: {error}")
    finally:
        cursor.close()
        Library.close()

def add_books():
    Library = connect_to_database()
    cursor = Library.cursor()
    try:
        title = input("Enter the title of the book: ")
        author = input("Enter the author of the book: ")
        genre = input("Enter the genre of the book: ")
        release_date = input("Enter the release date of the book (YYYY-MM-DD): ")
        num_copies = int(input("Enter the number of copies to add: "))
        for _ in range(num_copies):
            book_id = generate_book_id(cursor)
            cursor.execute("INSERT INTO Books (book_id, title, author, genre, release_date, checked_out) VALUES (%s, %s, %s, %s, %s, %s)",
                           (book_id, title, author, genre, release_date, False))
        Library.commit()
        print(f"{num_copies} copies of '{title}' have been added to the library.")
    except mysql.connector.Error as error:
        print(f"Error adding books: {error}")
    finally:
        cursor.close()
        Library.close()


def edit_book_status():
    Library = connect_to_database()
    cursor = Library.cursor()
    try:
        book_id = input("Enter the book ID: ")
        cursor.execute("SELECT title, checked_out FROM Books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        if book:
            if book[1]:
                cursor.execute("DELETE FROM checking_log WHERE book_id = %s", (book_id,))
                cursor.execute("UPDATE Books SET checked_out = %s WHERE book_id = %s", (False, book_id))
                print(f"{book[0]} (Book ID: {book_id}) has been returned.")
            else:
                library_card_no = input("Enter the library card number of the user checking out the book: ")
                cursor.execute("SELECT first_name, last_name FROM Account WHERE library_card_no = %s", (library_card_no,))
                user = cursor.fetchone()
                if user:
                    cursor.execute("INSERT INTO checking_log (library_card_no, first_name, last_name, book_id, checked_out_date, return_date) VALUES (%s, %s, %s, %s, CURDATE(), CURDATE() + INTERVAL 14 DAY)",
                                   (library_card_no, user[0], user[1], book_id))
                    cursor.execute("UPDATE Books SET checked_out = %s WHERE book_id = %s", (True, book_id))
                    print(f"{book[0]} checked out by {user[0]} {user[1]}.")
        else:
            print("No book found with that ID.")
        Library.commit()
    except mysql.connector.Error as error:
        print(f"Error updating book status: {error}")
    finally:
        cursor.close()
        Library.close()



if __name__ == "__main__":
    main_menu()
