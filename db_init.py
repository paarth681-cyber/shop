import sqlite3
import os

def init_db(path='shop.db'):
    """
    Initializes the database with professional schema.
    Adds cost_price, selling_price, profit, is_paid for credit tracking.
    """
    db_dir = os.path.dirname(path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    
    cur.execute("PRAGMA foreign_keys = ON")

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        sku TEXT UNIQUE,
        quantity INTEGER NOT NULL DEFAULT 0,
        cost_price REAL NOT NULL DEFAULT 0.0,
        selling_price REAL NOT NULL DEFAULT 0.0,
        threshold INTEGER NOT NULL DEFAULT 5
    );

    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        customer_name TEXT,
        notes TEXT,
        total_amount REAL NOT NULL,
        profit REAL NOT NULL DEFAULT 0.0,
        is_paid INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        cost_price REAL NOT NULL DEFAULT 0.0,
        FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE SET NULL
    );
    
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        status TEXT NOT NULL CHECK(status IN ('Pending', 'Completed', 'Cancelled')),
        date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        notes TEXT
    );
    """)

    try:
        cur.execute("ALTER TABLE products ADD COLUMN cost_price REAL NOT NULL DEFAULT 0.0;")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE products ADD COLUMN selling_price REAL NOT NULL DEFAULT 0.0;")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE products RENAME COLUMN price TO selling_price;")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE sales ADD COLUMN profit REAL NOT NULL DEFAULT 0.0;")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE sales ADD COLUMN is_paid INTEGER NOT NULL DEFAULT 1;")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE sale_items ADD COLUMN cost_price REAL NOT NULL DEFAULT 0.0;")
    except sqlite3.OperationalError:
        pass

    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        products = [
            ('Dairy Milk', 'DM100', 50, 40.0, 50.0, 10),
            ('Parle-G Biscuits', 'PG101', 100, 8.0, 10.0, 20),
            ('Detergent Powder 1kg', 'DP200', 30, 90.0, 120.0, 10),
            ('Basmati Rice 10kg', 'RB10', 20, 550.0, 650.0, 5),
            ('Refined Sugar 1kg', 'SUG1', 80, 35.0, 42.0, 20)
        ]
        cur.executemany("INSERT INTO products (name, sku, quantity, cost_price, selling_price, threshold) VALUES (?, ?, ?, ?, ?, ?)", products)
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    db_path = os.path.join(os.path.dirname(__file__), 'shop.db')
    print(f"Initializing database at: {db_path}")
    init_db(db_path)
    print("Database initialization complete.")
