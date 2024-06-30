import mysql.connector
import random
from decimal import Decimal
import os

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="0612049471",
        database="library"
    )

def generate_library_card_no(cursor):
    while True:
        number = 'D0' + ''.join(random.choices('0123456789', k=8))
        cursor.execute("SELECT library_card_no FROM Account WHERE library_card_no = %s", (number,))
        if cursor.fetchone() is None:
            return number

def create_account():
    try:
        Library = connect_to_database()
        cursor = Library.cursor()
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        is_admin_input = input("Is the user an admin? (yes/no): ")
        is_admin = True if is_admin_input.lower() == 'yes' else False
        balance = float(input("Initial Balance (numeric value): "))
        library_card_no = generate_library_card_no(cursor)
        query = """
        INSERT INTO Account (library_card_no, first_name, last_name, isAdmin, balance)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (library_card_no, first_name, last_name, is_admin, balance))
        Library.commit()
        print(f"Account created successfully! Your library card number is {library_card_no}")
    except mysql.connector.Error as error:
        print(f"Failed to create account: {error}")
    finally:
        if Library.is_connected():
            cursor.close()
            Library.close()

def see_account_information():
    try:
        Library = connect_to_database()
        cursor = Library.cursor()
        library_card_no = input("Enter Library Card Number: ")
        cursor.execute("SELECT * FROM Account WHERE library_card_no = %s", (library_card_no,))
        account = cursor.fetchone()
        if account:
            print("\nAccount Information:")
            print("Library Card No: ", account[0])
            print("First Name: ", account[1])
            print("Last Name: ", account[2])
            print("Is Admin: ", "Yes" if account[3] else "No")
            print("Balance: $", account[4])
        else:
            print("No account found with that library card number.")
    except mysql.connector.Error as error:
        print(f"Error: {error}")
    finally:
        if Library.is_connected():
            cursor.close()
            Library.close()

def edit_balance():
    try:
        Library = connect_to_database()
        cursor = Library.cursor()
        library_card_no = input("Enter Library Card Number: ")
        cursor.execute("SELECT first_name, last_name, balance FROM Account WHERE library_card_no = %s", (library_card_no,))
        account = cursor.fetchone()
        if account:
            print(f"Account for {account[0]} {account[1]} with current balance: ${account[2]}")
            change = Decimal(input("Enter amount to add/subtract from balance: "))  # Convert input to Decimal
            new_balance = account[2] + change  # Now adding two Decimals
            cursor.execute("UPDATE Account SET balance = %s WHERE library_card_no = %s", (new_balance, library_card_no))
            Library.commit()
            print(f"Account balance updated.\n\nNew Balance: ${new_balance}")
        else:
            print("No account found with that library card number.")
    except mysql.connector.Error as error:
        print(f"Error: {error}")
    finally:
        if Library.is_connected():
            cursor.close()
            Library.close()

def clear_screen():
    os.system('cls')

def menu():
    while True:
        clear_screen()  # Clear the screen before showing the menu
        print("\n1. Create Account")
        print("2. See Account Information")
        print("3. Edit Balance")
        print("4. Exit")
        choice = input("Enter choice: ")
        if choice == '1 ':
            create_account()
        elif choice == '2':
            see_account_information()
        elif choice == '3':
            edit_balance()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please choose again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    menu()
