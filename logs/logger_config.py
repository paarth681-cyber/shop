"""
Shop Manager Pro - Logging Configuration
Professional logging system with rotating files, crash reporting, and telemetry
"""

import logging
import logging.handlers
import os
import sys
import traceback
import json
import platform
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox, QApplication

class ShopManagerLogger:
    """
    Professional logging system for Shop Manager Pro
    Features:
    - Rotating file handler with size limits
    - Crash reporting with automatic saves
    - User-friendly error dialogs
    - Optional telemetry collection
    """
    
    def __init__(self, log_level=logging.INFO):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize main logger
        self.logger = logging.getLogger("ShopManagerPro")
        self.logger.setLevel(log_level)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        self.setup_file_handler()
        self.setup_console_handler()
        self.setup_crash_handler()
        
        # Telemetry settings (default off for privacy)
        self.telemetry_enabled = self.load_telemetry_setting()
        
        self.logger.info("=" * 60)
        self.logger.info("Shop Manager Pro Logger Initialized")
        self.logger.info(f"Python: {platform.python_version()}")
        self.logger.info(f"Platform: {platform.platform()}")
        self.logger.info(f"Telemetry: {'Enabled' if self.telemetry_enabled else 'Disabled'}")
        self.logger.info("=" * 60)
    
    def setup_file_handler(self):
        """Setup rotating file handler"""
        log_file = self.log_dir / "shop.log"
        
        # Rotating file handler with 5MB max size, 5 backup files
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5_000_000,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # Detailed format for file logs
        file_formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(module)s:%(lineno)d | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        self.logger.addHandler(file_handler)
    
    def setup_console_handler(self):
        """Setup console handler for development"""
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Simpler format for console
        console_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(module)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        self.logger.addHandler(console_handler)
    
    def setup_crash_handler(self):
        """Setup automatic crash reporting"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                # Allow keyboard interrupt to work normally
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            # Create crash report
            crash_report = self.create_crash_report(exc_type, exc_value, exc_traceback)
            
            # Save crash report to file
            crash_filename = f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            crash_file = self.log_dir / crash_filename
            
            with open(crash_file, 'w', encoding='utf-8') as f:
                f.write(crash_report)
            
            # Log the crash
            self.logger.critical("CRITICAL: Application crashed", exc_info=(exc_type, exc_value, exc_traceback))
            
            # Show user-friendly dialog if GUI is available
            try:
                if QApplication.instance():
                    self.show_crash_dialog(crash_filename)
            except:
                pass  # GUI might not be available
            
            # Call original hook
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        
        # Set the exception hook
        sys.excepthook = handle_exception
    
    def create_crash_report(self, exc_type, exc_value, exc_traceback):
        """Create detailed crash report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        crash_report = f"""
SHOP MANAGER PRO - CRASH REPORT
{'='*50}
Timestamp: {timestamp}
Python Version: {platform.python_version()}
Platform: {platform.platform()}
Architecture: {platform.architecture()}

EXCEPTION DETAILS:
{'='*50}
Exception Type: {exc_type.__name__}
Exception Message: {str(exc_value)}

STACK TRACE:
{'='*50}
{''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))}

SYSTEM INFORMATION:
{'='*50}
OS: {platform.system()} {platform.release()}
Processor: {platform.processor()}
Machine: {platform.machine()}

PYTHON PATH:
{'='*50}
{chr(10).join(sys.path)}
"""
        return crash_report
    
    def show_crash_dialog(self, crash_filename):
        """Show user-friendly crash dialog"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Application Error")
        msg.setText("Shop Manager Pro has encountered an unexpected error and needs to close.")
        msg.setInformativeText(
            f"A crash report has been saved to:\nlogs/{crash_filename}\n\n"
            "Please contact support with this file for assistance."
        )
        msg.setDetailedText(f"Crash report saved to: logs/{crash_filename}")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def show_error_dialog(self, title, message, details=None):
        """Show user-friendly error dialog for recoverable errors"""
        try:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle(title)
            msg.setText(message)
            
            if details:
                msg.setDetailedText(str(details))
            
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
        except:
            # Fallback if GUI is not available
            print(f"ERROR: {title} - {message}")
            if details:
                print(f"Details: {details}")
    
    def log_user_action(self, action, details=None):
        """Log user actions for audit trail"""
        message = f"USER ACTION: {action}"
        if details:
            message += f" | {details}"
        self.logger.info(message)
        
        # Add to telemetry if enabled
        if self.telemetry_enabled:
            self.record_telemetry("user_action", {"action": action, "details": details})
    
    def log_database_operation(self, operation, table, details=None):
        """Log database operations"""
        message = f"DB OPERATION: {operation} on {table}"
        if details:
            message += f" | {details}"
        self.logger.debug(message)
    
    def log_error(self, error, context="", show_dialog=False):
        """Log errors with optional user dialog"""
        error_msg = f"ERROR in {context}: {str(error)}"
        self.logger.error(error_msg, exc_info=True)
        
        if show_dialog:
            self.show_error_dialog(
                "Application Error",
                f"An error occurred: {str(error)}",
                error_msg
            )
    
    def load_telemetry_setting(self):
        """Load telemetry preference from settings"""
        settings_file = self.log_dir / "settings.json"
        try:
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get("telemetry_enabled", False)
        except:
            pass
        return False  # Default to disabled
    
    def save_telemetry_setting(self, enabled):
        """Save telemetry preference"""
        settings_file = self.log_dir / "settings.json"
        try:
            settings = {"telemetry_enabled": enabled, "updated": datetime.now().isoformat()}
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            self.telemetry_enabled = enabled
            self.logger.info(f"Telemetry setting changed to: {enabled}")
        except Exception as e:
            self.logger.error(f"Failed to save telemetry setting: {e}")
    
    def record_telemetry(self, event_type, data):
        """Record anonymized telemetry data (opt-in only)"""
        if not self.telemetry_enabled:
            return
        
        try:
            telemetry_file = self.log_dir / "telemetry.log"
            
            telemetry_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": data,
                "session_id": getattr(self, 'session_id', 'unknown'),
                "version": "2.0"
            }
            
            with open(telemetry_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(telemetry_entry) + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to record telemetry: {e}")
    
    def start_session(self):
        """Start a new logging session"""
        import uuid
        self.session_id = str(uuid.uuid4())[:8]
        self.logger.info(f"SESSION START: {self.session_id}")
        
        if self.telemetry_enabled:
            self.record_telemetry("session_start", {
                "platform": platform.system(),
                "python_version": platform.python_version()
            })
    
    def end_session(self):
        """End the current logging session"""
        if hasattr(self, 'session_id'):
            self.logger.info(f"SESSION END: {self.session_id}")
            
            if self.telemetry_enabled:
                self.record_telemetry("session_end", {
                    "session_id": self.session_id
                })

# Global logger instance
logger_instance = None

def get_logger():
    """Get global logger instance"""
    global logger_instance
    if logger_instance is None:
        logger_instance = ShopManagerLogger()
    return logger_instance

def init_logging(log_level=logging.INFO):
    """Initialize logging system"""
    global logger_instance
    logger_instance = ShopManagerLogger(log_level)
    return logger_instance

# Convenience functions
def log_info(message, context=""):
    """Log info message"""
    logger = get_logger()
    if context:
        message = f"[{context}] {message}"
    logger.logger.info(message)

def log_error(error, context="", show_dialog=False):
    """Log error with optional dialog"""
    logger = get_logger()
    logger.log_error(error, context, show_dialog)

def log_user_action(action, details=None):
    """Log user action"""
    logger = get_logger()
    logger.log_user_action(action, details)

def log_db_operation(operation, table, details=None):
    """Log database operation"""
    logger = get_logger()
    logger.log_database_operation(operation, table, details)