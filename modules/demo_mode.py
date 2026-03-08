"""
Shop Manager Pro - Interactive Demo Mode
Provides a comprehensive guided tour for new users
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QWidget, QScrollArea, QFrame, QTextEdit,
                           QProgressBar, QCheckBox, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QPen
import json
import os
from datetime import datetime
from logger_config import log_user_action, log_info


class DemoStep:
    """Represents a single step in the demo tour"""
    
    def __init__(self, title, description, target_widget=None, action=None, 
                 duration=3000, highlight=True, next_auto=False):
        self.title = title
        self.description = description
        self.target_widget = target_widget
        self.action = action  # Function to execute during this step
        self.duration = duration  # How long to show this step
        self.highlight = highlight  # Whether to highlight the target widget
        self.next_auto = next_auto  # Auto-advance to next step
        self.completed = False


class HighlightOverlay(QWidget):
    """Overlay widget to highlight specific areas during demo"""
    
    def __init__(self, parent, target_rect=None):
        super().__init__(parent)
        self.target_rect = target_rect
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(parent.size())
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Semi-transparent dark overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))
        
        if self.target_rect:
            # Clear the highlighted area
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.target_rect, QColor(0, 0, 0, 0))
            
            # Draw highlight border
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 123, 255), 3)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.target_rect)


class DemoDialog(QDialog):
    """Main demo dialog with step-by-step tour"""
    
    step_completed = pyqtSignal(int)  # Signal when a step is completed
    demo_finished = pyqtSignal()     # Signal when demo is complete
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.current_step = 0
        self.steps = []
        self.overlay = None
        self.setup_ui()
        self.create_demo_steps()
        self.apply_styles()
        
        log_user_action("demo_mode_started")
    
    def setup_ui(self):
        """Set up the demo dialog UI"""
        self.setWindowTitle("Shop Manager Pro - Interactive Demo")
        self.setModal(True)
        self.resize(600, 500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QFrame()
        header.setObjectName("demoHeader")
        header_layout = QVBoxLayout(header)
        
        title = QLabel("🎯 Welcome to Shop Manager Pro!")
        title.setObjectName("demoTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Interactive Demo & Tutorial")
        subtitle.setObjectName("demoSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("demoProgress")
        layout.addWidget(self.progress_bar)
        
        # Content area
        content_frame = QFrame()
        content_frame.setObjectName("demoContent")
        content_layout = QVBoxLayout(content_frame)
        
        # Step title
        self.step_title = QLabel()
        self.step_title.setObjectName("stepTitle")
        self.step_title.setWordWrap(True)
        content_layout.addWidget(self.step_title)
        
        # Step description
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.step_description = QTextEdit()
        self.step_description.setObjectName("stepDescription")
        self.step_description.setReadOnly(True)
        scroll_area.setWidget(self.step_description)
        content_layout.addWidget(scroll_area)
        
        # Tips section
        self.tips_frame = QFrame()
        self.tips_frame.setObjectName("tipsFrame")
        tips_layout = QVBoxLayout(self.tips_frame)
        
        tips_label = QLabel("💡 Pro Tips:")
        tips_label.setObjectName("tipsLabel")
        tips_layout.addWidget(tips_label)
        
        self.tips_text = QLabel()
        self.tips_text.setObjectName("tipsText")
        self.tips_text.setWordWrap(True)
        tips_layout.addWidget(self.tips_text)
        
        content_layout.addWidget(self.tips_frame)
        layout.addWidget(content_frame)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        # Left side buttons
        self.skip_demo_btn = QPushButton("Skip Demo")
        self.skip_demo_btn.setObjectName("skipButton")
        self.skip_demo_btn.clicked.connect(self.skip_demo)
        nav_layout.addWidget(self.skip_demo_btn)
        
        nav_layout.addStretch()
        
        # Right side buttons
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.setObjectName("navButton")
        self.prev_btn.clicked.connect(self.previous_step)
        self.prev_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.setObjectName("navButton")
        self.next_btn.clicked.connect(self.next_step)
        nav_layout.addWidget(self.next_btn)
        
        self.finish_btn = QPushButton("Start Using App")
        self.finish_btn.setObjectName("finishButton")
        self.finish_btn.clicked.connect(self.finish_demo)
        self.finish_btn.hide()
        nav_layout.addWidget(self.finish_btn)
        
        layout.addLayout(nav_layout)
        
        # Auto-advance timer
        self.auto_timer = QTimer()
        self.auto_timer.setSingleShot(True)
        self.auto_timer.timeout.connect(self.auto_next_step)
    
    def create_demo_steps(self):
        """Create all demo steps"""
        self.steps = [
            # Welcome & Overview
            DemoStep(
                "Welcome to Shop Manager Pro! 🎉",
                """
                <h2>Professional Point of Sale & Business Management System</h2>
                
                <p><strong>Shop Manager Pro</strong> is a comprehensive business management solution designed for retail stores, 
                service businesses, and entrepreneurs. This interactive demo will show you all the powerful features.</p>
                
                <h3>What You'll Learn:</h3>
                <ul>
                <li>🛒 <strong>Point of Sale (POS)</strong> - Process sales with dynamic pricing</li>
                <li>📊 <strong>Dashboard</strong> - Monitor business performance</li>
                <li>📦 <strong>Inventory Management</strong> - Track products and stock</li>
                <li>👥 <strong>Customer Management</strong> - Build customer relationships</li>
                <li>🏪 <strong>Supplier Management</strong> - Manage vendor relationships</li>
                <li>📈 <strong>Reports & Analytics</strong> - Make data-driven decisions</li>
                <li>👤 <strong>User Management</strong> - Multi-user with role-based access</li>
                <li>💰 <strong>Tax Configuration</strong> - Dynamic tax rates by category</li>
                <li>🎯 <strong>Discount Management</strong> - Advanced promotion system</li>
                </ul>
                
                <p><em>Estimated tour time: 8-10 minutes</em></p>
                """,
                duration=5000,
                next_auto=False
            ),
            
            # Dashboard Overview
            DemoStep(
                "📊 Dashboard - Your Business Command Center",
                """
                <h2>Real-time Business Overview</h2>
                
                <p>The Dashboard is your central hub for monitoring business performance. 
                It provides at-a-glance insights into your daily operations.</p>
                
                <h3>Key Dashboard Features:</h3>
                <ul>
                <li><strong>Sales Summary Cards</strong> - Today's revenue, transactions, and average sale</li>
                <li><strong>Quick Stats</strong> - Total customers, active products, low stock alerts</li>
                <li><strong>Recent Activity</strong> - Latest sales and transactions</li>
                <li><strong>Low Stock Alerts</strong> - Products needing reorder</li>
                <li><strong>Quick Action Buttons</strong> - Jump to POS, add products, view reports</li>
                </ul>
                
                <h3>Smart Analytics:</h3>
                <ul>
                <li>📈 Revenue trends and growth indicators</li>
                <li>🏆 Top-selling products and categories</li>
                <li>👥 Customer activity and loyalty insights</li>
                <li>⚠️ Business alerts and notifications</li>
                </ul>
                """,
                action=lambda: self.navigate_to_tab(0) if self.main_window else None,
                duration=4000
            ),
            
            # POS System
            DemoStep(
                "🛒 Point of Sale (POS) - Smart Transaction Processing",
                """
                <h2>Advanced Point of Sale System</h2>
                
                <p>The POS system is the heart of your sales operations, featuring intelligent 
                pricing, discount application, and customer management.</p>
                
                <h3>POS Features:</h3>
                <ul>
                <li><strong>Product Search</strong> - Quick barcode or name search</li>
                <li><strong>Smart Cart</strong> - Easy quantity adjustments</li>
                <li><strong>Dynamic Tax Calculation</strong> - Automatic tax by product category</li>
                <li><strong>Intelligent Discounts</strong> - Auto-applied based on rules</li>
                <li><strong>Customer Selection</strong> - Link sales to customer accounts</li>
                <li><strong>Real-time Totals</strong> - Subtotal, discounts, tax, final total</li>
                </ul>
                
                <h3>Smart Pricing Engine:</h3>
                <ul>
                <li>🎯 <strong>Automatic Discounts</strong> - Volume, customer tier, promotional</li>
                <li>💰 <strong>Dynamic Tax Rates</strong> - Different rates by product category</li>
                <li>🏷️ <strong>Customer Tier Pricing</strong> - VIP, Premium, Regular discounts</li>
                <li>📊 <strong>Real-time Calculations</strong> - Instant price updates</li>
                </ul>
                """,
                action=lambda: self.navigate_to_tab(1) if self.main_window else None,
                duration=4000
            ),
            
            # Product Management
            DemoStep(
                "📦 Product Management - Complete Inventory Control",
                """
                <h2>Professional Inventory Management</h2>
                
                <p>Manage your entire product catalog with advanced features for 
                pricing, categories, suppliers, and stock control.</p>
                
                <h3>Product Features:</h3>
                <ul>
                <li><strong>Product Catalog</strong> - SKU, names, descriptions, images</li>
                <li><strong>Pricing Management</strong> - Cost price, sell price, margins</li>
                <li><strong>Stock Tracking</strong> - Real-time quantity updates</li>
                <li><strong>Supplier Linking</strong> - Connect products to suppliers</li>
                <li><strong>Tax Categories</strong> - Assign tax rates by product type</li>
                <li><strong>Advanced Search</strong> - Filter by stock, price, category</li>
                </ul>
                
                <h3>Inventory Intelligence:</h3>
                <ul>
                <li>🔍 <strong>Smart Filters</strong> - In stock, low stock, out of stock</li>
                <li>⚠️ <strong>Low Stock Alerts</strong> - Automated reorder notifications</li>
                <li>📊 <strong>Inventory Valuation</strong> - Total value at cost and retail</li>
                <li>📈 <strong>Sales Analytics</strong> - Best sellers and slow movers</li>
                </ul>
                """,
                action=lambda: self.navigate_to_tab(2) if self.main_window else None,
                duration=4000
            ),
            
            # Customer Management
            DemoStep(
                "👥 Customer Management - Build Lasting Relationships",
                """
                <h2>Advanced Customer Relationship Management</h2>
                
                <p>Build strong customer relationships with detailed profiles, 
                purchase history, and loyalty programs.</p>
                
                <h3>Customer Features:</h3>
                <ul>
                <li><strong>Customer Profiles</strong> - Contact info, addresses, notes</li>
                <li><strong>Tier System</strong> - Regular, Premium, VIP classifications</li>
                <li><strong>Purchase History</strong> - Complete transaction records</li>
                <li><strong>Loyalty Tracking</strong> - Total purchases and visit frequency</li>
                <li><strong>Automated Promotions</strong> - Tier-based discount application</li>
                <li><strong>Communication Tools</strong> - Email and phone management</li>
                </ul>
                
                <h3>Customer Intelligence:</h3>
                <ul>
                <li>🎯 <strong>Segmentation</strong> - Group customers by behavior and value</li>
                <li>💰 <strong>Lifetime Value</strong> - Track customer profitability</li>
                <li>🏆 <strong>Top Customers</strong> - Identify your best clients</li>
                <li>📊 <strong>Buying Patterns</strong> - Understand customer preferences</li>
                </ul>
                """,
                action=lambda: self.navigate_to_tab(3) if self.main_window else None,
                duration=4000
            ),
            
            # Supplier Management
            DemoStep(
                "🏪 Supplier Management - Vendor Relationship Tools",
                """
                <h2>Complete Supplier Management System</h2>
                
                <p>Manage your supplier relationships with detailed vendor profiles 
                and product sourcing tools.</p>
                
                <h3>Supplier Features:</h3>
                <ul>
                <li><strong>Vendor Profiles</strong> - Contact information and terms</li>
                <li><strong>Product Linking</strong> - Connect products to suppliers</li>
                <li><strong>Order History</strong> - Track purchase orders and deliveries</li>
                <li><strong>Performance Tracking</strong> - Supplier reliability metrics</li>
                <li><strong>Communication Log</strong> - Record all supplier interactions</li>
                <li><strong>Contract Management</strong> - Terms, pricing agreements</li>
                </ul>
                
                <h3>Supply Chain Intelligence:</h3>
                <ul>
                <li>📊 <strong>Cost Analysis</strong> - Compare supplier pricing</li>
                <li>⏰ <strong>Lead Times</strong> - Track delivery performance</li>
                <li>🎯 <strong>Preferred Vendors</strong> - Mark top-performing suppliers</li>
                <li>📈 <strong>Purchase Analytics</strong> - Spending patterns by supplier</li>
                </ul>
                """,
                action=lambda: self.navigate_to_tab(4) if self.main_window else None,
                duration=4000
            ),
            
            # Reports & Analytics
            DemoStep(
                "📈 Reports & Analytics - Data-Driven Decisions",
                """
                <h2>Comprehensive Business Intelligence</h2>
                
                <p>Make informed decisions with detailed reports, analytics, 
                and business intelligence tools.</p>
                
                <h3>Report Categories:</h3>
                <ul>
                <li><strong>Sales Reports</strong> - Daily, weekly, monthly revenue analysis</li>
                <li><strong>Product Performance</strong> - Best sellers, profit margins</li>
                <li><strong>Customer Analytics</strong> - Behavior patterns, loyalty metrics</li>
                <li><strong>Inventory Reports</strong> - Stock levels, turnover rates</li>
                <li><strong>Financial Summaries</strong> - P&L, cash flow, tax reports</li>
                <li><strong>Discount Analytics</strong> - Promotion effectiveness</li>
                </ul>
                
                <h3>Advanced Analytics:</h3>
                <ul>
                <li>📊 <strong>Interactive Charts</strong> - Visual data representation</li>
                <li>📅 <strong>Date Range Filters</strong> - Custom period analysis</li>
                <li>📁 <strong>Export Options</strong> - PDF, Excel, CSV formats</li>
                <li>🔄 <strong>Scheduled Reports</strong> - Automated report generation</li>
                </ul>
                """,
                action=lambda: self.navigate_to_tab(5) if self.main_window else None,
                duration=4000
            ),
            
            # User Management
            DemoStep(
                "👤 User Management - Multi-User & Security",
                """
                <h2>Advanced User Management & Security</h2>
                
                <p>Secure multi-user environment with role-based access control 
                and comprehensive audit trails.</p>
                
                <h3>User System Features:</h3>
                <ul>
                <li><strong>Role-Based Access</strong> - Admin, Manager, Cashier roles</li>
                <li><strong>User Profiles</strong> - Individual accounts and preferences</li>
                <li><strong>Permission Control</strong> - Fine-grained access management</li>
                <li><strong>Session Management</strong> - Secure login/logout tracking</li>
                <li><strong>Password Security</strong> - Change password functionality</li>
                <li><strong>Activity Logging</strong> - Complete user action audit trail</li>
                </ul>
                
                <h3>Security Features:</h3>
                <ul>
                <li>🔐 <strong>Secure Authentication</strong> - Encrypted password storage</li>
                <li>📝 <strong>Audit Trails</strong> - Track all user activities</li>
                <li>🛡️ <strong>Role Enforcement</strong> - Restrict access by user type</li>
                <li>⏰ <strong>Session Tracking</strong> - Monitor active sessions</li>
                </ul>
                """,
                action=lambda: self.navigate_to_tab(6) if self.main_window else None,
                duration=4000
            ),
            
            # Tax Configuration
            DemoStep(
                "💰 Tax Configuration - Dynamic Tax Management",
                """
                <h2>Professional Tax Management System</h2>
                
                <p>Configure and manage complex tax structures with support for 
                multiple tax categories and rates.</p>
                
                <h3>Tax Management Features:</h3>
                <ul>
                <li><strong>Tax Categories</strong> - Standard, Food, Medical, Luxury rates</li>
                <li><strong>Dynamic Rates</strong> - Easily adjust tax percentages</li>
                <li><strong>Product Assignment</strong> - Link products to tax categories</li>
                <li><strong>Real-time Updates</strong> - Instant POS system updates</li>
                <li><strong>Tax History</strong> - Track rate changes over time</li>
                <li><strong>Compliance Tools</strong> - Support for local tax regulations</li>
                </ul>
                
                <h3>Advanced Tax Features:</h3>
                <ul>
                <li>🎯 <strong>Category-Based</strong> - Different rates for product types</li>
                <li>📊 <strong>Tax Reporting</strong> - Detailed tax collection reports</li>
                <li>⚙️ <strong>Easy Configuration</strong> - User-friendly tax setup</li>
                <li>🔄 <strong>Automatic Calculation</strong> - POS integration</li>
                </ul>
                
                <p><em>Access via toolbar: Tax Config button</em></p>
                """,
                duration=4000
            ),
            
            # Discount Management
            DemoStep(
                "🎯 Discount Management - Advanced Promotion System",
                """
                <h2>Intelligent Discount & Promotion Engine</h2>
                
                <p>Create sophisticated discount rules that automatically apply 
                during checkout based on customer, purchase, and timing criteria.</p>
                
                <h3>Discount Types:</h3>
                <ul>
                <li><strong>Percentage Discounts</strong> - 10% off, 25% off, etc.</li>
                <li><strong>Fixed Amount</strong> - $10 off, $50 off orders</li>
                <li><strong>Customer Tier</strong> - VIP, Premium customer discounts</li>
                <li><strong>Volume Discounts</strong> - Bulk purchase incentives</li>
                <li><strong>Minimum Purchase</strong> - Spend $X, save $Y deals</li>
                <li><strong>Time-Limited</strong> - Promotional periods and expiration</li>
                </ul>
                
                <h3>Smart Features:</h3>
                <ul>
                <li>🤖 <strong>Auto-Application</strong> - Best discount automatically applied</li>
                <li>📊 <strong>Usage Analytics</strong> - Track promotion effectiveness</li>
                <li>🎯 <strong>Rule Testing</strong> - Preview discount calculations</li>
                <li>📈 <strong>Performance Metrics</strong> - ROI on promotions</li>
                </ul>
                
                <p><em>Access via toolbar: Discount Management button</em></p>
                """,
                duration=4000
            ),
            
            # System Features
            DemoStep(
                "⚙️ System Features - Professional Tools",
                """
                <h2>Enterprise-Grade System Features</h2>
                
                <p>Shop Manager Pro includes professional tools for logging, 
                monitoring, and system management.</p>
                
                <h3>System Tools:</h3>
                <ul>
                <li><strong>Comprehensive Logging</strong> - All activities tracked</li>
                <li><strong>Crash Recovery</strong> - Automatic error reporting</li>
                <li><strong>Database Backup</strong> - Automatic data protection</li>
                <li><strong>Performance Monitoring</strong> - System health checks</li>
                <li><strong>Settings Management</strong> - Customizable preferences</li>
                <li><strong>Data Export</strong> - Multiple format support</li>
                </ul>
                
                <h3>Professional Features:</h3>
                <ul>
                <li>📝 <strong>Audit Trail</strong> - Complete activity history</li>
                <li>🔒 <strong>Data Security</strong> - Encrypted sensitive information</li>
                <li>🎨 <strong>Modern UI</strong> - Professional design system</li>
                <li>⌨️ <strong>Keyboard Shortcuts</strong> - Power user efficiency</li>
                <li>📱 <strong>Responsive Design</strong> - Works on different screen sizes</li>
                <li>🌐 <strong>Privacy Focused</strong> - Optional telemetry (opt-in)</li>
                </ul>
                """,
                duration=4000
            ),
            
            # Getting Started
            DemoStep(
                "🚀 Getting Started - Your Next Steps",
                """
                <h2>Ready to Start Using Shop Manager Pro!</h2>
                
                <p>You've completed the demo tour! Here are your recommended next steps 
                to get your business up and running.</p>
                
                <h3>Quick Start Checklist:</h3>
                <ol>
                <li>✅ <strong>Set Up Tax Rates</strong> - Configure your local tax rates</li>
                <li>✅ <strong>Add Suppliers</strong> - Enter your vendor information</li>
                <li>✅ <strong>Import Products</strong> - Add your inventory</li>
                <li>✅ <strong>Create Customer Tiers</strong> - Set up loyalty programs</li>
                <li>✅ <strong>Configure Discounts</strong> - Create promotional rules</li>
                <li>✅ <strong>Train Your Team</strong> - Show staff the POS system</li>
                </ol>
                
                <h3>Pro Tips for Success:</h3>
                <ul>
                <li>💡 Start with the POS system for immediate sales processing</li>
                <li>📊 Check the Dashboard daily for business insights</li>
                <li>🎯 Use discount rules to boost sales and customer loyalty</li>
                <li>📈 Review Reports weekly to track performance</li>
                <li>🔄 Keep inventory updated for accurate stock levels</li>
                </ul>
                
                <h3>Need Help?</h3>
                <ul>
                <li>📖 <strong>Help Menu</strong> - Built-in documentation</li>
                <li>🎓 <strong>Re-run Demo</strong> - Available anytime from Help menu</li>
                <li>📝 <strong>System Logs</strong> - Detailed activity tracking</li>
                </ul>
                """,
                duration=5000
            )
        ]
        
        self.progress_bar.setMaximum(len(self.steps))
        self.update_step_display()
    
    def navigate_to_tab(self, index):
        """Navigate main window to specific tab"""
        if self.main_window and hasattr(self.main_window, 'content_area'):
            self.main_window.content_area.setCurrentIndex(index)
            # Also update navigation buttons
            if hasattr(self.main_window, 'nav_buttons'):
                for i, btn in enumerate(self.main_window.nav_buttons):
                    btn.setChecked(i == index)
    
    def update_step_display(self):
        """Update the display for the current step"""
        if not self.steps or self.current_step >= len(self.steps):
            return
        
        step = self.steps[self.current_step]
        
        # Update progress
        self.progress_bar.setValue(self.current_step + 1)
        
        # Update content
        self.step_title.setText(step.title)
        self.step_description.setHtml(step.description)
        
        # Update navigation buttons
        self.prev_btn.setEnabled(self.current_step > 0)
        
        if self.current_step == len(self.steps) - 1:
            self.next_btn.hide()
            self.finish_btn.show()
        else:
            self.next_btn.show()
            self.finish_btn.hide()
        
        # Execute step action
        if step.action:
            try:
                step.action()
            except Exception as e:
                log_info(f"Demo step action error: {e}")
        
        # Set up auto-advance timer if needed
        if step.next_auto and step.duration > 0:
            self.auto_timer.start(step.duration)
        
        # Add tips based on step
        self.update_tips(self.current_step)
        
        log_user_action(f"demo_step_viewed", f"step: {self.current_step + 1}, title: {step.title}")
    
    def update_tips(self, step_index):
        """Update tips based on current step"""
        tips = {
            0: "Take your time! This demo will help you understand all features.",
            1: "The Dashboard updates in real-time as you use the system.",
            2: "Try adding products to your cart and see the smart pricing in action!",
            3: "Products are organized with SKUs for easy barcode scanning.",
            4: "Customer tiers automatically apply different discount rates.",
            5: "Suppliers can be linked to multiple products for easy reordering.",
            6: "All reports can be exported to PDF or Excel for external use.",
            7: "Different user roles see different features based on permissions.",
            8: "Tax rates automatically apply based on product categories.",
            9: "Discounts can stack and the system always applies the best deal.",
            10: "All system activities are logged for security and troubleshooting.",
            11: "You can re-run this demo anytime from the Help menu!"
        }
        
        tip_text = tips.get(step_index, "Explore the interface and try different features!")
        self.tips_text.setText(tip_text)
    
    def next_step(self):
        """Move to the next step"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_step_display()
            log_user_action(f"demo_step_next", f"moved to step {self.current_step + 1}")
    
    def previous_step(self):
        """Move to the previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step_display()
            log_user_action(f"demo_step_previous", f"moved to step {self.current_step + 1}")
    
    def auto_next_step(self):
        """Auto-advance to next step"""
        self.next_step()
    
    def skip_demo(self):
        """Skip the demo"""
        reply = QMessageBox.question(
            self, "Skip Demo",
            "Are you sure you want to skip the demo?\n\n"
            "You can always run it again from the Help menu.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            log_user_action("demo_skipped", f"at step {self.current_step + 1}")
            self.mark_demo_completed()
            self.reject()
    
    def finish_demo(self):
        """Complete the demo"""
        log_user_action("demo_completed")
        self.mark_demo_completed()
        
        # Show completion message
        QMessageBox.information(
            self, "Demo Complete! 🎉",
            "Congratulations! You've completed the Shop Manager Pro demo.\n\n"
            "You're now ready to start using the application.\n\n"
            "Tips:\n"
            "• Start with the POS system for immediate sales\n"
            "• Check the Dashboard regularly for insights\n"
            "• Use the Help menu if you need assistance\n\n"
            "Happy selling! 🛒"
        )
        
        self.demo_finished.emit()
        self.accept()
    
    def mark_demo_completed(self):
        """Mark demo as completed in settings"""
        try:
            settings_file = "logs/settings.json"
            settings = {}
            
            # Load existing settings
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            
            # Mark demo as completed
            settings["demo_completed"] = True
            settings["demo_completed_date"] = datetime.now().isoformat()
            
            # Ensure logs directory exists
            os.makedirs("logs", exist_ok=True)
            
            # Save settings
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
            log_info("Demo marked as completed in settings")
            
        except Exception as e:
            log_info(f"Failed to save demo completion status: {e}")
    
    def apply_styles(self):
        """Apply modern styles to the demo dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            #demoHeader {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 10px;
            }
            
            #demoTitle {
                color: white;
                font-size: 24px;
                font-weight: bold;
                margin: 0;
            }
            
            #demoSubtitle {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                margin: 5px 0 0 0;
            }
            
            #demoProgress {
                height: 8px;
                border-radius: 4px;
                background-color: #e9ecef;
                margin: 10px 0;
            }
            
            #demoProgress::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #007bff, stop:1 #28a745);
                border-radius: 4px;
            }
            
            #demoContent {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #e9ecef;
            }
            
            #stepTitle {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
            }
            
            #stepDescription {
                border: none;
                background-color: transparent;
                font-size: 14px;
                line-height: 1.6;
                color: #495057;
            }
            
            #tipsFrame {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
                margin-top: 15px;
            }
            
            #tipsLabel {
                font-weight: bold;
                color: #fd7e14;
                font-size: 14px;
                margin-bottom: 8px;
            }
            
            #tipsText {
                color: #6c757d;
                font-size: 13px;
                font-style: italic;
            }
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #004085;
            }
            
            #navButton {
                background-color: #6c757d;
            }
            
            #navButton:hover {
                background-color: #5a6268;
            }
            
            #navButton:disabled {
                background-color: #e9ecef;
                color: #6c757d;
            }
            
            #skipButton {
                background-color: #dc3545;
            }
            
            #skipButton:hover {
                background-color: #c82333;
            }
            
            #finishButton {
                background-color: #28a745;
                font-size: 16px;
                padding: 12px 24px;
            }
            
            #finishButton:hover {
                background-color: #218838;
            }
        """)


def should_show_demo():
    """Check if demo should be shown (first time use)"""
    try:
        settings_file = "logs/settings.json"
        
        if not os.path.exists(settings_file):
            return True
        
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        return not settings.get("demo_completed", False)
        
    except Exception:
        return True  # Show demo if we can't determine status


def show_demo_dialog(main_window=None):
    """Show the demo dialog"""
    demo = DemoDialog(main_window)
    return demo.exec()


if __name__ == "__main__":
    # Test the demo dialog
    app = QApplication([])
    demo = DemoDialog()
    demo.show()
    app.exec()