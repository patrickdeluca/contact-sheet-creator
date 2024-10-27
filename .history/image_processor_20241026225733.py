# image_processor.py

import os
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageOps
import pillow_heif
import piexif
from PyQt5.QtGui import QPixmap


class ImageProcessor:
    """Image processor for handling contact sheet creation and image manipulation."""

    THUMBNAIL_SIZE = (150, 150)
    IMAGE_FORMATS = ('.jpg', '.jpeg', '.png', '.heic', '.bmp', '.gif')
    DATE_FORMAT = '%Y:%m:%d %H:%M:%S'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y %H:%M:%S'

    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.images_info = []

    def _get_font(self, font_name, size):
        """Get a PIL ImageFont object, falling back to default if needed."""
        try:
            font_path = self.settings_manager.resources.get_font_path(font_name)
            return ImageFont.truetype(font_path, size)
        except Exception as e:
            print(f"Error loading font {font_name}: {e}")
            try:
                # Fallback to default font
                default_path = self.settings_manager.resources.default_font
                return ImageFont.truetype(default_path, size)
            except Exception as e:
                print(f"Error loading default font: {e}")
                return ImageFont.load_default()

[... rest of the image_processor.py code unchanged ...]
