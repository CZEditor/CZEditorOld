import os
import sys
from sys import exit  # Just in case Nuitka throws another tantrum


def checkAndInstall():
    import czeditor.util.installhelper
    # Checks for missing runtime dependencies and installs them
    # if possible or prompts the user to install them manually
    czeditor.util.installhelper.checkAndInstall()


def startApp():
    # Check for missing runtime dependencies and install them if possible
    checkAndInstall()

    from PySide6.QtCore import QDir
    from PySide6.QtWidgets import QApplication
    from czeditor.czeditor import Window

    # Set up resource paths for Qt internals like stylesheets
    # Use importlib.resources when it's possible to do so
    root = os.path.dirname(os.path.abspath(__file__))
    QDir.addSearchPath("res", os.path.join(root, "res"))
    for path in os.listdir(os.path.join(root, "res")):
        if os.path.isdir(os.path.join(root, "res", path)):
            QDir.addSearchPath(path, os.path.join(root, "res", path))

    # Start the app
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    startApp()
