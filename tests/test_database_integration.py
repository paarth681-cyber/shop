"""
Integration Tests for Database Operations
Tests database operations using in-memory SQLite for isolation and speed
"""

import unittest
import sqlite3
from decimal import Decimal
from datetime import datetime, date
import sys
import os

# Add parent directory to path 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DatabaseTestCase(unittest.TestCase):
    """Base class for database integration tests"""
    
    def setUp(self):
        """Set up in-memory database for each test"""
        self.conn = sqlite3.connect(':memory:')  # In-memory database
        self.cursor = self.conn.cursor()
        self.create_test_schema()
        self.insert_test_data()
    
    def tearDown(self):
        """Clean up database connection"""
        self.conn.close()
    
    def create_test_schema(self):
        """Create test database schema"""
        # Users table
        self.cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'cashier',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Suppliers table
        self.cursor.execute('''
            CREATE TABLE suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        self.cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                quantity INTEGER DEFAULT 0,
                cost_price REAL DEFAULT 0,
                sell_price REAL DEFAULT 0,
                supplier_id INTEGER,
                tax_category TEXT DEFAULT 'standard',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )
        ''')
        
        # Customers table
        self.cursor.execute('''
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                tier TEXT DEFAULT 'regular',
                total_purchases REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sales table
        self.cursor.execute('''
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                customer_id INTEGER,
                user_id INTEGER,
                subtotal REAL NOT NULL,
                discount_amount REAL DEFAULT 0,
                tax_amount REAL NOT NULL,
                total_amount REAL NOT NULL,
                paid INTEGER DEFAULT 1,
                note TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Sale lines table
        self.cursor.execute('''
            CREATE TABLE sale_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                line_total REAL NOT NULL,
                discount_amount REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Discount rules table
        self.cursor.execute('''
            CREATE TABLE discount_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                discount_type TEXT NOT NULL,
                value REAL NOT NULL,
                min_quantity INTEGER,
                min_amount REAL,
                customer_tier TEXT,
                valid_from DATE,
                valid_to DATE,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def insert_test_data(self):
        """Insert sample test data"""
        # Users
        users_data = [
            ('admin', 'admin123', 'admin'),
            ('manager', 'manager123', 'manager'),
            ('cashier', 'cashier123', 'cashier'),
            ('test_user', 'test123', 'cashier')
        ]
        self.cursor.executemany(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            users_data
        )
        
        # Suppliers
        suppliers_data = [
            ('Premium Tech Solutions', '555-0100', 'contact@premiumtech.com', '1000 Corporate Blvd'),
            ('Global Electronics', '555-0200', 'sales@globalelec.com', '2000 Tech Street'),
            ('Local Supplier Co', '555-0300', 'info@localsupplier.com', '123 Local Ave')
        ]
        self.cursor.executemany(
            'INSERT INTO suppliers (name, phone, email, address) VALUES (?, ?, ?, ?)',
            suppliers_data
        )
        
        # Products
        products_data = [
            ('PRO001', 'MacBook Pro 16"', 'Professional laptop', 12, 2200.00, 2799.00, 1, 'standard'),
            ('PRO002', 'iPhone 15 Pro', 'Latest smartphone', 25, 800.00, 1199.00, 1, 'standard'),
            ('PRO003', 'iPad Air', 'Tablet device', 18, 450.00, 699.00, 1, 'standard'),
            ('PRO004', 'AirPods Pro', 'Wireless earbuds', 35, 180.00, 279.00, 1, 'standard'),
            ('FOOD001', 'Organic Apple', 'Fresh organic apple', 100, 1.50, 2.99, 3, 'food'),
            ('MED001', 'Vitamin D3', 'Health supplement', 50, 15.00, 29.99, 3, 'medical')
        ]
        self.cursor.executemany(
            'INSERT INTO products (sku, name, description, quantity, cost_price, sell_price, supplier_id, tax_category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            products_data
        )
        
        # Customers
        customers_data = [
            ('Walk-in Customer', '', '', '', 'regular', 0),
            ('Corporate Client A', '555-2001', 'clientA@corp.com', '500 Business St', 'premium', 5000.00),
            ('VIP Customer', '555-2002', 'vip@customer.com', '750 VIP Ave', 'vip', 15000.00),
            ('John Doe', '555-1234', 'john@email.com', '123 Main St', 'regular', 250.00)
        ]
        self.cursor.executemany(
            'INSERT INTO customers (name, phone, email, address, tier, total_purchases) VALUES (?, ?, ?, ?, ?, ?)',
            customers_data
        )
        
        # Discount rules
        discount_rules_data = [
            ('10% off orders over $100', 'percentage', 10.0, None, 100.0, None, None, None, 1),
            ('$50 off bulk orders', 'fixed_amount', 50.0, 10, None, None, None, None, 1),
            ('VIP customer discount', 'customer_tier', 15.0, None, None, 'vip', None, None, 1),
            ('Premium tier discount', 'customer_tier', 5.0, None, None, 'premium', None, None, 1)
        ]
        self.cursor.executemany(
            'INSERT INTO discount_rules (name, discount_type, value, min_quantity, min_amount, customer_tier, valid_from, valid_to, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            discount_rules_data
        )
        
        self.conn.commit()

class TestUserOperations(DatabaseTestCase):
    """Test user-related database operations"""
    
    def test_create_user(self):
        """Test creating a new user"""
        self.cursor.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
            ('new_user', 'password123', 'manager')
        )
        self.conn.commit()
        
        # Verify user was created
        self.cursor.execute('SELECT username, role FROM users WHERE username = ?', ('new_user',))
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'new_user')
        self.assertEqual(result[1], 'manager')
    
    def test_authenticate_user(self):
        """Test user authentication"""
        # Valid credentials
        self.cursor.execute(
            'SELECT id, username, role FROM users WHERE username = ? AND password = ?',
            ('admin', 'admin123')
        )
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[1], 'admin')
        self.assertEqual(result[2], 'admin')
        
        # Invalid credentials
        self.cursor.execute(
            'SELECT id FROM users WHERE username = ? AND password = ?',
            ('admin', 'wrong_password')
        )
        result = self.cursor.fetchone()
        
        self.assertIsNone(result)
    
    def test_update_user_password(self):
        """Test updating user password"""
        self.cursor.execute(
            'UPDATE users SET password = ? WHERE username = ?',
            ('new_password', 'test_user')
        )
        self.conn.commit()
        
        # Verify password was updated
        self.cursor.execute(
            'SELECT id FROM users WHERE username = ? AND password = ?',
            ('test_user', 'new_password')
        )
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result)
    
    def test_delete_user(self):
        """Test deleting a user"""
        # First verify user exists
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('test_user',))
        count_before = self.cursor.fetchone()[0]
        self.assertEqual(count_before, 1)
        
        # Delete user
        self.cursor.execute('DELETE FROM users WHERE username = ?', ('test_user',))
        self.conn.commit()
        
        # Verify user was deleted
        self.cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('test_user',))
        count_after = self.cursor.fetchone()[0]
        self.assertEqual(count_after, 0)

