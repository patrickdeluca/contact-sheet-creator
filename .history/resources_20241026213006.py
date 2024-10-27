# resources.py

class Resources:
    def __init__(self):
        self.dark_theme_stylesheet = """
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QPushButton {
            background-color: #3c3c3c;
            border: 1px solid #505050;
            color: #ffffff;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #505050;
        }
        QPushButton:pressed {
            background-color: #404040;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #3c3c3c;
            border: 1px solid #505050;
            color: #ffffff;
            padding: 3px;
            border-radius: 3px;
        }
        QListWidget {
            background-color: #3c3c3c;
            border: 1px solid #505050;
            color: #ffffff;
        }
        QMenuBar {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QMenuBar::item:selected {
            background-color: #505050;
        }
        QMenu {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #505050;
        }
        QMenu::item:selected {
            background-color: #505050;
        }
        QStatusBar {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QSlider::groove:horizontal {
            border: 1px solid #505050;
            height: 8px;
            background: #3c3c3c;
            margin: 2px 0;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #808080;
            border: 1px solid #505050;
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }
        QGroupBox {
            border: 1px solid #505050;
            border-radius: 5px;
            margin-top: 1em;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        """

        self.light_theme_stylesheet = """
        QWidget {
            background-color: #f0f0f0;
            color: #000000;
        }
        QPushButton {
            background-color: #e0e0e0;
            border: 1px solid #c0c0c0;
            color: #000000;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #ffffff;
            border: 1px solid #c0c0c0;
            color: #000000;
            padding: 3px;
            border-radius: 3px;
        }
        QListWidget {
            background-color: #ffffff;
            border: 1px solid #c0c0c0;
            color: #000000;
        }
        QMenuBar {
            background-color: #f0f0f0;
            color: #000000;
        }
        QMenuBar::item:selected {
            background-color: #d0d0d0;
        }
        QMenu {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #c0c0c0;
        }
        QMenu::item:selected {
            background-color: #d0d0d0;
        }
        QStatusBar {
            background-color: #f0f0f0;
            color: #000000;
        }
        QSlider::groove:horizontal {
            border: 1px solid #c0c0c0;
            height: 8px;
            background: #ffffff;
            margin: 2px 0;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #e0e0e0;
            border: 1px solid #c0c0c0;
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }
        QGroupBox {
            border: 1px solid #c0c0c0;
            border-radius: 5px;
            margin-top: 1em;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        """
