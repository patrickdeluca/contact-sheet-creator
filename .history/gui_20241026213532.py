# gui.py

import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog, QListWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QComboBox,
    QCheckBox, QLineEdit, QTextEdit, QListWidgetItem, QSplitter,
    QGraphicsView, QGraphicsScene, QAction, QMenuBar, QStatusBar, 
    QSlider, QMessageBox, QMenu
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QKeySequence
from PyQt5.QtCore import Qt, QSize
from image_processor import ImageProcessor
from settings_manager import SettingsManager
from resources import Resources

class ContactSheetCreatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Contact Sheet Pro'
        self.left = 100
        self.top = 100
        self.width = 1200
        self.height = 800
        self.dark_mode = False

        # Load settings
        self.settings_manager = SettingsManager()
        self.image_processor = ImageProcessor(self.settings_manager)
        self.resources = Resources()

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Menu Bar
        self.menu_bar = QMenuBar(self)
        self.createMenuBar()

        # Status Bar with Copyright
        self.status_bar = QStatusBar(self)
        copyright_label = QLabel("© 2024 Patrick DeLuca")
        self.status_bar.addPermanentWidget(copyright_label)
        self.status_bar.showMessage('Ready')

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addLayout(self.createTopLayout())
        main_layout.addWidget(self.createMainSplitter())
        main_layout.addWidget(self.status_bar)
        self.setLayout(main_layout)

        # Initialize fields with settings
        self._initializeFields()
        
        # Apply initial theme
        self.applyTheme()

    def createMenuBar(self):
        # File Menu
        file_menu = self.menu_bar.addMenu('&File')
        self._createFileMenu(file_menu)

        # Edit Menu
        edit_menu = self.menu_bar.addMenu('&Edit')
        self._createEditMenu(edit_menu)

        # View Menu
        view_menu = self.menu_bar.addMenu('&View')
        self._createViewMenu(view_menu)

        # Help Menu
        help_menu = self.menu_bar.addMenu('&Help')
        self._createHelpMenu(help_menu)

    def _createFileMenu(self, menu):
        open_action = QAction('&Open Image Folder', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.selectImageFolder)
        menu.addAction(open_action)

        save_action = QAction('&Create Contact Sheet', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.createContactSheet)
        menu.addAction(save_action)

        menu.addSeparator()

        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)

    def _createEditMenu(self, menu):
        settings_action = QAction('&Settings', self)
        settings_action.triggered.connect(self.openSettingsDialog)
        menu.addAction(settings_action)

    def _createViewMenu(self, menu):
        theme_action = QAction('&Toggle Theme', self)
        theme_action.triggered.connect(self.toggleTheme)
        menu.addAction(theme_action)

    def _createHelpMenu(self, menu):
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.showAboutDialog)
        menu.addAction(about_action)

    def showAboutDialog(self):
        about_text = (
            "Contact Sheet Pro\n\n"
            "Version 1.0.0\n"
            "Copyright © 2024 Patrick DeLuca\n"
            "GitHub: patrickdeluca\n\n"
            "A professional tool for creating contact sheets "
            "with EXIF data and customizable layouts."
        )
        QMessageBox.about(self, "About Contact Sheet Pro", about_text)

[... rest of the existing GUI code ...]
