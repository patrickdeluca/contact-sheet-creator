import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog, QListWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QComboBox,
    QCheckBox, QLineEdit, QTextEdit, QListWidgetItem, QSplitter,
    QGraphicsView, QGraphicsScene, QAction, QMenuBar, QStatusBar, QSlider, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QKeySequence
from PyQt5.QtCore import Qt, QSize
from image_processor import ImageProcessor
from settings_manager import SettingsManager
from resources import Resources

class ContactSheetCreatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Contact Sheet Creator'
        self.left = 100
        self.top = 100
        self.width = 1200
        self.height = 800
        self.dark_mode = False

        # Load settings
        self.settings_manager = SettingsManager()
        self.image_processor = ImageProcessor(self.settings_manager)  # Pass settings_manager to ImageProcessor
        self.resources = Resources()

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Menu Bar
        self.menu_bar = QMenuBar(self)
        self.createMenuBar()

        # Status Bar
        self.status_bar = QStatusBar(self)
        self.status_bar.showMessage('Ready')

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addLayout(self.createTopLayout())
        main_layout.addWidget(self.createMainSplitter())
        main_layout.addWidget(self.status_bar)
        self.setLayout(main_layout)

        # Initialize fields with settings
        self.context_text_edit.setPlainText(self.settings_manager.context_text)
        self.font_combo_box.setCurrentText(self.settings_manager.font_name)
        self.font_size_combo_box.setCurrentText(str(self.settings_manager.font_size))
        self.export_format_combo_box.setCurrentText(self.settings_manager.export_format)
        self.quality_slider.setValue(self.settings_manager.quality)
        self.filename_pattern_line_edit.setText(self.settings_manager.filename_pattern)
        self.include_metadata_checkbox.setChecked(self.settings_manager.include_metadata)
        self.watermark_text_line_edit.setText(self.settings_manager.watermark_text)
        self.save_folder_line_edit.setText(self.settings_manager.save_folder)

        # Apply initial theme
        self.applyTheme()

    def createMenuBar(self):
        # File Menu
        file_menu = self.menu_bar.addMenu('&File')

        open_action = QAction('&Open Image Folder', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.selectImageFolder)
        file_menu.addAction(open_action)

        save_action = QAction('&Create Contact Sheet', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.createContactSheet)
        file_menu.addAction(save_action)

        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = self.menu_bar.addMenu('&Edit')

        settings_action = QAction('&Settings', self)
        settings_action.triggered.connect(self.openSettingsDialog)
        edit_menu.addAction(settings_action)

        # View Menu
        view_menu = self.menu_bar.addMenu('&View')

        theme_action = QAction('&Toggle Theme', self)
        theme_action.triggered.connect(self.toggleTheme)
        view_menu.addAction(theme_action)

    def createTopLayout(self):
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
        # Left Panel (Image List and Controls)
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # Image List
        self.image_list_widget = QListWidget()
        self.image_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.image_list_widget.itemSelectionChanged.connect(self.updatePreview)

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
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        settings_group_box = QGroupBox('Settings')
        settings_layout = QVBoxLayout()

        # Context Text
        context_text_label = QLabel('Context Text:')
        self.context_text_edit = QTextEdit()
        self.context_text_edit.textChanged.connect(self.updatePreview)

        # Font Selection
        font_label = QLabel('Font:')
        self.font_combo_box = QComboBox()
        self.font_combo_box.addItems(['Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana'])
        self.font_combo_box.currentTextChanged.connect(self.updatePreview)

        # Font Size
        font_size_label = QLabel('Size:')
        self.font_size_combo_box = QComboBox()
        self.font_size_combo_box.addItems([str(size) for size in range(12, 31, 2)])
        self.font_size_combo_box.currentTextChanged.connect(self.updatePreview)

        # Export Format
        export_format_label = QLabel('Export Format:')
        self.export_format_combo_box = QComboBox()
        self.export_format_combo_box.addItems(['JPEG', 'PNG', 'PDF'])
        self.export_format_combo_box.currentTextChanged.connect(self.updatePreview)

        # Quality Slider
        quality_label = QLabel('Quality:')
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setMinimum(1)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(80)
        self.quality_slider.valueChanged.connect(self.updatePreview)

        # Filename Pattern
        filename_pattern_label = QLabel('Filename Pattern:')
        self.filename_pattern_line_edit = QLineEdit('contact_sheet_{number}')

        # Include Metadata
        self.include_metadata_checkbox = QCheckBox('Include EXIF Data')
        self.include_metadata_checkbox.setChecked(True)
        self.include_metadata_checkbox.stateChanged.connect(self.updatePreview)

        # Watermark Text
        watermark_label = QLabel('Watermark Text:')
        self.watermark_text_line_edit = QLineEdit()
        self.watermark_text_line_edit.textChanged.connect(self.updatePreview)

        # Add widgets to settings layout
        settings_layout.addWidget(context_text_label)
        settings_layout.addWidget(self.context_text_edit)
        settings_layout.addWidget(font_label)
        settings_layout.addWidget(self.font_combo_box)
        settings_layout.addWidget(font_size_label)
        settings_layout.addWidget(self.font_size_combo_box)
        settings_layout.addWidget(export_format_label)
        settings_layout.addWidget(self.export_format_combo_box)
        settings_layout.addWidget(quality_label)
        settings_layout.addWidget(self.quality_slider)
        settings_layout.addWidget(filename_pattern_label)
        settings_layout.addWidget(self.filename_pattern_line_edit)
        settings_layout.addWidget(self.include_metadata_checkbox)
        settings_layout.addWidget(watermark_label)
        settings_layout.addWidget(self.watermark_text_line_edit)

        settings_group_box.setLayout(settings_layout)
        right_layout.addWidget(settings_group_box)

        # Preview Section
        self.preview_graphics_view = QGraphicsView()
        self.preview_graphics_scene = QGraphicsScene()
        self.preview_graphics_view.setScene(self.preview_graphics_scene)
        self.preview_graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)

        # Zoom Controls
        zoom_in_button = QPushButton('Zoom In')
        zoom_in_button.clicked.connect(self.zoomIn)
        zoom_out_button = QPushButton('Zoom Out')
        zoom_out_button.clicked.connect(self.zoomOut)

        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(zoom_in_button)
        zoom_layout.addWidget(zoom_out_button)

        right_layout.addLayout(zoom_layout)
        right_layout.addWidget(self.preview_graphics_view)
        right_widget.setLayout(right_layout)

        # Splitter to make panes resizable
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 800])

        return splitter

    def selectImageFolder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Image Folder', os.getcwd())
        if folder:
            self.image_folder_line_edit.setText(folder)
            self.image_processor.loadImagesFromFolder(folder)
            self.loadImages()

    def selectSaveFolder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Save Folder', os.getcwd())
        if folder:
            self.save_folder_line_edit.setText(folder)

    def loadImages(self):
        self.image_list_widget.clear()
        for info in self.image_processor.images_info:
            item = QListWidgetItem(info['filename'])
            item.setData(Qt.UserRole, info)
            if self.thumbnail_view:
                pixmap = QPixmap(info['thumbnail_path']).scaled(100, 100, Qt.KeepAspectRatio)
                item.setIcon(QIcon(pixmap))
            self.image_list_widget.addItem(item)
        self.status_bar.showMessage(f"Loaded {len(self.image_processor.images_info)} images.")

    def toggleView(self):
        self.thumbnail_view = not self.thumbnail_view
        self.loadImages()

    def rotateLeft(self):
        selected_items = self.image_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Images Selected", "Please select images to rotate.")
            return
        for item in selected_items:
            info = item.data(Qt.UserRole)
            self.image_processor.rotateImage(info, -90)
        self.loadImages()

    def rotateRight(self):
        selected_items = self.image_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Images Selected", "Please select images to rotate.")
            return
        for item in selected_items:
            info = item.data(Qt.UserRole)
            self.image_processor.rotateImage(info, 90)
        self.loadImages()

    def updatePreview(self):
        # Implement real-time preview update
        # For simplicity, this example doesn't implement the full preview logic
        pass

    def zoomIn(self):
        self.preview_graphics_view.scale(1.2, 1.2)

    def zoomOut(self):
        self.preview_graphics_view.scale(0.8, 0.8)

    def createContactSheet(self):
        if not self.image_processor.images_info:
            QMessageBox.warning(self, "No Images", "Please load images first.")
            return
        if not self.save_folder_line_edit.text():
            QMessageBox.warning(self, "No Save Folder", "Please select a save folder.")
            return

        # Gather settings
        self.settings_manager.context_text = self.context_text_edit.toPlainText()
        self.settings_manager.font_name = self.font_combo_box.currentText()
        self.settings_manager.font_size = int(self.font_size_combo_box.currentText())
        self.settings_manager.export_format = self.export_format_combo_box.currentText()
        self.settings_manager.quality = self.quality_slider.value()
        self.settings_manager.filename_pattern = self.filename_pattern_line_edit.text()
        self.settings_manager.include_metadata = self.include_metadata_checkbox.isChecked()
        self.settings_manager.watermark_text = self.watermark_text_line_edit.text()
        self.settings_manager.save_folder = self.save_folder_line_edit.text()

        # Get selected images
        selected_items = self.image_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Images Selected", "Please select images to include in the contact sheet.")
            return
        selected_images_info = [item.data(Qt.UserRole) for item in selected_items]

        # Create contact sheet
        self.image_processor.createContactSheet(selected_images_info, self.settings_manager)
        QMessageBox.information(self, "Success", "Contact sheet created successfully.")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if os.path.isfile(filepath):
                self.image_processor.addImage(filepath)
        self.loadImages()

    def toggleTheme(self):
        self.dark_mode = not self.dark_mode
        self.applyTheme()

    def applyTheme(self):
        if self.dark_mode:
            self.setStyleSheet(self.resources.dark_theme_stylesheet)
        else:
            self.setStyleSheet(self.resources.light_theme_stylesheet)

    def openSettingsDialog(self):
        # Implement a settings dialog window
        QMessageBox.information(self, "Settings", "Settings dialog not yet implemented.")
    
    def createContactSheet(self):
        if not self.image_processor.images_info:
            QMessageBox.warning(self, "No Images", "Please load images first.")
            return
        if not self.save_folder_line_edit.text():
            QMessageBox.warning(self, "No Save Folder", "Please select a save folder.")
            return

        # Gather settings
        self.settings_manager.context_text = self.context_text_edit.toPlainText()
        self.settings_manager.font_name = self.font_combo_box.currentText()
        self.settings_manager.font_size = int(self.font_size_combo_box.currentText())
        self.settings_manager.export_format = self.export_format_combo_box.currentText()
        self.settings_manager.quality = self.quality_slider.value()
        self.settings_manager.filename_pattern = self.filename_pattern_line_edit.text()
        self.settings_manager.include_metadata = self.include_metadata_checkbox.isChecked()
        self.settings_manager.watermark_text = self.watermark_text_line_edit.text()
        self.settings_manager.save_folder = self.save_folder_line_edit.text()

        # Save current settings
        self.settings_manager.save_settings()

        # Get selected images
        selected_items = self.image_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Images Selected", "Please select images to include in the contact sheet.")
            return
        selected_images_info = [item.data(Qt.UserRole) for item in selected_items]

        # Create contact sheet
        success = self.image_processor.createContactSheet(selected_images_info)
        if success:
            QMessageBox.information(self, "Success", "Contact sheet created successfully.")
            self.status_bar.showMessage("Contact sheet created successfully.", 5000)
        else:
            QMessageBox.warning(self, "Error", "An error occurred while creating the contact sheet.")

    def updatePreview(self):
        # Implement real-time preview update
        # Generate a preview of the contact sheet and display it in the preview_graphics_view
        selected_items = self.image_list_widget.selectedItems()
        if not selected_items:
            self.preview_graphics_scene.clear()
            return
        selected_images_info = [item.data(Qt.UserRole) for item in selected_items]

        # Update settings from GUI inputs
        self.settings_manager.context_text = self.context_text_edit.toPlainText()
        self.settings_manager.font_name = self.font_combo_box.currentText()
        self.settings_manager.font_size = int(self.font_size_combo_box.currentText())
        self.settings_manager.export_format = self.export_format_combo_box.currentText()
        self.settings_manager.quality = self.quality_slider.value()
        self.settings_manager.filename_pattern = self.filename_pattern_line_edit.text()
        self.settings_manager.include_metadata = self.include_metadata_checkbox.isChecked()
        self.settings_manager.watermark_text = self.watermark_text_line_edit.text()
        self.settings_manager.save_folder = self.save_folder_line_edit.text()

        # Generate a preview image
        preview_image = self.image_processor.generatePreview(selected_images_info)
        if preview_image:
            self.preview_graphics_scene.clear()
            pixmap = self.image_processor.imageToPixmap(preview_image)
            self.preview_graphics_scene.addPixmap(pixmap)
            self.preview_graphics_view.fitInView(self.preview_graphics_scene.sceneRect(), Qt.KeepAspectRatio)
        else:
            self.preview_graphics_scene.clear()

    def closeEvent(self, event):
        # Save settings when the application is closed
        self.settings_manager.save_settings()
        event.accept()

    def openSettingsDialog(self):
        # Implement a settings dialog window
        QMessageBox.information(self, "Settings", "Settings dialog not yet implemented.")
        # You can create a separate QDialog class to handle advanced settings if needed
