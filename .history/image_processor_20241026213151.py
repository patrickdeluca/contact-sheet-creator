# image_processor.py

import os
import io
from PIL import Image, ImageDraw, ImageFont, ImageOps
import pillow_heif
import piexif
from datetime import datetime
from PyQt5.QtGui import QPixmap


class ImageProcessor:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.images_info = []

    def loadImagesFromFolder(self, folder_path):
        self.images_info.clear()
        image_formats = ('.jpg', '.jpeg', '.png', '.heic', '.bmp', '.gif')
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(image_formats):
                file_path = os.path.join(folder_path, filename)
                try:
                    pillow_heif.register_heif_opener()
                    image = Image.open(file_path)
                    thumbnail_path = os.path.join(
                        folder_path, f".thumbnail_{filename}")
                    image.thumbnail((150, 150))
                    image.save(thumbnail_path)
                    exif_dict = self.extractExifData(image)
                    date_time = self.getDateTimeFromExif(exif_dict)
                    date_time_formatted = (
                        date_time.strftime('%m/%d/%Y %H:%M:%S')
                        if date_time else 'Unknown Date'
                    )
                    self.images_info.append({
                        'filename': filename,
                        'path': file_path,
                        'thumbnail_path': thumbnail_path,
                        'exif': exif_dict,
                        'date_time': date_time_formatted,
                        'rotation': 0
                    })
                except Exception as e:
                    print(f"Error loading image {filename}: {e}")

    def addImage(self, file_path):
        filename = os.path.basename(file_path)
        valid_extensions = ('.jpg', '.jpeg', '.png', '.heic', '.bmp', '.gif')
        if filename.lower().endswith(valid_extensions):
            try:
                pillow_heif.register_heif_opener()
                image = Image.open(file_path)
                thumbnail_path = os.path.join(
                    os.path.dirname(file_path),
                    f".thumbnail_{filename}"
                )
                image.thumbnail((150, 150))
                image.save(thumbnail_path)
                exif_dict = self.extractExifData(image)
                date_time = self.getDateTimeFromExif(exif_dict)
                date_time_formatted = (
                    date_time.strftime('%m/%d/%Y %H:%M:%S')
                    if date_time else 'Unknown Date'
                )
                self.images_info.append({
                    'filename': filename,
                    'path': file_path,
                    'thumbnail_path': thumbnail_path,
                    'exif': exif_dict,
                    'date_time': date_time_formatted,
                    'rotation': 0
                })
            except Exception as e:
                print(f"Error adding image {filename}: {e}")

    def rotateImage(self, info, angle):
        try:
            image = Image.open(info['path'])
            image = image.rotate(angle, expand=True)
            image.save(info['path'])
            # Update thumbnail
            image.thumbnail((150, 150))
            image.save(info['thumbnail_path'])
            info['rotation'] = (info['rotation'] + angle) % 360
        except Exception as e:
            print(f"Error rotating image {info['filename']}: {e}")

    def extractExifData(self, image):
        exif_dict = {}
        try:
            exif_bytes = image.info.get('exif', b'')
            if exif_bytes:
                exif_dict = piexif.load(exif_bytes)
        except Exception as e:
            print(f"Error extracting EXIF data: {e}")
        return exif_dict

    def getDateTimeFromExif(self, exif_dict):
        try:
            exif = exif_dict.get('Exif', {})
            date_time_str = exif.get(piexif.ExifIFD.DateTimeOriginal)
            if date_time_str:
                date_time_str = date_time_str.decode('utf-8')
                date_time = datetime.strptime(
                    date_time_str,
                    '%Y:%m:%d %H:%M:%S'
                )
                return date_time
        except Exception as e:
            print(f"Error parsing EXIF date: {e}")
        return None

    def createContactSheet(self, images_info):
        settings = self.settings_manager
        save_folder = settings.save_folder
        os.makedirs(save_folder, exist_ok=True)
        filename_pattern = settings.filename_pattern
        export_format = settings.export_format.lower()
        quality = settings.quality
        watermark_text = settings.watermark_text
        context_text = settings.context_text
        font_name = settings.font_name
        font_size = settings.font_size

        # Sort images by date_time
        images_info.sort(key=lambda x: x['date_time'])

        # Generate contact sheets (8.5 x 11 inches at 300 DPI)
        page_width, page_height = 2550, 3300
        margin = 50

        # Calculate layout
        images_per_page = min(4, len(images_info))
        cols = 2
        rows = (images_per_page + cols - 1) // cols
        thumb_width = (page_width - (cols + 1) * margin) // cols
        thumb_height = (
            page_height - (rows + 1) * margin - 200
        ) // rows

        try:
            font = ImageFont.truetype(font_name, font_size)
        except IOError:
            font = ImageFont.load_default()

        pages = []
        total_images = len(images_info)
        for i in range(0, total_images, images_per_page):
            page = Image.new('RGB', (page_width, page_height), 'white')
            draw = ImageDraw.Draw(page)
            y_offset = margin

            if context_text:
                draw.text(
                    (margin, y_offset),
                    context_text,
                    fill='black',
                    font=font
                )
                y_offset += font_size + margin

            for idx, info in enumerate(images_info[i:i + images_per_page]):
                row = (idx // cols)
                col = (idx % cols)
                x = margin + col * (thumb_width + margin)
                y = y_offset + row * (thumb_height + margin + 50)

                img = Image.open(info['path'])
                if info['rotation']:
                    img = img.rotate(info['rotation'], expand=True)
                img_resized = ImageOps.contain(img, (thumb_width, thumb_height))
                paste_x = x + (thumb_width - img_resized.width) // 2
                paste_y = y + (thumb_height - img_resized.height) // 2
                page.paste(img_resized, (paste_x, paste_y))

                # Draw text under image
                text = f"{info['filename']}\n{info['date_time']}"
                text_font = ImageFont.truetype(font_name, 20)
                text_x = x
                text_y = y + thumb_height + 5
                draw.text((text_x, text_y), text, fill='black', font=text_font)

            # Apply watermark if any
            if watermark_text:
                watermark_font = ImageFont.truetype(font_name, 40)
                watermark_width = draw.textlength(
                    watermark_text,
                    font=watermark_font
                )
                watermark_height = font_size
                watermark_position = (
                    page_width - watermark_width - margin,
                    page_height - watermark_height - margin
                )
                draw.text(
                    watermark_position,
                    watermark_text,
                    fill='grey',
                    font=watermark_font
                )

            pages.append(page)

        # Save contact sheets
        for idx, page in enumerate(pages):
            page_number = str(idx + 1).zfill(3)
            filename = filename_pattern.replace('{number}', page_number)
            output_path = os.path.join(
                save_folder,
                f"{filename}.{export_format}"
            )
            if export_format == 'pdf':
                page.save(output_path, 'PDF', resolution=300)
            elif export_format in ['jpg', 'jpeg']:
                page.save(output_path, 'JPEG', quality=quality)
            elif export_format == 'png':
                compress = int((100 - quality) / 10)
                page.save(output_path, 'PNG', compress_level=compress)
            else:
                page.save(output_path)
        return True

    def generatePreview(self, images_info):
        if not images_info:
            return None

        settings = self.settings_manager
        # Smaller size for preview
        page_width, page_height = 800, 600
        margin = 10

        # Calculate layout
        images_per_page = min(4, len(images_info))
        cols = 2
        rows = (images_per_page + cols - 1) // cols
        thumb_width = (page_width - (cols + 1) * margin) // cols
        thumb_height = (page_height - (rows + 1) * margin - 50) // rows

        try:
            font = ImageFont.truetype(settings.font_name, settings.font_size)
        except IOError:
            font = ImageFont.load_default()

        page = Image.new('RGB', (page_width, page_height), 'white')
        draw = ImageDraw.Draw(page)
        y_offset = margin

        if settings.context_text:
            draw.text(
                (margin, y_offset),
                settings.context_text,
                fill='black',
                font=font
            )
            y_offset += settings.font_size + margin

        for idx, info in enumerate(images_info[:images_per_page]):
            row = (idx // cols)
            col = (idx % cols)
            x = margin + col * (thumb_width + margin)
            y = y_offset + row * (thumb_height + margin + 30)

            img = Image.open(info['path'])
            if info['rotation']:
                img = img.rotate(info['rotation'], expand=True)
            img_resized = ImageOps.contain(img, (thumb_width, thumb_height))
            paste_x = x + (thumb_width - img_resized.width) // 2
            paste_y = y + (thumb_height - img_resized.height) // 2
            page.paste(img_resized, (paste_x, paste_y))

            # Draw text under image
            text = f"{info['filename']}\n{info['date_time']}"
            text_font = ImageFont.truetype(settings.font_name, 12)
            text_x = x
            text_y = y + thumb_height + 5
            draw.text((text_x, text_y), text, fill='black', font=text_font)

        # Apply watermark if any
        if settings.watermark_text:
            watermark_font = ImageFont.truetype(settings.font_name, 20)
            watermark_width = draw.textlength(
                settings.watermark_text,
                font=watermark_font
            )
            watermark_height = settings.font_size
            watermark_position = (
                page_width - watermark_width - margin,
                page_height - watermark_height - margin
            )
            draw.text(
                watermark_position,
                settings.watermark_text,
                fill='grey',
                font=watermark_font
            )

        return page

    def imageToPixmap(self, image):
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        return pixmap
