import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog, QListWidget,
    QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox,
    QCheckBox, QLineEdit, QTextEdit, QListWidgetItem, QSplitter,
    QGraphicsView, QGraphicsScene, QAction, QMenuBar, QStatusBar,
    QSlider, QMessageBox, QSizePolicy
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
        self.width = 1600
        self.height = 1000
        self.dark_mode = False

        # Preview state
        self.current_preview_page = 1
        self.total_preview_pages = 1

        # Load settings
        self.settings_manager = SettingsManager()
        self.image_processor = ImageProcessor(self.settings_manager)
        self.resources = Resources()

        self.preview_graphics_view = QGraphicsView()
        self.initUI()

    def _createPreviewSection(self):
        """Create the preview section."""
        preview_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Preview View
        self.preview_graphics_view = QGraphicsView()
        self.preview_graphics_scene = QGraphicsScene()
        self.preview_graphics_view.setScene(self.preview_graphics_scene)
        self.preview_graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)

        # Set size policy for preview
        self.preview_graphics_view.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        # Navigation Controls
        nav_layout = QHBoxLayout()

        # Zoom Controls
        zoom_in_btn = QPushButton('Zoom In')
        zoom_out_btn = QPushButton('Zoom Out')
        zoom_in_btn.clicked.connect(self.zoomIn)
        zoom_out_btn.clicked.connect(self.zoomOut)

        # Page Navigation
        self.prev_page_btn = QPushButton('Previous Page')
        self.next_page_btn = QPushButton('Next Page')
        self.page_label = QLabel('Page 1 of 1')

        self.prev_page_btn.clicked.connect(self.previousPreviewPage)
        self.next_page_btn.clicked.connect(self.nextPreviewPage)

        nav_layout.addWidget(zoom_in_btn)
        nav_layout.addWidget(zoom_out_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_page_btn)
        nav_layout.addWidget(self.page_label)
        nav_layout.addWidget(self.next_page_btn)

        layout.addLayout(nav_layout)
        layout.addWidget(self.preview_graphics_view)
        preview_widget.setLayout(layout)
        return preview_widget

    def previousPreviewPage(self):
        """Show previous preview page."""
        if self.current_preview_page > 1:
            self.current_preview_page -= 1
            self.updatePreview()
            self._updateNavigationButtons()

    def nextPreviewPage(self):
        """Show next preview page."""
        if self.current_preview_page < self.total_preview_pages:
            self.current_preview_page += 1
            self.updatePreview()
            self._updateNavigationButtons()

    def _updateNavigationButtons(self):
        """Update the state of navigation buttons."""
        self.prev_page_btn.setEnabled(self.current_preview_page > 1)
        self.next_page_btn.setEnabled(
            self.current_preview_page < self.total_preview_pages
        )

    def updatePreview(self):
        """Update the preview display."""
        selected_items = self.image_list_widget.selectedItems()
        if not selected_items:
            self.preview_graphics_scene.clear()
            self.total_preview_pages = 1
            self.current_preview_page = 1
            self._updateNavigationButtons()
            return

        selected_images = [item.data(Qt.UserRole) for item in selected_items]
        self._updateSettings()

        # Get total pages first
        self.total_preview_pages = self.image_processor.get_total_pages(
            len(selected_images)
        )

        # Ensure current page is valid
        self.current_preview_page = min(
            self.current_preview_page,
            self.total_preview_pages
        )

        preview_image = self.image_processor.generate_preview(
            selected_images,
            self.current_preview_page
        )

        if preview_image:
            self._updatePreviewDisplay(preview_image)
            self.page_label.setText(
                f'Page {self.current_preview_page} of {self.total_preview_pages}'
            )
            self._updateNavigationButtons()
        else:
            self.preview_graphics_scene.clear()


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
        left_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

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
        splitter.setSizes([300, 1300])  # Give more space to the right panel
        
        # Set minimum sizes to prevent panels from disappearing
        left_widget.setMinimumWidth(200)
        right_widget.setMinimumWidth(800)

        return splitter

    def _createRightPanel(self):
        """Create the right panel with settings and preview."""
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Settings and Preview in horizontal layout
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Settings Group (now on the left side)
        settings_group = self._createSettingsGroup()
        settings_group.setMaximumWidth(300)  # Limit settings width
        h_layout.addWidget(settings_group)

        # Preview Section (now on the right side)
        preview_section = self._createPreviewSection()
        h_layout.addWidget(preview_section, stretch=2)  # Give preview more space

        right_layout.addLayout(h_layout)
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
        self.context_text_edit.setMaximumHeight(100)  # Limit height
        self.context_text_edit.textChanged.connect(self.updatePreview)
        return self.context_text_edit

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
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Preview View
        self.preview_graphics_view = QGraphicsView()
        self.preview_graphics_scene = QGraphicsScene()
        self.preview_graphics_view.setScene(self.preview_graphics_scene)
        self.preview_graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Set size policy for preview
        self.preview_graphics_view.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        # Navigation Controls
        nav_layout = QHBoxLayout()
        
        # Zoom Controls
        zoom_in_btn = QPushButton('Zoom In')
        zoom_out_btn = QPushButton('Zoom Out')
        zoom_in_btn.clicked.connect(self.zoomIn)
        zoom_out_btn.clicked.connect(self.zoomOut)
        
        # Page Navigation
        prev_page_btn = QPushButton('Previous Page')
        next_page_btn = QPushButton('Next Page')
        self.page_label = QLabel('Page 1 of 1')
        
        prev_page_btn.clicked.connect(self.previousPreviewPage)
        next_page_btn.clicked.connect(self.nextPreviewPage)
        
        nav_layout.addWidget(zoom_in_btn)
        nav_layout.addWidget(zoom_out_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(prev_page_btn)
        nav_layout.addWidget(self.page_label)
        nav_layout.addWidget(next_page_btn)

        layout.addLayout(nav_layout)
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

    def showStatusMessage(self, message, timeout=0):
        """Show a message in the status bar."""
        self.status_message.setText(message)

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
        self.showStatusMessage(msg)

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

        preview_image = self.image_processor.generate_preview(
            selected_images,
            self.current_preview_page
        )
        if preview_image:
            self._updatePreviewDisplay(preview_image)
            # Update total pages
            self.total_preview_pages = (
                len(selected_images) + self.image_processor.images_per_page - 1
            ) // self.image_processor.images_per_page
            self.page_label.setText(
                f'Page {self.current_preview_page} of {self.total_preview_pages}'
            )
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
        self.showStatusMessage("Contact sheet created successfully.", 5000)

    def _showErrorMessage(self):
        """Show error message if contact sheet creation fails."""
        QMessageBox.warning(
            self,
            "Error",
            "An error occurred while creating the contact sheet."
        )
        self.showStatusMessage("Error creating contact sheet", 5000)

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
