import random
import string
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import simpledialog, messagebox, ttk
import mysql.connector
from decimal import Decimal

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="0612049471",
        database="library"
    )

def set_dark_mode():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TFrame", background="#2e2e2e")
    style.configure("TLabel", background="#2e2e2e", foreground="white")
    style.configure("TButton", background="#444444", foreground="white")
    style.map("TButton", background=[("active", "#666666")])
    style.configure("Treeview", background="#2e2e2e", foreground="white", fieldbackground="#2e2e2e", bordercolor="#444444", borderwidth=1)
    style.map("Treeview.Heading", background=[("active", "#666666")])

def login():
    global current_user
    last_name = last_name_entry.get()
    library_card_no = library_card_entry.get()
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Account WHERE last_name = %s AND library_card_no = %s", (last_name, library_card_no))
    account = cursor.fetchone()
    if account:
        current_user = account
        login_frame.pack_forget()
        if account[3]:
            admin_frame.pack(fill=tk.X)
        else:
            user_frame.pack(fill=tk.X)
    else:
        messagebox.showerror("Error", "No account found with that information.")
    cursor.close()
    db.close()

def show_account_information():
    account_info = f"""
    Account Information:

    Library Card No: {current_user[0]}
    Name: {current_user[1]} {current_user[2]}
    Balance: ${current_user[4]}
    """
    messagebox.showinfo("Account Information", account_info)

def show_books_checked_out():
    db = connect_to_database()
    cursor = db.cursor()
    query = """
        SELECT b.book_id, b.title, cl.return_date
        FROM Books b
        JOIN checking_log cl ON b.book_id = cl.book_id
    """
    if not current_user[3]:
        query += " WHERE cl.library_card_no = %s AND b.checked_out = TRUE"
        cursor.execute(query, (current_user[0],))
    else:
        query += " WHERE b.checked_out = TRUE"
        cursor.execute(query)

    books = cursor.fetchall()
    cursor.close()
    db.close()
    books_window = tk.Toplevel(root)
    books_window.title("Books Checked Out" if current_user[3] else "My Books")
    books_window.configure(bg="#2e2e2e")
    tree = ttk.Treeview(books_window, columns=("book_id", "title", "return_date"), show='headings')
    tree.heading("book_id", text="Book ID")
    tree.heading("title", text="Title")
    tree.heading("return_date", text="Return Date")
    for book in books:
        tree.insert("", "end", values=book)
    tree.pack(fill=tk.BOTH, expand=True)


def check_out_book():
    book_id = simpledialog.askstring("Input", "Enter Book ID:")
    if book_id is None:
        return
    
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT checked_out FROM Books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()
    if not book:
        messagebox.showerror("Error", "Book does not exist.")
        return
    if book[0]:
        cursor.execute("UPDATE checking_log SET return_date = CURDATE() WHERE book_id = %s AND return_date IS NULL", (book_id,))
        cursor.execute("UPDATE Books SET checked_out = FALSE WHERE book_id = %s", (book_id,))
        db.commit()
        messagebox.showinfo("Success", f"Book '{book_id}' has been checked in successfully.")
        return
    
    due_date = datetime.now() + timedelta(weeks=2)
    if current_user[3]:
        library_card_no = simpledialog.askstring("Input", "Enter Library Card Number for user:")
    else:   
        library_card_no = current_user[0]
    cursor.execute("SELECT first_name, last_name FROM Account WHERE library_card_no = %s", (library_card_no,))
    account = cursor.fetchone()
    if not account:
        messagebox.showerror("Error", "Account not found.")
        return
    cursor.execute("""
        INSERT INTO checking_log (library_card_no, first_name, last_name, book_id, checked_out_date, return_date)
        VALUES (%s, %s, %s, %s, CURDATE(), %s)
    """, (library_card_no, account[0], account[1], book_id, due_date.strftime('%Y-%m-%d')))
    cursor.execute("UPDATE Books SET checked_out = TRUE WHERE book_id = %s", (book_id,))
    db.commit()
    messagebox.showinfo("Success", f"Book '{book_id}' checked out successfully, due on {due_date.strftime('%Y-%m-%d')}.")
    cursor.close()
    db.close()

def generate_library_card_no(cursor):
    while True:
        number = 'D0' + ''.join(random.choices('0123456789', k=8))
        cursor.execute("SELECT library_card_no FROM Account WHERE library_card_no = %s", (number,))
        if cursor.fetchone() is None:
            return number

