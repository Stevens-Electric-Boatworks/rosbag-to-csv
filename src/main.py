import random
import sys

from PySide6 import QtWidgets, QtCore

from src.main_page import MainPage

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainPage()
    widget.setWindowTitle("ROS2 Bag to CSV")
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())