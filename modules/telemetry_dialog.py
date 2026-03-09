"""
Shop Manager Pro - Telemetry Settings Dialog
Optional anonymized telemetry collection with user consent
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QCheckBox, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt
from ui.design_system import DesignSystem, StyleSheets

class TelemetryDialog(QDialog):
    """Dialog for telemetry settings and user consent"""
    
    def __init__(self, parent=None, current_setting=False):
        super().__init__(parent)
        self.current_setting = current_setting
        self.result_setting = current_setting
        
        self.setWindowTitle("Telemetry & Analytics Settings")
        self.setModal(True)
        self.setFixedSize(600, 500)
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup the telemetry settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(DesignSystem.get_spacing('lg'))
        
        # Header
        header_label = QLabel("📊 Help Improve Shop Manager Pro")
        header_label.setFont(DesignSystem.get_font('xl', 'bold'))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Description
        description = QLabel(
            "Shop Manager Pro can collect anonymous usage statistics to help us improve the application. "
            "This information helps us understand how features are used and identify areas for improvement."
        )
        description.setWordWrap(True)
        description.setFont(DesignSystem.get_font('base'))
        layout.addWidget(description)
        
        # Telemetry options
        telemetry_group = QGroupBox("Telemetry Settings")
        telemetry_group.setFont(DesignSystem.get_font('lg', 'semibold'))
        telemetry_layout = QVBoxLayout(telemetry_group)
        
        # Enable telemetry checkbox
        self.enable_checkbox = QCheckBox("Enable anonymous usage analytics")
        self.enable_checkbox.setChecked(self.current_setting)
        self.enable_checkbox.setFont(DesignSystem.get_font('base', 'medium'))
        telemetry_layout.addWidget(self.enable_checkbox)
        
        # Benefits list
        benefits_label = QLabel("Benefits of enabling telemetry:")
        benefits_label.setFont(DesignSystem.get_font('sm', 'semibold'))
        telemetry_layout.addWidget(benefits_label)
        
        benefits_list = QLabel(
            "• Help identify and fix bugs faster\n"
            "• Understand which features are most useful\n"
            "• Improve application performance\n"
            "• Guide future development priorities"
        )
        benefits_list.setFont(DesignSystem.get_font('sm'))
        benefits_list.setStyleSheet(f"color: {DesignSystem.get_color('success')}; margin-left: 20px;")
        telemetry_layout.addWidget(benefits_list)
        
        layout.addWidget(telemetry_group)
        
        # Privacy information
        privacy_group = QGroupBox("Privacy Information")
        privacy_group.setFont(DesignSystem.get_font('lg', 'semibold'))
        privacy_layout = QVBoxLayout(privacy_group)
        
        privacy_text = QTextEdit()
        privacy_text.setReadOnly(True)
        privacy_text.setMaximumHeight(120)
        privacy_text.setPlainText(
            "WHAT WE COLLECT:\n"
            "• Application usage patterns (which features are used)\n"
            "• Performance metrics (load times, error rates)\n"
            "• System information (OS version, Python version)\n"
            "• Session duration and frequency\n\n"
            "WHAT WE DON'T COLLECT:\n"
            "• Personal information or user data\n"
            "• Customer names, addresses, or contact information\n"
            "• Product details, prices, or business data\n"
            "• Any sensitive or confidential information\n\n"
            "All data is anonymized and cannot be traced back to individual users."
        )
        privacy_layout.addWidget(privacy_text)
        
        layout.addWidget(privacy_group)
        
        # Data examples
        examples_group = QGroupBox("Example Data Collected")
        examples_group.setFont(DesignSystem.get_font('base', 'semibold'))
        examples_layout = QVBoxLayout(examples_group)
        
        example_text = QLabel(
            "• \"POS tab opened\" - helps us know this feature is popular\n"
            "• \"Application startup time: 2.3s\" - helps us optimize performance\n"
            "• \"Platform: Windows 11\" - helps us test on popular systems\n"
            "• \"Session duration: 45 minutes\" - helps us understand usage patterns"
        )
        example_text.setFont(DesignSystem.get_font('xs'))
        example_text.setWordWrap(True)
        examples_layout.addWidget(example_text)
        
        layout.addWidget(examples_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("secondaryButton")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def apply_styles(self):
        """Apply professional styling"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {DesignSystem.get_color('bg_primary')};
                color: {DesignSystem.get_color('text_primary')};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {DesignSystem.get_color('gray_300')};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {DesignSystem.get_color('primary')};
            }}
            
            QCheckBox {{
                font-size: 14px;
                spacing: 10px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid {DesignSystem.get_color('gray_400')};
                background-color: {DesignSystem.get_color('white')};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {DesignSystem.get_color('primary')};
                border-color: {DesignSystem.get_color('primary')};
                image: url(data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/%3E%3C/svg%3E);
            }}
            
            QTextEdit {{
                background-color: {DesignSystem.get_color('gray_50')};
                border: 1px solid {DesignSystem.get_color('gray_300')};
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
                line-height: 1.4;
            }}
            
            #primaryButton {{
                {StyleSheets.primary_button()}
            }}
            
            #secondaryButton {{
                {StyleSheets.secondary_button()}
            }}
        """)
    
    def save_settings(self):
        """Save telemetry settings"""
        self.result_setting = self.enable_checkbox.isChecked()
        self.accept()
    
    def get_setting(self):
        """Get the user's telemetry preference"""
        return self.result_setting

def show_telemetry_dialog(parent=None, current_setting=False):
    """Show telemetry settings dialog and return user preference"""
    dialog = TelemetryDialog(parent, current_setting)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_setting()
    return current_setting  # Return current setting if cancelled
