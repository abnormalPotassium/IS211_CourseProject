import functools
import sqlite3
from sqlite3 import Error
import requests
from flask import Flask, render_template, request, redirect, session, flash, url_for, g, jsonify


app = Flask(__name__)

@app.route('/', methods= ['GET', 'POST'])
@app.route('/login', methods= ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        
        conn = sqlite3.connect(r'D:\Coding Projects\IS211_CourseProject\book.db')
        with conn:
            cur = conn.cursor()

            cur.execute("SELECT * FROM accounts")
            accounts = dict(cur.fetchall())

        if username not in accounts.keys():
            error = 'Incorrect username.'
        elif password != accounts[username]:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['account_id'] = username
            return redirect('/dashboard')

        flash(error)

    return render_template('login.html')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('account_id') is None:
            return redirect('/login')

        return view(**kwargs)

    return wrapped_view

@app.route('/register', methods= ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        
        conn = sqlite3.connect(r'D:\Coding Projects\IS211_CourseProject\book.db')
        with conn:
            cur = conn.cursor()

            cur.execute("SELECT * FROM accounts")
            accounts = dict(cur.fetchall())

            if username in accounts.keys():
                error = 'Username Taken!'

            if error is None:
                try:
                    cur.execute("INSERT INTO accounts VALUES(?,?)", [username, password])
                    session.clear()
                    session['account_id'] = username
                    return redirect('/dashboard')
                except Error as e:
                    flash(e)
                    return redirect('/register')

        flash(error)

    return render_template('register.html')

@app.route('/logout')
def logout():

    session.pop('account_id', None)

    return redirect('/login')


@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect(r'D:\Coding Projects\IS211_CourseProject\book.db')
    user = session.get('account_id')
    with conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                    SELECT books.book_title, books.book_author, books.book_pages, books.book_rating, books.book_thumbnail, books.book_id
                    FROM books
                    INNER JOIN books_accounts ON books.book_id = books_accounts.book_id
                    WHERE books_accounts.account_id=?""", (user,))
            books = cur.fetchall()
            return render_template('dashboard.html', book_list = books, username = user)
        except Error as e:
            flash(e)
            return render_template('dashboard.html', book_list = None, username = user)

@app.route('/remove_book', methods = ['POST'])
@login_required
def remove_book():
    if request.method == 'POST':
        book_del = request.form['book_id']
        user = session.get('account_id')

        conn = sqlite3.connect(r'D:\Coding Projects\IS211_CourseProject\book.db')
        cur = conn.cursor()
        with conn:
            try:
                cur.execute("DELETE FROM books_accounts WHERE book_id = ? AND account_id = ?", (book_del, user))
                return redirect('/dashboard')
            except Error as e:
                flash(e)
                return redirect('/dashboard')

@app.route('/add_book', methods = ['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        isbn = request.form['book_isbn']
        title = request.form['book_title']
        error = None
        
        if not isbn and not title:
            error = 'Please enter something into a field.' 
        
        elif isbn:
            if not 9<len(isbn)<14:
                error = 'Please enter a valid ISBN.'
            else:
                book_data = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}')
                print(book_data)
                book_json = dict(book_data.json())
                print(book_json)
                print(type(book_json))
                print(isbn)
                print(title)

                if book_json['totalItems'] == 0:
                    error = 'This ISBN doesn\'t seem to be linked to a book.'
                else:
                    book = {}
                    try:
                        book['title'] = book_json['items'][0]['volumeInfo']['title']
                        print(book)
                    except:
                        book['title'] = None
                    try:
                        book['author'] = book_json['items'][0]['volumeInfo']['authors'][0]
                        print(book)
                    except:
                        book['author'] = None
                    try:
                        book['pages'] = book_json['items'][0]['volumeInfo']['pageCount']
                        print(book)
                    except:
                        book['pages'] = None
                    try:
                        book['rating'] = book_json['items'][0]['volumeInfo']['averageRating']
                        print(book)
                    except:
                        book['rating'] = None
                    try:
                        book['thumbnail'] = book_json['items'][0]['volumeInfo']['imageLinks']['thumbnail']
                        print(book)
                        print(type(book))
                        print(error)
                    except:
                        book['thumbnail'] = 'https://user-images.githubusercontent.com/101482/29592647-40da86ca-875a-11e7-8bc3-941700b0a323.png'
        else:
            book_data = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={title}')
            book_json = book_data.json()

            if book_json['totalItems'] == 0:
                error = 'This title doesn\'t seem to be linked to a book.'
            else:
                book = {}
                try:
                    book['title'] = book_json['items'][0]['volumeInfo']['title']
                except:
                    book['title'] = None
                try:
                    book['author'] = book_json['items'][0]['volumeInfo']['authors'][0]
                except:
                    book['author'] = None
                try:
                    book['pages'] = book_json['items'][0]['volumeInfo']['pageCount']
                except:
                    book['pages'] = None
                try:
                    book['rating'] = book_json['items'][0]['volumeInfo']['averageRating']
                except:
                    book['rating'] = None
                try:
                    book['thumbnail'] = book_json['items'][0]['volumeInfo']['imageLinks']['thumbnail']
                except:
                    book['thumbnail'] = 'https://user-images.githubusercontent.com/101482/29592647-40da86ca-875a-11e7-8bc3-941700b0a323.png'

        if not error:
            conn = sqlite3.connect(r'D:\Coding Projects\IS211_CourseProject\book.db')
            cur = conn.cursor()
            user = session.get('account_id')
            print(user)
            with conn:
                try:
                    cur.execute("INSERT INTO books VALUES(null,?,?,?,?,?)", list(book.values()))
                    cur.execute("INSERT INTO books_accounts VALUES(last_insert_rowid(),?)", (user,))
                    flash(f'{book["title"]} succesfully added to your list!')
                    return redirect('/add_book')
                except Error as e:
                    flash(e)
                    return redirect('/add_book')
        
        flash(error)
    return render_template('add_book.html')

if __name__ == '__main__':
    app.secret_key = 'sekrit'
    app.run()