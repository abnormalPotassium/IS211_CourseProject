import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def define_table(db_file,script):
    conn = sqlite3.connect(db_file)
    with conn:
        cur = conn.cursor()

        qry = open(script,'r').read()
        cur.executescript(qry)

def load_table(db_file):
    conn = sqlite3.connect(db_file)
    with conn:
        cur = conn.cursor()

        books = (
            ('Programming Android', 'Zigurd Mednieks', 542, 3.5, 'http://books.google.com/books/content?id=QP7VvnhDOOsC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api')
        )

        accounts = (
            ('tahmad7', 'password123')
        )

        books_accounts = (
            (1, 'tahmad7')
        )

        cur.execute("INSERT INTO books VALUES(null,?,?,?,?,?)", books)
        cur.execute("INSERT INTO accounts VALUES(?,?)", accounts)
        cur.execute("INSERT INTO books_accounts VALUES(?,?)", books_accounts)

if __name__ == '__main__':
    create_connection(r'D:\Coding Projects\IS211_CourseProject\book.db')
    define_table(r'D:\Coding Projects\IS211_CourseProject\book.db', r'D:\Coding Projects\IS211_CourseProject\schema.sql')