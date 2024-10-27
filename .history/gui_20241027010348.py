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

[Previous methods unchanged until _createPreviewSection]

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

[Rest of the file unchanged]