class TestProductOperations(DatabaseTestCase):
    """Test product-related database operations"""
    
    def test_create_product(self):
        """Test creating a new product"""
        product_data = ('TEST001', 'Test Product', 'Test Description', 10, 50.00, 75.00, 1, 'standard')
        self.cursor.execute(
            'INSERT INTO products (sku, name, description, quantity, cost_price, sell_price, supplier_id, tax_category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            product_data
        )
        self.conn.commit()
        
        # Verify product was created
        self.cursor.execute('SELECT sku, name, quantity FROM products WHERE sku = ?', ('TEST001',))
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'TEST001')
        self.assertEqual(result[1], 'Test Product')
        self.assertEqual(result[2], 10)
    
    def test_update_product_inventory(self):
        """Test updating product inventory"""
        # Reduce inventory (sale)
        self.cursor.execute(
            'UPDATE products SET quantity = quantity - ? WHERE sku = ?',
            (5, 'PRO001')
        )
        self.conn.commit()
        
        # Verify inventory was updated
        self.cursor.execute('SELECT quantity FROM products WHERE sku = ?', ('PRO001',))
        quantity = self.cursor.fetchone()[0]
        self.assertEqual(quantity, 7)  # 12 - 5 = 7
    
    def test_search_products(self):
        """Test searching products"""
        # Search by name
        self.cursor.execute(
            'SELECT sku, name FROM products WHERE LOWER(name) LIKE ?',
            ('%macbook%',)
        )
        results = self.cursor.fetchall()
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 'PRO001')
        
        # Search by category
        self.cursor.execute(
            'SELECT COUNT(*) FROM products WHERE tax_category = ?',
            ('standard',)
        )
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 4)  # 4 standard tax category products
    
    def test_low_stock_products(self):
        """Test finding low stock products"""
        # Update a product to low stock
        self.cursor.execute('UPDATE products SET quantity = 3 WHERE sku = ?', ('PRO001',))
        self.conn.commit()
        
        # Find low stock products (less than 10)
        self.cursor.execute(
            'SELECT sku, name, quantity FROM products WHERE quantity < 10 AND quantity > 0 ORDER BY quantity ASC'
        )
        results = self.cursor.fetchall()
        
        self.assertGreater(len(results), 0)
        # PRO001 should be in the results
        low_stock_skus = [result[0] for result in results]
        self.assertIn('PRO001', low_stock_skus)

