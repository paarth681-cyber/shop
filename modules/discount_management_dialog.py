"""
Discount Management Dialog
Allows administrators to create and manage discount rules
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                           QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
                           QComboBox, QHeaderView, QMessageBox, QGroupBox,
                           QFormLayout, QDoubleSpinBox, QCheckBox, QSpinBox,
                           QDateEdit, QTabWidget, QWidget, QScrollArea, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QIcon
import sqlite3
from datetime import datetime, date
from logger_config import log_info, log_error, log_user_action, log_db_operation


class DiscountManagementDialog(QDialog):
    """Dialog for managing discount rules and promotions"""
    
    discounts_updated = pyqtSignal()  # Signal emitted when discount rules are modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Discount Management")
        self.setModal(True)
        self.resize(1000, 700)
        
        # Database connection
        self.db_path = "shop_manager.db"
        
        self.setup_ui()
        self.setup_styles()
        self.create_discount_tables()
        self.load_discount_rules()
        
        log_user_action("discount_management_opened")
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Discount & Promotion Management")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Discount Rules Tab
        rules_tab = QWidget()
        self.setup_rules_tab(rules_tab)
        tab_widget.addTab(rules_tab, "Discount Rules")
        
        # Active Promotions Tab
        promotions_tab = QWidget()
        self.setup_promotions_tab(promotions_tab)
        tab_widget.addTab(promotions_tab, "Active Promotions")
        
        layout.addWidget(tab_widget)
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Store current editing item
        self.current_editing_id = None
    
    def setup_rules_tab(self, parent):
        """Set up the discount rules tab"""
        layout = QHBoxLayout(parent)
        
        # Left side - Discount rules table
        left_group = QGroupBox("Discount Rules")
        left_layout = QVBoxLayout(left_group)
        
        # Discount rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(8)
        self.rules_table.setHorizontalHeaderLabels([
            "Name", "Type", "Value", "Min Qty", "Min Amount", "Customer Tier", "Valid Period", "Active"
        ])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rules_table.itemSelectionChanged.connect(self.on_rule_selection_changed)
        left_layout.addWidget(self.rules_table)
        
        # Rule table buttons
        rule_buttons_layout = QHBoxLayout()
        self.add_rule_btn = QPushButton("Add Rule")
        self.edit_rule_btn = QPushButton("Edit Selected")
        self.delete_rule_btn = QPushButton("Delete Selected")
        self.test_rule_btn = QPushButton("Test Rule")
        
        self.edit_rule_btn.setEnabled(False)
        self.delete_rule_btn.setEnabled(False)
        self.test_rule_btn.setEnabled(False)
        
        self.add_rule_btn.clicked.connect(self.add_discount_rule)
        self.edit_rule_btn.clicked.connect(self.edit_discount_rule)
        self.delete_rule_btn.clicked.connect(self.delete_discount_rule)
        self.test_rule_btn.clicked.connect(self.test_discount_rule)
        
        rule_buttons_layout.addWidget(self.add_rule_btn)
        rule_buttons_layout.addWidget(self.edit_rule_btn)
        rule_buttons_layout.addWidget(self.delete_rule_btn)
        rule_buttons_layout.addWidget(self.test_rule_btn)
        rule_buttons_layout.addStretch()
        left_layout.addLayout(rule_buttons_layout)
        
        layout.addWidget(left_group, 2)
        
        # Right side - Discount rule form
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        right_group = QGroupBox("Discount Rule Details")
        right_layout = QFormLayout(right_group)
        
        # Basic rule information
        self.rule_name_input = QLineEdit()
        self.rule_name_input.setPlaceholderText("e.g., '10% off bulk orders'")
        
        self.rule_type_combo = QComboBox()
        self.rule_type_combo.addItems([
            "percentage", "fixed_amount", "buy_x_get_y", "customer_tier"
        ])
        self.rule_type_combo.currentTextChanged.connect(self.on_rule_type_changed)
        
        self.rule_value_input = QDoubleSpinBox()
        self.rule_value_input.setRange(0.0, 10000.0)
        self.rule_value_input.setDecimals(2)
        
        # Conditions
        self.min_quantity_input = QSpinBox()
        self.min_quantity_input.setRange(0, 1000)
        self.min_quantity_input.setSpecialValueText("No minimum")
        
        self.min_amount_input = QDoubleSpinBox()
        self.min_amount_input.setRange(0.0, 100000.0)
        self.min_amount_input.setDecimals(2)
        self.min_amount_input.setSpecialValueText("No minimum")
        self.min_amount_input.setPrefix("$")
        
        self.customer_tier_combo = QComboBox()
        self.customer_tier_combo.addItems(["Any", "regular", "premium", "vip"])
        
        # Validity period
        self.valid_from_date = QDateEdit()
        self.valid_from_date.setDate(QDate.currentDate())
        self.valid_from_date.setCalendarPopup(True)
        
        self.valid_to_date = QDateEdit()
        self.valid_to_date.setDate(QDate.currentDate().addDays(30))
        self.valid_to_date.setCalendarPopup(True)
        
        # Advanced options
        self.active_checkbox = QCheckBox("Active")
        self.active_checkbox.setChecked(True)
        
        self.stackable_checkbox = QCheckBox("Stackable with other discounts")
        
        # Description/Notes
        self.rule_description = QTextEdit()
        self.rule_description.setMaximumHeight(80)
        self.rule_description.setPlaceholderText("Optional description or notes about this discount rule...")
        
        # Add fields to form
        right_layout.addRow("Rule Name:", self.rule_name_input)
        right_layout.addRow("Discount Type:", self.rule_type_combo)
        right_layout.addRow("Value:", self.rule_value_input)
        right_layout.addRow("", QLabel())  # Spacer
        
        conditions_label = QLabel("Conditions:")
        conditions_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_layout.addRow("", conditions_label)
        
        right_layout.addRow("Min Quantity:", self.min_quantity_input)
        right_layout.addRow("Min Amount:", self.min_amount_input)
        right_layout.addRow("Customer Tier:", self.customer_tier_combo)
        right_layout.addRow("", QLabel())  # Spacer
        
        validity_label = QLabel("Validity Period:")
        validity_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_layout.addRow("", validity_label)
        
        right_layout.addRow("Valid From:", self.valid_from_date)
        right_layout.addRow("Valid To:", self.valid_to_date)
        right_layout.addRow("", QLabel())  # Spacer
        
        options_label = QLabel("Options:")
        options_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_layout.addRow("", options_label)
        
        right_layout.addRow("", self.active_checkbox)
        right_layout.addRow("", self.stackable_checkbox)
        right_layout.addRow("Description:", self.rule_description)
        
        # Form buttons
        form_buttons_layout = QHBoxLayout()
        self.save_rule_btn = QPushButton("Save Rule")
        self.clear_form_btn = QPushButton("Clear Form")
        
        self.save_rule_btn.clicked.connect(self.save_discount_rule)
        self.clear_form_btn.clicked.connect(self.clear_rule_form)
        
        form_buttons_layout.addWidget(self.save_rule_btn)
        form_buttons_layout.addWidget(self.clear_form_btn)
        form_buttons_layout.addStretch()
        right_layout.addRow("", form_buttons_layout)
        
        # Quick presets
        presets_label = QLabel("Quick Presets:")
        presets_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_layout.addRow("", presets_label)
        
        presets_layout = QVBoxLayout()
        preset_buttons = [
            ("10% off $100+", "percentage", 10.0, 0, 100.0, "Any"),
            ("$20 off $200+", "fixed_amount", 20.0, 0, 200.0, "Any"),
            ("VIP 15% off", "customer_tier", 15.0, 0, 0.0, "vip"),
            ("Buy 5 Get 10%", "percentage", 10.0, 5, 0.0, "Any")
        ]
        
        for name, disc_type, value, min_qty, min_amt, tier in preset_buttons:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, n=name, t=disc_type, v=value, q=min_qty, a=min_amt, c=tier: 
                              self.apply_rule_preset(n, t, v, q, a, c))
            presets_layout.addWidget(btn)
        
        right_layout.addRow("", presets_layout)
        
        scroll_layout.addWidget(right_group)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area, 1)
    
    def setup_promotions_tab(self, parent):
        """Set up the active promotions tab"""
        layout = QVBoxLayout(parent)
        
        # Stats section
        stats_group = QGroupBox("Promotion Statistics")
        stats_layout = QHBoxLayout(stats_group)
        
        self.active_promos_label = QLabel("Active Promotions: 0")
        self.total_savings_label = QLabel("Total Savings Today: $0.00")
        self.most_used_label = QLabel("Most Used: None")
        
        stats_layout.addWidget(self.active_promos_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.total_savings_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.most_used_label)
        
        layout.addWidget(stats_group)
        
        # Active promotions table
        promo_group = QGroupBox("Active Promotions")
        promo_layout = QVBoxLayout(promo_group)
        
        self.promotions_table = QTableWidget()
        self.promotions_table.setColumnCount(6)
        self.promotions_table.setHorizontalHeaderLabels([
            "Name", "Type", "Value", "Uses Today", "Total Savings", "Expires"
        ])
        self.promotions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        promo_layout.addWidget(self.promotions_table)
        
        # Promotion buttons
        promo_buttons_layout = QHBoxLayout()
        self.refresh_promos_btn = QPushButton("Refresh")
        self.deactivate_promo_btn = QPushButton("Deactivate Selected")
        self.view_usage_btn = QPushButton("View Usage Details")
        
        self.refresh_promos_btn.clicked.connect(self.refresh_promotions)
        self.deactivate_promo_btn.clicked.connect(self.deactivate_promotion)
        self.view_usage_btn.clicked.connect(self.view_usage_details)
        
        promo_buttons_layout.addWidget(self.refresh_promos_btn)
        promo_buttons_layout.addWidget(self.deactivate_promo_btn)
        promo_buttons_layout.addWidget(self.view_usage_btn)
        promo_buttons_layout.addStretch()
        promo_layout.addLayout(promo_buttons_layout)
        
        layout.addWidget(promo_group)
    
    def setup_styles(self):
        """Set up dialog styles"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            #dialogTitle {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px 0;
                text-align: center;
            }
            
            QTabWidget::pane {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #f1f3f4;
                color: #495057;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            
            QTabBar::tab:selected {
                background-color: #007bff;
                color: white;
            }
            
            QTabBar::tab:hover {
                background-color: #0056b3;
                color: white;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: #f8f9fa;
            }
            
            QTableWidget {
                background-color: white;
                gridline-color: #e9ecef;
                selection-background-color: #007bff;
                selection-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e9ecef;
            }
            
            QHeaderView::section {
                background-color: #f1f3f4;
                color: #495057;
                padding: 10px;
                border: none;
                border-right: 1px solid #dee2e6;
                font-weight: bold;
            }
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #004085;
            }
            
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
            
            QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QDateEdit {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
            }
            
            QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            
            QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
                padding: 8px;
            }
            
            QTextEdit:focus {
                border-color: #007bff;
            }
            
            QCheckBox {
                font-weight: bold;
                color: #495057;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
    
    def create_discount_tables(self):
        """Create discount-related tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Discount rules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discount_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    discount_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    min_quantity INTEGER DEFAULT 0,
                    min_amount REAL DEFAULT 0.0,
                    customer_tier TEXT,
                    valid_from DATE,
                    valid_to DATE,
                    is_active INTEGER DEFAULT 1,
                    is_stackable INTEGER DEFAULT 0,
                    description TEXT,
                    usage_count INTEGER DEFAULT 0,
                    total_savings REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Discount usage log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discount_usage_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discount_rule_id INTEGER NOT NULL,
                    sale_id INTEGER,
                    discount_amount REAL NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (discount_rule_id) REFERENCES discount_rules (id),
                    FOREIGN KEY (sale_id) REFERENCES sales (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            log_info("DATABASE: Discount tables created/verified")
            
        except sqlite3.Error as e:
            log_error(f"DATABASE ERROR: Failed to create discount tables: {e}")
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to create discount tables:\n{e}")
    
    def load_discount_rules(self):
        """Load discount rules from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, discount_type, value, min_quantity, min_amount,
                       customer_tier, valid_from, valid_to, is_active
                FROM discount_rules
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            
            self.rules_table.setRowCount(len(rows))
            
            for row_idx, (rule_id, name, disc_type, value, min_qty, min_amt, 
                         tier, valid_from, valid_to, is_active) in enumerate(rows):
                
                self.rules_table.setItem(row_idx, 0, QTableWidgetItem(name))
                self.rules_table.setItem(row_idx, 1, QTableWidgetItem(disc_type.replace('_', ' ').title()))
                
                # Format value based on type
                if disc_type == 'percentage':
                    value_text = f"{value}%"
                else:
                    value_text = f"${value:.2f}"
                self.rules_table.setItem(row_idx, 2, QTableWidgetItem(value_text))
                
                self.rules_table.setItem(row_idx, 3, QTableWidgetItem(str(min_qty) if min_qty else "-"))
                self.rules_table.setItem(row_idx, 4, QTableWidgetItem(f"${min_amt:.2f}" if min_amt else "-"))
                self.rules_table.setItem(row_idx, 5, QTableWidgetItem(tier if tier and tier != 'Any' else "All"))
                
                # Format validity period
                if valid_from and valid_to:
                    period = f"{valid_from} to {valid_to}"
                else:
                    period = "No expiry"
                self.rules_table.setItem(row_idx, 6, QTableWidgetItem(period))
                
                # Active status
                status_item = QTableWidgetItem("✓ Active" if is_active else "✗ Inactive")
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.rules_table.setItem(row_idx, 7, status_item)
                
                # Store rule ID in first column for reference
                self.rules_table.item(row_idx, 0).setData(Qt.ItemDataRole.UserRole, rule_id)
            
            conn.close()
            log_info(f"DATABASE: Loaded {len(rows)} discount rules")
            
            # Load promotion stats
            self.load_promotion_stats()
            
        except sqlite3.Error as e:
            log_error(f"DATABASE ERROR: Failed to load discount rules: {e}")
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to load discount rules:\n{e}")
    
    def load_promotion_stats(self):
        """Load and display promotion statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count active promotions
            cursor.execute('SELECT COUNT(*) FROM discount_rules WHERE is_active = 1')
            active_count = cursor.fetchone()[0]
            
            # Total savings today
            today = date.today().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COALESCE(SUM(discount_amount), 0)
                FROM discount_usage_log
                WHERE DATE(applied_at) = ?
            ''', (today,))
            total_savings = cursor.fetchone()[0]
            
            # Most used discount today
            cursor.execute('''
                SELECT dr.name, COUNT(*) as usage_count
                FROM discount_usage_log dul
                JOIN discount_rules dr ON dul.discount_rule_id = dr.id
                WHERE DATE(dul.applied_at) = ?
                GROUP BY dr.id
                ORDER BY usage_count DESC
                LIMIT 1
            ''', (today,))
            
            most_used_result = cursor.fetchone()
            most_used = most_used_result[0] if most_used_result else "None"
            
            # Update labels
            self.active_promos_label.setText(f"Active Promotions: {active_count}")
            self.total_savings_label.setText(f"Total Savings Today: ${total_savings:.2f}")
            self.most_used_label.setText(f"Most Used: {most_used}")
            
            # Load active promotions table
            self.load_active_promotions()
            
            conn.close()
            
        except sqlite3.Error as e:
            log_error(f"DATABASE ERROR: Failed to load promotion stats: {e}")
    
    def load_active_promotions(self):
        """Load active promotions into the promotions table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = date.today().strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT dr.id, dr.name, dr.discount_type, dr.value, dr.valid_to,
                       COALESCE(COUNT(dul.id), 0) as uses_today,
                       COALESCE(SUM(dul.discount_amount), 0) as total_savings_today
                FROM discount_rules dr
                LEFT JOIN discount_usage_log dul ON dr.id = dul.discount_rule_id 
                    AND DATE(dul.applied_at) = ?
                WHERE dr.is_active = 1 
                    AND (dr.valid_to IS NULL OR dr.valid_to >= ?)
                GROUP BY dr.id
                ORDER BY uses_today DESC
            ''', (today, today))
            
            rows = cursor.fetchall()
            
            self.promotions_table.setRowCount(len(rows))
            
            for row_idx, (rule_id, name, disc_type, value, valid_to, uses_today, savings_today) in enumerate(rows):
                self.promotions_table.setItem(row_idx, 0, QTableWidgetItem(name))
                self.promotions_table.setItem(row_idx, 1, QTableWidgetItem(disc_type.replace('_', ' ').title()))
                
                # Format value
                if disc_type == 'percentage':
                    value_text = f"{value}%"
                else:
                    value_text = f"${value:.2f}"
                self.promotions_table.setItem(row_idx, 2, QTableWidgetItem(value_text))
                
                self.promotions_table.setItem(row_idx, 3, QTableWidgetItem(str(uses_today)))
                self.promotions_table.setItem(row_idx, 4, QTableWidgetItem(f"${savings_today:.2f}"))
                
                # Format expiry
                expiry = valid_to if valid_to else "Never"
                self.promotions_table.setItem(row_idx, 5, QTableWidgetItem(expiry))
                
                # Store rule ID for reference
                self.promotions_table.item(row_idx, 0).setData(Qt.ItemDataRole.UserRole, rule_id)
            
            conn.close()
            
        except sqlite3.Error as e:
            log_error(f"DATABASE ERROR: Failed to load active promotions: {e}")
    
    def on_rule_selection_changed(self):
        """Handle discount rule selection change"""
        selected_rows = self.rules_table.selectionModel().selectedRows()
        
        if selected_rows:
            self.edit_rule_btn.setEnabled(True)
            self.delete_rule_btn.setEnabled(True)
            self.test_rule_btn.setEnabled(True)
            
            # Load selected rule into form
            row = selected_rows[0].row()
            rule_id = self.rules_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.load_rule_into_form(rule_id)
        else:
            self.edit_rule_btn.setEnabled(False)
            self.delete_rule_btn.setEnabled(False)
            self.test_rule_btn.setEnabled(False)
            self.current_editing_id = None
    
    def load_rule_into_form(self, rule_id):
        """Load discount rule data into the form"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, discount_type, value, min_quantity, min_amount,
                       customer_tier, valid_from, valid_to, is_active, 
                       is_stackable, description
                FROM discount_rules WHERE id = ?
            ''', (rule_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                (name, disc_type, value, min_qty, min_amt, tier, valid_from, 
                 valid_to, is_active, is_stackable, description) = result
                
                self.rule_name_input.setText(name)
                
                # Set discount type
                type_index = self.rule_type_combo.findText(disc_type)
                if type_index >= 0:
                    self.rule_type_combo.setCurrentIndex(type_index)
                
                self.rule_value_input.setValue(value)
                self.min_quantity_input.setValue(min_qty or 0)
                self.min_amount_input.setValue(min_amt or 0.0)
                
                # Set customer tier
                if tier:
                    tier_index = self.customer_tier_combo.findText(tier)
                    if tier_index >= 0:
                        self.customer_tier_combo.setCurrentIndex(tier_index)
                else:
                    self.customer_tier_combo.setCurrentIndex(0)  # "Any"
                
                # Set dates
                if valid_from:
                    self.valid_from_date.setDate(QDate.fromString(valid_from, "yyyy-MM-dd"))
                if valid_to:
                    self.valid_to_date.setDate(QDate.fromString(valid_to, "yyyy-MM-dd"))
                
                self.active_checkbox.setChecked(bool(is_active))
                self.stackable_checkbox.setChecked(bool(is_stackable))
                
                if description:
                    self.rule_description.setPlainText(description)
                
                self.current_editing_id = rule_id
                
        except sqlite3.Error as e:
            log_error(f"DATABASE ERROR: Failed to load rule {rule_id}: {e}")
    
    def on_rule_type_changed(self, rule_type):
        """Handle discount type change to update UI"""
        if rule_type == "percentage":
            self.rule_value_input.setSuffix("%")
            self.rule_value_input.setMaximum(100.0)
        else:
            self.rule_value_input.setSuffix("")
            self.rule_value_input.setMaximum(10000.0)
            self.rule_value_input.setPrefix("$")
    
    def apply_rule_preset(self, name, disc_type, value, min_qty, min_amt, tier):
        """Apply a preset discount rule"""
        self.rule_name_input.setText(name)
        
        type_index = self.rule_type_combo.findText(disc_type)
        if type_index >= 0:
            self.rule_type_combo.setCurrentIndex(type_index)
        
        self.rule_value_input.setValue(value)
        self.min_quantity_input.setValue(min_qty)
        self.min_amount_input.setValue(min_amt)
        
        tier_index = self.customer_tier_combo.findText(tier)
        if tier_index >= 0:
            self.customer_tier_combo.setCurrentIndex(tier_index)
        
        self.current_editing_id = None
        log_user_action(f"discount_preset_applied | name: {name}")
    
    def add_discount_rule(self):
        """Start adding a new discount rule"""
        self.clear_rule_form()
        self.rule_name_input.setFocus()
        log_user_action("discount_add_started")
    
    def edit_discount_rule(self):
        """Edit selected discount rule"""
        if not self.current_editing_id:
            QMessageBox.warning(self, "Warning", "Please select a discount rule to edit.")
            return
        
        log_user_action(f"discount_edit_started | id: {self.current_editing_id}")
    
    def delete_discount_rule(self):
        """Delete selected discount rule"""
        if not self.current_editing_id:
            QMessageBox.warning(self, "Warning", "Please select a discount rule to delete.")
            return
        
        rule_name = self.rule_name_input.text()
        
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the '{rule_name}' discount rule?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM discount_rules WHERE id = ?', (self.current_editing_id,))
                conn.commit()
                conn.close()
                
                log_user_action(f"discount_deleted | name: {rule_name}, id: {self.current_editing_id}")
                
                self.load_discount_rules()
                self.clear_rule_form()
                self.discounts_updated.emit()
                
                QMessageBox.information(self, "Success", 
                                      f"Discount rule '{rule_name}' deleted successfully.")
                
            except sqlite3.Error as e:
                log_error(f"DATABASE ERROR: Failed to delete discount rule: {e}")
                QMessageBox.critical(self, "Database Error", 
                                   f"Failed to delete discount rule:\n{e}")
    
    def test_discount_rule(self):
        """Test the selected discount rule"""
        if not self.current_editing_id:
            QMessageBox.warning(self, "Warning", "Please select a discount rule to test.")
            return
        
        # Simple test dialog (can be expanded)
        test_amount = 150.0
        test_quantity = 3
        
        # Calculate discount (simplified)
        rule_type = self.rule_type_combo.currentText()
        value = self.rule_value_input.value()
        min_qty = self.min_quantity_input.value()
        min_amt = self.min_amount_input.value()
        
        if test_quantity < min_qty or test_amount < min_amt:
            discount = 0
            message = f"Test failed: Conditions not met\n" \
                     f"(Min qty: {min_qty}, Min amount: ${min_amt:.2f})"
        else:
            if rule_type == "percentage":
                discount = test_amount * (value / 100)
            else:
                discount = value
            
            message = f"Test successful!\n" \
                     f"Test amount: ${test_amount:.2f}\n" \
                     f"Test quantity: {test_quantity}\n" \
                     f"Discount applied: ${discount:.2f}\n" \
                     f"Final amount: ${test_amount - discount:.2f}"
        
        QMessageBox.information(self, "Discount Rule Test", message)
        log_user_action(f"discount_rule_tested | id: {self.current_editing_id}, discount: ${discount:.2f}")
    
    def save_discount_rule(self):
        """Save discount rule to database"""
        name = self.rule_name_input.text().strip()
        disc_type = self.rule_type_combo.currentText()
        value = self.rule_value_input.value()
        min_qty = self.min_quantity_input.value() or None
        min_amt = self.min_amount_input.value() or None
        tier = self.customer_tier_combo.currentText()
        if tier == "Any":
            tier = None
        
        valid_from = self.valid_from_date.date().toString("yyyy-MM-dd")
        valid_to = self.valid_to_date.date().toString("yyyy-MM-dd")
        is_active = 1 if self.active_checkbox.isChecked() else 0
        is_stackable = 1 if self.stackable_checkbox.isChecked() else 0
        description = self.rule_description.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a rule name.")
            self.rule_name_input.setFocus()
            return
        
        if value <= 0:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid discount value.")
            self.rule_value_input.setFocus()
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if self.current_editing_id:
                # Update existing rule
                cursor.execute('''
                    UPDATE discount_rules 
                    SET name = ?, discount_type = ?, value = ?, min_quantity = ?,
                        min_amount = ?, customer_tier = ?, valid_from = ?, valid_to = ?,
                        is_active = ?, is_stackable = ?, description = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (name, disc_type, value, min_qty, min_amt, tier, valid_from, valid_to,
                      is_active, is_stackable, description, self.current_editing_id))
                
                action = "updated"
                log_user_action(f"discount_updated | name: {name}, id: {self.current_editing_id}")
            else:
                # Insert new rule
                cursor.execute('''
                    INSERT INTO discount_rules (name, discount_type, value, min_quantity,
                                              min_amount, customer_tier, valid_from, valid_to,
                                              is_active, is_stackable, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, disc_type, value, min_qty, min_amt, tier, valid_from, valid_to,
                      is_active, is_stackable, description))
                
                action = "created"
                log_user_action(f"discount_created | name: {name}")
            
            conn.commit()
            conn.close()
            
            self.load_discount_rules()
            self.clear_rule_form()
            self.discounts_updated.emit()
            
            QMessageBox.information(self, "Success", 
                                  f"Discount rule '{name}' {action} successfully.")
            
        except sqlite3.Error as e:
            log_error(f"DATABASE ERROR: Failed to save discount rule: {e}")
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to save discount rule:\n{e}")
    
    def clear_rule_form(self):
        """Clear the discount rule form"""
        self.rule_name_input.clear()
        self.rule_type_combo.setCurrentIndex(0)
        self.rule_value_input.setValue(0.0)
        self.min_quantity_input.setValue(0)
        self.min_amount_input.setValue(0.0)
        self.customer_tier_combo.setCurrentIndex(0)
        self.valid_from_date.setDate(QDate.currentDate())
        self.valid_to_date.setDate(QDate.currentDate().addDays(30))
        self.active_checkbox.setChecked(True)
        self.stackable_checkbox.setChecked(False)
        self.rule_description.clear()
        self.current_editing_id = None
        
        # Clear table selection
        self.rules_table.clearSelection()
    
    def refresh_promotions(self):
        """Refresh promotion statistics and data"""
        self.load_promotion_stats()
        log_user_action("promotions_refreshed")
    
    def deactivate_promotion(self):
        """Deactivate selected promotion"""
        selected_rows = self.promotions_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a promotion to deactivate.")
            return
        
        row = selected_rows[0].row()
        rule_id = self.promotions_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        rule_name = self.promotions_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, "Confirm Deactivation",
            f"Are you sure you want to deactivate '{rule_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('UPDATE discount_rules SET is_active = 0 WHERE id = ?', (rule_id,))
                conn.commit()
                conn.close()
                
                log_user_action(f"promotion_deactivated | name: {rule_name}, id: {rule_id}")
                
                self.load_discount_rules()
                QMessageBox.information(self, "Success", f"Promotion '{rule_name}' deactivated.")
                
            except sqlite3.Error as e:
                log_error(f"DATABASE ERROR: Failed to deactivate promotion: {e}")
                QMessageBox.critical(self, "Database Error", 
                                   f"Failed to deactivate promotion:\n{e}")
    
    def view_usage_details(self):
        """View detailed usage information for selected promotion"""
        selected_rows = self.promotions_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a promotion to view details.")
            return
        
        row = selected_rows[0].row()
        rule_name = self.promotions_table.item(row, 0).text()
        uses_today = self.promotions_table.item(row, 3).text()
        total_savings = self.promotions_table.item(row, 4).text()
        
        # Simple details dialog (can be expanded with more detailed statistics)
        details = f"Promotion: {rule_name}\n" \
                 f"Uses Today: {uses_today}\n" \
                 f"Total Savings Today: {total_savings}\n\n" \
                 f"For more detailed analytics, check the Reports section."
        
        QMessageBox.information(self, "Usage Details", details)
        log_user_action(f"promotion_usage_viewed | name: {rule_name}")


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = DiscountManagementDialog()
    dialog.show()
    sys.exit(app.exec())