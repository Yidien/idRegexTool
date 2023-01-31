import sys
import Ui
from PySide6.QtWidgets import QApplication


app = QApplication()
ui = Ui.Ui()
ui.show()
sys.exit(app.exec())