class TestCustomerOperations(DatabaseTestCase):
    """Test customer-related database operations"""
    
    def test_create_customer(self):
        """Test creating a new customer"""
        customer_data = ('Jane Smith', '555-9999', 'jane@email.com', '456 Oak St', 'premium', 0)
        self.cursor.execute(
            'INSERT INTO customers (name, phone, email, address, tier, total_purchases) VALUES (?, ?, ?, ?, ?, ?)',
            customer_data
        )
        self.conn.commit()
        
        # Verify customer was created
        self.cursor.execute('SELECT name, tier FROM customers WHERE email = ?', ('jane@email.com',))
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'Jane Smith')
        self.assertEqual(result[1], 'premium')
    
    def test_update_customer_purchases(self):
        """Test updating customer total purchases"""
        # Update total purchases
        self.cursor.execute(
            'UPDATE customers SET total_purchases = total_purchases + ? WHERE id = ?',
            (500.00, 4)  # John Doe
        )
        self.conn.commit()
        
        # Verify update
        self.cursor.execute('SELECT total_purchases FROM customers WHERE id = ?', (4,))
        total = self.cursor.fetchone()[0]
        self.assertEqual(total, 750.00)  # 250.00 + 500.00
    
    def test_customer_tier_upgrade(self):
        """Test customer tier upgrade logic"""
        # Simulate a customer reaching VIP status
        self.cursor.execute(
            'UPDATE customers SET tier = ?, total_purchases = ? WHERE id = ?',
            ('vip', 10000.00, 4)
        )
        self.conn.commit()
        
        # Verify tier upgrade
        self.cursor.execute('SELECT tier, total_purchases FROM customers WHERE id = ?', (4,))
        result = self.cursor.fetchone()
        
        self.assertEqual(result[0], 'vip')
        self.assertEqual(result[1], 10000.00)

