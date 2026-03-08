"""
Shop Manager Pro - Professional PyQt6 Edition
Modern desktop application with blue/red/yellow/white theme
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from design_system import DesignSystem, StyleSheets, IconSystem, SHORTCUTS
from logger_config import (
    init_logging, get_logger, log_info, log_error, 
    log_user_action, log_db_operation
)
from telemetry_dialog import show_telemetry_dialog
from tax_config_dialog import TaxConfigDialog
from discount_management_dialog import DiscountManagementDialog
from demo_mode import should_show_demo, show_demo_dialog

# AI components
try:
    from ai_widgets_qt import AIControlPanel
    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    log_error(f"AI features not available: {e}")

class LoginDialog(QDialog):
    """Professional login dialog with modern styling"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shop Manager Pro - Sign In")
        self.setFixedSize(450, 600)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        
        self.current_user = None
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        """Setup the login UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section with gradient-like background
        header = QFrame()
        header.setObjectName("loginHeader")
        header.setFixedHeight(180)
        header_layout = QVBoxLayout(header)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo and title
        logo_label = QLabel("SMP")
        logo_label.setObjectName("logoLabel")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo_label)
        
        title_label = QLabel("Shop Manager Pro")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Enterprise Edition")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        main_layout.addWidget(header)
        
        # Form section
        form_widget = QWidget()
        form_widget.setObjectName("formSection")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(DesignSystem.get_spacing('lg'))
        
        # Welcome message
        welcome_label = QLabel("Welcome Back")
        welcome_label.setObjectName("welcomeLabel")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(welcome_label)
        
        subtitle = QLabel("Please sign in to your account")
        subtitle.setObjectName("welcomeSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(subtitle)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setObjectName("fieldLabel")
        form_layout.addWidget(username_label)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        self.username_edit.setObjectName("loginField")
        form_layout.addWidget(self.username_edit)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")
        form_layout.addWidget(password_label)
        
        password_container = QHBoxLayout()
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setObjectName("loginField")
        password_container.addWidget(self.password_edit)
        
        # Show/Hide password button
        self.show_password_btn = QPushButton("👁️")
        self.show_password_btn.setObjectName("showPasswordButton")
        self.show_password_btn.setFixedSize(40, 40)
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_container.addWidget(self.show_password_btn)
        
        form_layout.addLayout(password_container)
        
        # Buttons layout
        buttons_layout = QVBoxLayout()
        
        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setObjectName("primaryButton")
        self.login_button.clicked.connect(self.handle_login)
        buttons_layout.addWidget(self.login_button)
        
        # Change password button
        change_password_btn = QPushButton("Change Password")
        change_password_btn.setObjectName("secondaryButton")
        change_password_btn.clicked.connect(self.show_change_password_dialog)
        buttons_layout.addWidget(change_password_btn)
        
        form_layout.addLayout(buttons_layout)
        
        # Demo accounts info
        demo_frame = QFrame()
        demo_frame.setObjectName("demoFrame")
        demo_layout = QVBoxLayout(demo_frame)
        demo_layout.setContentsMargins(20, 20, 20, 20)
        
        demo_title = QLabel("Demo Accounts")
        demo_title.setObjectName("demoTitle")
        demo_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        demo_layout.addWidget(demo_title)
        
        demo_accounts = [
            "Administrator: admin / admin123",
            "Manager: manager / manager123",
            "Cashier: cashier / cashier123"
        ]
        
        for account in demo_accounts:
            demo_label = QLabel(account)
            demo_label.setObjectName("demoAccount")
            demo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            demo_layout.addWidget(demo_label)
        
        form_layout.addWidget(demo_frame)
        main_layout.addWidget(form_widget)
        
        # Connect Enter key to login
        self.username_edit.returnPressed.connect(self.password_edit.setFocus)
        self.password_edit.returnPressed.connect(self.handle_login)
        
        # Focus username field
        self.username_edit.setFocus()
        
    def apply_styles(self):
        """Apply professional styling"""
        self.setStyleSheet(f"""
            QDialog {{
                background: linear-gradient(135deg, {DesignSystem.get_color('primary')} 0%, {DesignSystem.get_color('primary_dark')} 100%);
                border-radius: 16px;
            }}
            
            #loginHeader {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {DesignSystem.get_color('primary')},
                    stop:1 {DesignSystem.get_color('primary_dark')});
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }}
            
            #logoLabel {{
                background-color: {DesignSystem.get_color('accent')};
                color: {DesignSystem.get_color('text_inverse')};
                font-size: 32px;
                font-weight: bold;
                border-radius: 40px;
                min-width: 80px;
                max-width: 80px;
                min-height: 80px;
                max-height: 80px;
            }}
            
            #titleLabel {{
                color: {DesignSystem.get_color('text_inverse')};
                font-size: 24px;
                font-weight: bold;
                margin: 15px 0 5px 0;
            }}
            
            #subtitleLabel {{
                color: {DesignSystem.get_color('gray_300')};
                font-size: 12px;
                margin-bottom: 20px;
            }}
            
            #formSection {{
                background-color: {DesignSystem.get_color('white')};
                border-bottom-left-radius: 16px;
                border-bottom-right-radius: 16px;
            }}
            
            #welcomeLabel {{
                color: {DesignSystem.get_color('text_primary')};
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            
            #welcomeSubtitle {{
                color: {DesignSystem.get_color('text_secondary')};
                font-size: 12px;
                margin-bottom: 30px;
            }}
            
            #fieldLabel {{
                color: {DesignSystem.get_color('text_primary')};
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 5px;
            }}
            
            #loginField {{
                background-color: {DesignSystem.get_color('gray_50')};
                border: 2px solid {DesignSystem.get_color('gray_200')};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: {DesignSystem.get_color('text_primary')};
                min-height: 20px;
            }}
            
            #loginField:focus {{
                border-color: {DesignSystem.get_color('primary')};
                background-color: {DesignSystem.get_color('white')};
            }}
            
            #primaryButton {{
                background-color: {DesignSystem.get_color('primary')};
                color: {DesignSystem.get_color('text_inverse')};
                border: none;
                border-radius: 8px;
                padding: 15px 20px;
                font-size: 14px;
                font-weight: 600;
                min-height: 20px;
            }}
            
            #primaryButton:hover {{
                background-color: {DesignSystem.get_color('primary_dark')};
            }}
            
            #primaryButton:pressed {{
                background-color: {DesignSystem.get_color('primary_light')};
            }}
            
            #secondaryButton {{
                background-color: transparent;
                color: {DesignSystem.get_color('primary')};
                border: 2px solid {DesignSystem.get_color('primary')};
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
                min-height: 20px;
                margin-top: 10px;
            }}
            
            #secondaryButton:hover {{
                background-color: {DesignSystem.get_color('primary_lighter')};
            }}
            
            #showPasswordButton {{
                background-color: transparent;
                border: none;
                font-size: 16px;
                padding: 8px;
                border-radius: 4px;
            }}
            
            #showPasswordButton:hover {{
                background-color: {DesignSystem.get_color('gray_100')};
            }}
            
            #showPasswordButton:checked {{
                background-color: {DesignSystem.get_color('primary_lighter')};
            }}
            
            #demoFrame {{
                background-color: {DesignSystem.get_color('gray_50')};
                border: 1px solid {DesignSystem.get_color('gray_200')};
                border-radius: 8px;
                margin-top: 20px;
            }}
            
            #demoTitle {{
                color: {DesignSystem.get_color('text_primary')};
                font-size: 12px;
                font-weight: 600;
                margin-bottom: 10px;
            }}
            
            #demoAccount {{
                color: {DesignSystem.get_color('text_secondary')};
                font-size: 10px;
                margin: 2px 0;
            }}
        """)
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        log_user_action("login_attempt", f"username: {username}")
        
        if not username or not password:
            log_error("Login validation error: empty credentials", "LoginDialog")
            QMessageBox.warning(self, "Authentication Error", "Please enter both username and password")
            return
        
        # Check credentials
        try:
            if self.verify_credentials(username, password):
                role = self.get_user_role(username)
                self.current_user = {'username': username, 'role': role}
                log_user_action("login_success", f"username: {username}, role: {role}")
                self.accept()
            else:
                log_user_action("login_failed", f"username: {username}")
                QMessageBox.critical(self, "Authentication Failed", "Invalid credentials")
                self.password_edit.clear()
                self.password_edit.setFocus()
        except Exception as e:
            log_error(e, "LoginDialog.handle_login", show_dialog=True)
    
    def verify_credentials(self, username, password):
        """Verify user credentials"""
        try:
            conn = sqlite3.connect("shop.db")
            cur = conn.cursor()
            cur.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
            result = cur.fetchone()
            conn.close()
            log_db_operation("SELECT", "users", f"credential verification for {username}")
            return result is not None
        except Exception as e:
            log_error(e, "LoginDialog.verify_credentials")
            return False
    
    def get_user_role(self, username):
        """Get user role"""
        try:
            conn = sqlite3.connect("shop.db")
            cur = conn.cursor()
            cur.execute('SELECT role FROM users WHERE username = ?', (username,))
            result = cur.fetchone()
            conn.close()
            return result[0] if result else 'cashier'
        except:
            return 'cashier'
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_btn.isChecked():
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("🙈")
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁️")
    
    def show_change_password_dialog(self):
        """Show change password dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Change Password")
        dialog.setModal(True)
        dialog.setFixedSize(400, 300)
        
        layout = QFormLayout(dialog)
        
        # Username field
        username_edit = QLineEdit()
        username_edit.setPlaceholderText("Enter username")
        layout.addRow("Username:", username_edit)
        
        # Current password field
        current_password_edit = QLineEdit()
        current_password_edit.setPlaceholderText("Enter current password")
        current_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Current Password:", current_password_edit)
        
        # New password field
        new_password_edit = QLineEdit()
        new_password_edit.setPlaceholderText("Enter new password")
        new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("New Password:", new_password_edit)
        
        # Confirm password field
        confirm_password_edit = QLineEdit()
        confirm_password_edit.setPlaceholderText("Confirm new password")
        confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Confirm Password:", confirm_password_edit)
        
        # Buttons
        buttons = QHBoxLayout()
        change_btn = QPushButton("Change Password")
        change_btn.setObjectName("primaryButton")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        
        buttons.addWidget(change_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
        
        def change_password():
            username = username_edit.text().strip()
            current_password = current_password_edit.text().strip()
            new_password = new_password_edit.text().strip()
            confirm_password = confirm_password_edit.text().strip()
            
            if not all([username, current_password, new_password, confirm_password]):
                QMessageBox.warning(dialog, "Error", "All fields are required")
                return
            
            if new_password != confirm_password:
                QMessageBox.warning(dialog, "Error", "New passwords do not match")
                return
            
            if len(new_password) < 6:
                QMessageBox.warning(dialog, "Error", "Password must be at least 6 characters long")
                return
            
            # Verify current credentials
            if not self.verify_credentials(username, current_password):
                QMessageBox.critical(dialog, "Error", "Invalid username or current password")
                return
            
            # Update password
            try:
                conn = sqlite3.connect("shop.db")
                cur = conn.cursor()
                cur.execute('UPDATE users SET password = ? WHERE username = ?', (new_password, username))
                conn.commit()
                conn.close()
                
                log_user_action("password_changed", f"username: {username}")
                log_db_operation("UPDATE", "users", f"password change for {username}")
                QMessageBox.information(dialog, "Success", "Password changed successfully!")
                dialog.accept()
                
            except Exception as e:
                log_error(e, "LoginDialog.change_password", show_dialog=True)
        
        change_btn.clicked.connect(change_password)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()

class DashboardWidget(QWidget):
    """Professional dashboard with analytics"""
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(DesignSystem.get_spacing('xl'))
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Business Dashboard")
        title.setFont(DesignSystem.get_font('xxxl', 'bold'))
        title.setStyleSheet(f"color: {DesignSystem.get_color('text_primary')};")
        header.addWidget(title)
        
        refresh_btn = QPushButton(f"{IconSystem.get_icon('refresh')} Refresh")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.refresh_data)
        header.addWidget(refresh_btn)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(DesignSystem.get_spacing('lg'))
        
        stats = self.get_dashboard_stats()
        stat_cards = [
            (IconSystem.get_icon('dashboard'), "Total Sales", f"${stats['total_sales']:.2f}", DesignSystem.get_color('success')),
            (IconSystem.get_icon('products'), "Products", str(stats['total_products']), DesignSystem.get_color('primary')),
            (IconSystem.get_icon('customers'), "Customers", str(stats['total_customers']), DesignSystem.get_color('highlight')),
            ("📈", "This Month", f"${stats['month_sales']:.2f}", DesignSystem.get_color('accent'))
        ]
        
        for icon, title, value, color in stat_cards:
            card = self.create_stat_card(icon, title, value, color)
            stats_layout.addWidget(card)
        
        layout.addLayout(stats_layout)
        
        # Content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(DesignSystem.get_spacing('lg'))
        
        # Recent activities
        activities_card = self.create_activities_card()
        content_layout.addWidget(activities_card, 1)
        
        # Low stock items
        low_stock_card = self.create_low_stock_card()
        content_layout.addWidget(low_stock_card, 1)
        
        # Quick actions
        actions_card = self.create_actions_card()
        content_layout.addWidget(actions_card, 1)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
    def create_stat_card(self, icon, title, value, color):
        """Create a statistics card"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setFixedHeight(120)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            font-size: 32px;
            color: {color};
            margin-bottom: 10px;
        """)
        layout.addWidget(icon_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(DesignSystem.get_font('xl', 'bold'))
        value_label.setStyleSheet(f"color: {DesignSystem.get_color('text_primary')};")
        layout.addWidget(value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(DesignSystem.get_font('sm'))
        title_label.setStyleSheet(f"color: {DesignSystem.get_color('text_secondary')};")
        layout.addWidget(title_label)
        
        card.setStyleSheet(f"""
            #statCard {{
                background-color: {DesignSystem.get_color('white')};
                border: 1px solid {DesignSystem.get_color('gray_200')};
                border-radius: 12px;
                padding: 20px;
            }}
            #statCard:hover {{
                border-color: {color};
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        return card
    
    def create_activities_card(self):
        """Create recent activities card"""
        card = QFrame()
        card.setObjectName("contentCard")
        
        layout = QVBoxLayout(card)
        
        # Header
        header = QLabel(f"{IconSystem.get_icon('reports')} Recent Activities")
        header.setFont(DesignSystem.get_font('lg', 'semibold'))
        header.setStyleSheet(f"color: {DesignSystem.get_color('text_primary')}; padding: 10px 0;")
        layout.addWidget(header)
        
        # Activities list
        activities = self.get_recent_activities()
        for activity in activities:
            activity_item = QLabel(f"• {activity}")
            activity_item.setStyleSheet(f"""
                color: {DesignSystem.get_color('text_secondary')};
                padding: 5px 0;
                font-size: 12px;
            """)
            layout.addWidget(activity_item)
        
        layout.addStretch()
        return card
    
    def create_actions_card(self):
        """Create quick actions card"""
        card = QFrame()
        card.setObjectName("contentCard")
        
        layout = QVBoxLayout(card)
        
        # Header
        header = QLabel(f"⚡ Quick Actions")
        header.setFont(DesignSystem.get_font('lg', 'semibold'))
        header.setStyleSheet(f"color: {DesignSystem.get_color('text_primary')}; padding: 10px 0;")
        layout.addWidget(header)
        
        # Action buttons
        actions = [
            (f"{IconSystem.get_icon('pos')} New Sale", "primaryButton", lambda: self.main_window.switch_page(1) if self.main_window else None),
            (f"{IconSystem.get_icon('add')} Add Product", "successButton", lambda: self.main_window.switch_page(2) if self.main_window else None),
            (f"{IconSystem.get_icon('add')} Add Customer", "accentButton", lambda: self.main_window.switch_page(3) if self.main_window else None),
            (f"{IconSystem.get_icon('reports')} View Reports", "secondaryButton", lambda: self.main_window.switch_page(5) if self.main_window else None)
        ]
        
        for text, style, action in actions:
            btn = QPushButton(text)
            btn.setObjectName(style)
            btn.clicked.connect(action)
            layout.addWidget(btn)
        
        layout.addStretch()
        return card
    
    def create_low_stock_card(self):
        """Create low stock items card"""
        card = QFrame()
        card.setObjectName("contentCard")
        
        layout = QVBoxLayout(card)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel(f"{IconSystem.get_icon('warning')} Low Stock Items")
        header.setFont(DesignSystem.get_font('lg', 'semibold'))
        header.setStyleSheet(f"color: {DesignSystem.get_color('text_primary')}; padding: 10px 0;")
        header_layout.addWidget(header)
        
        # View all button
        view_all_btn = QPushButton("View All")
        view_all_btn.setObjectName("secondaryButton")
        view_all_btn.setFixedSize(80, 30)
        view_all_btn.clicked.connect(lambda: self.main_window.switch_page(2) if self.main_window else None)
        header_layout.addWidget(view_all_btn)
        
        layout.addLayout(header_layout)
        
        # Low stock items list
        low_stock_items = self.get_low_stock_items()
        if low_stock_items:
            for item in low_stock_items[:5]:  # Show only first 5 items
                item_widget = QFrame()
                item_widget.setStyleSheet(f"""
                    QFrame {{
                        background-color: {DesignSystem.get_color('highlight_lighter')};
                        border-left: 3px solid {DesignSystem.get_color('highlight')};
                        border-radius: 4px;
                        padding: 8px;
                        margin: 2px 0;
                    }}
                """)
                
                item_layout = QVBoxLayout(item_widget)
                item_layout.setContentsMargins(8, 4, 8, 4)
                
                name_label = QLabel(item[0])  # Product name
                name_label.setFont(DesignSystem.get_font('sm', 'semibold'))
                name_label.setStyleSheet(f"color: {DesignSystem.get_color('text_primary')};")
                item_layout.addWidget(name_label)
                
                stock_label = QLabel(f"Stock: {item[1]} units")
                stock_label.setFont(DesignSystem.get_font('xs'))
                stock_label.setStyleSheet(f"color: {DesignSystem.get_color('text_secondary')};")
                item_layout.addWidget(stock_label)
                
                layout.addWidget(item_widget)
        else:
            no_items_label = QLabel("✅ All items are well stocked")
            no_items_label.setStyleSheet(f"""
                color: {DesignSystem.get_color('success')};
                padding: 20px;
                font-size: 12px;
                text-align: center;
            """)
            no_items_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_items_label)
        
        layout.addStretch()
        return card
    
    def get_low_stock_items(self):
        """Get items with low stock (less than 10)"""
        try:
            conn = sqlite3.connect("shop.db")
            cur = conn.cursor()
            cur.execute("SELECT name, quantity FROM products WHERE quantity > 0 AND quantity < 10 ORDER BY quantity ASC LIMIT 10")
            items = cur.fetchall()
            conn.close()
            return items
        except:
            return []
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            
            cur.execute("SELECT COALESCE(SUM(total_amount), 0) FROM sales")
            total_sales = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM products")
            total_products = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM customers")
            total_customers = cur.fetchone()[0]
            
            cur.execute("SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE date LIKE ?", 
                       (f"{datetime.now().strftime('%Y-%m')}%",))
            month_sales = cur.fetchone()[0]
            
            conn.close()
            
            return {
                'total_sales': total_sales,
                'total_products': total_products,
                'total_customers': total_customers,
                'month_sales': month_sales
            }
        except:
            return {'total_sales': 0, 'total_products': 0, 'total_customers': 0, 'month_sales': 0}
    
    def get_recent_activities(self):
        """Get recent activities"""
        return [
            "Sale #1001 completed - $2,799.00",
            "New product added: iPhone 15 Pro",
            "Customer registered: Tech Startup Inc",
            "Inventory updated for MacBook Pro",
            "Monthly report generated"
        ]
    
    def refresh_data(self):
        """Refresh dashboard data"""
        # Recreate the dashboard
        for i in reversed(range(self.layout().count())):
            child = self.layout().itemAt(i).widget()
            if child:
                child.setParent(None)
        self.setup_ui()

class POSWidget(QWidget):
    """Complete Point of Sale system"""
    
    def __init__(self):
        super().__init__()
        self.cart_items = []
        self.selected_customer = None
        self.setup_ui()
        self.load_products()
        
    def setup_ui(self):
        """Setup POS interface"""
        layout = QHBoxLayout(self)
        layout.setSpacing(DesignSystem.get_spacing('lg'))
        
        # Left panel - Products
        left_panel = self.create_products_panel()
        layout.addWidget(left_panel, 2)
        
        # Right panel - Cart and checkout
        right_panel = self.create_cart_panel()
        layout.addWidget(right_panel, 1)
        
    def create_products_panel(self):
        """Create products selection panel"""
        panel = QFrame()
        panel.setObjectName("contentCard")
        layout = QVBoxLayout(panel)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel(f"{IconSystem.get_icon('products')} Product Selection")
        title.setFont(DesignSystem.get_font('lg', 'semibold'))
        header_layout.addWidget(title)
        
        # Search
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search products...")
        self.search_box.textChanged.connect(self.filter_products)
        header_layout.addWidget(self.search_box)
        
        layout.addLayout(header_layout)
        
        # Products grid
        scroll_area = QScrollArea()
        self.products_widget = QWidget()
        self.products_layout = QGridLayout(self.products_widget)
        self.products_layout.setSpacing(DesignSystem.get_spacing('base'))
        scroll_area.setWidget(self.products_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        return panel
    
    def create_cart_panel(self):
        """Create cart and checkout panel"""
        panel = QFrame()
        panel.setObjectName("contentCard")
        layout = QVBoxLayout(panel)
        
        # Customer selection
        customer_layout = QHBoxLayout()
        customer_layout.addWidget(QLabel("Customer:"))
        
        self.customer_combo = QComboBox()
        self.customer_combo.setObjectName("customerCombo")
        self.load_customers()
        customer_layout.addWidget(self.customer_combo)
        
        add_customer_btn = QPushButton("New")
        add_customer_btn.setObjectName("primaryButton")
        add_customer_btn.clicked.connect(self.add_new_customer)
        customer_layout.addWidget(add_customer_btn)
        
        layout.addLayout(customer_layout)
        
        # Cart header
        cart_title = QLabel(f"{IconSystem.get_icon('pos')} Shopping Cart")
        cart_title.setFont(DesignSystem.get_font('lg', 'semibold'))
        layout.addWidget(cart_title)
        
        # Cart items
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Product", "Qty", "Price", "Total"])
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.cart_table)
        
        # Cart actions
        cart_actions = QHBoxLayout()
        remove_btn = QPushButton(f"{IconSystem.get_icon('delete')} Remove")
        remove_btn.setObjectName("accentButton")
        remove_btn.clicked.connect(self.remove_cart_item)
        cart_actions.addWidget(remove_btn)
        
        clear_btn = QPushButton("Clear Cart")
        clear_btn.setObjectName("secondaryButton")
        clear_btn.clicked.connect(self.clear_cart)
        cart_actions.addWidget(clear_btn)
        
        layout.addLayout(cart_actions)
        
        # Total section
        total_frame = QFrame()
        total_frame.setStyleSheet(f"background-color: {DesignSystem.get_color('gray_50')}; border-radius: 8px; padding: 15px;")
        total_layout = QVBoxLayout(total_frame)
        
        self.subtotal_label = QLabel("Subtotal: $0.00")
        self.subtotal_label.setFont(DesignSystem.get_font('base', 'medium'))
        total_layout.addWidget(self.subtotal_label)
        
        self.tax_label = QLabel("Tax (8.5%): $0.00")
        total_layout.addWidget(self.tax_label)
        
        self.total_label = QLabel("TOTAL: $0.00")
        self.total_label.setFont(DesignSystem.get_font('lg', 'bold'))
        self.total_label.setStyleSheet(f"color: {DesignSystem.get_color('primary')};")
        total_layout.addWidget(self.total_label)
        
        layout.addWidget(total_frame)
        
        # Checkout button
        self.checkout_btn = QPushButton(f"{IconSystem.get_icon('success')} CHECKOUT")
        self.checkout_btn.setObjectName("successButton")
        self.checkout_btn.setFont(DesignSystem.get_font('base', 'bold'))
        self.checkout_btn.setMinimumHeight(50)
        self.checkout_btn.clicked.connect(self.process_checkout)
        layout.addWidget(self.checkout_btn)
        
        return panel
    
    def load_products(self):
        """Load products from database"""
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            cur.execute("SELECT id, sku, name, description, sell_price, quantity FROM products WHERE quantity > 0")
            products = cur.fetchall()
            conn.close()
            
            self.display_products(products)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load products: {str(e)}")
    
    def display_products(self, products):
        """Display products in grid"""
        # Clear existing products
        for i in reversed(range(self.products_layout.count())):
            child = self.products_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add products
        row, col = 0, 0
        for product in products:
            product_card = self.create_product_card(product)
            self.products_layout.addWidget(product_card, row, col)
            col += 1
            if col >= 3:  # 3 products per row
                col = 0
                row += 1
    
    def create_product_card(self, product):
        """Create product selection card"""
        card = QPushButton()
        card.setFixedSize(180, 120)
        card.clicked.connect(lambda: self.add_to_cart(product))
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Product name
        name_label = QLabel(product[2])  # name
        name_label.setFont(DesignSystem.get_font('sm', 'semibold'))
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # Price
        price_label = QLabel(f"${product[4]:.2f}")  # sell_price
        price_label.setFont(DesignSystem.get_font('lg', 'bold'))
        price_label.setStyleSheet(f"color: {DesignSystem.get_color('success')};")
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(price_label)
        
        # Stock
        stock_label = QLabel(f"Stock: {product[5]}")  # quantity
        stock_label.setFont(DesignSystem.get_font('xs'))
        stock_label.setStyleSheet(f"color: {DesignSystem.get_color('text_secondary')};")
        stock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(stock_label)
        
        card.setStyleSheet(f"""
            QPushButton {{
                background-color: {DesignSystem.get_color('white')};
                border: 2px solid {DesignSystem.get_color('gray_200')};
                border-radius: 8px;
                padding: 10px;
            }}
            QPushButton:hover {{
                border-color: {DesignSystem.get_color('primary')};
                background-color: {DesignSystem.get_color('primary_lighter')};
            }}
        """)
        
        return card
    
    def add_to_cart(self, product):
        """Add product to cart"""
        # Check if item already in cart
        for i, item in enumerate(self.cart_items):
            if item['id'] == product[0]:
                self.cart_items[i]['quantity'] += 1
                break
        else:
            # Add new item
            self.cart_items.append({
                'id': product[0],
                'sku': product[1],
                'name': product[2],
                'price': product[4],
                'quantity': 1,
                'stock': product[5]
            })
        
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update cart table and totals"""
        self.cart_table.setRowCount(len(self.cart_items))
        
        subtotal = 0
        for i, item in enumerate(self.cart_items):
            self.cart_table.setItem(i, 0, QTableWidgetItem(item['name']))
            
            qty_item = QTableWidgetItem(str(item['quantity']))
            self.cart_table.setItem(i, 1, qty_item)
            
            self.cart_table.setItem(i, 2, QTableWidgetItem(f"${item['price']:.2f}"))
            
            line_total = item['quantity'] * item['price']
            self.cart_table.setItem(i, 3, QTableWidgetItem(f"${line_total:.2f}"))
            
            subtotal += line_total
        
        # Calculate tax using dynamic rates
        tax = self.calculate_dynamic_tax()
        
        # Apply discount rules
        discount_amount = self.calculate_discounts(subtotal)
        
        # Calculate final total
        discounted_subtotal = subtotal - discount_amount
        total = discounted_subtotal + tax
        
        # Update display
        self.subtotal_label.setText(f"Subtotal: ${subtotal:.2f}")
        
        if discount_amount > 0:
            if not hasattr(self, 'discount_label'):
                self.discount_label = QLabel()
                self.discount_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
                # Find the layout and insert discount label
                parent_layout = self.subtotal_label.parent().layout()
                if parent_layout:
                    # Insert after subtotal label
                    for i in range(parent_layout.count()):
                        if parent_layout.itemAt(i).widget() == self.subtotal_label:
                            parent_layout.insertWidget(i + 1, self.discount_label)
                            break
            self.discount_label.setText(f"Discount: -${discount_amount:.2f}")
            self.discount_label.setVisible(True)
        else:
            if hasattr(self, 'discount_label'):
                self.discount_label.setVisible(False)
        
        # Get dynamic tax rate
        tax_rate = self.get_current_tax_rate()
        self.tax_label.setText(f"Tax ({tax_rate:.1f}%): ${tax:.2f}")
        self.total_label.setText(f"TOTAL: ${total:.2f}")
        
        self.checkout_btn.setEnabled(len(self.cart_items) > 0)
    
    def remove_cart_item(self):
        """Remove selected item from cart"""
        current_row = self.cart_table.currentRow()
        if current_row >= 0:
            self.cart_items.pop(current_row)
            self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items from cart"""
        self.cart_items.clear()
        self.update_cart_display()
    
    def get_current_tax_rate(self):
        """Get the current applicable tax rate"""
        try:
            # For now, use a weighted average of tax rates based on cart items
            # In a more sophisticated system, each product would have a tax category
            conn = sqlite3.connect("shop_manager.db")
            cursor = conn.cursor()
            
            # Get the most common tax rate (standard)
            cursor.execute('''
                SELECT rate FROM tax_rates 
                WHERE category = 'standard' AND is_active = 1
                LIMIT 1
            ''')
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 8.5  # Default fallback
            
        except Exception as e:
            log_error(f"Failed to get tax rate: {e}")
            return 8.5  # Default fallback
    
    def calculate_dynamic_tax(self):
        """Calculate tax using dynamic tax rates"""
        if not self.cart_items:
            return 0.0
        
        try:
            conn = sqlite3.connect("shop_manager.db")
            cursor = conn.cursor()
            
            total_tax = 0.0
            
            for item in self.cart_items:
                line_subtotal = item['quantity'] * item['price']
                
                # Get product tax category (if we had it in products table)
                # For now, use standard rate for all products
                cursor.execute('''
                    SELECT rate FROM tax_rates 
                    WHERE category = 'standard' AND is_active = 1
                    LIMIT 1
                ''')
                result = cursor.fetchone()
                tax_rate = result[0] if result else 8.5
                
                item_tax = line_subtotal * (tax_rate / 100)
                total_tax += item_tax
            
            conn.close()
            return total_tax
            
        except Exception as e:
            log_error(f"Failed to calculate dynamic tax: {e}")
            # Fallback to standard calculation
            subtotal = sum(item['quantity'] * item['price'] for item in self.cart_items)
            return subtotal * 0.085
    
    def calculate_discounts(self, subtotal):
        """Calculate applicable discount amount"""
        if not self.cart_items or subtotal <= 0:
            return 0.0
        
        try:
            conn = sqlite3.connect("shop_manager.db")
            cursor = conn.cursor()
            
            # Get customer info to check tier
            customer_id = self.customer_combo.currentData()
            customer_tier = 'regular'  # default
            
            if customer_id:
                cursor.execute('SELECT tier FROM customers WHERE id = ?', (customer_id,))
                result = cursor.fetchone()
                customer_tier = result[0] if result else 'regular'
            
            total_quantity = sum(item['quantity'] for item in self.cart_items)
            
            # Get applicable discount rules
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT id, name, discount_type, value, min_quantity, min_amount, customer_tier
                FROM discount_rules
                WHERE is_active = 1
                    AND (valid_from IS NULL OR valid_from <= ?)
                    AND (valid_to IS NULL OR valid_to >= ?)
                    AND (min_quantity IS NULL OR min_quantity <= ?)
                    AND (min_amount IS NULL OR min_amount <= ?)
                    AND (customer_tier IS NULL OR customer_tier = ?)
                ORDER BY value DESC
            ''', (today, today, total_quantity, subtotal, customer_tier))
            
            applicable_rules = cursor.fetchall()
            
            best_discount = 0.0
            applied_rule = None
            
            for rule in applicable_rules:
                rule_id, name, discount_type, value, min_qty, min_amt, tier = rule
                
                # Skip if conditions not met
                if min_qty and total_quantity < min_qty:
                    continue
                if min_amt and subtotal < min_amt:
                    continue
                if tier and tier != customer_tier:
                    continue
                
                # Calculate discount amount
                if discount_type == 'percentage':
                    discount = subtotal * (value / 100)
                elif discount_type == 'fixed_amount':
                    discount = value
                elif discount_type == 'customer_tier':
                    discount = subtotal * (value / 100)
                else:
                    continue
                
                # Take the best discount
                if discount > best_discount:
                    best_discount = discount
                    applied_rule = rule
            
            conn.close()
            
            # Log applied discount
            if applied_rule and best_discount > 0:
                log_user_action("discount_applied", f"rule: {applied_rule[1]}, amount: ${best_discount:.2f}")
                
                # Store applied discount for checkout
                self.applied_discount = {
                    'rule_id': applied_rule[0],
                    'rule_name': applied_rule[1],
                    'amount': best_discount
                }
            else:
                self.applied_discount = None
            
            return best_discount
            
        except Exception as e:
            log_error(f"Failed to calculate discounts: {e}")
            return 0.0
    
    def load_customers(self):
        """Load customers into combo box"""
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM customers ORDER BY name")
            customers = cur.fetchall()
            conn.close()
            
            self.customer_combo.clear()
            for customer in customers:
                self.customer_combo.addItem(customer[1], customer[0])
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load customers: {str(e)}")
    
    def add_new_customer(self):
        """Add new customer dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Customer")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        phone_edit = QLineEdit()
        email_edit = QLineEdit()
        address_edit = QTextEdit()
        address_edit.setMaximumHeight(80)
        
        layout.addRow("Name:", name_edit)
        layout.addRow("Phone:", phone_edit)
        layout.addRow("Email:", email_edit)
        layout.addRow("Address:", address_edit)
        
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
        
        def save_customer():
            if not name_edit.text().strip():
                QMessageBox.warning(dialog, "Error", "Customer name is required")
                return
            
            try:
                conn = sqlite3.connect("shop_manager.db")
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)",
                    (name_edit.text(), phone_edit.text(), email_edit.text(), address_edit.toPlainText())
                )
                conn.commit()
                conn.close()
                
                self.load_customers()
                dialog.accept()
                QMessageBox.information(dialog, "Success", "Customer added successfully")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to add customer: {str(e)}")
        
        save_btn.clicked.connect(save_customer)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def filter_products(self):
        """Filter products based on search"""
        search_text = self.search_box.text().lower()
        if search_text:
            try:
                conn = sqlite3.connect("shop_manager.db")
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, sku, name, description, sell_price, quantity FROM products WHERE quantity > 0 AND (LOWER(name) LIKE ? OR LOWER(sku) LIKE ? OR LOWER(description) LIKE ?)",
                    (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%")
                )
                products = cur.fetchall()
                conn.close()
                self.display_products(products)
            except:
                pass
        else:
            self.load_products()
    
    def process_checkout(self):
        """Process the sale"""
        if not self.cart_items:
            return
        
        log_user_action("checkout_started", f"items: {len(self.cart_items)}")
        
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            
            # Calculate totals with dynamic pricing
            subtotal = sum(item['quantity'] * item['price'] for item in self.cart_items)
            discount_amount = self.calculate_discounts(subtotal)
            tax = self.calculate_dynamic_tax()
            
            discounted_subtotal = subtotal - discount_amount
            total = discounted_subtotal + tax
            
            log_info(f"Processing sale: subtotal=${subtotal:.2f}, tax=${tax:.2f}, total=${total:.2f}", "POS")
            
            # Get customer ID
            customer_id = self.customer_combo.currentData() or 1  # Default to walk-in
            
            # Create sale record with discount information
            cur.execute(
                "INSERT INTO sales (date, customer_id, subtotal, discount_amount, tax_amount, total_amount, paid, user_id, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), customer_id, subtotal, discount_amount, tax, total, 1, 1, "POS Sale")
            )
            sale_id = cur.lastrowid
            log_db_operation("INSERT", "sales", f"sale_id: {sale_id}, total: ${total:.2f}")
            
            # Add sale lines and update inventory
            for item in self.cart_items:
                line_total = item['quantity'] * item['price']
                cur.execute(
                    "INSERT INTO sale_lines (sale_id, product_id, qty, price, line_total) VALUES (?, ?, ?, ?, ?)",
                    (sale_id, item['id'], item['quantity'], item['price'], line_total)
                )
                
                # Update inventory
                cur.execute(
                    "UPDATE products SET quantity = quantity - ? WHERE id = ?",
                    (item['quantity'], item['id'])
                )
                log_db_operation("UPDATE", "products", f"product_id: {item['id']}, qty_sold: {item['quantity']}")
            
            # Log discount usage if applicable
            if hasattr(self, 'applied_discount') and self.applied_discount:
                try:
                    cur.execute(
                        "INSERT INTO discount_usage_log (discount_rule_id, sale_id, discount_amount) VALUES (?, ?, ?)",
                        (self.applied_discount['rule_id'], sale_id, self.applied_discount['amount'])
                    )
                    
                    # Update discount rule usage statistics
                    cur.execute(
                        "UPDATE discount_rules SET usage_count = usage_count + 1, total_savings = total_savings + ? WHERE id = ?",
                        (self.applied_discount['amount'], self.applied_discount['rule_id'])
                    )
                    
                    log_db_operation("INSERT", "discount_usage_log", 
                                   f"rule_id: {self.applied_discount['rule_id']}, amount: ${self.applied_discount['amount']:.2f}")
                except Exception as discount_error:
                    log_error(f"Failed to log discount usage: {discount_error}")
            
            conn.commit()
            conn.close()
            
            log_user_action("sale_completed", f"sale_id: {sale_id}, total: ${total:.2f}, items: {len(self.cart_items)}")
            
            # Show receipt
            applied_discount = self.applied_discount if hasattr(self, 'applied_discount') else None
            self.show_receipt(sale_id, self.cart_items, subtotal, discount_amount, tax, total, applied_discount)
            
            # Clear cart
            self.clear_cart()
            self.load_products()  # Refresh to show updated stock
            
            QMessageBox.information(self, "Success", f"Sale completed successfully!\nSale ID: {sale_id}")
            
        except Exception as e:
            log_error(e, "POS.process_checkout", show_dialog=True)
    
    def show_receipt(self, sale_id, items, subtotal, discount_amount, tax, total, applied_discount=None):
        """Show receipt dialog with discount information"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Receipt")
        dialog.resize(400, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Receipt content
        receipt = QTextEdit()
        receipt.setReadOnly(True)
        
        receipt_text = f"""
=== SHOP MANAGER PRO ===
    Professional Receipt

Sale ID: {sale_id}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Customer: {self.customer_combo.currentText()}

{'='*30}
ITEMS:
{'='*30}
"""
        
        for item in items:
            line_total = item['quantity'] * item['price']
            receipt_text += f"{item['name']}\n  {item['quantity']} x ${item['price']:.2f} = ${line_total:.2f}\n\n"
        
        receipt_text += f"""
{'='*30}
Subtotal: ${subtotal:.2f}"""
        
        # Add discount information if applicable
        if applied_discount and discount_amount > 0:
            receipt_text += f"""
Discount ({applied_discount['rule_name']}): -${discount_amount:.2f}
Discounted Subtotal: ${subtotal - discount_amount:.2f}"""
        
        # Get dynamic tax rate for display
        tax_rate = self.get_current_tax_rate()
        receipt_text += f"""
Tax ({tax_rate:.1f}%): ${tax:.2f}
TOTAL: ${total:.2f}
{'='*30}

Thank you for your business!
        """
        
        if applied_discount and discount_amount > 0:
            receipt_text += f"\nYou saved ${discount_amount:.2f} with '{applied_discount['rule_name']}'!\n"
        
        receipt.setPlainText(receipt_text)
        layout.addWidget(receipt)
        
        # Buttons
        buttons = QHBoxLayout()
        print_btn = QPushButton(f"{IconSystem.get_icon('print')} Print")
        print_btn.setObjectName("primaryButton")
        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondaryButton")
        
        buttons.addWidget(print_btn)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)
        
        close_btn.clicked.connect(dialog.accept)
        print_btn.clicked.connect(lambda: QMessageBox.information(dialog, "Print", "Receipt sent to printer"))
        
        dialog.exec()

class ProductsWidget(QWidget):
    """Complete Products management system"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_products()
        
    def setup_ui(self):
        """Setup products management interface"""
        layout = QVBoxLayout(self)
        
        # Header with actions
        header_layout = QHBoxLayout()
        
        title = QLabel(f"{IconSystem.get_icon('products')} Products Management")
        title.setFont(DesignSystem.get_font('xxxl', 'bold'))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Action buttons
        add_btn = QPushButton(f"{IconSystem.get_icon('add')} Add Product")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self.add_product)
        header_layout.addWidget(add_btn)
        
        export_btn = QPushButton(f"{IconSystem.get_icon('export')} Export")
        export_btn.setObjectName("secondaryButton")
        export_btn.clicked.connect(self.export_products)
        header_layout.addWidget(export_btn)
        
        layout.addLayout(header_layout)
        
        # Search and filter
        search_layout = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search products by name, SKU, or description...")
        self.search_box.textChanged.connect(self.filter_products)
        search_layout.addWidget(self.search_box)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories", "Electronics", "Accessories", "Hardware"])
        self.category_filter.currentTextChanged.connect(self.filter_products)
        search_layout.addWidget(self.category_filter)
        
        self.stock_filter = QComboBox()
        self.stock_filter.addItems(["All Stock Levels", "In Stock", "Low Stock (<10)", "Out of Stock"])
        self.stock_filter.currentTextChanged.connect(self.filter_products)
        search_layout.addWidget(self.stock_filter)
        
        layout.addLayout(search_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels([
            "SKU", "Name", "Description", "Stock", "Cost Price", "Sell Price", "Supplier"
        ])
        
        # Set column widths
        header = self.products_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.products_table.setColumnWidth(0, 100)
        self.products_table.setColumnWidth(1, 200)
        self.products_table.setColumnWidth(2, 250)
        self.products_table.setColumnWidth(3, 80)
        self.products_table.setColumnWidth(4, 100)
        self.products_table.setColumnWidth(5, 100)
        
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.itemDoubleClicked.connect(self.edit_product)
        
        layout.addWidget(self.products_table)
        
        # Bottom actions
        bottom_layout = QHBoxLayout()
        
        edit_btn = QPushButton(f"{IconSystem.get_icon('edit')} Edit")
        edit_btn.setObjectName("primaryButton")
        edit_btn.clicked.connect(self.edit_product)
        bottom_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton(f"{IconSystem.get_icon('delete')} Delete")
        delete_btn.setObjectName("accentButton")
        delete_btn.clicked.connect(self.delete_product)
        bottom_layout.addWidget(delete_btn)
        
        bottom_layout.addStretch()
        
        refresh_btn = QPushButton(f"{IconSystem.get_icon('refresh')} Refresh")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.clicked.connect(self.load_products)
        bottom_layout.addWidget(refresh_btn)
        
        layout.addLayout(bottom_layout)
        
    def load_products(self):
        """Load products from database"""
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            cur.execute("""
                SELECT p.id, p.sku, p.name, p.description, p.quantity, p.cost_price, p.sell_price, s.name as supplier_name
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                ORDER BY p.name
            """)
            products = cur.fetchall()
            conn.close()
            
            self.display_products(products)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load products: {str(e)}")
    
    def display_products(self, products):
        """Display products in table"""
        self.products_table.setRowCount(len(products))
        
        for i, product in enumerate(products):
            # Store product ID in first column as hidden data
            sku_item = QTableWidgetItem(product[1])
            sku_item.setData(Qt.ItemDataRole.UserRole, product[0])  # Store ID
            self.products_table.setItem(i, 0, sku_item)
            
            self.products_table.setItem(i, 1, QTableWidgetItem(product[2] or ""))
            self.products_table.setItem(i, 2, QTableWidgetItem(product[3] or ""))
            
            # Stock with color coding
            stock_item = QTableWidgetItem(str(product[4]))
            if product[4] == 0:
                stock_item.setBackground(QColor(DesignSystem.get_color('accent_lighter')))
            elif product[4] < 10:
                stock_item.setBackground(QColor(DesignSystem.get_color('highlight_lighter')))
            self.products_table.setItem(i, 3, stock_item)
            
            self.products_table.setItem(i, 4, QTableWidgetItem(f"${product[5]:.2f}"))
            self.products_table.setItem(i, 5, QTableWidgetItem(f"${product[6]:.2f}"))
            self.products_table.setItem(i, 6, QTableWidgetItem(product[7] or "No Supplier"))
    
    def filter_products(self):
        """Filter products based on search and filters"""
        search_text = self.search_box.text().lower()
        stock_filter = self.stock_filter.currentText()
        
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            
            query = """
                SELECT p.id, p.sku, p.name, p.description, p.quantity, p.cost_price, p.sell_price, s.name as supplier_name
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE 1=1
            """
            params = []
            
            if search_text:
                query += " AND (LOWER(p.name) LIKE ? OR LOWER(p.sku) LIKE ? OR LOWER(p.description) LIKE ?)"
                params.extend([f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"])
            
            if stock_filter == "In Stock":
                query += " AND p.quantity > 0"
            elif stock_filter == "Low Stock (<10)":
                query += " AND p.quantity > 0 AND p.quantity < 10"
            elif stock_filter == "Out of Stock":
                query += " AND p.quantity = 0"
            
            query += " ORDER BY p.name"
            
            cur.execute(query, params)
            products = cur.fetchall()
            conn.close()
            
            self.display_products(products)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Filter error: {str(e)}")
    
    def add_product(self):
        """Add new product"""
        self.show_product_dialog()
    
    def edit_product(self):
        """Edit selected product"""
        current_row = self.products_table.currentRow()
        if current_row >= 0:
            product_id = self.products_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            self.show_product_dialog(product_id)
    
    def show_product_dialog(self, product_id=None):
        """Show add/edit product dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Product" if product_id else "Add New Product")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QFormLayout(dialog)
        
        # Form fields
        sku_edit = QLineEdit()
        name_edit = QLineEdit()
        description_edit = QTextEdit()
        description_edit.setMaximumHeight(80)
        quantity_edit = QSpinBox()
        quantity_edit.setRange(0, 999999)
        cost_price_edit = QDoubleSpinBox()
        cost_price_edit.setRange(0, 999999.99)
        cost_price_edit.setDecimals(2)
        sell_price_edit = QDoubleSpinBox()
        sell_price_edit.setRange(0, 999999.99)
        sell_price_edit.setDecimals(2)
        
        supplier_combo = QComboBox()
        self.load_suppliers_combo(supplier_combo)
        
        layout.addRow("SKU:", sku_edit)
        layout.addRow("Name:", name_edit)
        layout.addRow("Description:", description_edit)
        layout.addRow("Quantity:", quantity_edit)
        layout.addRow("Cost Price:", cost_price_edit)
        layout.addRow("Sell Price:", sell_price_edit)
        layout.addRow("Supplier:", supplier_combo)
        
        # Load existing data if editing
        if product_id:
            try:
                conn = sqlite3.connect("shop_manager.db")
                cur = conn.cursor()
                cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
                product = cur.fetchone()
                conn.close()
                
                if product:
                    sku_edit.setText(product[1] or "")
                    name_edit.setText(product[2] or "")
                    description_edit.setPlainText(product[3] or "")
                    quantity_edit.setValue(product[4] or 0)
                    cost_price_edit.setValue(product[5] or 0)
                    sell_price_edit.setValue(product[6] or 0)
                    
                    # Set supplier
                    for i in range(supplier_combo.count()):
                        if supplier_combo.itemData(i) == product[7]:
                            supplier_combo.setCurrentIndex(i)
                            break
            except Exception as e:
                QMessageBox.warning(dialog, "Warning", f"Failed to load product data: {str(e)}")
        
        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
        
        def save_product():
            if not name_edit.text().strip():
                QMessageBox.warning(dialog, "Error", "Product name is required")
                return
            
            if not sku_edit.text().strip():
                QMessageBox.warning(dialog, "Error", "SKU is required")
                return
            
            try:
                conn = sqlite3.connect("shop_manager.db")
                cur = conn.cursor()
                
                supplier_id = supplier_combo.currentData()
                
                if product_id:
                    # Update existing product
                    cur.execute("""
                        UPDATE products SET sku=?, name=?, description=?, quantity=?, 
                        cost_price=?, sell_price=?, supplier_id=? WHERE id=?
                    """, (
                        sku_edit.text(), name_edit.text(), description_edit.toPlainText(),
                        quantity_edit.value(), cost_price_edit.value(), sell_price_edit.value(),
                        supplier_id, product_id
                    ))
                else:
                    # Add new product
                    cur.execute("""
                        INSERT INTO products (sku, name, description, quantity, cost_price, sell_price, supplier_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        sku_edit.text(), name_edit.text(), description_edit.toPlainText(),
                        quantity_edit.value(), cost_price_edit.value(), sell_price_edit.value(),
                        supplier_id
                    ))
                
                conn.commit()
                conn.close()
                
                self.load_products()
                dialog.accept()
                QMessageBox.information(self, "Success", "Product saved successfully")
                
            except sqlite3.IntegrityError:
                QMessageBox.critical(dialog, "Error", "SKU already exists. Please use a unique SKU.")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to save product: {str(e)}")
        
        save_btn.clicked.connect(save_product)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()
    
    def load_suppliers_combo(self, combo):
        """Load suppliers into combo box"""
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM suppliers ORDER BY name")
            suppliers = cur.fetchall()
            conn.close()
            
            combo.clear()
            combo.addItem("No Supplier", None)
            for supplier in suppliers:
                combo.addItem(supplier[1], supplier[0])
        except:
            pass
    
    def delete_product(self):
        """Delete selected product"""
        current_row = self.products_table.currentRow()
        if current_row >= 0:
            product_id = self.products_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            product_name = self.products_table.item(current_row, 1).text()
            
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete '{product_name}'?\n\nThis action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    conn = sqlite3.connect("shop_manager.db")
                    cur = conn.cursor()
                    cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
                    conn.commit()
                    conn.close()
                    
                    self.load_products()
                    QMessageBox.information(self, "Success", "Product deleted successfully")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete product: {str(e)}")
    
    def export_products(self):
        """Export products to CSV"""
        try:
            import csv
            from datetime import datetime
            
            filename = f"products_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            cur.execute("""
                SELECT p.sku, p.name, p.description, p.quantity, p.cost_price, p.sell_price, s.name as supplier_name
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                ORDER BY p.name
            """)
            products = cur.fetchall()
            conn.close()
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["SKU", "Name", "Description", "Stock", "Cost Price", "Sell Price", "Supplier"])
                for product in products:
                    writer.writerow(product)
            
            QMessageBox.information(self, "Success", f"Products exported to {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export products: {str(e)}")

class CustomersWidget(QWidget):
    """Complete Customers management system"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_customers()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel(f"{IconSystem.get_icon('customers')} Customer Management")
        title.setFont(DesignSystem.get_font('xxxl', 'bold'))
        header.addWidget(title)
        header.addStretch()
        
        add_btn = QPushButton(f"{IconSystem.get_icon('add')} Add Customer")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self.add_customer)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # Search
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search customers...")
        self.search_box.textChanged.connect(self.filter_customers)
        layout.addWidget(self.search_box)
        
        # Table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(4)
        self.customers_table.setHorizontalHeaderLabels(["Name", "Phone", "Email", "Address"])
        self.customers_table.horizontalHeader().setStretchLastSection(True)
        self.customers_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.customers_table.itemDoubleClicked.connect(self.edit_customer)
        layout.addWidget(self.customers_table)
        
        # Actions
        actions = QHBoxLayout()
        edit_btn = QPushButton(f"{IconSystem.get_icon('edit')} Edit")
        edit_btn.setObjectName("primaryButton")
        edit_btn.clicked.connect(self.edit_customer)
        actions.addWidget(edit_btn)
        
        delete_btn = QPushButton(f"{IconSystem.get_icon('delete')} Delete")
        delete_btn.setObjectName("accentButton")
        delete_btn.clicked.connect(self.delete_customer)
        actions.addWidget(delete_btn)
        actions.addStretch()
        
        refresh_btn = QPushButton(f"{IconSystem.get_icon('refresh')} Refresh")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.clicked.connect(self.load_customers)
        actions.addWidget(refresh_btn)
        
        layout.addLayout(actions)
    
    def load_customers(self):
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            cur.execute("SELECT id, name, phone, email, address FROM customers ORDER BY name")
            customers = cur.fetchall()
            conn.close()
            
            self.customers_table.setRowCount(len(customers))
            for i, customer in enumerate(customers):
                item = QTableWidgetItem(customer[1])
                item.setData(Qt.ItemDataRole.UserRole, customer[0])
                self.customers_table.setItem(i, 0, item)
                
                self.customers_table.setItem(i, 1, QTableWidgetItem(customer[2] or ""))
                self.customers_table.setItem(i, 2, QTableWidgetItem(customer[3] or ""))
                self.customers_table.setItem(i, 3, QTableWidgetItem(customer[4] or ""))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def filter_customers(self):
        search_text = self.search_box.text().lower()
        for i in range(self.customers_table.rowCount()):
            show_row = any(search_text in (self.customers_table.item(i, j).text().lower() if self.customers_table.item(i, j) else "")
                          for j in range(self.customers_table.columnCount()))
            self.customers_table.setRowHidden(i, not show_row)
    
    def add_customer(self):
        self.show_customer_dialog()
    
    def edit_customer(self):
        row = self.customers_table.currentRow()
        if row >= 0:
            customer_id = self.customers_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.show_customer_dialog(customer_id)
    
    def show_customer_dialog(self, customer_id=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Customer" if customer_id else "Add Customer")
        dialog.resize(400, 300)
        
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        phone_edit = QLineEdit()
        email_edit = QLineEdit()
        address_edit = QTextEdit()
        address_edit.setMaximumHeight(80)
        
        layout.addRow("Name:", name_edit)
        layout.addRow("Phone:", phone_edit)
        layout.addRow("Email:", email_edit)
        layout.addRow("Address:", address_edit)
        
        if customer_id:
            try:
                conn = sqlite3.connect("shop_manager.db")
                cur = conn.cursor()
                cur.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
                customer = cur.fetchone()
                conn.close()
                
                if customer:
                    name_edit.setText(customer[1] or "")
                    phone_edit.setText(customer[2] or "")
                    email_edit.setText(customer[3] or "")
                    address_edit.setPlainText(customer[4] or "")
            except Exception as e:
                QMessageBox.warning(dialog, "Warning", str(e))
        
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
        
        def save():
            if not name_edit.text().strip():
                QMessageBox.warning(dialog, "Error", "Name is required")
                return
            
            try:
                conn = sqlite3.connect("shop_manager.db")
                cur = conn.cursor()
                
                if customer_id:
                    cur.execute("""
                        UPDATE customers SET name=?, phone=?, email=?, address=? WHERE id=?
                    """, (name_edit.text(), phone_edit.text(), email_edit.text(), 
                         address_edit.toPlainText(), customer_id))
                else:
                    cur.execute("""
                        INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)
                    """, (name_edit.text(), phone_edit.text(), email_edit.text(), 
                         address_edit.toPlainText()))
                
                conn.commit()
                conn.close()
                self.load_customers()
                dialog.accept()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Error", str(e))
        
        save_btn.clicked.connect(save)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec()
    
    def delete_customer(self):
        row = self.customers_table.currentRow()
        if row >= 0:
            customer_id = self.customers_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            name = self.customers_table.item(row, 0).text()
            
            reply = QMessageBox.question(self, "Delete Customer", 
                                       f"Delete '{name}'?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    conn = sqlite3.connect("shop_manager.db")
                    cur = conn.cursor()
                    cur.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
                    conn.commit()
                    conn.close()
                    self.load_customers()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

class SuppliersWidget(QWidget):
    """Complete Suppliers management system"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_suppliers()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel(f"{IconSystem.get_icon('suppliers')} Supplier Management")
        title.setFont(DesignSystem.get_font('xxxl', 'bold'))
        header.addWidget(title)
        header.addStretch()
        
        add_btn = QPushButton(f"{IconSystem.get_icon('add')} Add Supplier")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self.add_supplier)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # Search
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search suppliers...")
        self.search_box.textChanged.connect(self.filter_suppliers)
        layout.addWidget(self.search_box)
        
        # Table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(4)
        self.suppliers_table.setHorizontalHeaderLabels(["Name", "Phone", "Email", "Address"])
        self.suppliers_table.horizontalHeader().setStretchLastSection(True)
        self.suppliers_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.suppliers_table.itemDoubleClicked.connect(self.edit_supplier)
        layout.addWidget(self.suppliers_table)
        
        # Actions
        actions = QHBoxLayout()
        edit_btn = QPushButton(f"{IconSystem.get_icon('edit')} Edit")
        edit_btn.setObjectName("primaryButton")
        edit_btn.clicked.connect(self.edit_supplier)
        actions.addWidget(edit_btn)
        
        delete_btn = QPushButton(f"{IconSystem.get_icon('delete')} Delete")
        delete_btn.setObjectName("accentButton")
        delete_btn.clicked.connect(self.delete_supplier)
        actions.addWidget(delete_btn)
        actions.addStretch()
        
        refresh_btn = QPushButton(f"{IconSystem.get_icon('refresh')} Refresh")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.clicked.connect(self.load_suppliers)
        actions.addWidget(refresh_btn)
        
        layout.addLayout(actions)
    
    def load_suppliers(self):
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            cur.execute("SELECT id, name, phone, email, address FROM suppliers ORDER BY name")
            suppliers = cur.fetchall()
            conn.close()
            
            self.suppliers_table.setRowCount(len(suppliers))
            for i, supplier in enumerate(suppliers):
                item = QTableWidgetItem(supplier[1])
                item.setData(Qt.ItemDataRole.UserRole, supplier[0])
                self.suppliers_table.setItem(i, 0, item)
                
                self.suppliers_table.setItem(i, 1, QTableWidgetItem(supplier[2] or ""))
                self.suppliers_table.setItem(i, 2, QTableWidgetItem(supplier[3] or ""))
                self.suppliers_table.setItem(i, 3, QTableWidgetItem(supplier[4] or ""))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def filter_suppliers(self):
        search_text = self.search_box.text().lower()
        for i in range(self.suppliers_table.rowCount()):
            show_row = any(search_text in (self.suppliers_table.item(i, j).text().lower() if self.suppliers_table.item(i, j) else "")
                          for j in range(self.suppliers_table.columnCount()))
            self.suppliers_table.setRowHidden(i, not show_row)
    
    def add_supplier(self):
        self.show_supplier_dialog()
    
    def edit_supplier(self):
        row = self.suppliers_table.currentRow()
        if row >= 0:
            supplier_id = self.suppliers_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.show_supplier_dialog(supplier_id)
    
    def show_supplier_dialog(self, supplier_id=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Supplier" if supplier_id else "Add Supplier")
        dialog.resize(400, 300)
        
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        phone_edit = QLineEdit()
        email_edit = QLineEdit()
        address_edit = QTextEdit()
        address_edit.setMaximumHeight(80)
        
        layout.addRow("Name:", name_edit)
        layout.addRow("Phone:", phone_edit)
        layout.addRow("Email:", email_edit)
        layout.addRow("Address:", address_edit)
        
        if supplier_id:
            try:
                conn = sqlite3.connect("shop_manager.db")
                cur = conn.cursor()
                cur.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
                supplier = cur.fetchone()
                conn.close()
                
                if supplier:
                    name_edit.setText(supplier[1] or "")
                    phone_edit.setText(supplier[2] or "")
                    email_edit.setText(supplier[3] or "")
                    address_edit.setPlainText(supplier[4] or "")
            except Exception as e:
                QMessageBox.warning(dialog, "Warning", str(e))
        
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
        
        def save():
            if not name_edit.text().strip():
                QMessageBox.warning(dialog, "Error", "Name is required")
                return
            
            try:
                conn = sqlite3.connect("shop_manager.db")
                cur = conn.cursor()
                
                if supplier_id:
                    cur.execute("""
                        UPDATE suppliers SET name=?, phone=?, email=?, address=? WHERE id=?
                    """, (name_edit.text(), phone_edit.text(), email_edit.text(), 
                         address_edit.toPlainText(), supplier_id))
                else:
                    cur.execute("""
                        INSERT INTO suppliers (name, phone, email, address) VALUES (?, ?, ?, ?)
                    """, (name_edit.text(), phone_edit.text(), email_edit.text(), 
                         address_edit.toPlainText()))
                
                conn.commit()
                conn.close()
                self.load_suppliers()
                dialog.accept()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Error", str(e))
        
        save_btn.clicked.connect(save)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec()
    
    def delete_supplier(self):
        row = self.suppliers_table.currentRow()
        if row >= 0:
            supplier_id = self.suppliers_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            name = self.suppliers_table.item(row, 0).text()
            
            reply = QMessageBox.question(self, "Delete Supplier", 
                                       f"Delete '{name}'?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    conn = sqlite3.connect("shop_manager.db")
                    cur = conn.cursor()
                    cur.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
                    conn.commit()
                    conn.close()
                    self.load_suppliers()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

class ReportsWidget(QWidget):
    """Complete Reports and Analytics system"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel(f"{IconSystem.get_icon('reports')} Reports & Analytics")
        title.setFont(DesignSystem.get_font('xxxl', 'bold'))
        header.addWidget(title)
        header.addStretch()
        
        export_btn = QPushButton(f"{IconSystem.get_icon('export')} Export Report")
        export_btn.setObjectName("primaryButton")
        export_btn.clicked.connect(self.export_report)
        header.addWidget(export_btn)
        
        layout.addLayout(header)
        
        # Report tabs
        tab_widget = QTabWidget()
        
        # Sales Report
        sales_tab = self.create_sales_report()
        tab_widget.addTab(sales_tab, "Sales Report")
        
        # Inventory Report
        inventory_tab = self.create_inventory_report()
        tab_widget.addTab(inventory_tab, "Inventory Report")
        
        # Customer Report
        customer_tab = self.create_customer_report()
        tab_widget.addTab(customer_tab, "Customer Report")
        
        layout.addWidget(tab_widget)
    
    def create_sales_report(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Date range selection
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        date_layout.addWidget(self.from_date)
        
        date_layout.addWidget(QLabel("To:"))
        
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.to_date)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.refresh_sales_report)
        date_layout.addWidget(refresh_btn)
        
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Sales table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels(["Date", "Sale ID", "Customer", "Items", "Total", "Status"])
        self.sales_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.sales_table)
        
        # Summary
        summary_layout = QHBoxLayout()
        self.total_sales_label = QLabel("Total Sales: $0.00")
        self.total_sales_label.setFont(DesignSystem.get_font('lg', 'bold'))
        summary_layout.addWidget(self.total_sales_label)
        
        self.sales_count_label = QLabel("Number of Sales: 0")
        summary_layout.addWidget(self.sales_count_label)
        summary_layout.addStretch()
        
        layout.addLayout(summary_layout)
        
        self.refresh_sales_report()
        return widget
    
    def create_inventory_report(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filter options
        filter_layout = QHBoxLayout()
        
        self.stock_filter = QComboBox()
        self.stock_filter.addItems(["All Products", "In Stock", "Low Stock", "Out of Stock"])
        self.stock_filter.currentTextChanged.connect(self.refresh_inventory_report)
        filter_layout.addWidget(self.stock_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels(["Product", "SKU", "Stock", "Value", "Status"])
        self.inventory_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.inventory_table)
        
        # Summary
        summary_layout = QHBoxLayout()
        self.inventory_value_label = QLabel("Total Inventory Value: $0.00")
        self.inventory_value_label.setFont(DesignSystem.get_font('lg', 'bold'))
        summary_layout.addWidget(self.inventory_value_label)
        
        self.products_count_label = QLabel("Total Products: 0")
        summary_layout.addWidget(self.products_count_label)
        summary_layout.addStretch()
        
        layout.addLayout(summary_layout)
        
        self.refresh_inventory_report()
        return widget
    
    def create_customer_report(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Customer table
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(["Customer", "Total Purchases", "Last Purchase", "Status"])
        self.customer_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.customer_table)
        
        self.refresh_customer_report()
        return widget
    
    def refresh_sales_report(self):
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            
            from_date_str = self.from_date.date().toString('yyyy-MM-dd')
            to_date_str = self.to_date.date().toString('yyyy-MM-dd')
            
            cur.execute("""
                SELECT s.date, s.id, c.name, COUNT(sl.id) as items, s.total_amount, 
                       CASE WHEN s.paid = 1 THEN 'Paid' ELSE 'Pending' END as status
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.id
                LEFT JOIN sale_lines sl ON s.id = sl.sale_id
                WHERE DATE(s.date) BETWEEN ? AND ?
                GROUP BY s.id
                ORDER BY s.date DESC
            """, (from_date_str, to_date_str))
            sales = cur.fetchall()
            
            self.sales_table.setRowCount(len(sales))
            total_amount = 0
            
            for i, sale in enumerate(sales):
                self.sales_table.setItem(i, 0, QTableWidgetItem(sale[0]))
                self.sales_table.setItem(i, 1, QTableWidgetItem(str(sale[1])))
                self.sales_table.setItem(i, 2, QTableWidgetItem(sale[2] or "Walk-in"))
                self.sales_table.setItem(i, 3, QTableWidgetItem(str(sale[3])))
                self.sales_table.setItem(i, 4, QTableWidgetItem(f"${sale[4]:.2f}"))
                self.sales_table.setItem(i, 5, QTableWidgetItem(sale[5]))
                
                total_amount += sale[4]
            
            self.total_sales_label.setText(f"Total Sales: ${total_amount:.2f}")
            self.sales_count_label.setText(f"Number of Sales: {len(sales)}")
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def refresh_inventory_report(self):
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            
            query = "SELECT name, sku, quantity, sell_price FROM products WHERE 1=1"
            filter_text = self.stock_filter.currentText()
            
            if filter_text == "In Stock":
                query += " AND quantity > 0"
            elif filter_text == "Low Stock":
                query += " AND quantity > 0 AND quantity < 10"
            elif filter_text == "Out of Stock":
                query += " AND quantity = 0"
            
            query += " ORDER BY name"
            
            cur.execute(query)
            products = cur.fetchall()
            
            self.inventory_table.setRowCount(len(products))
            total_value = 0
            
            for i, product in enumerate(products):
                value = product[2] * product[3]  # quantity * price
                status = "Out of Stock" if product[2] == 0 else ("Low Stock" if product[2] < 10 else "In Stock")
                
                self.inventory_table.setItem(i, 0, QTableWidgetItem(product[0]))
                self.inventory_table.setItem(i, 1, QTableWidgetItem(product[1]))
                self.inventory_table.setItem(i, 2, QTableWidgetItem(str(product[2])))
                self.inventory_table.setItem(i, 3, QTableWidgetItem(f"${value:.2f}"))
                self.inventory_table.setItem(i, 4, QTableWidgetItem(status))
                
                total_value += value
            
            self.inventory_value_label.setText(f"Total Inventory Value: ${total_value:.2f}")
            self.products_count_label.setText(f"Total Products: {len(products)}")
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def refresh_customer_report(self):
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            
            cur.execute("""
                SELECT c.name, COALESCE(SUM(s.total_amount), 0) as total_purchases,
                       MAX(s.date) as last_purchase,
                       CASE WHEN MAX(s.date) IS NULL THEN 'No Purchases'
                            WHEN DATE(MAX(s.date)) >= DATE('now', '-30 days') THEN 'Active'
                            ELSE 'Inactive' END as status
                FROM customers c
                LEFT JOIN sales s ON c.id = s.customer_id
                GROUP BY c.id, c.name
                ORDER BY total_purchases DESC
            """)
            customers = cur.fetchall()
            
            self.customer_table.setRowCount(len(customers))
            
            for i, customer in enumerate(customers):
                self.customer_table.setItem(i, 0, QTableWidgetItem(customer[0]))
                self.customer_table.setItem(i, 1, QTableWidgetItem(f"${customer[1]:.2f}"))
                self.customer_table.setItem(i, 2, QTableWidgetItem(customer[2] or "Never"))
                self.customer_table.setItem(i, 3, QTableWidgetItem(customer[3]))
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def export_report(self):
        try:
            import csv
            filename = f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            cur.execute("""
                SELECT s.date, s.id, c.name, s.total_amount, s.note
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.id
                ORDER BY s.date DESC
            """)
            sales = cur.fetchall()
            conn.close()
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Sale ID", "Customer", "Total", "Note"])
                for sale in sales:
                    writer.writerow(sale)
            
            QMessageBox.information(self, "Success", f"Report exported to {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class UsersWidget(QWidget):
    """Complete User administration system"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_users()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel(f"{IconSystem.get_icon('users')} User Management")
        title.setFont(DesignSystem.get_font('xxxl', 'bold'))
        header.addWidget(title)
        header.addStretch()
        
        add_btn = QPushButton(f"{IconSystem.get_icon('add')} Add User")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self.add_user)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels(["Username", "Role", "Created"])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.users_table.itemDoubleClicked.connect(self.edit_user)
        layout.addWidget(self.users_table)
        
        # Actions
        actions = QHBoxLayout()
        edit_btn = QPushButton(f"{IconSystem.get_icon('edit')} Edit")
        edit_btn.setObjectName("primaryButton")
        edit_btn.clicked.connect(self.edit_user)
        actions.addWidget(edit_btn)
        
        delete_btn = QPushButton(f"{IconSystem.get_icon('delete')} Delete")
        delete_btn.setObjectName("accentButton")
        delete_btn.clicked.connect(self.delete_user)
        actions.addWidget(delete_btn)
        actions.addStretch()
        
        refresh_btn = QPushButton(f"{IconSystem.get_icon('refresh')} Refresh")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.clicked.connect(self.load_users)
        actions.addWidget(refresh_btn)
        
        layout.addLayout(actions)
    
    def load_users(self):
        try:
            conn = sqlite3.connect("shop_manager.db")
            cur = conn.cursor()
            cur.execute("SELECT id, username, role FROM users ORDER BY username")
            users = cur.fetchall()
            conn.close()
            
            self.users_table.setRowCount(len(users))
            for i, user in enumerate(users):
                item = QTableWidgetItem(user[1])
                item.setData(Qt.ItemDataRole.UserRole, user[0])
                self.users_table.setItem(i, 0, item)
                
                self.users_table.setItem(i, 1, QTableWidgetItem(user[2].title()))
                self.users_table.setItem(i, 2, QTableWidgetItem(datetime.now().strftime('%Y-%m-%d')))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def add_user(self):
        self.show_user_dialog()
    
    def edit_user(self):
        row = self.users_table.currentRow()
        if row >= 0:
            user_id = self.users_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.show_user_dialog(user_id)
    
    def show_user_dialog(self, user_id=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit User" if user_id else "Add User")
        dialog.resize(400, 200)
        
        layout = QFormLayout(dialog)
        
        username_edit = QLineEdit()
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        role_combo = QComboBox()
        role_combo.addItems(["cashier", "manager", "admin"])
        
        layout.addRow("Username:", username_edit)
        layout.addRow("Password:", password_edit)
        layout.addRow("Role:", role_combo)
        
        if user_id:
            try:
                conn = sqlite3.connect("shop_manager.db")
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user = cur.fetchone()
                conn.close()
                
                if user:
                    username_edit.setText(user[1] or "")
                    role_combo.setCurrentText(user[3] or "cashier")
                    # Don't show password for security
            except Exception as e:
                QMessageBox.warning(dialog, "Warning", str(e))
        
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
        
        def save():
            if not username_edit.text().strip():
                QMessageBox.warning(dialog, "Error", "Username is required")
                return
            
            if not user_id and not password_edit.text().strip():
                QMessageBox.warning(dialog, "Error", "Password is required for new users")
                return
            
            try:
                conn = sqlite3.connect("shop_manager.db")
                cur = conn.cursor()
                
                if user_id:
                    if password_edit.text().strip():
                        cur.execute("""
                            UPDATE users SET username=?, password=?, role=? WHERE id=?
                        """, (username_edit.text(), password_edit.text(), role_combo.currentText(), user_id))
                    else:
                        cur.execute("""
                            UPDATE users SET username=?, role=? WHERE id=?
                        """, (username_edit.text(), role_combo.currentText(), user_id))
                else:
                    cur.execute("""
                        INSERT INTO users (username, password, role) VALUES (?, ?, ?)
                    """, (username_edit.text(), password_edit.text(), role_combo.currentText()))
                
                conn.commit()
                conn.close()
                self.load_users()
                dialog.accept()
                
            except sqlite3.IntegrityError:
                QMessageBox.critical(dialog, "Error", "Username already exists")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", str(e))
        
        save_btn.clicked.connect(save)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec()
    
    def delete_user(self):
        row = self.users_table.currentRow()
        if row >= 0:
            user_id = self.users_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            username = self.users_table.item(row, 0).text()
            
            if username == "admin":
                QMessageBox.warning(self, "Error", "Cannot delete the admin user")
                return
            
            reply = QMessageBox.question(self, "Delete User", 
                                       f"Delete user '{username}'?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    conn = sqlite3.connect("shop_manager.db")
                    cur = conn.cursor()
                    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
                    conn.commit()
                    conn.close()
                    self.load_users()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

class MainWindow(QMainWindow):
    """Professional main application window"""
    
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.setWindowTitle("Shop Manager Pro Enterprise")
        self.setMinimumSize(1400, 900)
        self.showMaximized()
        
        # Initialize logging
        self.logger = get_logger()
        self.logger.start_session()
        log_info(f"Main window initialized for user: {user_info['username']}", "MainWindow")
        
        # Initialize database
        self.init_database()
        
        self.setup_ui()
        self.apply_styles()
        self.setup_shortcuts()
        
        log_user_action("application_started", f"user: {user_info['username']}, role: {user_info['role']}")
        
        # Check if demo should be shown (first time use)
        self.check_first_time_demo()
        
    def init_database(self):
        """Initialize database with sample data (same as before)"""
        if not os.path.exists("shop.db"):
            conn = sqlite3.connect("shop.db")
            cur = conn.cursor()
            
            # Create tables (same structure as previous version)
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
            
            # Sample data
            sample_data = [
                ("INSERT OR IGNORE INTO users (username,password,role) VALUES (?,?,?)", 
                 [("admin", "admin123", "admin"), ("manager", "manager123", "manager"), ("cashier", "cashier123", "cashier")]),
                
                ("INSERT OR IGNORE INTO suppliers (name,phone,email,address) VALUES (?,?,?,?)",
                 [("Premium Tech Solutions", "555-0100", "contact@premiumtech.com", "1000 Corporate Blvd"),
                  ("Global Electronics", "555-0200", "sales@globalelec.com", "2000 Tech Street")]),
                
                ("INSERT OR IGNORE INTO products (sku,name,description,quantity,cost_price,sell_price,supplier_id) VALUES (?,?,?,?,?,?,?)",
                 [("PRO001", "MacBook Pro 16\"", "Professional laptop", 12, 2200.00, 2799.00, 1),
                  ("PRO002", "iPhone 15 Pro", "Latest smartphone", 25, 800.00, 1199.00, 1),
                  ("PRO003", "iPad Air", "Tablet device", 18, 450.00, 699.00, 1),
                  ("PRO004", "AirPods Pro", "Wireless earbuds", 35, 180.00, 279.00, 1)]),
                
                ("INSERT OR IGNORE INTO customers (name,phone,email,address) VALUES (?,?,?,?)",
                 [("Walk-in Customer", "", "", ""),
                  ("Corporate Client A", "555-2001", "clientA@corp.com", "500 Business St"),
                  ("Enterprise Solutions", "555-2002", "contact@enterprise.com", "750 Commerce Ave")])
            ]
            
            for query, data in sample_data:
                for item in data:
                    cur.execute(query, item)
            
            conn.commit()
            conn.close()
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        self.content_area = QStackedWidget()
        main_layout.addWidget(self.content_area, 1)
        
        # Add pages
        self.dashboard = DashboardWidget(self)
        self.content_area.addWidget(self.dashboard)
        
        # Add complete functional tabs
        self.pos_widget = POSWidget()
        self.products_widget = ProductsWidget()
        self.customers_widget = CustomersWidget()
        self.suppliers_widget = SuppliersWidget()
        self.reports_widget = ReportsWidget()
        self.users_widget = UsersWidget()
        
        self.content_area.addWidget(self.pos_widget)
        self.content_area.addWidget(self.products_widget)
        self.content_area.addWidget(self.customers_widget)
        self.content_area.addWidget(self.suppliers_widget)
        self.content_area.addWidget(self.reports_widget)
        self.content_area.addWidget(self.users_widget)
        
        # Initialize AI widget first
        self.ai_widget = None
        if AI_AVAILABLE:
            try:
                self.ai_widget = AIControlPanel()
                self.content_area.addWidget(self.ai_widget)
                log_info("AI features initialized successfully")
            except Exception as e:
                log_error(f"Failed to initialize AI features: {e}")
                self.ai_widget = None
        
        # Setup toolbar
        self.setup_toolbar()
        
        # Setup status bar
        self.setup_status_bar()
        
    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setObjectName("sidebarHeader")
        header.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo = QLabel("SMP")
        logo.setObjectName("sidebarLogo")
        header_layout.addWidget(logo)
        
        title = QLabel("Shop Manager Pro")
        title.setObjectName("sidebarTitle")
        header_layout.addWidget(title)
        
        layout.addWidget(header)
        
        # User info
        user_info = QFrame()
        user_info.setObjectName("userInfo")
        user_info_layout = QVBoxLayout(user_info)
        
        welcome = QLabel(f"Welcome, {self.user_info['username']}")
        welcome.setObjectName("welcomeText")
        user_info_layout.addWidget(welcome)
        
        role = QLabel(f"Role: {self.user_info['role'].title()}")
        role.setObjectName("roleText")
        user_info_layout.addWidget(role)
        
        layout.addWidget(user_info)
        
        # Navigation buttons
        nav_items = [
            (f"{IconSystem.get_icon('dashboard')} Dashboard", 0),
            (f"{IconSystem.get_icon('pos')} Point of Sale", 1),
            (f"{IconSystem.get_icon('products')} Products", 2),
            (f"{IconSystem.get_icon('customers')} Customers", 3),
            (f"{IconSystem.get_icon('suppliers')} Suppliers", 4),
            (f"{IconSystem.get_icon('reports')} Reports", 5),
        ]
        
        # Add Users tab for admin
        if self.user_info['role'] == 'admin':
            nav_items.append((f"{IconSystem.get_icon('users')} Users", 6))
        
        # Add AI tab if available (check after AI widget creation)
        if AI_AVAILABLE:
            # Force check for AI widget availability
            ai_index = 7 if self.user_info['role'] == 'admin' else 6
            nav_items.append(("🤖 AI Assistant", ai_index))
        
        self.nav_buttons = []
        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        # Set dashboard as active
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
        
        layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton(f"{IconSystem.get_icon('logout')} Sign Out")
        logout_btn.setObjectName("logoutButton")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        return sidebar
    
    def switch_page(self, index):
        """Switch to a different page"""
        page_names = ["Dashboard", "POS", "Products", "Customers", "Suppliers", "Reports", "Users", "AI Assistant"]
        page_name = page_names[index] if index < len(page_names) else f"Page {index}"
        
        log_user_action("page_switch", f"switched to {page_name} (index: {index})")
        
        # Check if trying to access AI tab
        if page_name == "AI Assistant":
            if not AI_AVAILABLE or self.ai_widget is None:
                # Show message if AI not available
                QMessageBox.information(self, "AI Features", 
                                       "AI features are not available.\n\n" +
                                       "Please ensure AI dependencies are installed:\n" +
                                       "pip install -r requirements_ai.txt")
                return
        
        self.content_area.setCurrentIndex(index)
        
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
    
    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setObjectName("mainToolbar")
        
        # Quick actions
        toolbar.addAction(f"{IconSystem.get_icon('add')} New", self.new_item)
        toolbar.addAction(f"{IconSystem.get_icon('save')} Save", self.save_item)
        toolbar.addAction(f"{IconSystem.get_icon('refresh')} Refresh", self.refresh_current)
        toolbar.addSeparator()
        toolbar.addAction(f"{IconSystem.get_icon('search')} Search", self.show_search)
        toolbar.addAction(f"{IconSystem.get_icon('export')} Export", self.export_data)
        toolbar.addSeparator()
        toolbar.addSeparator()
        
        # Configuration menu
        toolbar.addAction(f"{IconSystem.get_icon('settings')} Tax Config", self.show_tax_config)
        toolbar.addAction(f"{IconSystem.get_icon('settings')} Discount Management", self.show_discount_management)
        
        toolbar.addSeparator()
        toolbar.addAction(f"{IconSystem.get_icon('settings')} Telemetry Settings", self.show_telemetry_settings)
        toolbar.addAction("🎓 Interactive Demo", self.show_interactive_demo)
        toolbar.addAction(f"{IconSystem.get_icon('help')} Help", self.show_help)
    
    def setup_status_bar(self):
        """Setup status bar"""
        status_bar = self.statusBar()
        status_bar.setObjectName("mainStatusBar")
        
        # Status messages
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)
        
        status_bar.addPermanentWidget(QLabel(f"User: {self.user_info['username']}"))
        status_bar.addPermanentWidget(QLabel(f"Role: {self.user_info['role'].title()}"))
        
        # Current time
        self.time_label = QLabel()
        status_bar.addPermanentWidget(self.time_label)
        
        # Update time every second
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()
    
    def update_time(self):
        """Update current time in status bar"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        shortcuts = [
            (SHORTCUTS['new_item'], self.new_item),
            (SHORTCUTS['save'], self.save_item),
            (SHORTCUTS['refresh'], self.refresh_current),
            (SHORTCUTS['search'], self.show_search),
            (SHORTCUTS['quit'], self.close),
            (SHORTCUTS['help'], self.show_help),
        ]
        
        for key, slot in shortcuts:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(slot)
    
    def apply_styles(self):
        """Apply professional styling"""
        self.setStyleSheet(f"""
            {StyleSheets.main_window()}
            
            /* Sidebar Styles */
            #sidebar {{
                background-color: {DesignSystem.get_color('gray_800')};
                border-right: 1px solid {DesignSystem.get_color('gray_700')};
            }}
            
            #sidebarHeader {{
                background-color: {DesignSystem.get_color('primary')};
                padding: 20px;
            }}
            
            #sidebarLogo {{
                background-color: {DesignSystem.get_color('accent')};
                color: {DesignSystem.get_color('text_inverse')};
                font-size: 18px;
                font-weight: bold;
                border-radius: 20px;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
                margin-right: 10px;
            }}
            
            #sidebarTitle {{
                color: {DesignSystem.get_color('text_inverse')};
                font-size: 16px;
                font-weight: bold;
            }}
            
            #userInfo {{
                background-color: {DesignSystem.get_color('gray_700')};
                padding: 20px;
                border-bottom: 1px solid {DesignSystem.get_color('gray_600')};
            }}
            
            #welcomeText {{
                color: {DesignSystem.get_color('text_inverse')};
                font-size: 14px;
                font-weight: 600;
            }}
            
            #roleText {{
                color: {DesignSystem.get_color('gray_300')};
                font-size: 12px;
                margin-top: 5px;
            }}
            
            #navButton {{
                background-color: transparent;
                color: {DesignSystem.get_color('gray_300')};
                border: none;
                text-align: left;
                padding: 15px 20px;
                font-size: 14px;
                min-height: 20px;
                border-left: 3px solid transparent;
            }}
            
            #navButton:hover {{
                background-color: {DesignSystem.get_color('gray_700')};
                color: {DesignSystem.get_color('text_inverse')};
            }}
            
            #navButton:checked {{
                background-color: {DesignSystem.get_color('primary')};
                color: {DesignSystem.get_color('text_inverse')};
                border-left-color: {DesignSystem.get_color('highlight')};
                font-weight: 600;
            }}
            
            #logoutButton {{
                background-color: {DesignSystem.get_color('accent')};
                color: {DesignSystem.get_color('text_inverse')};
                border: none;
                padding: 15px 20px;
                font-size: 14px;
                font-weight: 600;
                margin: 20px;
                border-radius: 8px;
            }}
            
            #logoutButton:hover {{
                background-color: {DesignSystem.get_color('accent_dark')};
            }}
            
            /* Content area styles */
            #contentCard {{
                background-color: {DesignSystem.get_color('white')};
                border: 1px solid {DesignSystem.get_color('gray_200')};
                border-radius: 12px;
                padding: 20px;
                margin: 10px;
            }}
            
            /* Button styles */
            #primaryButton {{
                {StyleSheets.primary_button()}
            }}
            
            #successButton {{
                {StyleSheets.success_button()}
            }}
            
            #accentButton {{
                {StyleSheets.accent_button()}
            }}
            
            #secondaryButton {{
                {StyleSheets.secondary_button()}
            }}
            
            /* Toolbar styles */
            #mainToolbar {{
                {StyleSheets.toolbar()}
            }}
            
            /* Status bar styles */
            #mainStatusBar {{
                {StyleSheets.status_bar()}
            }}
        """)
    
    def new_item(self):
        """Handle new item action"""
        self.status_label.setText("New item action triggered")
    
    def save_item(self):
        """Handle save action"""
        self.status_label.setText("Save action triggered")
    
    def refresh_current(self):
        """Refresh current page"""
        current_index = self.content_area.currentIndex()
        if current_index == 0:  # Dashboard
            self.dashboard.refresh_data()
        self.status_label.setText("Data refreshed")
    
    def show_search(self):
        """Show search dialog"""
        self.status_label.setText("Search dialog opened")
    
    def export_data(self):
        """Export current data"""
        self.status_label.setText("Export functionality triggered")
    
    def show_tax_config(self):
        """Show tax configuration dialog"""
        try:
            dialog = TaxConfigDialog(self)
            dialog.tax_rates_updated.connect(self.on_tax_rates_updated)
            dialog.exec()
        except Exception as e:
            log_error(f"Failed to open tax config dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open tax configuration:\n{e}")
    
    def show_discount_management(self):
        """Show discount management dialog"""
        try:
            dialog = DiscountManagementDialog(self)
            dialog.discounts_updated.connect(self.on_discounts_updated)
            dialog.exec()
        except Exception as e:
            log_error(f"Failed to open discount management dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open discount management:\n{e}")
    
    def on_tax_rates_updated(self):
        """Handle tax rates update"""
        # Refresh any UI components that depend on tax rates
        log_info("Tax rates updated - refreshing dependent components")
        self.status_label.setText("Tax rates updated successfully")
    
    def on_discounts_updated(self):
        """Handle discount rules update"""
        # Refresh any UI components that depend on discount rules
        log_info("Discount rules updated - refreshing dependent components")
        self.status_label.setText("Discount rules updated successfully")
    
    def check_first_time_demo(self):
        """Check if this is first time use and show demo"""
        if should_show_demo():
            # Delay demo slightly to allow window to fully load
            QTimer.singleShot(1000, self.show_first_time_demo)
    
    def show_first_time_demo(self):
        """Show the first-time user demo"""
        try:
            # Show welcome message first
            reply = QMessageBox.question(
                self, "Welcome to Shop Manager Pro! 🎉",
                "Welcome to Shop Manager Pro!\n\n"
                "This appears to be your first time using the application. "
                "Would you like to take an interactive tour to learn about all the features?\n\n"
                "The demo takes about 8-10 minutes and will show you:"
                "\n• Point of Sale system with smart pricing"
                "\n• Inventory and customer management"
                "\n• Tax configuration and discount rules"
                "\n• Reports and analytics"
                "\n• And much more!\n\n"
                "You can always access the demo later from the Help menu.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.show_interactive_demo()
        except Exception as e:
            log_error(f"Failed to show first-time demo: {e}")
    
    def show_interactive_demo(self):
        """Show the interactive demo dialog"""
        try:
            show_demo_dialog(self)
        except Exception as e:
            log_error(f"Failed to show interactive demo: {e}")
            QMessageBox.critical(self, "Error", f"Failed to show demo:\n{e}")
    
    def show_telemetry_settings(self):
        """Show telemetry settings dialog"""
        log_user_action("telemetry_settings_opened")
        
        current_setting = self.logger.telemetry_enabled
        new_setting = show_telemetry_dialog(self, current_setting)
        
        if new_setting != current_setting:
            self.logger.save_telemetry_setting(new_setting)
            log_user_action("telemetry_setting_changed", f"enabled: {new_setting}")
            
            QMessageBox.information(self, "Settings Saved", 
                                  f"Telemetry has been {'enabled' if new_setting else 'disabled'}.")
    
    def show_help(self):
        """Show help dialog"""
        log_user_action("help_opened")
        
        QMessageBox.information(self, "Help", 
                               "Shop Manager Pro Enterprise Edition\n\n"
                               "🎓 Need help getting started?\n"
                               "Click 'Interactive Demo' in the toolbar for a guided tour!\n\n"
                               "Keyboard shortcuts:\n"
                               f"• {SHORTCUTS['new_item']} - New item\n"
                               f"• {SHORTCUTS['save']} - Save\n"
                               f"• {SHORTCUTS['refresh']} - Refresh\n"
                               f"• {SHORTCUTS['search']} - Search\n"
                               f"• {SHORTCUTS['help']} - Help\n"
                               f"• {SHORTCUTS['quit']} - Quit\n\n"
                               "Features:\n"
                               "• Point of Sale with smart pricing\n"
                               "• Inventory & customer management\n"
                               "• Tax configuration & discount rules\n"
                               "• Reports & analytics\n"
                               "• Multi-user with role-based access")
    
    def logout(self):
        """Handle logout"""
        reply = QMessageBox.question(self, "Sign Out", 
                                   "Are you sure you want to sign out?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            log_user_action("logout", f"user: {self.user_info['username']}")
            self.logger.end_session()
            log_info("Application closing normally", "MainWindow")
            
            self.close()
            app = QApplication.instance()
            app.quit()

class ShopManagerApp(QApplication):
    """Main application class"""
    
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        
        # Initialize logging system first
        init_logging()
        log_info("Shop Manager Pro starting up", "Application")
        
        self.setApplicationName("Shop Manager Pro Enterprise")
        self.setApplicationVersion("2.0")
        self.setOrganizationName("Shop Manager Pro")
        
        # Set application icon (if available)
        self.setWindowIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        # Apply global styles
        self.setStyleSheet(f"""
            QApplication {{
                font-family: '{DesignSystem.FONTS['primary']}';
                font-size: {DesignSystem.FONT_SIZES['base']}px;
            }}
        """)
        
    def run(self):
        """Run the application"""
        # Show login dialog
        login_dialog = LoginDialog()
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            # Create and show main window
            main_window = MainWindow(login_dialog.current_user)
            main_window.show()
            return self.exec()
        else:
            return 0

def main():
    """Main entry point"""
    app = ShopManagerApp(sys.argv)
    return app.run()

if __name__ == "__main__":
    sys.exit(main())