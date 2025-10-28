from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QFileDialog

from utils import ros_bag_utils
from utils.ros_bag_utils import ROSAnalysisResult


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
        self.analysis_container_layout = None
        self.analysis_container = None
        self.export_container = None
        self.export_container_layout = None
        self.selection = []
        self.dir = ""
        self.export_button = None
        main_layout = QtWidgets.QVBoxLayout(self)

        # === Scroll Area ===
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        scroll_widget = QtWidgets.QWidget()
        scroll_area.setWidget(scroll_widget)

        self.scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)

        title = label_from_text("<h1><b>ROS2 Bag to CSV</b></h1>")
        self.scroll_layout.addWidget(title)

        description = label_from_text(
            """<div style="line-height: 1.5;">
                    <h3>This utility converts ROS2 Bag .mcap log files into .csv files for analysis.</h3>
                    <p>For more information on the surrounding project, visit 
                    <a href="https://github.com/Stevens-Electric-Boatworks">Stevens Electric Boatworks</a> on GitHub!</p>
                    </div>"""
        )
        self.scroll_layout.addWidget(description)

        # === Contact ===
        contact = label_from_text("""<div style="line-height: 1;">
            <h1>Contact</h1>
            <p><b>Ishaan Sayal</b><br>
            <a href="https://github.com/EmeraldWither">github.com/EmeraldWither</a><br>
            Email: isayal@stevens.org</p>
            </div>""")
        self.scroll_layout.addWidget(contact)
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.scroll_layout.addWidget(line)

        getting_started = label_from_text("""
        <div style="line-height: 1;">
            <h1>Getting Started</h1>
            <p>1) <b>Import the ROS2 bag folder. Please note that you must import the full folder WITH metadata and .mcap db.</b> <br><br>
            2) <b>Select the desired ROS2 data sets</b><br>
                e.g) "/electrical/temp_sensors/out.outlet_temp"<br><br>
            3) <b>Hit convert, and analyse the resulting .csv file!</b><br>
            </div>
        """)
        self.scroll_layout.addWidget(getting_started)

        self.import_button = QtWidgets.QPushButton("Import ROSBag Directory")
        self.scroll_layout.addWidget(self.import_button)
        self.import_button.clicked.connect(self.import_file)
        self.scroll_layout.addStretch()

    @QtCore.Slot()
    def import_file(self):
        self.dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        result = ros_bag_utils.get_topics(self.dir)
        self.create_dropdown(result)

    def create_dropdown(self, analysis_result:ROSAnalysisResult):
        if self.analysis_container is not None:
            print("Destroying OLD!")
            self.analysis_container.setParent(None)
            self.analysis_container.destroy()
        self.analysis_container = QtWidgets.QWidget()
        self.analysis_container_layout = QtWidgets.QVBoxLayout(self.analysis_container)
        if self.export_container is not None:
            print("Destroying OLD export!!")
            self.export_container.setParent(None)
            self.export_container.destroy()


        self.analysis_container_layout.addWidget(label_from_text("""
        <p><h3>Please select the topics and data you want exported into a CSV file.</h3></p>
        """))
        self.tree = QtWidgets.QTreeWidget()
        for item in analysis_result.topics:
            # high level
            top_level = QtWidgets.QTreeWidgetItem()
            top_level.setText(0, str(item))
            top_level.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
            for data in analysis_result.topics[item]:
                data_item = QtWidgets.QTreeWidgetItem()
                data_item.setText(0, str(data) + " : " + str(analysis_result.topics[item][data]))
                top_level.addChild(data_item)
                data_item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)

            self.tree.addTopLevelItem(top_level)

        self.tree.setHeaderHidden(True)
        self.tree.itemChanged.connect(self.on_item_changed)

        self.analysis_container_layout.addWidget(self.tree)
        self.analysis_container_layout.addStretch()

        self.export_button = QtWidgets.QPushButton("Export as CSV")
        self.analysis_container_layout.addWidget(self.export_button)
        self.analysis_container_layout.addStretch()
        self.export_button.clicked.connect(self.export_to_csv)

        self.scroll_layout.addWidget(self.analysis_container)
    def export_to_csv(self):
        export_dir = str(QFileDialog.getExistingDirectory(self, "Select Export Directory"))
        result_file = ros_bag_utils.export(self.dir, self.get_selected_topics(), export_dir)
        self.export_container = QtWidgets.QWidget()
        self.export_container_layout = QtWidgets.QVBoxLayout(self.export_container)
        self.export_container_layout.addWidget(label_from_text(f"<h3>It was exported to {result_file}</h3>"))
        self.export_container_layout.addStretch()
        self.export_button.setDisabled(True)
        self.scroll_layout.addWidget(self.export_container)


    def on_item_changed(self, item, column):
        self.tree.blockSignals(True)
        state = item.checkState(column)
        for i in range(item.childCount()):
            item.child(i).setCheckState(0, state)
        parent = item.parent()
        if parent is not None:
            all_checked = all(parent.child(i).checkState(0) == QtCore.Qt.CheckState.Checked
                              for i in range(parent.childCount()))
            all_unchecked = all(parent.child(i).checkState(0) == QtCore.Qt.CheckState.Unchecked
                                for i in range(parent.childCount()))
            if all_checked:
                parent.setCheckState(0, QtCore.Qt.CheckState.Checked)
            elif all_unchecked:
                parent.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
            else:
                parent.setCheckState(0, QtCore.Qt.CheckState.PartiallyChecked)

        self.tree.blockSignals(False)

        print(f"Topics: {self.get_selected_topics()}")

    def get_selected_topics(self):
        selected = []
        def recurse(item, path=""):
            for i in range(item.childCount()):
                child = item.child(i)
                if child.checkState(0) != QtCore.Qt.CheckState.Unchecked:
                    new_path = f"{path}.{child.text(0).split(" : ")[0]}" if path else child.text(0)
                    selected.append(new_path)
                    recurse(child, new_path)

        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            if top.checkState(0) != QtCore.Qt.CheckState.Unchecked:
                recurse(top, top.text(0))

        return selected



