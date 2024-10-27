# gui.py

import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog, QListWidget,
    QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox,
    QCheckBox, QLineEdit, QTextEdit, QListWidgetItem, QSplitter,
    QGraphicsView, QGraphicsScene, QAction, QMenuBar, QStatusBar, 
    QSlider, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
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
        self.width = 1200
        self.height = 800
        self.dark_mode = False

        # Load settings
        self.settings_manager = SettingsManager()
        self.image_processor = ImageProcessor(self.settings_manager)
        self.resources = Resources()

        self.initUI()

    def initUI(self):
        """Initialize the user interface."""
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
        self.initializeFields()
        
        # Apply initial theme
        self.applyTheme()

    def initializeFields(self):
        """Initialize all fields with settings values."""
        settings = self.settings_manager
        self.context_text_edit.setPlainText(settings.context_text)
        self.font_combo_box.setCurrentText(settings.font_name)
        self.font_size_combo_box.setCurrentText(str(settings.font_size))
        self.export_format_combo_box.setCurrentText(settings.export_format)
        self.quality_slider.setValue(settings.quality)
        pattern = settings.filename_pattern
        self.filename_pattern_line_edit.setText(pattern)
        self.include_metadata_checkbox.setChecked(settings.include_metadata)
        self.watermark_text_line_edit.setText(settings.watermark_text)
        self.save_folder_line_edit.setText(settings.save_folder)

    def createMenuBar(self):
        """Create and populate the menu bar."""
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
        """Create the File menu items."""
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
        """Create the Edit menu items."""
        settings_action = QAction('&Settings', self)
        settings_action.triggered.connect(self.openSettingsDialog)
        menu.addAction(settings_action)

    def _createViewMenu(self, menu):
        """Create the View menu items."""
        theme_action = QAction('&Toggle Theme', self)
        theme_action.triggered.connect(self.toggleTheme)
        menu.addAction(theme_action)

    def _createHelpMenu(self, menu):
        """Create the Help menu items."""
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.showAboutDialog)
        menu.addAction(about_action)

    def showAboutDialog(self):
        """Show the About dialog."""
        about_text = (
            "Contact Sheet Pro\n\n"
            "Version 1.0.0\n"
            "Copyright © 2024 Patrick DeLuca\n"
            "GitHub: patrickdeluca\n\n"
            "A professional tool for creating contact sheets "
            "with EXIF data and customizable layouts."
        )
        QMessageBox.about(self, "About Contact Sheet Pro", about_text)

    def createTopLayout(self):
        """Create the top section of the interface."""
        # Image Folder Selection
        image_folder_label = QLabel('Image Folder:')
        self.image_folder_line_edit = QLineEdit()
        image_folder_button = QPushButton('📁')
        image_folder_button.clicked.connect(self.selectImageFolder)
        image_folder_layout = QHBoxLayout()
        image_folder_layout.addWidget(image_folder_label)
        image_folder_layout.addWidget(self.image_folder_line_edit)
        image_folder_layout.addWidget(image_folder_button)

        # Save Folder Selection
        save_folder_label = QLabel('Save To:')
        self.save_folder_line_edit = QLineEdit()
        save_folder_button = QPushButton('📁')
        save_folder_button.clicked.connect(self.selectSaveFolder)
        save_folder_layout = QHBoxLayout()
        save_folder_layout.addWidget(save_folder_label)
        save_folder_layout.addWidget(self.save_folder_line_edit)
        save_folder_layout.addWidget(save_folder_button)

        # Top layout
        top_layout = QHBoxLayout()
        top_layout.addLayout(image_folder_layout)
        top_layout.addLayout(save_folder_layout)

        return top_layout

    def createMainSplitter(self):
        """Create the main content area with left and right panels."""
        # Left Panel (Image List and Controls)
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # Image List
        self.image_list_widget = QListWidget()
        self.image_list_widget.setSelectionMode(
            QListWidget.ExtendedSelection
        )
        self.image_list_widget.itemSelectionChanged.connect(
            self.updatePreview
        )

        # Drag and Drop Support
        self.image_list_widget.setAcceptDrops(True)
        self.image_list_widget.dragEnterEvent = self.dragEnterEvent
        self.image_list_widget.dropEvent = self.dropEvent

        # View Toggle Button
        self.view_toggle_button = QPushButton('Toggle View')
        self.view_toggle_button.clicked.connect(self.toggleView)
        self.thumbnail_view = True

        # Image Editing Tools
        rotate_left_button = QPushButton('Rotate Left')
        rotate_left_button.clicked.connect(self.rotateLeft)
        rotate_right_button = QPushButton('Rotate Right')
        rotate_right_button.clicked.connect(self.rotateRight)

        editing_layout = QHBoxLayout()
        editing_layout.addWidget(self.view_toggle_button)
        editing_layout.addWidget(rotate_left_button)
        editing_layout.addWidget(rotate_right_button)

        # CREATE Button
        create_button = QPushButton('CREATE')
        create_button.setFont(QFont('Arial', 14, QFont.Bold))
        create_button.clicked.connect(self.createContactSheet)

        left_layout.addLayout(editing_layout)
        left_layout.addWidget(self.image_list_widget)
        left_layout.addWidget(create_button)
        left_widget.setLayout(left_layout)

        # Right Panel (Settings and Preview)
        right_widget = self._createRightPanel()

        # Splitter to make panes resizable
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 800])

        return splitter

    def _createRightPanel(self):
        """Create the right panel with settings and preview."""
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # Settings Group
        settings_group = self._createSettingsGroup()
        right_layout.addWidget(settings_group)

        # Preview Section
        preview_section = self._createPreviewSection()
        right_layout.addWidget(preview_section)

        right_widget.setLayout(right_layout)
        return right_widget

    def _createSettingsGroup(self):
        """Create the settings group box."""
        settings_group = QGroupBox('Settings')
        layout = QVBoxLayout()

        # Add settings controls
        controls = [
            ('Context Text:', self._createContextTextEdit()),
            ('Font:', self._createFontComboBox()),
            ('Size:', self._createFontSizeComboBox()),
            ('Export Format:', self._createExportFormatComboBox()),
            ('Quality:', self._createQualitySlider()),
            ('Filename Pattern:', self._createFilenamePatternEdit()),
            (None, self._createMetadataCheckbox()),
            ('Watermark Text:', self._createWatermarkEdit())
        ]

        for label_text, control in controls:
            if label_text:
                layout.addWidget(QLabel(label_text))
            layout.addWidget(control)

        settings_group.setLayout(layout)
        return settings_group

    def _createContextTextEdit(self):
        """Create the context text edit control."""
        self.context_text_edit = QTextEdit()
        self.context_text_edit.textChanged.connect(self.updatePreview)
        return self.context_text_edit

    def _createFontComboBox(self):
        """Create the font selection combo box."""
        self.font_combo_box = QComboBox()
        fonts = [
            'Arial',
            'Helvetica',
            'Times New Roman',
            'Courier New',
            'Verdana'
        ]
        self.font_combo_box.addItems(fonts)
        self.font_combo_box.currentTextChanged.connect(self.updatePreview)
        return self.font_combo_box

    def _createFontSizeComboBox(self):
        """Create the font size combo box."""
        self.font_size_combo_box = QComboBox()
        sizes = [str(size) for size in range(12, 31, 2)]
        self.font_size_combo_box.addItems(sizes)
        self.font_size_combo_box.currentTextChanged.connect(
            self.updatePreview
        )
        return self.font_size_combo_box

    def _createExportFormatComboBox(self):
        """Create the export format combo box."""
        self.export_format_combo_box = QComboBox()
        self.export_format_combo_box.addItems(['JPEG', 'PNG', 'PDF'])
        self.export_format_combo_box.currentTextChanged.connect(
            self.updatePreview
        )
        return self.export_format_combo_box

    def _createQualitySlider(self):
