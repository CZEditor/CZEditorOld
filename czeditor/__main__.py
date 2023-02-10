import os
import sys

from PySide6.QtCore import QDir

from czeditor.czeditor import *

# Set up resource paths for Qt internals like stylesheets 
# Use importlib.resources when it's possible to do so
root = os.path.dirname(os.path.abspath(__file__))
QDir.addSearchPath("res", os.path.join(root, "res"))
for path in os.listdir(os.path.join(root, "res")):
    if os.path.isdir(os.path.join(root, "res", path)):
        QDir.addSearchPath(path, os.path.join(root, "res", path))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())
