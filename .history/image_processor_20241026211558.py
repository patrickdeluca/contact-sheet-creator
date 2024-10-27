# image_processor.py

import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import pillow_heif
import piexif
from datetime import datetime

class ImageProcessor:
    def __init__(self):
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
                    thumbnail_path = os.path.join(folder_path, f".thumbnail_{filename}")
                    image.thumbnail((150, 150))
                    image.save(thumbnail_path)
                    exif_dict = self.extractExifData(image)
                    date_time = self.getDateTimeFromExif(exif_dict)
                    date_time_formatted = date_time.strftime('%m/%d/%Y %H:%M:%S') if date_time else 'Unknown Date'
                    self.images_info.append({
                        'filename': filename,
                        'path': file_path,
                        'thumbnail_path': thumbnail_path,
                        'exif': exif_dict,
                        'date_time': date_time_formatted,
                        'rotation': 0  # Rotation in degrees
                    })
                except Exception as e:
                    print(f"Error loading image {filename}: {e}")

    def addImage(self, file_path):
        # Similar to loadImagesFromFolder but adds a single image
        pass

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
                date_time = datetime.strptime(date_time_str, '%Y:%m:%d %H:%M:%S')
                return date_time
        except Exception as e:
            print(f"Error parsing EXIF date: {e}")
        return None

    def createContactSheet(self, images_info, settings):
        # Implement the logic to create the contact sheet using the images_info and settings
        # Apply context text, fonts, export options, metadata inclusion, watermarking, etc.
        pass

