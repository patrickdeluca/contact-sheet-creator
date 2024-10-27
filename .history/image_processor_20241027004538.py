import os
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from PIL import (
    Image, ImageDraw, ImageFont, ImageOps
)
import pillow_heif
import piexif
from PyQt5.QtGui import QPixmap


class ImageProcessor:
    """Handles contact sheet creation and image manipulation."""

    THUMBNAIL_SIZE = (150, 150)
    IMAGE_FORMATS = (
        '.jpg', '.jpeg', '.png',
        '.heic', '.bmp', '.gif'
    )
    DATE_FORMAT = '%Y:%m:%d %H:%M:%S'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y %H:%M:%S'

    def __init__(self, settings_manager):
        """Initialize with settings manager."""
        self.settings_manager = settings_manager
        self.images_info: List[Dict] = []
        self.images_per_page = 6  # Default value, will be updated by layout

[PREVIOUS METHODS UNCHANGED UNTIL generate_preview]

    def generate_preview(
        self,
        images_info: List[Dict],
        page_num: int = 1
    ) -> Optional[Image.Image]:
        """Generate a preview of the contact sheet for a specific page."""
        if not images_info:
            return None

        try:
            # Preview setup (scaled down from full size)
            preview_width = 800
            preview_height = int(preview_width * (11/8.5))
            page_size = (preview_width, preview_height)
            margin = 10
            
            layout = self._calculate_layout(
                len(images_info),
                page_size,
                margin
            )
            self.images_per_page = layout[0]  # Store for pagination

            font = self._get_font('Arial', self.settings_manager.font_size)
            
            # Calculate start and end indices for requested page
            start_idx = (page_num - 1) * self.images_per_page
            end_idx = min(start_idx + self.images_per_page, len(images_info))
            
            # Generate preview of requested page
            if start_idx < len(images_info):
                page_images = images_info[start_idx:end_idx]
                total_pages = (
                    len(images_info) + self.images_per_page - 1
                ) // self.images_per_page
                
                preview = self._generate_page(
                    page_images,
                    page_size,
                    layout,
                    margin,
                    font,
                    page_num,
                    total_pages
                )
                return preview
            return None
        except Exception as e:
            print(f"Error generating preview: {e}")
            return None

[REST OF FILE UNCHANGED]
