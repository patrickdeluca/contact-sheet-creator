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

        self.preview_graphics_view = QGraphicsView()
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
        """Create the quality slider control."""
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setMinimum(1)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(80)
        self.quality_slider.valueChanged.connect(self.updatePreview)
        return self.quality_slider

    def _createFilenamePatternEdit(self):
        """Create the filename pattern edit control."""
        self.filename_pattern_line_edit = QLineEdit('contact_sheet_{number}')
        return self.filename_pattern_line_edit

    def _createMetadataCheckbox(self):
        """Create the metadata checkbox control."""
        self.include_metadata_checkbox = QCheckBox('Include EXIF Data')
        self.include_metadata_checkbox.setChecked(True)
        self.include_metadata_checkbox.stateChanged.connect(self.updatePreview)
        return self.include_metadata_checkbox

    def _createWatermarkEdit(self):
        """Create the watermark text edit control."""
        self.watermark_text_line_edit = QLineEdit()
        self.watermark_text_line_edit.textChanged.connect(self.updatePreview)
        return self.watermark_text_line_edit

    def _createPreviewSection(self):
        """Create the preview section."""
        preview_widget = QWidget()
        layout = QVBoxLayout()

        # Preview View
        self.preview_graphics_view = QGraphicsView()
        self.preview_graphics_scene = QGraphicsScene()
        self.preview_graphics_view.setScene(self.preview_graphics_scene)
        self.preview_graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)

        # Zoom Controls
        zoom_layout = QHBoxLayout()
        zoom_in_btn = QPushButton('Zoom In')
        zoom_out_btn = QPushButton('Zoom Out')
        zoom_in_btn.clicked.connect(self.zoomIn)
        zoom_out_btn.clicked.connect(self.zoomOut)
        zoom_layout.addWidget(zoom_in_btn)
        zoom_layout.addWidget(zoom_out_btn)

        layout.addLayout(zoom_layout)
        layout.addWidget(self.preview_graphics_view)
        preview_widget.setLayout(layout)
        return preview_widget

    def selectImageFolder(self):
        """Handle image folder selection."""
        folder = QFileDialog.getExistingDirectory(
            self,
            'Select Image Folder',
            os.getcwd()
        )
        if folder:
            self.image_folder_line_edit.setText(folder)
            self.image_processor.load_images_from_folder(folder)
            self.loadImages()

    def selectSaveFolder(self):
        """Handle save folder selection."""
        folder = QFileDialog.getExistingDirectory(
            self,
            'Select Save Folder',
            os.getcwd()
        )
        if folder:
            self.save_folder_line_edit.setText(folder)

    def loadImages(self):
        """Load and display images in the list widget."""
        self.image_list_widget.clear()
        for info in self.image_processor.images_info:
            item = QListWidgetItem(info['filename'])
            item.setData(Qt.UserRole, info)
            if self.thumbnail_view:
                pixmap = QPixmap(info['thumbnail_path'])
                scaled_pixmap = pixmap.scaled(
                    100, 100,
                    Qt.KeepAspectRatio
                )
                item.setIcon(QIcon(scaled_pixmap))
            self.image_list_widget.addItem(item)

        msg = f"Loaded {len(self.image_processor.images_info)} images."
        self.status_bar.showMessage(msg)

    def toggleView(self):
        """Toggle between thumbnail and list view."""
        self.thumbnail_view = not self.thumbnail_view
        self.loadImages()

    def rotateLeft(self):
        """Rotate selected images left."""
        self._rotateImages(-90)

    def rotateRight(self):
        """Rotate selected images right."""
        self._rotateImages(90)

    def _rotateImages(self, angle):
        """Rotate selected images by the specified angle."""
        selected_items = self.image_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                "No Images Selected",
                "Please select images to rotate."
            )
            return

        for item in selected_items:
            info = item.data(Qt.UserRole)
            self.image_processor.rotate_image(info, angle)
        self.loadImages()

    def updatePreview(self):
        """Update the preview display."""
        selected_items = self.image_list_widget.selectedItems()
        if not selected_items:
            self.preview_graphics_scene.clear()
            return

        selected_images = [item.data(Qt.UserRole) for item in selected_items]
        self._updateSettings()

        preview_image = self.image_processor.generate_preview(selected_images)
        if preview_image:
            self._updatePreviewDisplay(preview_image)
        else:
            self.preview_graphics_scene.clear()

    def _updateSettings(self):
        """Update settings from GUI inputs."""
        settings = self.settings_manager
        settings.context_text = self.context_text_edit.toPlainText()
        settings.font_name = self.font_combo_box.currentText()
        settings.font_size = int(self.font_size_combo_box.currentText())
        settings.export_format = self.export_format_combo_box.currentText()
        settings.quality = self.quality_slider.value()
        settings.filename_pattern = self.filename_pattern_line_edit.text()
        settings.include_metadata = self.include_metadata_checkbox.isChecked()
        settings.watermark_text = self.watermark_text_line_edit.text()
        settings.save_folder = self.save_folder_line_edit.text()

    def _updatePreviewDisplay(self, preview_image):
        """Update the preview display with the given image."""
        self.preview_graphics_scene.clear()
        pixmap = self.image_processor.image_to_pixmap(preview_image)
        self.preview_graphics_scene.addPixmap(pixmap)
        self.preview_graphics_view.fitInView(
            self.preview_graphics_scene.sceneRect(),
            Qt.KeepAspectRatio
        )

    def zoomIn(self):
        """Zoom in on the preview."""
        self.preview_graphics_view.scale(1.2, 1.2)

    def zoomOut(self):
        """Zoom out on the preview."""
        self.preview_graphics_view.scale(0.8, 0.8)

    def createContactSheet(self):
        """Create the contact sheet."""
        if not self._validateContactSheetCreation():
            return

        self._updateSettings()
        self.settings_manager.save_settings()

        selected_items = self.image_list_widget.selectedItems()
        selected_images = [item.data(Qt.UserRole) for item in selected_items]

        if self.image_processor.create_contact_sheet(selected_images):
            self._showSuccessMessage()
        else:
            self._showErrorMessage()

    def _validateContactSheetCreation(self):
        """Validate conditions for contact sheet creation."""
        if not self.image_processor.images_info:
            QMessageBox.warning(self, "No Images", "Please load images first.")
            return False

        if not self.save_folder_line_edit.text():
            QMessageBox.warning(
                self,
                "No Save Folder",
                "Please select a save folder."
            )
            return False

        if not self.image_list_widget.selectedItems():
            QMessageBox.warning(
                self,
                "No Images Selected",
                "Please select images to include in the contact sheet."
            )
            return False

        return True

    def _showSuccessMessage(self):
        """Show success message after contact sheet creation."""
        QMessageBox.information(
            self,
            "Success",
            "Contact sheet created successfully."
        )
        self.status_bar.showMessage(
            "Contact sheet created successfully.",
            5000
        )

    def _showErrorMessage(self):
        """Show error message if contact sheet creation fails."""
        QMessageBox.warning(
            self,
            "Error",
            "An error occurred while creating the contact sheet."
        )

    def dragEnterEvent(self, event):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop events."""
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if os.path.isfile(filepath):
                self.image_processor.add_image(filepath)
        self.loadImages()

    def toggleTheme(self):
        """Toggle between light and dark themes."""
        self.dark_mode = not self.dark_mode
        self.applyTheme()

    def applyTheme(self):
        """Apply the current theme."""
        stylesheet = (
            self.resources.dark_theme_stylesheet
            if self.dark_mode
            else self.resources.light_theme_stylesheet
        )
        self.setStyleSheet(stylesheet)

    def openSettingsDialog(self):
        """Show the settings dialog."""
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog not yet implemented."
        )

    def closeEvent(self, event):
        """Handle application close event."""
        self.settings_manager.save_settings()
        event.accept()
