import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random
from sqlalchemy import create_engine, text
import pandas as pd


# Create database connection (creates 'library.db' file if it doesn't exist)
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# ─────────────────────────────────────────────
# Step 1: Create Authors table
# ─────────────────────────────────────────────
cursor.execute(
    '''
CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    country TEXT,
    birth_year INTEGER
)
'''
)

# ─────────────────────────────────────────────
# Step 2: Create Books table
# Note: FOREIGN KEY links books to their author
# ─────────────────────────────────────────────
cursor.execute(
    '''
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    isbn TEXT UNIQUE,
    publication_year INTEGER,
    genre TEXT,
    copies_available INTEGER DEFAULT 1 CHECK(copies_available >= 0),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
)
'''
)

# ─────────────────────────────────────────────
# Step 3: Create Members table
# Note: membership_type is restricted via CHECK constraint
# ─────────────────────────────────────────────
cursor.execute(
    '''
CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    join_date DATE DEFAULT CURRENT_DATE,
    membership_type TEXT CHECK(membership_type IN ('student', 'faculty', 'public'))
)
'''
)

# ─────────────────────────────────────────────
# Step 4: Create Borrowings table
# Note: Links both books and members via FOREIGN KEYs
# ─────────────────────────────────────────────
cursor.execute(
    '''
CREATE TABLE IF NOT EXISTS borrowings (
    borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    borrow_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    fine_amount REAL DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
)
'''
)

# ─────────────────────────────────────────────
# Insert sample authors (famous Egyptian authors)
# ─────────────────────────────────────────────
authors_data = [
    ('Naguib Mahfouz', 'mahfouz@literature.eg', 'Egypt', 1911),
    ('Taha Hussein', 'taha@literature.eg', 'Egypt', 1889),
    ('Nawal El Saadawi', 'nawal@literature.eg', 'Egypt', 1931),
    ('Alaa Al Aswany', 'alaa@literature.eg', 'Egypt', 1957),
    ('Ahdaf Soueif', 'ahdaf@literature.eg', 'Egypt', 1950),
]

cursor.executemany(
    '''
    INSERT INTO authors (name, email, country, birth_year)
    VALUES (?, ?, ?, ?)
''',
    authors_data,
)

# ─────────────────────────────────────────────
# Insert sample books
# author_id references the authors table above
# ─────────────────────────────────────────────
books_data = [
    ('Cairo Trilogy', 1, '978-0307947109', 1956, 'Fiction', 3),
    ('The Days', 2, '978-9774160011', 1929, 'Biography', 2),
    ('Woman at Point Zero', 3, '978-1848134171', 1975, 'Fiction', 2),
    ('The Yacoubian Building', 4, '978-0060878139', 2002, 'Fiction', 4),
    ('The Map of Love', 5, '978-0385720038', 1999, 'Fiction', 2),
    ('Palace Walk', 1, '978-0307947093', 1956, 'Fiction', 2),
    ('Children of Gebelawi', 1, '978-0894108723', 1959, 'Fiction', 1),
    ('God Dies by the Nile', 3, '978-1848134188', 1974, 'Fiction', 3),
]

cursor.executemany(
    '''
    INSERT INTO books (title, author_id, isbn, publication_year, genre, copies_available)
    VALUES (?, ?, ?, ?, ?, ?)
''',
    books_data,
)

# ─────────────────────────────────────────────
# Insert sample members
# ─────────────────────────────────────────────
members_data = [
    ('Ahmed Hassan', 'ahmed.hassan@university.edu', '0101234567', 'student'),
    ('Fatima Ali', 'fatima.ali@university.edu', '0109876543', 'student'),
    ('Mohamed Ibrahim', 'mohamed.ibrahim@university.edu', '0105555555', 'faculty'),
    ('Layla Mahmoud', 'layla.mahmoud@gmail.com', '0102222222', 'public'),
    ('Omar Khaled', 'omar.khaled@university.edu', '0103333333', 'student'),
]

cursor.executemany(
    '''
    INSERT INTO members (name, email, phone, membership_type)
    VALUES (?, ?, ?, ?)
''',
    members_data,
)