class TestSalesOperations(DatabaseTestCase):
    """Test sales-related database operations"""
    
    def test_create_sale(self):
        """Test creating a complete sale transaction"""
        # Create sale
        sale_data = (
            datetime.now().isoformat(),
            2,  # customer_id (Corporate Client A)
            1,  # user_id (admin)
            1199.00,  # subtotal
            0,  # discount_amount
            101.92,  # tax_amount (1199 * 0.085)
            1300.92,  # total_amount
            1,  # paid
            'Test sale'
        )
        
        self.cursor.execute(
            'INSERT INTO sales (date, customer_id, user_id, subtotal, discount_amount, tax_amount, total_amount, paid, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            sale_data
        )
        sale_id = self.cursor.lastrowid
        self.conn.commit()
        
        # Add sale line
        line_data = (
            sale_id,
            2,  # iPhone 15 Pro
            1,  # quantity
            1199.00,  # unit_price
            1199.00,  # line_total
            0,  # discount_amount
            101.92  # tax_amount
        )
        
        self.cursor.execute(
            'INSERT INTO sale_lines (sale_id, product_id, qty, unit_price, line_total, discount_amount, tax_amount) VALUES (?, ?, ?, ?, ?, ?, ?)',
            line_data
        )
        self.conn.commit()
        
        # Update product inventory
        self.cursor.execute(
            'UPDATE products SET quantity = quantity - ? WHERE id = ?',
            (1, 2)  # Reduce iPhone inventory by 1
        )
        self.conn.commit()
        
        # Verify sale was created
        self.cursor.execute('SELECT total_amount, customer_id FROM sales WHERE id = ?', (sale_id,))
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 1300.92)
        self.assertEqual(result[1], 2)
        
        # Verify inventory was updated
        self.cursor.execute('SELECT quantity FROM products WHERE id = ?', (2,))
        quantity = self.cursor.fetchone()[0]
        self.assertEqual(quantity, 24)  # 25 - 1 = 24
    
    def test_sale_with_discount(self):
        """Test creating a sale with discount applied"""
        sale_data = (
            datetime.now().isoformat(),
            3,  # VIP customer
            1,  # admin user
            2799.00,  # subtotal (MacBook Pro)
            279.90,  # discount_amount (10% VIP discount)
            214.13,  # tax_amount ((2799 - 279.90) * 0.085)
            2733.23,  # total_amount
            1,  # paid
            'VIP sale with discount'
        )
        
        self.cursor.execute(
            'INSERT INTO sales (date, customer_id, user_id, subtotal, discount_amount, tax_amount, total_amount, paid, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            sale_data
        )
        sale_id = self.cursor.lastrowid
        self.conn.commit()
        
        # Verify discount was applied
        self.cursor.execute('SELECT discount_amount, total_amount FROM sales WHERE id = ?', (sale_id,))
        result = self.cursor.fetchone()
        
        self.assertEqual(result[0], 279.90)
        self.assertEqual(result[1], 2733.23)
    
    def test_sales_reporting(self):
        """Test sales reporting queries"""
        # Create multiple sales for testing
        sales_data = [
            (datetime.now().isoformat(), 2, 1, 100.00, 0, 8.50, 108.50, 1, 'Sale 1'),
            (datetime.now().isoformat(), 3, 1, 200.00, 20.00, 15.30, 195.30, 1, 'Sale 2'),
            (datetime.now().isoformat(), 4, 2, 50.00, 0, 4.25, 54.25, 1, 'Sale 3')
        ]
        
        for sale in sales_data:
            self.cursor.execute(
                'INSERT INTO sales (date, customer_id, user_id, subtotal, discount_amount, tax_amount, total_amount, paid, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                sale
            )
        self.conn.commit()
        
        # Test total sales amount
        self.cursor.execute('SELECT SUM(total_amount) FROM sales')
        total_sales = self.cursor.fetchone()[0]
        self.assertGreater(total_sales, 350)  # Should be 358.05 (108.50 + 195.30 + 54.25)
        
        # Test sales count by user
        self.cursor.execute('SELECT user_id, COUNT(*) FROM sales GROUP BY user_id')
        results = self.cursor.fetchall()
        
        user_sales = {user_id: count for user_id, count in results}
        self.assertEqual(user_sales[1], 2)  # Admin made 2 sales
        self.assertEqual(user_sales[2], 1)  # Manager made 1 sale
        
        # Test average sale amount
        self.cursor.execute('SELECT AVG(total_amount) FROM sales')
        avg_sale = self.cursor.fetchone()[0]
        self.assertGreater(avg_sale, 100)  # Should be around 119.35

class TestInventoryOperations(DatabaseTestCase):
    """Test inventory-related database operations"""
    
    def test_inventory_valuation(self):
        """Test inventory valuation calculations"""
        # Calculate total inventory value at cost
        self.cursor.execute('SELECT SUM(quantity * cost_price) FROM products')
        cost_value = self.cursor.fetchone()[0]
        
        # Calculate total inventory value at retail
        self.cursor.execute('SELECT SUM(quantity * sell_price) FROM products')
        retail_value = self.cursor.fetchone()[0]
        
        self.assertGreater(cost_value, 0)
        self.assertGreater(retail_value, cost_value)  # Retail should be higher than cost
    
    def test_product_movement_tracking(self):
        """Test tracking product movements"""
        # Create a product movement log entry (simplified)
        original_qty = 12  # MacBook Pro original quantity
        
        # Simulate sale reducing inventory
        self.cursor.execute(
            'UPDATE products SET quantity = quantity - ? WHERE id = ?',
            (2, 1)  # Sell 2 MacBook Pros
        )
        
        # Verify movement
        self.cursor.execute('SELECT quantity FROM products WHERE id = ?', (1,))
        new_qty = self.cursor.fetchone()[0]
        
        self.assertEqual(new_qty, original_qty - 2)
    
    def test_reorder_point_calculation(self):
        """Test reorder point logic"""
        # Set low stock threshold and test
        low_stock_threshold = 10
        
        # Find products that need reordering
        self.cursor.execute(
            'SELECT id, sku, name, quantity FROM products WHERE quantity <= ?',
            (low_stock_threshold,)
        )
        
        results = self.cursor.fetchall()
        
        # Should initially have no products below threshold
        # (all test products have more than 10 units)
        self.assertEqual(len(results), 0)
        
        # Reduce stock to trigger reorder alert
        self.cursor.execute('UPDATE products SET quantity = 5 WHERE id = 1')
        
        # Test again
        self.cursor.execute(
            'SELECT id, sku, name, quantity FROM products WHERE quantity <= ?',
            (low_stock_threshold,)
        )
        
        results = self.cursor.fetchall()
        self.assertEqual(len(results), 1)  # MacBook Pro should now appear

