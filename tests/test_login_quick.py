#!/usr/bin/env python3
"""Quick login test"""

import sqlite3
import sys
from PyQt6.QtWidgets import QApplication

def test_login():
    print("Testing login system...")
    
    # Test database connection
    try:
        conn = sqlite3.connect('shop.db')
        cursor = conn.cursor()
        
        # Test credentials
        test_cases = [
            ('admin', 'admin123'),
            ('manager', 'manager123'),
            ('cashier', 'cashier123'),
            ('admin', 'wrong_password'),
            ('nonexistent', 'password')
        ]
        
        for username, password in test_cases:
            cursor.execute("SELECT username, password, role FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if user:
                stored_username, stored_password, role = user
                if stored_password == password:
                    print(f"✅ {username}/{password} - SUCCESS (role: {role})")
                else:
                    print(f"❌ {username}/{password} - WRONG PASSWORD (expected: {stored_password})")
            else:
                print(f"❌ {username}/{password} - USER NOT FOUND")
        
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    # Test without GUI first
    test_login()
    
    # Test with minimal Qt app
    print("\nTesting with Qt application...")
    app = QApplication(sys.argv)
    
    try:
        from shop_manager_pro_qt import LoginDialog
        dialog = LoginDialog()
        print("✅ LoginDialog created successfully")
        
        # Don't show dialog, just test creation
        
    except Exception as e:
        print(f"❌ Error creating LoginDialog: {e}")
    
    print("Test complete.")