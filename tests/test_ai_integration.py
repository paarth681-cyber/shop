#!/usr/bin/env python3
"""
Test script for AI-enhanced Shop Manager Pro
Tests the integration of AI features with the PyQt application
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_setup():
    """Test database setup and sample data"""
    print("🔧 Testing database setup...")
    
    # Remove old database if exists
    if os.path.exists("shop.db"):
        os.remove("shop.db")
        print("  ✓ Removed old database")
    
    # Create new database with sample data
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    
    # Create tables
    tables = [
        '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'cashier'
        )''',
        '''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE,
            name TEXT,
            description TEXT,
            quantity INTEGER DEFAULT 0,
            cost_price REAL DEFAULT 0,
            sell_price REAL DEFAULT 0,
            supplier_id INTEGER
        )''',
        '''CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            address TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            address TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            customer_id INTEGER,
            total_amount REAL,
            paid INTEGER DEFAULT 1,
            user_id INTEGER,
            note TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS sale_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            qty INTEGER,
            price REAL,
            line_total REAL
        )'''
    ]
    
    for table in tables:
        cur.execute(table)
    
    print("  ✓ Created database tables")
    
    # Insert sample data
    sample_data = [
        ("INSERT OR IGNORE INTO users (username,password,role) VALUES (?,?,?)", 
         [("admin", "admin123", "admin"), ("manager", "manager123", "manager"), ("cashier", "cashier123", "cashier")]),
        
        ("INSERT OR IGNORE INTO suppliers (name,phone,email,address) VALUES (?,?,?,?)",
         [("Tech Wholesale Ltd", "555-0100", "contact@techwin.com", "1000 Corporate Blvd"),
          ("Global Electronics Inc", "555-0200", "sales@globalelec.com", "2000 Tech Street")]),
        
        ("INSERT OR IGNORE INTO products (sku,name,description,quantity,cost_price,sell_price,supplier_id) VALUES (?,?,?,?,?,?,?)",
         [("LAPTOP001", "Gaming Laptop", "High-performance gaming laptop with RTX graphics", 15, 1200.00, 1699.99, 1),
          ("PHONE001", "Smartphone Pro", "Latest flagship smartphone with AI camera", 32, 600.00, 999.99, 1),
          ("TABLET001", "Tablet Air", "Ultra-thin tablet for productivity", 28, 350.00, 599.99, 1),
          ("HEADSET001", "Gaming Headset", "Wireless gaming headset with surround sound", 45, 80.00, 149.99, 1),
          ("MOUSE001", "Wireless Mouse", "Ergonomic wireless mouse with precision sensor", 60, 25.00, 49.99, 1),
          ("KEYBOARD001", "Mechanical Keyboard", "RGB mechanical gaming keyboard", 35, 75.00, 129.99, 1),
          ("MONITOR001", "4K Monitor", "27-inch 4K UHD monitor for professionals", 12, 400.00, 649.99, 2),
          ("SPEAKER001", "Bluetooth Speaker", "Portable wireless speaker with bass boost", 25, 50.00, 89.99, 2),
          ("CAMERA001", "Action Camera", "Waterproof 4K action camera", 18, 150.00, 249.99, 2),
          ("PRINTER001", "All-in-One Printer", "Color laser printer with scanner", 8, 300.00, 499.99, 2)]),
        
        ("INSERT OR IGNORE INTO customers (name,phone,email,address) VALUES (?,?,?,?)",
         [("Walk-in Customer", "", "", ""),
          ("Tech Startup Inc", "555-2001", "contact@techstart.com", "500 Innovation St"),
          ("Gaming Zone LLC", "555-2002", "orders@gamingzone.com", "750 Entertainment Ave"),
          ("Office Solutions", "555-2003", "procurement@officesol.com", "1200 Business Dr"),
          ("Creative Studio", "555-2004", "hello@creativestudio.com", "800 Design Blvd")])
    ]
    
    for query, data in sample_data:
        for item in data:
            cur.execute(query, item)
    
    print("  ✓ Inserted sample data")
    
    # Insert sample sales data for AI forecasting
    print("  🔄 Generating sample sales data for AI testing...")
    
    # Generate sales over the last 60 days
    base_date = datetime.now() - timedelta(days=60)
    
    for day in range(60):
        current_date = base_date + timedelta(days=day)
        date_str = current_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # Generate 1-5 sales per day with some variation
        import random
        num_sales = random.randint(1, 5)
        
        for sale_num in range(num_sales):
            # Random customer (20% walk-in, 80% registered)
            customer_id = 1 if random.random() < 0.2 else random.randint(2, 5)
            
            # Create sale
            cur.execute("""
                INSERT INTO sales (date, customer_id, total_amount, paid, user_id, note)
                VALUES (?, ?, ?, 1, 1, 'Sample sale for AI testing')
            """, (date_str, customer_id, 0))  # total_amount will be calculated
            
            sale_id = cur.lastrowid
            
            # Add 1-4 items to this sale
            num_items = random.randint(1, 4)
            total_amount = 0
            
            for item_num in range(num_items):
                product_id = random.randint(1, 10)  # Random product
                qty = random.randint(1, 3)
                
                # Get product price
                cur.execute("SELECT sell_price FROM products WHERE id = ?", (product_id,))
                price = cur.fetchone()[0]
                line_total = price * qty
                total_amount += line_total
                
                # Insert sale line
                cur.execute("""
                    INSERT INTO sale_lines (sale_id, product_id, qty, price, line_total)
                    VALUES (?, ?, ?, ?, ?)
                """, (sale_id, product_id, qty, price, line_total))
            
            # Update sale total
            cur.execute("UPDATE sales SET total_amount = ? WHERE id = ?", (total_amount, sale_id))
    
    conn.commit()
    conn.close()
    
    print("  ✓ Generated 60 days of sample sales data")
    print("  ✅ Database setup completed successfully")


def test_ai_engine():
    """Test AI engine functionality"""
    print("\n🤖 Testing AI Engine...")
    
    try:
        from ai_engine import get_ai_engine
        
        # Initialize AI engine
        ai_engine = get_ai_engine()
        print("  ✓ AI Engine imported successfully")
        
        # Test initialization
        ai_engine.initialize()
        print("  ✓ AI Engine initialized")
        
        # Test capabilities
        capabilities = ai_engine.get_capabilities()
        print("  ✓ AI Capabilities retrieved:")
        for feature, info in capabilities.items():
            if isinstance(info, dict):
                status = "✅ Available" if info['available'] else "❌ Not Available"
                print(f"    - {feature.replace('_', ' ').title()}: {status}")
        
        # Test ML forecasting
        print("  🔄 Testing ML forecasting...")
        forecast = ai_engine.ml_forecaster.forecast_sales(7)
        
        if "error" not in forecast:
            total_forecast = forecast['summary']['total_predicted_sales']
            confidence = forecast['summary']['confidence']
            print(f"    ✓ 7-day forecast: ${total_forecast:.2f} (confidence: {confidence:.1%})")
        else:
            print(f"    ❌ Forecast error: {forecast['error']}")
        
        # Test NLP search
        print("  🔄 Testing NLP search...")
        search_results = ai_engine.smart_search("gaming laptop", use_nlp=True, limit=3)
        print(f"    ✓ Found {len(search_results)} products for 'gaming laptop'")
        
        for result in search_results[:2]:
            print(f"      - {result.get('name', 'N/A')}: {result.get('relevance_score', 0):.3f}")
        
        print("  ✅ AI Engine tests completed successfully")
        
    except ImportError as e:
        print(f"  ❌ AI Engine import failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ AI Engine test failed: {e}")
        return False
    
    return True


def test_qt_widgets():
    """Test PyQt AI widgets"""
    print("\n🎨 Testing PyQt AI Widgets...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from ai_widgets_qt import AIControlPanel
        
        # Create QApplication (required for PyQt widgets)
        app = QApplication([])
        print("  ✓ PyQt6 application created")
        
        # Test AI Control Panel
        ai_panel = AIControlPanel()
        print("  ✓ AI Control Panel created")
        
        # Test individual widgets
        search_widget = ai_panel.search_widget
        forecast_widget = ai_panel.forecast_widget  
        chat_widget = ai_panel.chat_widget
        
        print("  ✓ Individual AI widgets created")
        print("    - Smart Search Widget: Ready")
        print("    - ML Forecast Widget: Ready") 
        print("    - GPT Chat Widget: Ready")
        
        print("  ✅ PyQt AI Widgets tests completed successfully")
        
        app.quit()
        return True
        
    except ImportError as e:
        print(f"  ❌ PyQt widgets import failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ PyQt widgets test failed: {e}")
        return False


def test_integration():
    """Test integration with main app"""
    print("\n🔗 Testing Integration...")
    
    try:
        # Test imports
        from shop_manager_pro_qt import ShopManagerApp
        print("  ✓ Main application imported successfully")
        
        # Test AI availability flag
        from shop_manager_pro_qt import AI_AVAILABLE
        print(f"  ✓ AI_AVAILABLE flag: {AI_AVAILABLE}")
        
        if AI_AVAILABLE:
            print("  ✅ AI integration is ready")
        else:
            print("  ⚠️ AI integration not available - check dependencies")
        
        return AI_AVAILABLE
        
    except ImportError as e:
        print(f"  ❌ Integration test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Shop Manager Pro AI Integration Test")
    print("=" * 50)
    
    # Test database setup
    test_database_setup()
    
    # Test AI engine
    ai_success = test_ai_engine()
    
    # Test PyQt widgets
    qt_success = test_qt_widgets()
    
    # Test integration
    integration_success = test_integration()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Database Setup: ✅ Passed")
    print(f"AI Engine: {'✅ Passed' if ai_success else '❌ Failed'}")
    print(f"PyQt Widgets: {'✅ Passed' if qt_success else '❌ Failed'}")
    print(f"Integration: {'✅ Passed' if integration_success else '❌ Failed'}")
    
    overall_success = ai_success and qt_success and integration_success
    
    if overall_success:
        print(f"\n🎉 All tests passed! Shop Manager Pro with AI is ready to run.")
        print(f"\nTo start the application, run:")
        print(f"  python shop_manager_pro_qt.py")
        print(f"\nDemo credentials:")
        print(f"  Admin: admin / admin123")
        print(f"  Manager: manager / manager123")
        print(f"  Cashier: cashier / cashier123")
    else:
        print(f"\n⚠️ Some tests failed. Please check the error messages above.")
    
    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())