class TestReportingOperations(DatabaseTestCase):
    """Test reporting and analytics database operations"""
    
    def setUp(self):
        """Set up with more test data for reporting"""
        super().setUp()
        
        # Add more sales data for better reporting tests
        sales_data = [
            ('2024-10-01 10:00:00', 2, 1, 500.00, 50.00, 38.25, 488.25, 1, 'October sale 1'),
            ('2024-10-15 14:30:00', 3, 1, 1200.00, 120.00, 91.80, 1171.80, 1, 'October sale 2'),
            ('2024-10-25 16:45:00', 4, 2, 300.00, 0, 25.50, 325.50, 1, 'October sale 3'),
            ('2024-09-10 09:15:00', 2, 1, 750.00, 0, 63.75, 813.75, 1, 'September sale 1'),
            ('2024-09-20 11:20:00', 3, 1, 450.00, 45.00, 34.43, 439.43, 1, 'September sale 2')
        ]
        
        for sale in sales_data:
            self.cursor.execute(
                'INSERT INTO sales (date, customer_id, user_id, subtotal, discount_amount, tax_amount, total_amount, paid, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                sale
            )
        self.conn.commit()
    
    def test_monthly_sales_report(self):
        """Test monthly sales reporting"""
        # Get October 2024 sales
        self.cursor.execute("""
            SELECT 
                COUNT(*) as sale_count,
                SUM(subtotal) as total_subtotal,
                SUM(discount_amount) as total_discounts,
                SUM(total_amount) as total_sales
            FROM sales 
            WHERE date LIKE '2024-10-%'
        """)
        
        result = self.cursor.fetchone()
        
        self.assertEqual(result[0], 3)  # 3 sales in October
        self.assertEqual(result[1], 2000.00)  # Total subtotal
        self.assertEqual(result[2], 170.00)  # Total discounts
        
    def test_customer_analytics(self):
        """Test customer analytics queries"""
        # Top customers by purchase amount
        self.cursor.execute("""
            SELECT 
                c.name,
                c.tier,
                COUNT(s.id) as sale_count,
                SUM(s.total_amount) as total_spent
            FROM customers c
            LEFT JOIN sales s ON c.id = s.customer_id
            GROUP BY c.id
            ORDER BY total_spent DESC
        """)
        
        results = self.cursor.fetchall()
        
        # Should have data for all customers
        self.assertGreater(len(results), 0)
        
        # Results should be ordered by total spent (descending)
        for i in range(len(results) - 1):
            current_spent = results[i][3] or 0
            next_spent = results[i + 1][3] or 0
            self.assertGreaterEqual(current_spent, next_spent)
    
    def test_product_performance_report(self):
        """Test product performance analytics"""
        # Create sale lines for testing
        sale_lines_data = [
            (1, 1, 2, 2799.00, 5598.00, 0, 475.83),  # 2 MacBook Pros
            (2, 2, 1, 1199.00, 1199.00, 0, 101.92),  # 1 iPhone
            (3, 3, 3, 699.00, 2097.00, 0, 178.25),   # 3 iPads
            (4, 4, 5, 279.00, 1395.00, 0, 118.58),   # 5 AirPods
        ]
        
        for line in sale_lines_data:
            self.cursor.execute(
                'INSERT INTO sale_lines (sale_id, product_id, qty, unit_price, line_total, discount_amount, tax_amount) VALUES (?, ?, ?, ?, ?, ?, ?)',
                line
            )
        self.conn.commit()
        
        # Product performance query
        self.cursor.execute("""
            SELECT 
                p.name,
                p.sku,
                SUM(sl.qty) as units_sold,
                SUM(sl.line_total) as revenue,
                AVG(sl.unit_price) as avg_price
            FROM products p
            JOIN sale_lines sl ON p.id = sl.product_id
            GROUP BY p.id
            ORDER BY revenue DESC
        """)
        
        results = self.cursor.fetchall()
        
        # Should have results for products with sales
        self.assertGreater(len(results), 0)
        
        # MacBook Pro should be the top revenue generator
        top_product = results[0]
        self.assertEqual(top_product[1], 'PRO001')  # SKU
        self.assertEqual(top_product[2], 2)  # Units sold
    
    def test_tax_reporting(self):
        """Test tax reporting calculations"""
        # Total tax collected
        self.cursor.execute('SELECT SUM(tax_amount) FROM sales')
        total_tax = self.cursor.fetchone()[0]
        
        self.assertGreater(total_tax, 0)
        
        # Tax by category (would need to join with products for real implementation)
        # This is a simplified version
        self.cursor.execute("""
            SELECT 
                p.tax_category,
                SUM(sl.tax_amount) as category_tax
            FROM sale_lines sl
            JOIN products p ON sl.product_id = p.id
            GROUP BY p.tax_category
        """)
        
        results = self.cursor.fetchall()
        
        # Should have tax data by category
        tax_categories = [result[0] for result in results]
        self.assertIn('standard', tax_categories)