# ─────────────────────────────────────────────
# Insert sample borrowings (randomly generated)
# Fine = 2 EGP per day overdue
# ─────────────────────────────────────────────
borrowings_data = []
base_date = datetime(2024, 2, 1)

for i in range(20):
    book_id = random.randint(1, 8)
    member_id = random.randint(1, 5)
    days_ago = random.randint(1, 60)
    borrow_date = (base_date - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    due_date = (base_date - timedelta(days=days_ago) + timedelta(days=14)).strftime(
        '%Y-%m-%d'
    )

    # Some books returned (70%), some still borrowed (30%)
    if random.random() > 0.3:  # 70% returned
        return_date = (
            base_date - timedelta(days=days_ago) + timedelta(days=random.randint(1, 20))
        ).strftime('%Y-%m-%d')
        # Calculate fine if overdue
        due = datetime.strptime(due_date, '%Y-%m-%d')
        returned = datetime.strptime(return_date, '%Y-%m-%d')
        days_late = max(0, (returned - due).days)
        fine = days_late * 2.0  # 2 EGP per day
    else:
        return_date = None
        fine = 0

    borrowings_data.append(
        (book_id, member_id, borrow_date, due_date, return_date, fine)
    )

cursor.executemany(
    '''
    INSERT INTO borrowings (book_id, member_id, borrow_date, due_date, return_date, fine_amount)
    VALUES (?, ?, ?, ?, ?, ?)
''',
    borrowings_data,
)

conn.commit()
print("✅ Library database created successfully!")
print(f"  - {len(authors_data)} authors")
print(f"  - {len(books_data)} books")
print(f"  - {len(members_data)} members")
print(f"  - {len(borrowings_data)} borrowings")

output_folder = os.path.join("outputs", "part1")
os.makedirs(output_folder, exist_ok=True)

engine = create_engine('sqlite:///library.db')


with engine.connect() as conn:
    # ─── Template for Task 1.1 ────────────────────────────────────────────────────
    # Hint: Use INNER JOIN to get author name from the authors table
    query1_1 = """
    SELECT
        bk.title ,
        a.name , 
        bk.publication_year 
    FROM books bk
    INNER JOIN authors a ON bk.author_id=a.author_id
    WHERE bk.genre = 'Fiction'
    AND bk.publication_year > 1960;
    """
    df1_1 = pd.read_sql_query(query1_1, conn)
    df1_1.to_csv(os.path.join(output_folder, 'task1_1.csv'), index=False)

    # ─── Template for Task 1.2 ────────────────────────────────────────────────────
    # Hint: Use INNER JOIN with borrowings and GROUP BY member
    query1_2 = """
    SELECT
        m.name ,
        m.email,
        COUNT(*) AS total_borrowings
    FROM members m
    INNER JOIN borrowings b ON b.member_id=m.member_id
    WHERE m.membership_type='student'
    GROUP BY m.member_id , m.name, m.email
    ORDER BY total_borrowings DESC
    """
    df1_2 = pd.read_sql_query(query1_2, conn)
    df1_2.to_csv(os.path.join(output_folder, 'task1_2.csv'), index=False)

    # ─── Template for Task 1.3 ────────────────────────────────────────────────────
    # Hint: Join members with borrowings, GROUP BY membership_type, use HAVING
    query1_3 = """
    SELECT 
        m.membership_type,
        COUNT(DISTINCT m.member_id) AS total_members,
        SUM(b.fine_amount) AS total_fines,
        SUM(b.fine_amount)/COUNT(DISTINCT m.member_id) AS avg_fine_per_member
    FROM members m
    INNER JOIN borrowings b ON b.member_id=m.member_id
    GROUP BY m.membership_type
    HAVING total_fines > 0
    """
    df1_3 = pd.read_sql_query(query1_3, conn)
    df1_3.to_csv(os.path.join(output_folder, 'task1_3.csv'), index=False)

with engine.connect() as conn:
    # ─── Template for Task 2.1 ────────────────────────────────────────────────────
    query2_1 = """
    -- Hint: Use LEFT JOIN to include books with 0 borrowings
    -- Hint: Use COUNT and GROUP BY
    -- Hint: Use CASE to show 'Never Borrowed' when count = 0
    SELECT 
        bk.title,
        a.name AS author_name,
        CASE
            WHEN COUNT(b.borrow_id) = 0 THEN 'Never Borrowed'
            ELSE CAST(COUNT(DISTINCT b.borrow_id) AS TEXT)
        END AS times_borrowed,
        bk.copies_available AS currently_available
    FROM books bk
    INNER JOIN authors a ON bk.author_id=a.author_id
    LEFT JOIN borrowings b ON bk.book_id=b.book_id
    GROUP BY bk.book_id 
    """
    df2_1 = pd.read_sql_query(query2_1, conn)
    df2_1.to_csv(os.path.join(output_folder, 'task2_1.csv'), index=False)

    # ─── Template for Task 2.2 ────────────────────────────────────────────────────
    query2_2 = """
    -- Hint: Use JULIANDAY(CURRENT_DATE) - JULIANDAY(due_date) for days
    -- Hint: WHERE return_date IS NULL AND due_date < CURRENT_DATE
    -- Hint: Multiply days_overdue by 2 for estimated fine
    SELECT 
        bk.title AS book_title,
        m.name AS borrower_name,
        b.borrow_date,
        b.due_date,
        JULIANDAY(CURRENT_DATE) - JULIANDAY(b.due_date) AS days_overdue,
        CAST(JULIANDAY(CURRENT_DATE) - JULIANDAY(b.due_date)AS INTEGER) * 2 AS estimated_fine
    FROM books bk 
    INNER JOIN borrowings b ON bk.book_id=b.book_id
    INNER JOIN members m ON m.member_id=b.member_id
    WHERE b.return_date IS NULL AND b.due_date < CURRENT_DATE
    ORDER BY days_overdue DESC
    """
    df2_2 = pd.read_sql_query(query2_2, conn)
    df2_2.to_csv(os.path.join(output_folder, 'task2_2.csv'), index=False)

    # ─── Template for Task 3.1 ────────────────────────────────────────────────────
with engine.connect() as conn:
    query3_1 = """
    WITH member_borrowing_stats AS (
        -- Step 1: Calculate borrowing statistics per member
        -- Your CTE here
        -- Hint: COUNT(*), COUNT(return_date), SUM(fine_amount)
        SELECT 
            m.member_id,
            m.name AS member_name,
            m.membership_type,
            COUNT(*) AS total_borrowings,
            COUNT(return_date) AS books_returned,
            COUNT(*)-COUNT(return_date) AS books_still_borrowed,
            SUM(fine_amount) AS total_fines_paid
        FROM borrowings b
        INNER JOIN members m ON m.member_id=b.member_id
        GROUP BY m.member_id, m.name, m.membership_type
    ),
    return_performance AS (
        -- Step 2: Calculate on-time returns
        -- Your CTE here
        -- Hint: Compare return_date <= due_date for on-time flag
        SELECT 
            m.member_id,
            SUM(CASE WHEN b.return_date IS NOT NULL AND b.return_date <= b.due_date THEN 1 ELSE 0 END) AS on_time_returns
        FROM borrowings b
        INNER JOIN members m ON m.member_id=b.member_id
        GROUP BY m.member_id 
    )
    SELECT
        -- Combine the CTEs
        -- Hint: Use CASE for member_category
        -- Hint: Use ROUND() for percentage
        mbs.member_name,
        mbs.membership_type,
        mbs.total_borrowings,
        mbs.books_returned,
        mbs.books_still_borrowed,
        mbs.total_fines_paid,

        CASE 
        WHEN mbs.books_returned = 0 THEN 0
        ELSE ROUND((rp.on_time_returns * 100.0) / mbs.books_returned, 2)
        END AS on_time_return_rate,

        CASE
        WHEN mbs.total_borrowings = 0 THEN 'Inactive'
        WHEN mbs.total_borrowings BETWEEN 1 AND 5 THEN 'Active'
        ELSE 'Very Active'
        END AS member_category
        
    FROM member_borrowing_stats mbs
    LEFT JOIN return_performance rp ON mbs.member_id = rp.member_id
    ORDER BY mbs.total_borrowings DESC
    """
    df3_1 = pd.read_sql_query(query3_1, conn)
    df3_1.to_csv(os.path.join(output_folder, 'task3_1.csv'), index=False)