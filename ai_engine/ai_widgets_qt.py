"""
Shop Manager Pro - AI-Enhanced PyQt6 Widgets
Smart widgets that integrate AI capabilities into the PyQt interface
"""

import sys
import sqlite3
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    import numpy as np
    
    # Try different matplotlib backends for PyQt6 compatibility
    try:
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    except ImportError:
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        except ImportError:
            FigureCanvas = None
            raise ImportError("No suitable matplotlib backend found")
    
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    FigureCanvas = None

from ai_engine import get_ai_engine
from logger_config import log_info, log_error, log_user_action


class AISearchWidget(QWidget):
    """Intelligent product search widget with NLP capabilities"""
    
    product_selected = pyqtSignal(dict)  # Signal when product is selected
    
    def __init__(self):
        super().__init__()
        self.ai_engine = get_ai_engine()
        self.search_results = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the search widget UI"""
        layout = QVBoxLayout(self)
        
        # Search frame
        search_frame = QHBoxLayout()
        
        # Search label and input
        search_label = QLabel("🔍 Smart Search:")
        search_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        search_frame.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products using AI...")
        self.search_input.textChanged.connect(self.on_search_change)
        self.search_input.returnPressed.connect(self.perform_search)
        search_frame.addWidget(self.search_input, 1)
        
        # AI toggle checkbox
        self.use_ai_checkbox = QCheckBox("AI Search")
        self.use_ai_checkbox.setChecked(True)
        search_frame.addWidget(self.use_ai_checkbox)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        search_frame.addWidget(self.search_button)
        
        layout.addLayout(search_frame)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Product Name", "SKU", "Price", "Stock", "Relevance", "Match Type"
        ])
        
        # Configure table
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Product Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # SKU
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Price
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Stock
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Relevance
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Match Type
        
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.doubleClicked.connect(self.on_item_double_click)
        
        layout.addWidget(self.results_table)
        
        # Status label
        self.status_label = QLabel("Ready for search...")
        self.status_label.setFont(QFont("Arial", 8))
        self.status_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Search timer for debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
    
    def on_search_change(self):
        """Handle search text changes for real-time search"""
        search_text = self.search_input.text().strip()
        if len(search_text) >= 3:  # Start searching after 3 characters
            self.search_timer.start(500)  # Debounce search
    
    def perform_search(self):
        """Perform the search operation"""
        search_text = self.search_input.text().strip()
        if not search_text:
            self.clear_results()
            return
        
        self.status_label.setText("🔄 Searching...")
        self.search_button.setEnabled(False)
        
        # Perform search in background thread
        self.search_thread = SearchThread(self.ai_engine, search_text, 
                                         self.use_ai_checkbox.isChecked())
        self.search_thread.results_ready.connect(self.update_results)
        self.search_thread.error_occurred.connect(self.show_search_error)
        self.search_thread.start()
    
    def update_results(self, results, search_text):
        """Update search results in UI"""
        self.search_results = results
        self.clear_results()
        
        if not results:
            self.status_label.setText(f"No results found for '{search_text}'")
            self.search_button.setEnabled(True)
            return
        
        # Populate results
        self.results_table.setRowCount(len(results))
        
        for i, result in enumerate(results):
            # Product name
            name_item = QTableWidgetItem(result.get('name', ''))
            self.results_table.setItem(i, 0, name_item)
            
            # SKU
            sku_item = QTableWidgetItem(result.get('sku', ''))
            self.results_table.setItem(i, 1, sku_item)
            
            # Price
            price_item = QTableWidgetItem(f"${result.get('price', 0):.2f}")
            self.results_table.setItem(i, 2, price_item)
            
            # Stock
            stock_item = QTableWidgetItem(str(result.get('quantity', 0)))
            self.results_table.setItem(i, 3, stock_item)
            
            # Relevance
            relevance_score = result.get('relevance_score', 0)
            relevance_text = f"{relevance_score:.3f}"
            
            # Add visual indicator for relevance level
            if relevance_score > 0.7:
                relevance_text = f"⭐ {relevance_text}"
            elif relevance_score > 0.4:
                relevance_text = f"✓ {relevance_text}"
            
            relevance_item = QTableWidgetItem(relevance_text)
            self.results_table.setItem(i, 4, relevance_item)
            
            # Match type
            match_item = QTableWidgetItem(result.get('match_explanation', 'N/A'))
            self.results_table.setItem(i, 5, match_item)
        
        ai_indicator = "🤖 AI" if self.use_ai_checkbox.isChecked() else "📊 Basic"
        self.status_label.setText(f"{ai_indicator} • Found {len(results)} results for '{search_text}'")
        self.search_button.setEnabled(True)
        
        log_user_action("ai_search_completed", f"query: '{search_text}', results: {len(results)}, ai_used: {self.use_ai_checkbox.isChecked()}")
    
    def show_search_error(self, error_msg):
        """Show search error"""
        self.status_label.setText(f"❌ Search error: {error_msg}")
        self.search_button.setEnabled(True)
    
    def clear_results(self):
        """Clear search results"""
        self.results_table.setRowCount(0)
        self.search_results = []
    
    def on_item_double_click(self, index):
        """Handle double-click on search result"""
        row = index.row()
        if 0 <= row < len(self.search_results):
            product = self.search_results[row]
            self.product_selected.emit(product)


class SearchThread(QThread):
    """Background search thread"""
    
    results_ready = pyqtSignal(list, str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ai_engine, search_text, use_ai):
        super().__init__()
        self.ai_engine = ai_engine
        self.search_text = search_text
        self.use_ai = use_ai
    
    def run(self):
        try:
            results = self.ai_engine.smart_search(self.search_text, use_nlp=self.use_ai, limit=50)
            self.results_ready.emit(results, self.search_text)
        except Exception as e:
            log_error(f"Search error: {e}")
            self.error_occurred.emit(str(e))


class MLForecastWidget(QWidget):
    """Machine Learning sales forecasting widget"""
    
    def __init__(self):
        super().__init__()
        self.ai_engine = get_ai_engine()
        self.forecast_data = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the forecast widget UI"""
        layout = QVBoxLayout(self)
        
        # Control frame
        control_frame = QHBoxLayout()
        
        title_label = QLabel("📊 ML Sales Forecasting")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        control_frame.addWidget(title_label)
        
        control_frame.addStretch()
        
        # Days input
        control_frame.addWidget(QLabel("Days ahead:"))
        self.days_input = QSpinBox()
        self.days_input.setRange(1, 365)
        self.days_input.setValue(30)
        self.days_input.setMinimumWidth(80)
        control_frame.addWidget(self.days_input)
        
        # Generate button
        self.generate_button = QPushButton("Generate Forecast")
        self.generate_button.clicked.connect(self.generate_forecast)
        control_frame.addWidget(self.generate_button)
        
        layout.addLayout(control_frame)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Summary tab
        self.summary_tab = QWidget()
        summary_layout = QVBoxLayout(self.summary_tab)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(QFont("Consolas", 10))
        summary_layout.addWidget(self.summary_text)
        
        # Initial message
        initial_text = """📊 ML Sales Forecasting

Click 'Generate Forecast' to create AI-powered sales predictions.

Features:
• Trend analysis using linear regression
• Seasonal pattern detection  
• Confidence scoring
• Exponential smoothing"""
        
        self.summary_text.setPlainText(initial_text)
        self.tab_widget.addTab(self.summary_tab, "📈 Summary")
        
        # Chart tab (if matplotlib available)
        if MATPLOTLIB_AVAILABLE:
            self.chart_tab = QWidget()
            chart_layout = QVBoxLayout(self.chart_tab)
            self.chart_placeholder = QLabel("📊 Forecast chart will appear here after generation")
            self.chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.chart_placeholder.setFont(QFont("Arial", 10))
            chart_layout.addWidget(self.chart_placeholder)
            self.tab_widget.addTab(self.chart_tab, "📊 Chart")
        
        # Details tab
        self.details_tab = QWidget()
        details_layout = QVBoxLayout(self.details_tab)
        
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(4)
        self.details_table.setHorizontalHeaderLabels([
            "Date", "Predicted Sales", "Confidence", "Day of Week"
        ])
        
        # Configure details table
        header = self.details_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.details_table.setAlternatingRowColors(True)
        
        details_layout.addWidget(self.details_table)
        self.tab_widget.addTab(self.details_tab, "📋 Details")
        
        layout.addWidget(self.tab_widget)
        
        # Status label
        self.status_label = QLabel("Ready to generate forecast...")
        self.status_label.setFont(QFont("Arial", 8))
        self.status_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.status_label)
    
    def generate_forecast(self):
        """Generate sales forecast"""
        days_ahead = self.days_input.value()
        self.status_label.setText("🔄 Generating ML forecast...")
        self.generate_button.setEnabled(False)
        
        # Run forecast in background
        self.forecast_thread = ForecastThread(self.ai_engine, days_ahead)
        self.forecast_thread.forecast_ready.connect(self.update_forecast)
        self.forecast_thread.error_occurred.connect(self.show_forecast_error)
        self.forecast_thread.start()
    
    def update_forecast(self, forecast_data):
        """Update forecast results in UI"""
        if "error" in forecast_data:
            self.show_forecast_error(forecast_data["message"])
            return
        
        self.forecast_data = forecast_data
        
        # Update summary
        self.update_summary(forecast_data)
        
        # Update chart if available
        if MATPLOTLIB_AVAILABLE:
            self.update_chart(forecast_data)
        
        # Update details
        self.update_details(forecast_data)
        
        # Update status
        total_forecast = forecast_data["summary"]["total_predicted_sales"]
        confidence = forecast_data["summary"]["confidence"]
        self.status_label.setText(f"✅ Forecast generated: ${total_forecast:.2f} (confidence: {confidence:.1%})")
        self.generate_button.setEnabled(True)
        
        log_user_action("ml_forecast_generated", f"days: {len(forecast_data['forecasts'])}, total: ${total_forecast:.2f}")
    
    def update_summary(self, forecast_data):
        """Update the summary tab"""
        summary = forecast_data["summary"]
        model_info = forecast_data["model_info"]
        
        summary_text = "🤖 ML Sales Forecast Summary\n"
        summary_text += "=" * 50 + "\n\n"
        
        # Key metrics
        summary_text += "📊 Key Predictions:\n"
        summary_text += f"• Total Predicted Sales: ${summary['total_predicted_sales']:,.2f}\n"
        summary_text += f"• Average Daily Sales: ${summary['avg_daily_prediction']:,.2f}\n"
        summary_text += f"• Historical Average: ${summary['historical_avg_daily']:,.2f}\n"
        
        # Performance indicators
        growth_rate = summary["growth_rate"]
        if growth_rate > 0:
            summary_text += f"• Growth Trend: +${growth_rate:.2f}/day (📈 Growing)\n"
        elif growth_rate < 0:
            summary_text += f"• Growth Trend: ${growth_rate:.2f}/day (📉 Declining)\n"
        else:
            summary_text += f"• Growth Trend: Stable (➡️)\n"
        
        summary_text += f"• Trend Direction: {summary['trend'].title()}\n"
        summary_text += f"• Confidence Score: {summary['confidence']:.1%}\n\n"
        
        # Model information
        summary_text += "🔧 Model Details:\n"
        summary_text += f"• Method: {model_info['forecast_method'].replace('_', ' ').title()}\n"
        summary_text += f"• Seasonal Adjustment: {model_info['seasonal_adjustment'].replace('_', ' ').title()}\n"
        summary_text += f"• Historical Data Points: {model_info['data_points_used']}\n\n"
        
        # Business insights
        summary_text += "💡 Business Insights:\n"
        
        confidence = summary["confidence"]
        if confidence > 0.7:
            summary_text += "• High confidence forecast - strong historical patterns detected\n"
        elif confidence > 0.4:
            summary_text += "• Moderate confidence forecast - some patterns detected\n"
        else:
            summary_text += "• Low confidence forecast - limited historical patterns\n"
        
        if abs(growth_rate) > 10:
            summary_text += "• Significant trend detected - monitor closely\n"
        
        comparison_ratio = summary["avg_daily_prediction"] / summary["historical_avg_daily"] if summary["historical_avg_daily"] > 0 else 1
        if comparison_ratio > 1.1:
            summary_text += "• Forecast shows improvement over historical average\n"
        elif comparison_ratio < 0.9:
            summary_text += "• Forecast shows decline from historical average\n"
        else:
            summary_text += "• Forecast aligns with historical performance\n"
        
        self.summary_text.setPlainText(summary_text)
    
    def update_chart(self, forecast_data):
        """Update the forecast chart"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        try:
            # Clear previous chart
            for i in reversed(range(self.chart_tab.layout().count())):
                child = self.chart_tab.layout().itemAt(i).widget()
                if child:
                    child.setParent(None)
            
            # Create matplotlib figure
            figure = Figure(figsize=(10, 6), dpi=100)
            canvas = FigureCanvas(figure)
            ax = figure.add_subplot(111)
            
            # Prepare data
            forecasts = forecast_data["forecasts"]
            dates = [datetime.strptime(f["date"], "%Y-%m-%d") for f in forecasts]
            sales = [f["predicted_sales"] for f in forecasts]
            
            # Plot forecast
            ax.plot(dates, sales, 'b-', linewidth=2, label='Predicted Sales')
            ax.fill_between(dates, sales, alpha=0.3)
            
            # Add confidence bands
            confidence = forecast_data["summary"]["confidence"]
            margin = [(1 - confidence) * s for s in sales]
            upper_bound = [s + m for s, m in zip(sales, margin)]
            lower_bound = [s - m for s, m in zip(sales, margin)]
            
            ax.fill_between(dates, lower_bound, upper_bound, alpha=0.2, color='gray', 
                          label=f'{confidence:.1%} Confidence Band')
            
            # Formatting
            ax.set_title('ML Sales Forecast', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Predicted Sales ($)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Rotate x-axis labels
            figure.autofmt_xdate()
            
            # Add to layout
            self.chart_tab.layout().addWidget(canvas)
            
        except Exception as e:
            log_error(f"Chart generation error: {e}")
            error_label = QLabel(f"❌ Chart error: {e}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.chart_tab.layout().addWidget(error_label)
    
    def update_details(self, forecast_data):
        """Update the details tab"""
        forecasts = forecast_data["forecasts"]
        self.details_table.setRowCount(len(forecasts))
        
        for i, forecast in enumerate(forecasts):
            # Date
            date_item = QTableWidgetItem(forecast["date"])
            self.details_table.setItem(i, 0, date_item)
            
            # Predicted Sales
            sales_item = QTableWidgetItem(f"${forecast['predicted_sales']:,.2f}")
            self.details_table.setItem(i, 1, sales_item)
            
            # Confidence
            confidence_item = QTableWidgetItem(f"{forecast['confidence']:.1%}")
            self.details_table.setItem(i, 2, confidence_item)
            
            # Day of week
            date_obj = datetime.strptime(forecast["date"], "%Y-%m-%d")
            day_item = QTableWidgetItem(date_obj.strftime("%A"))
            self.details_table.setItem(i, 3, day_item)
    
    def show_forecast_error(self, error_msg):
        """Show forecast error"""
        self.status_label.setText(f"❌ Forecast error: {error_msg}")
        self.generate_button.setEnabled(True)
        
        # Show error dialog
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Forecast Error")
        msg_box.setText(f"Failed to generate forecast:\n\n{error_msg}")
        msg_box.exec()


class ForecastThread(QThread):
    """Background forecast generation thread"""
    
    forecast_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ai_engine, days_ahead):
        super().__init__()
        self.ai_engine = ai_engine
        self.days_ahead = days_ahead
    
    def run(self):
        try:
            forecast_data = self.ai_engine.ml_forecaster.forecast_sales(self.days_ahead)
            self.forecast_ready.emit(forecast_data)
        except Exception as e:
            log_error(f"Forecast generation error: {e}")
            self.error_occurred.emit(str(e))


class GPTChatWidget(QWidget):
    """GPT-powered chat assistant widget"""
    
    def __init__(self):
        super().__init__()
        self.ai_engine = get_ai_engine()
        self.chat_history = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the chat widget UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🤖 GPT Business Assistant")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # API key button
        api_button = QPushButton("⚙️ API Key")
        api_button.clicked.connect(self.configure_api_key)
        header_layout.addWidget(api_button)
        
        layout.addLayout(header_layout)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Arial", 10))
        
        # Configure text formatting
        self.setup_chat_formats()
        
        layout.addWidget(self.chat_display)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        actions_layout.addWidget(QLabel("Quick Actions:"))
        
        quick_actions = [
            ("📊 Sales Report", "Generate a comprehensive sales report for the last 30 days"),
            ("📈 Business Insights", "What insights can you provide about my business performance?"),
            ("💡 Recommendations", "What recommendations do you have for improving my business?"),
            ("📋 Inventory Status", "How is my inventory doing? Any items need attention?"),
        ]
        
        for text, query in quick_actions:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, q=query: self.send_quick_message(q))
            actions_layout.addWidget(btn)
        
        layout.addLayout(actions_layout)
        
        # Input frame
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ask me anything about your business...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input, 1)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Status label
        self.status_label = QLabel("💬 Ready to chat - ask me anything about your business!")
        self.status_label.setFont(QFont("Arial", 8))
        self.status_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Initial welcome message
        self.add_message("system", "🤖 GPT Business Assistant Ready!")
        self.add_message("assistant", """Hello! I'm your AI business assistant. I can help you with:

• Sales analysis and reporting
• Business insights and trends  
• Inventory recommendations
• Performance optimization
• General business questions

What would you like to know about your business?""")
    
    def setup_chat_formats(self):
        """Setup text formats for different message types"""
        self.user_format = QTextCharFormat()
        self.user_format.setForeground(QColor("blue"))
        self.user_format.setFontWeight(QFont.Weight.Bold)
        
        self.assistant_format = QTextCharFormat()
        self.assistant_format.setForeground(QColor("green"))
        
        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QColor("red"))
        self.error_format.setFontItalic(True)
        
        self.system_format = QTextCharFormat()
        self.system_format.setForeground(QColor("gray"))
        self.system_format.setFontItalic(True)
    
    def configure_api_key(self):
        """Configure OpenAI API key"""
        api_key, ok = QInputDialog.getText(self, "Configure GPT API Key", 
                                          "Enter your OpenAI API Key:\n\n" +
                                          "Get your key from: https://platform.openai.com/api-keys",
                                          QLineEdit.EchoMode.Password)
        
        if ok and api_key.strip():
            self.ai_engine.gpt_assistant.set_api_key(api_key.strip())
            self.add_message("system", "✅ GPT API key configured successfully!")
    
    def add_message(self, sender, message):
        """Add a message to the chat display"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        timestamp = datetime.now().strftime("%H:%M")
        
        # Format message based on sender
        if sender == "user":
            cursor.insertText(f"[{timestamp}] You: ", self.user_format)
        elif sender == "assistant":
            cursor.insertText(f"[{timestamp}] AI: ", self.assistant_format)
        elif sender == "error":
            cursor.insertText(f"[{timestamp}] Error: ", self.error_format)
        else:  # system
            cursor.insertText(f"[{timestamp}] ", self.system_format)
        
        # Insert message content
        if sender == "user":
            cursor.insertText(f"{message}\n\n", self.user_format)
        elif sender == "assistant":
            cursor.insertText(f"{message}\n\n", self.assistant_format)
        elif sender == "error":
            cursor.insertText(f"{message}\n\n", self.error_format)
        else:
            cursor.insertText(f"{message}\n\n", self.system_format)
        
        # Scroll to bottom
        self.chat_display.ensureCursorVisible()
    
    def send_quick_message(self, message):
        """Send a pre-defined quick message"""
        self.message_input.setText(message)
        self.send_message()
    
    def send_message(self):
        """Send a message to GPT"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        # Check if API key is configured
        if not self.ai_engine.gpt_assistant.api_key:
            self.add_message("error", "GPT API key not configured. Please click '⚙️ API Key' to set it up.")
            return
        
        # Add user message to chat
        self.add_message("user", message)
        self.message_input.clear()
        
        # Update status
        self.status_label.setText("🔄 Thinking...")
        self.send_button.setEnabled(False)
        
        # Send to GPT in background
        self.gpt_thread = GPTThread(self.ai_engine, message)
        self.gpt_thread.response_ready.connect(self.handle_gpt_response)
        self.gpt_thread.error_occurred.connect(self.handle_gpt_error)
        self.gpt_thread.start()
    
    def handle_gpt_response(self, response):
        """Handle GPT response"""
        self.add_message("assistant", response)
        self.status_label.setText("💬 Ready for next question...")
        self.send_button.setEnabled(True)
        
        # Store in history
        self.chat_history.append({
            "timestamp": datetime.now(),
            "type": "response",
            "content": response
        })
        
        log_user_action("gpt_chat_response", f"response_length: {len(response)}")
    
    def handle_gpt_error(self, error_msg):
        """Handle GPT error"""
        self.add_message("error", f"Sorry, I encountered an error: {error_msg}")
        self.status_label.setText("❌ Error occurred - try again")
        self.send_button.setEnabled(True)


class GPTThread(QThread):
    """Background GPT processing thread"""
    
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ai_engine, message):
        super().__init__()
        self.ai_engine = ai_engine
        self.message = message
    
    def run(self):
        try:
            response = self.ai_engine.gpt_assistant.process_natural_query(self.message)
            self.response_ready.emit(response)
        except Exception as e:
            log_error(f"GPT chat error: {e}")
            self.error_occurred.emit(str(e))


class AIControlPanel(QWidget):
    """Main AI control panel that hosts all AI widgets"""
    
    def __init__(self):
        super().__init__()
        self.ai_engine = get_ai_engine()
        self.setup_ui()
        self.initialize_ai()
    
    def setup_ui(self):
        """Setup the AI control panel UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🤖 AI-Powered Shop Management")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Initialize AI button
        init_button = QPushButton("🔧 Initialize AI")
        init_button.clicked.connect(self.initialize_ai)
        header_layout.addWidget(init_button)
        
        layout.addLayout(header_layout)
        
        # Status label
        self.status_label = QLabel("🔄 AI Status: Initializing...")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.status_label)
        
        # Tab widget for AI features
        self.tab_widget = QTabWidget()
        
        # Smart Search tab
        self.search_widget = AISearchWidget()
        self.tab_widget.addTab(self.search_widget, "🔍 Smart Search")
        
        # ML Forecasting tab
        self.forecast_widget = MLForecastWidget()
        self.tab_widget.addTab(self.forecast_widget, "📊 Sales Forecast")
        
        # GPT Chat tab
        self.chat_widget = GPTChatWidget()
        self.tab_widget.addTab(self.chat_widget, "💬 Business Chat")
        
        layout.addWidget(self.tab_widget)
        
        # Capabilities overview
        caps_group = QGroupBox("🚀 AI Capabilities")
        caps_layout = QVBoxLayout(caps_group)
        
        capabilities_text = """🔍 Smart Search: Intelligent product search using TF-IDF and cosine similarity
📊 ML Forecasting: Sales predictions with exponential smoothing and trend analysis  
💬 GPT Assistant: Natural language business queries and automated report generation
🎯 Recommendations: Product similarity analysis for cross-selling opportunities
📈 Real-time Analytics: Advanced business intelligence with confidence scoring
🤖 Adaptive Learning: AI models that improve with your business data"""
        
        caps_label = QLabel(capabilities_text)
        caps_label.setFont(QFont("Arial", 9))
        caps_label.setWordWrap(True)
        caps_layout.addWidget(caps_label)
        
        layout.addWidget(caps_group)
    
    def initialize_ai(self):
        """Initialize the AI engine"""
        self.status_label.setText("🔄 AI Status: Initializing...")
        
        # Initialize in background
        self.init_thread = AIInitThread(self.ai_engine)
        self.init_thread.init_complete.connect(self.ai_init_complete)
        self.init_thread.init_error.connect(self.ai_init_error)
        self.init_thread.start()
    
    def ai_init_complete(self, capabilities):
        """Handle successful AI initialization"""
        # Count available features
        available_count = sum(1 for feature, info in capabilities.items() 
                             if isinstance(info, dict) and info.get('available', False))
        
        self.status_label.setText(f"✅ AI Status: Ready ({available_count} features active)")
        log_user_action("ai_engine_initialized", f"AI engine ready with {available_count} features")
    
    def ai_init_error(self, error_msg):
        """Handle AI initialization error"""
        self.status_label.setText(f"❌ AI Status: Error - {error_msg}")


class AIInitThread(QThread):
    """Background AI initialization thread"""
    
    init_complete = pyqtSignal(dict)
    init_error = pyqtSignal(str)
    
    def __init__(self, ai_engine):
        super().__init__()
        self.ai_engine = ai_engine
    
    def run(self):
        try:
            self.ai_engine.initialize()
            capabilities = self.ai_engine.get_capabilities()
            self.init_complete.emit(capabilities)
        except Exception as e:
            log_error(f"AI initialization failed: {e}")
            self.init_error.emit(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Test the AI control panel
    window = AIControlPanel()
    window.setWindowTitle("AI Control Panel Test")
    window.resize(1000, 800)
    window.show()
    
    sys.exit(app.exec())