def add_account():
    db = connect_to_database()
    cursor = db.cursor()
    first_name = simpledialog.askstring("Input", "First Name:")
    last_name = simpledialog.askstring("Input", "Last Name:")
    is_admin_input = simpledialog.askstring("Input", "Is the user an admin? (yes/no):")
    is_admin = is_admin_input.lower() == 'yes'
    balance = simpledialog.askfloat("Input", "Initial Balance:")
    library_card_no = generate_library_card_no(cursor)
    
    query = """
    INSERT INTO Account (library_card_no, first_name, last_name, is_admin, balance)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (library_card_no, first_name, last_name, is_admin, balance))
    db.commit()
    messagebox.showinfo("Success", f"Account created successfully! Library card number is {library_card_no}")
    cursor.close()
    db.close()

def generate_book_id(cursor):
    while True:
        book_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
        cursor.execute("SELECT book_id FROM Books WHERE book_id = %s", (book_id,))
        if not cursor.fetchone():
            return book_id

def add_books():
    db = connect_to_database()
    cursor = db.cursor()
    try:
        title = simpledialog.askstring("Input", "Enter the title of the book:")
        author = simpledialog.askstring("Input", "Enter the author of the book:")
        genre = simpledialog.askstring("Input", "Enter the genre of the book:")
        release_date = simpledialog.askstring("Input", "Enter the release date of the book (YYYY-MM-DD):")
        num_copies = simpledialog.askinteger("Input", "Enter the number of copies to add:")

        if None in (title, author, genre, release_date, num_copies):
            return

        for _ in range(num_copies):
            book_id = generate_book_id(cursor)
            cursor.execute("INSERT INTO Books (book_id, title, author, genre, release_date, checked_out) VALUES (%s, %s, %s, %s, %s, %s)",
                           (book_id, title, author, genre, release_date, False))
        db.commit()
        messagebox.showinfo("Success", f"{num_copies} copies of '{title}' have been added to the library.")
    except mysql.connector.Error as error:
        messagebox.showerror("Error", str(error))
    finally:
        cursor.close()
        db.close()

def sort_table(tree, col, reverse):
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    data.sort(reverse=reverse)
    for index, (val, child) in enumerate(data):
        tree.move(child, '', index)
    tree.heading(col, command=lambda: sort_table(tree, col, not reverse))

def show_accounts_table():
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Account LIMIT 100")
    records = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    table_window = tk.Toplevel(root)
    table_window.title("Accounts")
    table_window.configure(bg="#2e2e2e")
    tree = ttk.Treeview(table_window, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col, command=lambda _col=col: sort_table(tree, _col, False))
    for record in records:
        tree.insert("", "end", values=record)
    tree.pack(fill=tk.BOTH, expand=True)
    
    ttk.Button(table_window, text='Add Account', command=add_account).pack(pady=10)
    cursor.close()
    db.close()

def show_books_table():
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Books LIMIT 100")
    records = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    table_window = tk.Toplevel(root)
    table_window.title("Books")
    table_window.configure(bg="#2e2e2e")
    tree = ttk.Treeview(table_window, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col, command=lambda _col=col: sort_table(tree, _col, False))
    for record in records:
        tree.insert("", "end", values=record)
    tree.pack(fill=tk.BOTH, expand=True)
    
    cursor.close()
    db.close()

def show_checking_log_table():
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM checking_log LIMIT 100")
    records = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    table_window = tk.Toplevel(root)
    table_window.title("Checking Log")
    table_window.configure(bg="#2e2e2e")
    tree = ttk.Treeview(table_window, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col, command=lambda _col=col: sort_table(tree, _col, False))
    for record in records:
        tree.insert("", "end", values=record)
    tree.pack(fill=tk.BOTH, expand=True)
    
    cursor.close()
    db.close()

def main_window():
    global root, login_frame, last_name_entry, library_card_entry, user_frame, admin_frame, current_user
    current_user = None
    root = tk.Tk()
    root.title("Library Management System")
    root.geometry('600x300')

    set_dark_mode()

    root.configure(bg="#2e2e2e")

    login_frame = ttk.Frame(root)
    login_frame.pack(fill=tk.X, pady=20)

    ttk.Label(login_frame, text="Last Name:", background="#2e2e2e", foreground="white").pack(side=tk.LEFT, padx=5)
    last_name_entry = ttk.Entry(login_frame)
    last_name_entry.pack(side=tk.LEFT, padx=5)

    ttk.Label(login_frame, text="Library Card Number:", background="#2e2e2e", foreground="white").pack(side=tk.LEFT, padx=5)
    library_card_entry = ttk.Entry(login_frame)
    library_card_entry.pack(side=tk.LEFT, padx=5)

    ttk.Button(login_frame, text='Login', command=login).pack(side=tk.LEFT, padx=5)

    user_frame = ttk.Frame(root)
    ttk.Button(user_frame, text='Account Information', command=show_account_information).pack(fill=tk.X, pady=5)
    ttk.Button(user_frame, text='Books Checked Out', command=show_books_checked_out).pack(fill=tk.X, pady=5)
    ttk.Button(user_frame, text='Check Out a Book', command=check_out_book).pack(fill=tk.X, pady=5)

    admin_frame = ttk.Frame(root)
    ttk.Button(admin_frame, text='Account Information', command=show_account_information).pack(fill=tk.X, pady=5)
    ttk.Button(admin_frame, text='Books Checked Out', command=show_books_checked_out).pack(fill=tk.X, pady=5)
    ttk.Button(admin_frame, text='Check Out a Book', command=check_out_book).pack(fill=tk.X, pady=5)
    ttk.Button(admin_frame, text='Add Book', command=add_books).pack(fill=tk.X, pady=5)  # Add Book button for admin
    ttk.Button(admin_frame, text='Show Accounts Table', command=show_accounts_table).pack(fill=tk.X, pady=5)
    ttk.Button(admin_frame, text='Show Books Table', command=show_books_table).pack(fill=tk.X, pady=5)
    ttk.Button(admin_frame, text='Show Checking Log Table', command=show_checking_log_table).pack(fill=tk.X, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main_window()