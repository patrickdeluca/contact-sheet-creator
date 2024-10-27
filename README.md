# Contact Sheet Pro

Contact Sheet Pro is a professional-grade tool for creating customizable contact sheets from your photo collections. It automatically extracts and displays EXIF data, supports multiple formats, and offers flexible layout options.

Copyright © 2024 Patrick DeLuca (GitHub: patrickdeluca)

## Features

- **Intuitive Interface**: Easy-to-use GUI with drag-and-drop support
- **EXIF Data Integration**: Automatically extracts and displays date/time information
- **Multiple Format Support**: 
  - Input: JPG, JPEG, PNG, HEIC, BMP, GIF
  - Output: JPEG, PNG, PDF
- **Customization Options**:
  - Adjustable layout and image sizing
  - Custom watermarks
  - Context text for each sheet
  - Font selection and sizing
  - Quality settings
- **Preview Capability**: Real-time preview of contact sheets
- **Image Management**:
  - Rotate images
  - Reorder images
  - Select specific images for sheets
- **Multi-page Support**: Automatically creates additional pages for large collections
- **Theme Support**: Light and dark mode interface

## Installation

### Windows

1. Install Python 3.8+ from [python.org](https://www.python.org/downloads/)

2. Clone the repository:
```bash
git clone https://github.com/patrickdeluca/contact-sheet-pro.git
cd contact-sheet-pro
```

3. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

4. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Linux

1. Install required system packages:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv python3-qt5
```

2. Clone the repository:
```bash
git clone https://github.com/patrickdeluca/contact-sheet-pro.git
cd contact-sheet-pro
```

3. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

4. Install required dependencies:
```bash
pip install -r requirements.txt
```

### macOS

1. Install Python 3.8+ using Homebrew:
```bash
brew install python@3.8
```

2. Clone the repository:
```bash
git clone https://github.com/patrickdeluca/contact-sheet-pro.git
cd contact-sheet-pro
```

3. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

4. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Windows
```bash
python main.py
```

### Linux
Make sure you're running an X server or Wayland:
```bash
python3 main.py
```

### macOS
```bash
python3 main.py
```

### WSL (Windows Subsystem for Linux)
The application should be run natively on Windows rather than through WSL, as WSL doesn't provide direct GUI support. Use the Windows installation method instead.

## Usage

1. Launch the application using the appropriate command for your platform
2. Basic workflow:
   - Click 'Open Image Folder' or drag-and-drop images
   - Select images to include
   - Adjust layout and settings as needed
   - Preview the result
   - Click 'CREATE' to generate contact sheets

## Requirements

- Python 3.8+
- PyQt5
- Pillow
- pillow-heif
- piexif

## Configuration

- **Image Settings**:
  - Quality: 1-100
  - Format: JPEG, PNG, PDF
  - Layout: Automatic or custom arrangement

- **Text Options**:
  - Multiple font choices
  - Customizable font sizes
  - Watermark placement
  - Context text support

## Development

The project is structured into several key components:

- `main.py`: Application entry point
- `gui.py`: User interface implementation
- `image_processor.py`: Image handling and contact sheet generation
- `settings_manager.py`: Configuration management
- `resources.py`: Resource and theme management

## Troubleshooting

### Common Issues

1. **Qt platform plugin error**:
   - On Windows: Make sure you're running the application natively, not through WSL
   - On Linux: Install required Qt dependencies: `sudo apt-get install python3-qt5`
   - On macOS: Make sure you have the latest PyQt5 installed

2. **Missing dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Permission issues**:
   - Make sure you have write permissions in the target directory
   - On Linux/macOS, you might need to run: `chmod +x main.py`

### Getting Help

If you encounter any issues:
1. Check the Troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with:
   - Your operating system and version
   - Python version (`python --version`)
   - Full error message
   - Steps to reproduce the problem

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is proprietary software. Copyright © 2024 Patrick DeLuca. All rights reserved.

## Contact

Patrick DeLuca - GitHub: [@patrickdeluca](https://github.com/patrickdeluca)

Project Link: [https://github.com/patrickdeluca/contact-sheet-pro](https://github.com/patrickdeluca/contact-sheet-pro)
