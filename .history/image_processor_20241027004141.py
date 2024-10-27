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
        """Get a PIL ImageFont object, using system defaults."""
        try:
            # Try to use a default system font
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            try:
                # Try DejaVu Sans as a fallback (common on Linux)
                return ImageFont.truetype("DejaVuSans.ttf", size)
            except Exception:
                try:
                    # Try Liberation Sans as another fallback
                    return ImageFont.truetype("LiberationSans-Regular.ttf", size)
                except Exception:
                    # Last resort: use default bitmap font
                    return ImageFont.load_default()

    def load_images_from_folder(self, folder_path: str) -> None:
        """Load all supported images from the specified folder."""
        self.images_info.clear()
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(self.IMAGE_FORMATS):
                self._process_image_file(folder_path, filename)

    def _create_thumbnail(self, img: Image.Image, thumb_path: str) -> None:
        """Create and save a thumbnail image."""
        try:
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Create thumbnail
            thumb = img.copy()
            thumb.thumbnail(self.THUMBNAIL_SIZE)
            thumb.save(thumb_path, 'JPEG')
            
            # Verify thumbnail was created
            if not os.path.exists(thumb_path):
                raise Exception("Thumbnail file was not created")
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            # Create a blank thumbnail as fallback
            blank = Image.new('RGB', self.THUMBNAIL_SIZE, 'gray')
            blank.save(thumb_path, 'JPEG')

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
                self._create_thumbnail(img, thumb_path)
                
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
                self._create_thumbnail(rotated, info['thumbnail_path'])
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

    def _calculate_layout(
        self,
        total_images: int,
        page_size: Tuple[int, int],
        margin: int
    ) -> Tuple[int, int, int, int]:
        """Calculate optimal layout parameters for contact sheet."""
        width, height = page_size
        
        # Reserve space for context text and watermark
        usable_height = height - 200  # Reserve space for headers/footers
        
        # Calculate optimal grid size
        cell_min_size = 300  # Minimum size for each image cell
        max_cols = (width - margin) // (cell_min_size + margin)
        max_rows = (usable_height - margin) // (cell_min_size + margin + 50)
        
        # Ensure at least 2x2 grid
        cols = max(2, min(max_cols, 3))
        rows = max(2, min(max_rows, 3))
        
        images_per_page = cols * rows
        
        # Calculate thumbnail dimensions
        thumb_width = (width - (cols + 1) * margin) // cols
        thumb_height = (usable_height - (rows + 1) * margin - rows * 50) // rows
        
        return images_per_page, cols, thumb_width, thumb_height

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
            font = self._get_font('Arial', settings.font_size)
            
            # Generate all pages
            pages = []
            images_per_page = layout[0]
            
            for i in range(0, len(images_info), images_per_page):
                batch = images_info[i:i + images_per_page]
                page = self._generate_page(
                    batch,
                    page_size,
                    layout,
                    margin,
                    font,
                    i // images_per_page + 1,
                    (len(images_info) + images_per_page - 1) // images_per_page
                )
                pages.append(page)
            
            return self._save_pages(pages, settings)
        except Exception as e:
            print(f"Error creating contact sheet: {e}")
            return False

    def _generate_page(
        self,
        images: List[Dict],
        page_size: Tuple[int, int],
        layout_params: Tuple[int, int, int, int],
        margin: int,
        font: ImageFont.FreeTypeFont,
        page_num: int,
        total_pages: int
    ) -> Image.Image:
        """Generate a single contact sheet page."""
        page = Image.new('RGB', page_size, 'white')
        draw = ImageDraw.Draw(page)
        y_offset = margin

        # Add page number
        page_text = f"Page {page_num} of {total_pages}"
        text_width = draw.textlength(page_text, font=font)
        draw.text(
            (page_size[0] - margin - text_width, y_offset),
            page_text,
            fill='black',
            font=font
        )

        if self.settings_manager.context_text:
            draw.text(
                (margin, y_offset),
                self.settings_manager.context_text,
                fill='black',
                font=font
            )
            y_offset += self.settings_manager.font_size + margin

        self._add_images_to_page(
            page,
            images,
            layout_params[1],  # cols
            layout_params[2],  # thumb_width
            layout_params[3],  # thumb_height
            margin,
            y_offset
        )

        if self.settings_manager.watermark_text:
            self._add_watermark(
                page,
                draw,
                page_size[0],
                page_size[1],
                margin
            )

        return page

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
        caption_font = self._get_font('Arial', 20)
        
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
            draw = ImageDraw.Draw(page)
            draw.text(
                (x, y + thumb_height + 5),
                text,
                fill='black',
                font=caption_font
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
        watermark_font = self._get_font('Arial', 40)
        text_width = draw.textlength(
            self.settings_manager.watermark_text,
            font=watermark_font
        )
        text_height = 40
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

            font = self._get_font('Arial', self.settings_manager.font_size)
            
            # Generate preview of first page
            preview = self._generate_page(
                images_info[:layout[0]],
                page_size,
                layout,
                margin,
                font,
                1,
                (len(images_info) + layout[0] - 1) // layout[0]
            )
            return preview
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
