from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import os

app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)  # Generate a random secret key

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="0612049471",
        database="library"
    )

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        last_name = request.form['last_name']
        library_card_no = request.form['library_card_no']
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            query = "SELECT first_name, last_name, is_admin FROM Account WHERE last_name = %s AND library_card_no = %s"
            cursor.execute(query, (last_name, library_card_no))
            account = cursor.fetchone()
            cursor.close()
            conn.close()
            if account:
                session['logged_in'] = True
                session['first_name'] = account[0]
                session['last_name'] = account[1]
                session['is_admin'] = account[2]
                return redirect(url_for('account', first_name=account[0], last_name=account[1], is_admin=account[2]))
            else:
                return 'Login Failed'
        except mysql.connector.Error as e:
            return f"Database connection failed: {e}"
    return render_template('login.html')

@app.route('/account/<first_name>/<last_name>/<int:is_admin>')
def account(first_name, last_name, is_admin):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('account.html', first_name=first_name, last_name=last_name, is_admin=is_admin)

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    data_type = request.form.get('data_type')
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = connect_to_database()
    cursor = conn.cursor()
    if data_type == 'accounts':
        cursor.execute("SELECT * FROM Account")
    elif data_type == 'books':
        cursor.execute("SELECT * FROM Books")
    elif data_type == 'checking_log':
        cursor.execute("SELECT * FROM Checking_Log")
    else:
        cursor.close()
        conn.close()
        return jsonify({"error": "Invalid data type"}), 400

    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()

    # Convert query to dictionary
    result = [dict(zip(columns, row)) for row in rows]
    return jsonify(result)

@app.route('/fetch_account_data', methods=['POST'])
def fetch_account_data():
    library_card_no = request.form.get('library_card_no')
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = connect_to_database()
    cursor = conn.cursor()

    # Fetch account information
    cursor.execute("SELECT library_card_no, balance FROM Account WHERE library_card_no = %s", (library_card_no,))
    account_info = cursor.fetchone()

    # Fetch books checked out by this account
    cursor.execute("SELECT b.title, cl.checked_out_date FROM Books b JOIN Checking_Log cl ON b.book_id = cl.book_id WHERE cl.library_card_no = %s", (library_card_no,))
    books = cursor.fetchall()

    cursor.close()
    conn.close()

    # Prepare data to send back to the client
    account_data = {
        'library_card_no': account_info[0],
        'balance': account_info[1],
        'books': [{'title': book[0], 'date': book[1]} for book in books]
    }
    return jsonify(account_data)

if __name__ == "__main__":
    app.run(debug=True)
