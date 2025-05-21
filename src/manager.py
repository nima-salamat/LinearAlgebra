from PySide6.QtWidgets import QApplication
import qdarkstyle
from qdarkstyle.dark.palette import DarkPalette

from ui.ui import Window, QIcon, resource_path
import sys
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(palette=DarkPalette())) 
    win = Window(app)
    win.setWindowIcon(QIcon(resource_path("ui\\favicon.ico")))
    win.show()
    app.exec()

