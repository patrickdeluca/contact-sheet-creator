# settings_manager.py

import json
import os
from resources import Resources


class SettingsManager:
    def __init__(self):
        # Load resources
        self.resources = Resources()
        
        # Default settings
        self.context_text = ''
        self.font_name = self.resources.get_default_font()  # Use system font
        self.font_size = 20
        self.export_format = 'JPEG'
        self.quality = 80
        self.filename_pattern = 'contact_sheet_{number}'
        self.include_metadata = True
        self.watermark_text = ''
        self.save_folder = ''
        self.presets = {}
        self.settings_file = 'settings.json'
        self.presets_file = 'presets.json'
        self.load_settings()
        self.load_presets()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.context_text = data.get('context_text', '')
                    
                    # Ensure font is in available system fonts
                    font_name = data.get('font_name', '')
                    if font_name in self.resources.get_available_fonts():
                        self.font_name = font_name
                    else:
                        self.font_name = self.resources.get_default_font()
                    
                    self.font_size = data.get('font_size', 20)
                    self.export_format = data.get('export_format', 'JPEG')
                    self.quality = data.get('quality', 80)
                    self.filename_pattern = data.get(
                        'filename_pattern',
                        'contact_sheet_{number}'
                    )
                    self.include_metadata = data.get(
                        'include_metadata',
                        True
                    )
                    self.watermark_text = data.get('watermark_text', '')
                    self.save_folder = data.get('save_folder', '')
            except Exception as e:
                print(f"Error loading settings: {e}")
                self._set_defaults()
        else:
            self._set_defaults()
            self.save_settings()

    def _set_defaults(self):
        """Reset settings to defaults."""
        self.context_text = ''
        self.font_name = self.resources.get_default_font()
        self.font_size = 20
        self.export_format = 'JPEG'
        self.quality = 80
        self.filename_pattern = 'contact_sheet_{number}'
        self.include_metadata = True
        self.watermark_text = ''
        self.save_folder = ''

    def save_settings(self):
        data = {
            'context_text': self.context_text,
            'font_name': self.font_name,
            'font_size': self.font_size,
            'export_format': self.export_format,
            'quality': self.quality,
            'filename_pattern': self.filename_pattern,
            'include_metadata': self.include_metadata,
            'watermark_text': self.watermark_text,
            'save_folder': self.save_folder
        }
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_presets(self):
        if os.path.exists(self.presets_file):
            try:
                with open(self.presets_file, 'r') as f:
                    self.presets = json.load(f)
            except Exception as e:
                print(f"Error loading presets: {e}")
                self.presets = {}
        else:
            self.presets = {}
            self.save_presets()

    def save_preset(self, name):
        self.presets[name] = {
            'context_text': self.context_text,
            'font_name': self.font_name,
            'font_size': self.font_size,
            'export_format': self.export_format,
            'quality': self.quality,
            'filename_pattern': self.filename_pattern,
            'include_metadata': self.include_metadata,
            'watermark_text': self.watermark_text,
            'save_folder': self.save_folder
        }
        self.save_presets()

    def load_preset(self, name):
        preset = self.presets.get(name)
        if preset:
            self.context_text = preset.get('context_text', '')
            
            # Validate font name from preset
            font_name = preset.get('font_name', '')
            if font_name in self.resources.get_available_fonts():
                self.font_name = font_name
            else:
                self.font_name = self.resources.get_default_font()
            
            self.font_size = preset.get('font_size', 20)
            self.export_format = preset.get('export_format', 'JPEG')
            self.quality = preset.get('quality', 80)
            self.filename_pattern = preset.get(
                'filename_pattern',
                'contact_sheet_{number}'
            )
            self.include_metadata = preset.get('include_metadata', True)
            self.watermark_text = preset.get('watermark_text', '')
            self.save_folder = preset.get('save_folder', '')
            return True
        else:
            print(f"Preset '{name}' not found.")
            return False

    def save_presets(self):
        try:
            with open(self.presets_file, 'w') as f:
                json.dump(self.presets, f, indent=4)
        except Exception as e:
            print(f"Error saving presets: {e}")
