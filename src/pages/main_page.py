import os
from pathlib import Path

from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QFileDialog

from src import ros_bag_utils


def label_from_text(text:str) -> QtWidgets.QLabel:
    widget = QtWidgets.QLabel(text)
    widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    widget.setTextFormat(QtCore.Qt.TextFormat.RichText)
    widget.setWordWrap(True)
    widget.setOpenExternalLinks(True)
    return widget

class MainPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # === Layout setup ===
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(40, 40, 40, 40)  # more breathing room
        self.layout.setSpacing(25)  # vertical spacing between labels

        # === Title ===
        title = label_from_text("<h1><b>ROS2 Bag to CSV</b></h1>")
        self.layout.addWidget(title)

        # === Description ===
        description = label_from_text(
            """<div style="line-height: 1.5;">
                    <h3>This utility converts ROS2 Bag .mcap log files into .csv files for analysis.</h3>
                    <p>For more information on the surrounding project, visit 
                    <a href="https://github.com/Stevens-Electric-Boatworks">Stevens Electric Boatworks</a> on GitHub!</p>
                    </div>"""
        )
        self.layout.addWidget(description)

        # === Contact ===
        contact = label_from_text("""<div style="line-height: 1;">
            <h1>Contact</h1>
            <p><b>Ishaan Sayal</b><br>
            <a href="https://github.com/EmeraldWither">github.com/EmeraldWither</a><br>
            Email: isayal@stevens.org</p>
            </div>""")
        self.layout.addWidget(contact)
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.layout.addWidget(line)

        getting_started = label_from_text("""
        <div style="line-height: 1;">
            <h1>Getting Started</h1>
            <p>1) <b>Import the ROS2 bag folder. Please note that you must import the full folder WITH metadata and .mcap db.</b> <br><br>
            2) <b>Select the desired ROS2 data sets</b><br>
                e.g) "/electrical/temp_sensors/out.outlet_temp"<br><br>
            3) <b>Hit convert, and analyse the resulting .csv file!</b><br>
            </div>
        """)
        self.layout.addWidget(getting_started)

        import_button = QtWidgets.QPushButton("Import ROSBag Directory")
        self.layout.addWidget(import_button)
        import_button.clicked.connect(self.import_file)


        # === Spacer so content stays at top ===
        self.layout.addStretch()

    @QtCore.Slot()
    def import_file(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        print(f"Got the file {file}")
        result = ros_bag_utils.analyse(file)
        print(f"Final Result: {result}")




