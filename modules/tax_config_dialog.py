"""
Tax Configuration Dialog
Allows administrators to manage tax rates for different product categories
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                           QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
                           QComboBox, QHeaderView, QMessageBox, QGroupBox,
                           QFormLayout, QDoubleSpinBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import sqlite3
from logs.logger_config import log_info, log_error, log_user_action, log_db_operation


class TaxConfigDialog(QDialog):
    """Dialog for managing tax rates and categories"""
    
    tax_rates_updated = pyqtSignal()  # Signal emitted when tax rates are modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tax Configuration")
        self.setModal(True)
        self.resize(800, 600)
        
        # Database connection
        self.db_path = "shop_manager.db"
        
        self.setup_ui()
        self.setup_styles()
        self.load_tax_rates()
        
        log_user_action("tax_config_opened")
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Tax Rate Configuration")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        
        # Create main content area
        main_layout = QHBoxLayout()
        
        # Left side - Tax rates table
        left_group = QGroupBox("Tax Rates")
        left_layout = QVBoxLayout(left_group)
        
        # Tax rates table
        self.tax_table = QTableWidget()
        self.tax_table.setColumnCount(4)
        self.tax_table.setHorizontalHeaderLabels(["Category", "Rate (%)", "Description", "Active"])
        self.tax_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tax_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tax_table.itemSelectionChanged.connect(self.on_tax_selection_changed)
        left_layout.addWidget(self.tax_table)
        
        # Tax table buttons
        tax_buttons_layout = QHBoxLayout()
        self.add_tax_btn = QPushButton("Add Tax Rate")
        self.edit_tax_btn = QPushButton("Edit Selected")
        self.delete_tax_btn = QPushButton("Delete Selected")
        self.edit_tax_btn.setEnabled(False)
        self.delete_tax_btn.setEnabled(False)
        
        self.add_tax_btn.clicked.connect(self.add_tax_rate)
        self.edit_tax_btn.clicked.connect(self.edit_tax_rate)
        self.delete_tax_btn.clicked.connect(self.delete_tax_rate)
        
        tax_buttons_layout.addWidget(self.add_tax_btn)
        tax_buttons_layout.addWidget(self.edit_tax_btn)
        tax_buttons_layout.addWidget(self.delete_tax_btn)
        tax_buttons_layout.addStretch()
        left_layout.addLayout(tax_buttons_layout)
        
        main_layout.addWidget(left_group, 2)
        
        # Right side - Tax rate form
        right_group = QGroupBox("Tax Rate Details")
        right_layout = QFormLayout(right_group)
        
        # Form fields
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("e.g., standard, food, medical")
        
        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(0.0, 100.0)
        self.rate_input.setDecimals(3)
        self.rate_input.setSuffix("%")
        self.rate_input.setValue(8.5)
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Brief description of this tax category")
        
        self.active_checkbox = QCheckBox("Active")
        self.active_checkbox.setChecked(True)
        
        right_layout.addRow("Category:", self.category_input)
        right_layout.addRow("Tax Rate:", self.rate_input)
        right_layout.addRow("Description:", self.description_input)
        right_layout.addRow("", self.active_checkbox)
        
        # Form buttons
        form_buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.clear_btn = QPushButton("Clear Form")
        
        self.save_btn.clicked.connect(self.save_tax_rate)
        self.clear_btn.clicked.connect(self.clear_form)
        
        form_buttons_layout.addWidget(self.save_btn)
        form_buttons_layout.addWidget(self.clear_btn)
        form_buttons_layout.addStretch()
        right_layout.addRow("", form_buttons_layout)
        
        # Predefined tax categories section
        presets_label = QLabel("Quick Presets:")
        presets_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        right_layout.addRow("", presets_label)
        
        presets_layout = QVBoxLayout()
        
        preset_buttons = [
            ("Standard (8.5%)", "standard", 8.5, "General merchandise"),
            ("Food (2.0%)", "food", 2.0, "Food and beverages"),
            ("Medical (0.0%)", "medical", 0.0, "Medical supplies and prescriptions"),
            ("Luxury (12.0%)", "luxury", 12.0, "Luxury items and services")
        ]
        
        for text, category, rate, desc in preset_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, c=category, r=rate, d=desc: self.apply_preset(c, r, d))
            presets_layout.addWidget(btn)
        
        right_layout.addRow("", presets_layout)
        
        main_layout.addWidget(right_group, 1)
        layout.addLayout(main_layout)
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Store current editing item
        self.current_editing_id = None
    
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
            
            QLineEdit, QDoubleSpinBox {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
            }
            
            QLineEdit:focus, QDoubleSpinBox:focus {
                border-color: #007bff;
                outline: none;
            }
            
            QCheckBox {
                font-weight: bold;
                color: #495057;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #dee2e6;
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                background-color: #007bff;
                border-color: #007bff;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEuNSA1TDQgN0w4LjUgMi41IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
        """)
    
    def create_tax_rates_table(self):
        """Create tax rates table if it doesn't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tax_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT UNIQUE NOT NULL,
                    rate REAL NOT NULL,
                    description TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default tax rates if table is empty
            cursor.execute('SELECT COUNT(*) FROM tax_rates')
            count = cursor.fetchone()[0]
            
            if count == 0:
                default_rates = [
                    ('standard', 8.5, 'General merchandise tax rate', 1),
                    ('food', 2.0, 'Food and beverages tax rate', 1),
                    ('medical', 0.0, 'Medical supplies and prescriptions', 1)
                ]
                
                cursor.executemany('''
                    INSERT INTO tax_rates (category, rate, description, is_active)
                    VALUES (?, ?, ?, ?)
                ''', default_rates)
                
                log_info("DATABASE: Default tax rates inserted")
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            log_error(f"DATABASE ERROR: Failed to create tax_rates table: {e}")
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to create tax rates table:\n{e}")
    
    def load_tax_rates(self):
        """Load tax rates from database"""
        self.create_tax_rates_table()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, category, rate, description, is_active
                FROM tax_rates
                ORDER BY category
            ''')
            
            rows = cursor.fetchall()
            
            self.tax_table.setRowCount(len(rows))
            
            for row_idx, (tax_id, category, rate, description, is_active) in enumerate(rows):
                self.tax_table.setItem(row_idx, 0, QTableWidgetItem(category))
                self.tax_table.setItem(row_idx, 1, QTableWidgetItem(f"{rate:.3f}"))
                self.tax_table.setItem(row_idx, 2, QTableWidgetItem(description or ""))
                
                # Active status with checkbox-like display
                active_item = QTableWidgetItem("✓ Active" if is_active else "✗ Inactive")
                active_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tax_table.setItem(row_idx, 3, active_item)
                
                # Store tax ID in first column for reference
                self.tax_table.item(row_idx, 0).setData(Qt.ItemDataRole.UserRole, tax_id)
            
            conn.close()
            log_info(f"DATABASE: Loaded {len(rows)} tax rates")
            
        except sqlite3.Error as e:
            log_error(f"DATABASE ERROR: Failed to load tax rates: {e}")
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to load tax rates:\n{e}")
    
    def on_tax_selection_changed(self):
        """Handle tax rate selection change"""
        selected_rows = self.tax_table.selectionModel().selectedRows()
        
        if selected_rows:
            self.edit_tax_btn.setEnabled(True)
            self.delete_tax_btn.setEnabled(True)
            
            # Load selected tax rate into form
            row = selected_rows[0].row()
            category = self.tax_table.item(row, 0).text()
            rate = float(self.tax_table.item(row, 1).text())
            description = self.tax_table.item(row, 2).text()
            is_active = "Active" in self.tax_table.item(row, 3).text()
            tax_id = self.tax_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            
            self.category_input.setText(category)
            self.rate_input.setValue(rate)
            self.description_input.setText(description)
            self.active_checkbox.setChecked(is_active)
            self.current_editing_id = tax_id
            
        else:
            self.edit_tax_btn.setEnabled(False)
            self.delete_tax_btn.setEnabled(False)
            self.current_editing_id = None
    
    def apply_preset(self, category, rate, description):
        """Apply a preset tax rate"""
        self.category_input.setText(category)
        self.rate_input.setValue(rate)
        self.description_input.setText(description)
        self.active_checkbox.setChecked(True)
        self.current_editing_id = None
        
        log_user_action(f"tax_preset_applied | category: {category}, rate: {rate}%")
    
    def add_tax_rate(self):
        """Add new tax rate"""
        self.clear_form()
        self.category_input.setFocus()
        log_user_action("tax_add_started")
    
    def edit_tax_rate(self):
        """Edit selected tax rate"""
        if not self.current_editing_id:
            QMessageBox.warning(self, "Warning", "Please select a tax rate to edit.")
            return
        
        log_user_action(f"tax_edit_started | id: {self.current_editing_id}")
    
    def delete_tax_rate(self):
        """Delete selected tax rate"""
        if not self.current_editing_id:
            QMessageBox.warning(self, "Warning", "Please select a tax rate to delete.")
            return
        
        # Get category name for confirmation
        category = self.category_input.text()
        
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the '{category}' tax rate?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM tax_rates WHERE id = ?', (self.current_editing_id,))
                conn.commit()
                conn.close()
                
                log_user_action(f"tax_deleted | category: {category}, id: {self.current_editing_id}")
                
                self.load_tax_rates()
                self.clear_form()
                self.tax_rates_updated.emit()
                
                QMessageBox.information(self, "Success", 
                                      f"Tax rate '{category}' deleted successfully.")
                
            except sqlite3.Error as e:
                log_error(f"DATABASE ERROR: Failed to delete tax rate: {e}")
                QMessageBox.critical(self, "Database Error", 
                                   f"Failed to delete tax rate:\n{e}")
    
    def save_tax_rate(self):
        """Save tax rate to database"""
        category = self.category_input.text().strip().lower()
        rate = self.rate_input.value()
        description = self.description_input.text().strip()
        is_active = 1 if self.active_checkbox.isChecked() else 0
        
        if not category:
            QMessageBox.warning(self, "Validation Error", "Please enter a tax category.")
            self.category_input.setFocus()
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if self.current_editing_id:
                # Update existing tax rate
                cursor.execute('''
                    UPDATE tax_rates 
                    SET category = ?, rate = ?, description = ?, is_active = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (category, rate, description, is_active, self.current_editing_id))
                
                action = "updated"
                log_user_action(f"tax_updated | category: {category}, rate: {rate}%, id: {self.current_editing_id}")
                
            else:
                # Insert new tax rate
                cursor.execute('''
                    INSERT INTO tax_rates (category, rate, description, is_active)
                    VALUES (?, ?, ?, ?)
                ''', (category, rate, description, is_active))
                
                action = "created"
                log_user_action(f"tax_created | category: {category}, rate: {rate}%")
            
            conn.commit()
            conn.close()
            
            self.load_tax_rates()
            self.clear_form()
            self.tax_rates_updated.emit()
            
            QMessageBox.information(self, "Success", 
                                  f"Tax rate '{category}' {action} successfully.")
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Duplicate Category", 
                              f"Tax category '{category}' already exists.\n"
                              "Please choose a different category name.")
            
        except sqlite3.Error as e:
            log_error(f"DATABASE ERROR: Failed to save tax rate: {e}")
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to save tax rate:\n{e}")
    
    def clear_form(self):
        """Clear the form fields"""
        self.category_input.clear()
        self.rate_input.setValue(8.5)
        self.description_input.clear()
        self.active_checkbox.setChecked(True)
        self.current_editing_id = None
        
        # Clear table selection
        self.tax_table.clearSelection()
    
    def get_tax_rate(self, category):
        """Get tax rate for a specific category"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT rate FROM tax_rates 
                WHERE category = ? AND is_active = 1
            ''', (category.lower(),))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 8.5  # Default to 8.5% if not found
            
        except sqlite3.Error as e:
            log_error(f"DATABASE ERROR: Failed to get tax rate for {category}: {e}")
            return 8.5  # Default fallback
    
    def get_all_active_tax_rates(self):
        """Get all active tax rates as a dictionary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT category, rate FROM tax_rates 
                WHERE is_active = 1
                ORDER BY category
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            return {category: rate for category, rate in rows}
            
        except sqlite3.Error as e:
            log_error(f"DATABASE ERROR: Failed to get active tax rates: {e}")
            return {'standard': 8.5}  # Default fallback


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = TaxConfigDialog()
    dialog.show()
    sys.exit(app.exec())