class TestDataIntegrity(DatabaseTestCase):
    """Test data integrity and constraints"""
    
    def test_foreign_key_constraints(self):
        """Test foreign key constraint enforcement"""
        # This would only work if foreign key constraints are enabled
        # For SQLite, we need to enable them explicitly
        self.cursor.execute('PRAGMA foreign_keys = ON')
        
        # Try to create a sale with non-existent customer
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute(
                'INSERT INTO sales (customer_id, user_id, subtotal, tax_amount, total_amount) VALUES (?, ?, ?, ?, ?)',
                (999, 1, 100.00, 8.50, 108.50)  # customer_id 999 doesn't exist
            )
    
    def test_unique_constraints(self):
        """Test unique constraint enforcement"""
        # Try to create duplicate SKU
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute(
                'INSERT INTO products (sku, name, quantity, cost_price, sell_price) VALUES (?, ?, ?, ?, ?)',
                ('PRO001', 'Duplicate Product', 5, 100.00, 150.00)
            )
        
        # Try to create duplicate username
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute(
                'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                ('admin', 'password', 'user')
            )
    
    def test_data_consistency(self):
        """Test data consistency across transactions"""
        # Start a transaction
        self.cursor.execute('BEGIN')
        
        try:
            # Create a sale
            self.cursor.execute(
                'INSERT INTO sales (customer_id, user_id, subtotal, tax_amount, total_amount) VALUES (?, ?, ?, ?, ?)',
                (2, 1, 100.00, 8.50, 108.50)
            )
            sale_id = self.cursor.lastrowid
            
            # Add sale line
            self.cursor.execute(
                'INSERT INTO sale_lines (sale_id, product_id, qty, unit_price, line_total) VALUES (?, ?, ?, ?, ?)',
                (sale_id, 1, 1, 100.00, 100.00)
            )
            
            # Update inventory
            self.cursor.execute(
                'UPDATE products SET quantity = quantity - ? WHERE id = ?',
                (1, 1)
            )
            
            # Commit transaction
            self.conn.commit()
            
            # Verify all changes were made
            self.cursor.execute('SELECT COUNT(*) FROM sales WHERE id = ?', (sale_id,))
            sale_count = self.cursor.fetchone()[0]
            self.assertEqual(sale_count, 1)
            
            self.cursor.execute('SELECT COUNT(*) FROM sale_lines WHERE sale_id = ?', (sale_id,))
            line_count = self.cursor.fetchone()[0]
            self.assertEqual(line_count, 1)
            
        except Exception:
            # Rollback on error
            self.conn.rollback()
            raise

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestUserOperations,
        TestProductOperations,
        TestCustomerOperations,
        TestSalesOperations,
        TestInventoryOperations,
        TestReportingOperations,
        TestDataIntegrity
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Database Integration Test Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")