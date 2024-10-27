# image_processor.py

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

    def _get_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        """Get a PIL ImageFont object, falling back to default if needed."""
        try:
            font_path = self.settings_manager.resources.get_font_path(
                font_name
            )
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

    def load_images_from_folder(self, folder_path: str) -> None:
        """Load all supported images from the specified folder."""
        self.images_info.clear()
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(self.IMAGE_FORMATS):
                self._process_image_file(folder_path, filename)

    def _process_image_file(self, folder_path: str, filename: str) -> None:
        """Process a single image file and add it to images_info."""
        try:
            file_path = os.path.join(folder_path, filename)
            pillow_heif.register_heif_opener()
            with Image.open(file_path) as img:
                # Create thumbnail
                thumb_path = os.path.join(
                    folder_path,
                    f".thumbnail_{filename}"
                )
                img_copy = img.copy()
                img_copy.thumbnail(self.THUMBNAIL_SIZE)
                img_copy.save(thumb_path)
                
                # Extract metadata
                exif_dict = self.extract_exif_data(img)
                date_time = self.get_datetime_from_exif(exif_dict)
                date_str = (
                    date_time.strftime(self.DISPLAY_DATE_FORMAT)
                    if date_time else 'Unknown Date'
                )
                
                # Store image info
                self.images_info.append({
                    'filename': filename,
                    'path': file_path,
                    'thumbnail_path': thumb_path,
                    'exif': exif_dict,
                    'date_time': date_str,
                    'rotation': 0
                })
        except Exception as e:
            print(f"Error loading image {filename}: {e}")

    def add_image(self, file_path: str) -> None:
        """Add a single image to the collection."""
        filename = os.path.basename(file_path)
        if filename.lower().endswith(self.IMAGE_FORMATS):
            self._process_image_file(
                os.path.dirname(file_path),
                filename
            )

    def rotate_image(self, info: Dict, angle: int) -> None:
        """Rotate an image and its thumbnail by the specified angle."""
        try:
            with Image.open(info['path']) as img:
                rotated = img.rotate(angle, expand=True)
                rotated.save(info['path'])
                
                # Update thumbnail
                rotated.thumbnail(self.THUMBNAIL_SIZE)
                rotated.save(info['thumbnail_path'])
                info['rotation'] = (info['rotation'] + angle) % 360
        except Exception as e:
            print(f"Error rotating image {info['filename']}: {e}")

    def extract_exif_data(self, image: Image.Image) -> Dict:
        """Extract EXIF data from an image."""
        exif_dict = {}
        try:
            exif_bytes = image.info.get('exif', b'')
            if exif_bytes:
                exif_dict = piexif.load(exif_bytes)
        except Exception as e:
            print(f"Error extracting EXIF data: {e}")
        return exif_dict

    def get_datetime_from_exif(self, exif_dict: Dict) -> Optional[datetime]:
        """Extract datetime from EXIF data."""
        try:
            exif = exif_dict.get('Exif', {})
            date_time_str = exif.get(piexif.ExifIFD.DateTimeOriginal)
            if date_time_str:
                date_time_str = date_time_str.decode('utf-8')
                return datetime.strptime(
                    date_time_str,
                    self.DATE_FORMAT
                )
        except Exception as e:
            print(f"Error parsing EXIF date: {e}")
        return None

    def create_contact_sheet(self, images_info: List[Dict]) -> bool:
        """Create contact sheets from the provided images."""
        try:
            settings = self.settings_manager
            save_folder = settings.save_folder
            os.makedirs(save_folder, exist_ok=True)

            # Sort images by date_time
            images_info.sort(key=lambda x: x['date_time'])

            # Page setup (8.5 x 11 inches at 300 DPI)
            page_size = (2550, 3300)
            margin = 50

            layout = self._calculate_layout(
                len(images_info),
                page_size,
                margin
            )
            font = self._get_font(settings.font_name, settings.font_size)
            pages = self._generate_pages(
                images_info,
                page_size,
                layout,
                margin,
                font
            )
            return self._save_pages(pages, settings)
        except Exception as e:
            print(f"Error creating contact sheet: {e}")
            return False

    def _calculate_layout(
        self,
        total_images: int,
        page_size: Tuple[int, int],
        margin: int
    ) -> Tuple[int, int, int, int]:
        """Calculate layout parameters for contact sheet."""
        width, height = page_size
        images_per_page = min(4, total_images)
        cols = 2
        rows = (images_per_page + cols - 1) // cols
        
        thumb_width = (width - (cols + 1) * margin) // cols
        thumb_height = (height - (rows + 1) * margin - 200) // rows
        
        return images_per_page, cols, thumb_width, thumb_height

    def _generate_pages(
        self,
        images_info: List[Dict],
        page_size: Tuple[int, int],
        layout_params: Tuple[int, int, int, int],
        margin: int,
        font: ImageFont.FreeTypeFont
    ) -> List[Image.Image]:
        """Generate contact sheet pages."""
        pages = []
        images_per_page, cols, thumb_width, thumb_height = layout_params
        width, height = page_size

        for i in range(0, len(images_info), images_per_page):
            page = Image.new('RGB', page_size, 'white')
            draw = ImageDraw.Draw(page)
            y_offset = margin

            if self.settings_manager.context_text:
                draw.text(
                    (margin, y_offset),
                    self.settings_manager.context_text,
                    fill='black',
                    font=font
                )
                y_offset += self.settings_manager.font_size + margin

            batch = images_info[i:i + images_per_page]
            self._add_images_to_page(
                page,
                batch,
                cols,
                thumb_width,
                thumb_height,
                margin,
                y_offset
            )

            if self.settings_manager.watermark_text:
                self._add_watermark(page, draw, width, height, margin)

            pages.append(page)

        return pages

    def _add_images_to_page(
        self,
        page: Image.Image,
        images: List[Dict],
        cols: int,
        thumb_width: int,
        thumb_height: int,
        margin: int,
        y_offset: int
    ) -> None:
        """Add images to a contact sheet page."""
        for idx, info in enumerate(images):
            row = idx // cols
            col = idx % cols
            x = margin + col * (thumb_width + margin)
            y = y_offset + row * (thumb_height + margin + 50)

            with Image.open(info['path']) as img:
                if info['rotation']:
                    img = img.rotate(info['rotation'], expand=True)
                
                img_resized = ImageOps.contain(
                    img,
                    (thumb_width, thumb_height)
                )
                paste_x = x + (thumb_width - img_resized.width) // 2
                paste_y = y + (thumb_height - img_resized.height) // 2
                page.paste(img_resized, (paste_x, paste_y))

            # Add image caption
            text = f"{info['filename']}\n{info['date_time']}"
            text_font = self._get_font(
                self.settings_manager.font_name,
                20
            )
            draw = ImageDraw.Draw(page)
            draw.text(
                (x, y + thumb_height + 5),
                text,
                fill='black',
                font=text_font
            )

    def _add_watermark(
        self,
        page: Image.Image,
        draw: ImageDraw.ImageDraw,
        width: int,
        height: int,
        margin: int
    ) -> None:
        """Add watermark to a contact sheet page."""
        watermark_font = self._get_font(
            self.settings_manager.font_name,
            40
        )
        text_width = draw.textlength(
            self.settings_manager.watermark_text,
            font=watermark_font
        )
        text_height = self.settings_manager.font_size
        position = (
            width - text_width - margin,
            height - text_height - margin
        )
        draw.text(
            position,
            self.settings_manager.watermark_text,
            fill='grey',
            font=watermark_font
        )

    def _save_pages(
        self,
        pages: List[Image.Image],
        settings
    ) -> bool:
        """Save contact sheet pages to files."""
        try:
            for idx, page in enumerate(pages):
                page_number = str(idx + 1).zfill(3)
                filename = settings.filename_pattern.replace(
                    '{number}',
                    page_number
                )
                output_path = os.path.join(
                    settings.save_folder,
                    f"{filename}.{settings.export_format.lower()}"
                )
                
                if settings.export_format.lower() == 'pdf':
                    page.save(output_path, 'PDF', resolution=300)
                elif settings.export_format.lower() in ['jpg', 'jpeg']:
                    page.save(output_path, 'JPEG', quality=settings.quality)
                elif settings.export_format.lower() == 'png':
                    compress = int((100 - settings.quality) / 10)
                    page.save(output_path, 'PNG', compress_level=compress)
                else:
                    page.save(output_path)
            return True
        except Exception as e:
            print(f"Error saving pages: {e}")
            return False

    def generate_preview(self, images_info: List[Dict]) -> Optional[Image.Image]:
        """Generate a preview of the contact sheet."""
        if not images_info:
            return None

        try:
            # Preview setup
            page_size = (800, 600)
            margin = 10
            layout = self._calculate_layout(
                len(images_info),
                page_size,
                margin
            )

            font = self._get_font(
                self.settings_manager.font_name,
                self.settings_manager.font_size
            )
            pages = self._generate_pages(
                images_info[:layout[0]],
                page_size,
                layout,
                margin,
                font
            )
            return pages[0] if pages else None
        except Exception as e:
            print(f"Error generating preview: {e}")
            return None

    def image_to_pixmap(self, image: Image.Image) -> QPixmap:
        """Convert PIL Image to QPixmap."""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        return pixmap
