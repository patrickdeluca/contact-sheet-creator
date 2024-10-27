import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog, QListWidget,
    QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox,
    QCheckBox, QLineEdit, QTextEdit, QListWidgetItem, QSplitter,
    QGraphicsView, QGraphicsScene, QAction, QMenuBar, QStatusBar,
    QSlider, QMessageBox, QSizePolicy
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QFontDatabase
from PyQt5.QtCore import Qt
from image_processor import ImageProcessor
from settings_manager import SettingsManager
from resources import Resources


class ContactSheetCreatorGUI(QWidget):
    """Main GUI class for Contact Sheet Pro application."""

    def __init__(self):
        super().__init__()
        self.title = 'Contact Sheet Pro'
        self.left = 100
        self.top = 100
        self.width = 1600
        self.height = 1000
        self.dark_mode = False

        # Initialize font database
        self.font_db = QFontDatabase()
        
        # Load settings
        self.settings_manager = SettingsManager()
        self.image_processor = ImageProcessor(self.settings_manager)
        self.resources = Resources()

        self.preview_graphics_view = QGraphicsView()
        self.initUI()

    def _getAvailableFonts(self):
        """Get list of available system fonts."""
        return [family for family in self.font_db.families() if not family.startswith('@')]

    def _createFontComboBox(self):
        """Create the font selection combo box with available system fonts."""
        self.font_combo_box = QComboBox()
        available_fonts = self._getAvailableFonts()
        
        # Default system fonts to try
        preferred_fonts = [
            'Arial',
            'Helvetica',
            'Times New Roman',
            'Courier New',
            'Verdana',
            'Segoe UI',  # Windows default
            'SF Pro Text',  # macOS default
            'Roboto',  # Common cross-platform font
            'Liberation Sans'  # Linux default
        ]
        
        # Add available preferred fonts first
        fonts_to_add = [f for f in preferred_fonts if f in available_fonts]
        # Add remaining system fonts
        fonts_to_add.extend([f for f in available_fonts if f not in fonts_to_add])
        
        self.font_combo_box.addItems(fonts_to_add)
        
        # Set default font to first available preferred font
        for font in preferred_fonts:
            if font in fonts_to_add:
                self.font_combo_box.setCurrentText(font)
                break
        
        self.font_combo_box.currentTextChanged.connect(self.updatePreview)
        return self.font_combo_box

[REST OF FILE UNCHANGED FROM PREVIOUS VERSION]
