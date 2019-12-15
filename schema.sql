DROP TABLE IF EXISTS books;
CREATE TABLE books
( 
	book_id INTEGER PRIMARY KEY,
    book_title varchar(255) NOT NULL,
    book_author varchar(255) NOT NULL,
    book_pages INTEGER,
    book_rating DECIMAL(2,1),
    book_thumbnail varchar(255)
);

DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts
(
	account_id varchar(255) PRIMARY KEY,
    account_password varchar(255) NOT NULL
);

DROP TABLE IF EXISTS books_accounts;
CREATE TABLE books_accounts
(
    book_id INT,
    account_id varchar(255),
    FOREIGN KEY (book_id)
        REFERENCES books(book_id),
    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
);