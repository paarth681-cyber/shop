"""
Professional Design System for Shop Manager Pro
Modern blue/red/yellow/white theme with consistent styling
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
from PyQt6.QtWidgets import QApplication

class DesignSystem:
    """Professional design system with consistent colors, fonts, and styles"""
    
    # Color Palette - Professional Blue/Red/Yellow/White
    COLORS = {
        # Primary Colors
        'primary': '#2563EB',           # Professional Blue
        'primary_dark': '#1E40AF',      # Dark Blue
        'primary_light': '#3B82F6',     # Light Blue
        'primary_lighter': '#DBEAFE',   # Very Light Blue
        
        # Accent Colors
        'accent': '#DC2626',            # Professional Red
        'accent_dark': '#B91C1C',       # Dark Red
        'accent_light': '#EF4444',      # Light Red
        'accent_lighter': '#FEE2E2',    # Very Light Red
        
        # Highlight Colors
        'highlight': '#D97706',         # Professional Yellow/Orange
        'highlight_dark': '#B45309',    # Dark Yellow
        'highlight_light': '#F59E0B',   # Light Yellow
        'highlight_lighter': '#FEF3C7', # Very Light Yellow
        
        # Neutral Colors
        'white': '#FFFFFF',
        'gray_50': '#F9FAFB',
        'gray_100': '#F3F4F6',
        'gray_200': '#E5E7EB',
        'gray_300': '#D1D5DB',
        'gray_400': '#9CA3AF',
        'gray_500': '#6B7280',
        'gray_600': '#4B5563',
        'gray_700': '#374151',
        'gray_800': '#1F2937',
        'gray_900': '#111827',
        
        # Status Colors
        'success': '#059669',
        'success_light': '#10B981',
        'warning': '#D97706',
        'warning_light': '#F59E0B',
        'error': '#DC2626',
        'error_light': '#EF4444',
        'info': '#2563EB',
        'info_light': '#3B82F6',
        
        # Background Colors
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F9FAFB',
        'bg_tertiary': '#F3F4F6',
        'bg_surface': '#FFFFFF',
        'bg_overlay': 'rgba(0, 0, 0, 0.5)',
        
        # Text Colors
        'text_primary': '#111827',
        'text_secondary': '#6B7280',
        'text_tertiary': '#9CA3AF',
        'text_inverse': '#FFFFFF',
        'text_link': '#2563EB',
    }
    
    # Typography
    FONTS = {
        'primary': 'Segoe UI',
        'secondary': 'Arial',
        'monospace': 'Consolas',
    }
    
    FONT_SIZES = {
        'xs': 10,
        'sm': 11,
        'base': 12,
        'lg': 14,
        'xl': 16,
        'xxl': 18,
        'xxxl': 24,
        'display': 32,
    }
    
    FONT_WEIGHTS = {
        'light': 300,
        'normal': 400,
        'medium': 500,
        'semibold': 600,
        'bold': 700,
    }
    
    # Spacing System (pixels)
    SPACING = {
        'xs': 4,
        'sm': 8,
        'base': 12,
        'lg': 16,
        'xl': 20,
        'xxl': 24,
        'xxxl': 32,
        'huge': 48,
    }
    
    # Border Radius
    RADIUS = {
        'none': 0,
        'sm': 4,
        'base': 8,
        'lg': 12,
        'xl': 16,
        'full': 9999,
    }
    
    # Shadows
    SHADOWS = {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'base': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    }
    
    @classmethod
    def get_color(cls, color_name):
        """Get color value by name"""
        return cls.COLORS.get(color_name, '#000000')
    
    @classmethod
    def get_font(cls, size='base', weight='normal', family='primary'):
        """Create QFont with specified parameters"""
        font_family = cls.FONTS.get(family, 'Segoe UI')
        font_size = cls.FONT_SIZES.get(size, 12)
        font_weight = cls.FONT_WEIGHTS.get(weight, 400)
        
        font = QFont(font_family, font_size)
        font.setWeight(font_weight)
        return font
    
    @classmethod
    def get_spacing(cls, size='base'):
        """Get spacing value"""
        return cls.SPACING.get(size, 12)
    
    @classmethod
    def get_radius(cls, size='base'):
        """Get border radius value"""
        return cls.RADIUS.get(size, 8)

class StyleSheets:
    """Pre-defined style sheets for common components"""
    
    @staticmethod
    def main_window():
        return f"""
        QMainWindow {{
            background-color: {DesignSystem.get_color('bg_secondary')};
            color: {DesignSystem.get_color('text_primary')};
        }}
        """
    
    @staticmethod
    def primary_button():
        return f"""
        QPushButton {{
            background-color: {DesignSystem.get_color('primary')};
            color: {DesignSystem.get_color('text_inverse')};
            border: none;
            border-radius: {DesignSystem.get_radius('base')}px;
            padding: {DesignSystem.get_spacing('sm')}px {DesignSystem.get_spacing('lg')}px;
            font-size: {DesignSystem.FONT_SIZES['base']}px;
            font-weight: {DesignSystem.FONT_WEIGHTS['medium']};
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {DesignSystem.get_color('primary_dark')};
        }}
        QPushButton:pressed {{
            background-color: {DesignSystem.get_color('primary_dark')};
        }}
        QPushButton:disabled {{
            background-color: {DesignSystem.get_color('gray_300')};
            color: {DesignSystem.get_color('gray_500')};
        }}
        """
    
    @staticmethod
    def accent_button():
        return f"""
        QPushButton {{
            background-color: {DesignSystem.get_color('accent')};
            color: {DesignSystem.get_color('text_inverse')};
            border: none;
            border-radius: {DesignSystem.get_radius('base')}px;
            padding: {DesignSystem.get_spacing('sm')}px {DesignSystem.get_spacing('lg')}px;
            font-size: {DesignSystem.FONT_SIZES['base']}px;
            font-weight: {DesignSystem.FONT_WEIGHTS['medium']};
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {DesignSystem.get_color('accent_dark')};
        }}
        QPushButton:pressed {{
            background-color: {DesignSystem.get_color('accent_dark')};
        }}
        """
    
    @staticmethod
    def success_button():
        return f"""
        QPushButton {{
            background-color: {DesignSystem.get_color('success')};
            color: {DesignSystem.get_color('text_inverse')};
            border: none;
            border-radius: {DesignSystem.get_radius('base')}px;
            padding: {DesignSystem.get_spacing('sm')}px {DesignSystem.get_spacing('lg')}px;
            font-size: {DesignSystem.FONT_SIZES['base']}px;
            font-weight: {DesignSystem.FONT_WEIGHTS['medium']};
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {DesignSystem.get_color('success_light')};
        }}
        """
    
    @staticmethod
    def secondary_button():
        return f"""
        QPushButton {{
            background-color: transparent;
            color: {DesignSystem.get_color('text_primary')};
            border: 2px solid {DesignSystem.get_color('gray_300')};
            border-radius: {DesignSystem.get_radius('base')}px;
            padding: {DesignSystem.get_spacing('sm')}px {DesignSystem.get_spacing('lg')}px;
            font-size: {DesignSystem.FONT_SIZES['base']}px;
            font-weight: {DesignSystem.FONT_WEIGHTS['medium']};
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {DesignSystem.get_color('gray_50')};
            border-color: {DesignSystem.get_color('gray_400')};
        }}
        """
    
    @staticmethod
    def card():
        return f"""
        QFrame {{
            background-color: {DesignSystem.get_color('bg_surface')};
            border: 1px solid {DesignSystem.get_color('gray_200')};
            border-radius: {DesignSystem.get_radius('lg')}px;
            padding: {DesignSystem.get_spacing('lg')}px;
        }}
        """
    
    @staticmethod
    def input_field():
        return f"""
        QLineEdit {{
            background-color: {DesignSystem.get_color('white')};
            border: 2px solid {DesignSystem.get_color('gray_200')};
            border-radius: {DesignSystem.get_radius('base')}px;
            padding: {DesignSystem.get_spacing('sm')}px {DesignSystem.get_spacing('base')}px;
            font-size: {DesignSystem.FONT_SIZES['base']}px;
            color: {DesignSystem.get_color('text_primary')};
            min-height: 40px;
        }}
        QLineEdit:focus {{
            border-color: {DesignSystem.get_color('primary')};
            outline: none;
        }}
        QLineEdit:hover {{
            border-color: {DesignSystem.get_color('gray_300')};
        }}
        """
    
    @staticmethod
    def table():
        return f"""
        QTableWidget {{
            background-color: {DesignSystem.get_color('white')};
            border: 1px solid {DesignSystem.get_color('gray_200')};
            border-radius: {DesignSystem.get_radius('base')}px;
            gridline-color: {DesignSystem.get_color('gray_200')};
            font-size: {DesignSystem.FONT_SIZES['base']}px;
        }}
        QTableWidget::item {{
            padding: {DesignSystem.get_spacing('sm')}px;
            border-bottom: 1px solid {DesignSystem.get_color('gray_100')};
        }}
        QTableWidget::item:selected {{
            background-color: {DesignSystem.get_color('primary_lighter')};
            color: {DesignSystem.get_color('primary_dark')};
        }}
        QHeaderView::section {{
            background-color: {DesignSystem.get_color('gray_50')};
            padding: {DesignSystem.get_spacing('base')}px;
            border: none;
            border-bottom: 2px solid {DesignSystem.get_color('gray_200')};
            font-weight: {DesignSystem.FONT_WEIGHTS['semibold']};
        }}
        """
    
    @staticmethod
    def tab_widget():
        return f"""
        QTabWidget::pane {{
            border: 1px solid {DesignSystem.get_color('gray_200')};
            background-color: {DesignSystem.get_color('white')};
            border-radius: {DesignSystem.get_radius('base')}px;
        }}
        QTabBar::tab {{
            background-color: {DesignSystem.get_color('gray_100')};
            color: {DesignSystem.get_color('text_secondary')};
            padding: {DesignSystem.get_spacing('base')}px {DesignSystem.get_spacing('xl')}px;
            margin-right: 2px;
            border-top-left-radius: {DesignSystem.get_radius('base')}px;
            border-top-right-radius: {DesignSystem.get_radius('base')}px;
            font-weight: {DesignSystem.FONT_WEIGHTS['medium']};
        }}
        QTabBar::tab:selected {{
            background-color: {DesignSystem.get_color('primary')};
            color: {DesignSystem.get_color('text_inverse')};
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {DesignSystem.get_color('gray_200')};
            color: {DesignSystem.get_color('text_primary')};
        }}
        """
    
    @staticmethod
    def toolbar():
        return f"""
        QToolBar {{
            background-color: {DesignSystem.get_color('primary')};
            border: none;
            padding: {DesignSystem.get_spacing('base')}px;
            spacing: {DesignSystem.get_spacing('base')}px;
        }}
        QToolBar QToolButton {{
            background-color: transparent;
            color: {DesignSystem.get_color('text_inverse')};
            border: none;
            border-radius: {DesignSystem.get_radius('base')}px;
            padding: {DesignSystem.get_spacing('sm')}px {DesignSystem.get_spacing('base')}px;
            font-size: {DesignSystem.FONT_SIZES['base']}px;
            font-weight: {DesignSystem.FONT_WEIGHTS['medium']};
            min-height: 32px;
        }}
        QToolBar QToolButton:hover {{
            background-color: {DesignSystem.get_color('primary_dark')};
        }}
        QToolBar QToolButton:pressed {{
            background-color: {DesignSystem.get_color('primary_light')};
        }}
        """
    
    @staticmethod
    def sidebar():
        return f"""
        QFrame {{
            background-color: {DesignSystem.get_color('gray_800')};
            color: {DesignSystem.get_color('text_inverse')};
            border: none;
            min-width: 250px;
        }}
        QPushButton {{
            background-color: transparent;
            color: {DesignSystem.get_color('gray_300')};
            border: none;
            text-align: left;
            padding: {DesignSystem.get_spacing('base')}px {DesignSystem.get_spacing('xl')}px;
            font-size: {DesignSystem.FONT_SIZES['base']}px;
            min-height: 44px;
        }}
        QPushButton:hover {{
            background-color: {DesignSystem.get_color('gray_700')};
            color: {DesignSystem.get_color('text_inverse')};
        }}
        QPushButton:checked {{
            background-color: {DesignSystem.get_color('primary')};
            color: {DesignSystem.get_color('text_inverse')};
            font-weight: {DesignSystem.FONT_WEIGHTS['medium']};
        }}
        """
    
    @staticmethod
    def status_bar():
        return f"""
        QStatusBar {{
            background-color: {DesignSystem.get_color('gray_100')};
            color: {DesignSystem.get_color('text_secondary')};
            border-top: 1px solid {DesignSystem.get_color('gray_200')};
            font-size: {DesignSystem.FONT_SIZES['sm']}px;
        }}
        """
    
    @staticmethod
    def combo_box():
        return f"""
        QComboBox {{
            background-color: {DesignSystem.get_color('white')};
            border: 2px solid {DesignSystem.get_color('gray_200')};
            border-radius: {DesignSystem.get_radius('base')}px;
            padding: {DesignSystem.get_spacing('sm')}px {DesignSystem.get_spacing('base')}px;
            font-size: {DesignSystem.FONT_SIZES['base']}px;
            min-height: 40px;
        }}
        QComboBox:focus {{
            border-color: {DesignSystem.get_color('primary')};
        }}
        QComboBox::drop-down {{
            border: none;
            background-color: transparent;
        }}
        QComboBox::down-arrow {{
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0ibTQgNiA0IDQgNC00IiBzdHJva2U9IiM2QjcyODAiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
        }}
        """

class IconSystem:
    """Consistent icon system"""
    
    @staticmethod
    def get_icon_style(color=None, size=16):
        """Get base icon style"""
        color = color or DesignSystem.get_color('text_primary')
        return f"color: {color}; font-size: {size}px;"
    
    # Unicode icons for consistency
    ICONS = {
        'dashboard': '📊',
        'pos': '🛍️',
        'products': '📦',
        'customers': '👥',
        'suppliers': '🏭',
        'reports': '📈',
        'users': '👤',
        'settings': '⚙️',
        'logout': '🚪',
        'add': '➕',
        'edit': '✏️',
        'delete': '🗑️',
        'search': '🔍',
        'save': '💾',
        'cancel': '❌',
        'refresh': '🔄',
        'export': '📤',
        'import': '📥',
        'print': '🖨️',
        'help': '❓',
        'info': 'ℹ️',
        'warning': '⚠️',
        'error': '❌',
        'success': '✅',
    }
    
    @classmethod
    def get_icon(cls, name):
        """Get icon by name"""
        return cls.ICONS.get(name, '•')

# Keyboard shortcuts
SHORTCUTS = {
    'new_item': 'Ctrl+N',
    'save': 'Ctrl+S',
    'delete': 'Del',
    'refresh': 'F5',
    'search': 'Ctrl+F',
    'quit': 'Ctrl+Q',
    'close_tab': 'Ctrl+W',
    'next_tab': 'Ctrl+Tab',
    'prev_tab': 'Ctrl+Shift+Tab',
    'print': 'Ctrl+P',
    'export': 'Ctrl+E',
    'help': 'F1',
}