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
            color: #ffffff;
        }
        QLineEdit, QTextEdit {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QListWidget {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QMenuBar, QMenu, QMenu::item {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QStatusBar {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        """
        self.light_theme_stylesheet = """
        QWidget {
            background-color: #f0f0f0;
            color: #000000;
        }
        QMenuBar, QMenu, QMenu::item {
            background-color: #f0f0f0;
            color: #000000;
        }
        QStatusBar {
            background-color: #f0f0f0;
            color: #000000;
        }
        """
        # Other resources like icons, images...

