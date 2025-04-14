import os
import maya.cmds as mc
import maya.mel as mel
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

def maya_main_window():
    """Return the Maya main window widget as a Python object."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class BfaOpsAnimExporter(QtWidgets.QMainWindow):
    def __init__(self, parent=maya_main_window()):
        super(BfaOpsAnimExporter, self).__init__(parent)

        self.setWindowTitle("Anim Exporter")
        self.setFixedSize(400, 200)

        self.create_ui()

    def create_ui(self):
        """Create the UI elements."""
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QVBoxLayout(central_widget)

        # Prep Button
        self.prep_btn = QtWidgets.QPushButton("Prep", self)
        self.prep_btn.clicked.connect(self.prepare_scene)
        layout.addWidget(self.prep_btn)

        # Time Range Section
        layout.addWidget(self.create_label("Set Time Range"))
        time_range_layout = QtWidgets.QHBoxLayout()
        self.min_time_btn = QtWidgets.QPushButton("Set Min Time", self)
        self.min_time_btn.clicked.connect(self.set_min_time)
        time_range_layout.addWidget(self.min_time_btn)

        self.max_time_btn = QtWidgets.QPushButton("Set Max Time", self)
        self.max_time_btn.clicked.connect(self.set_max_time)
        time_range_layout.addWidget(self.max_time_btn)
        layout.addLayout(time_range_layout)

        # Export Section
        layout.addWidget(self.create_label("Exporting"))
        export_layout = QtWidgets.QVBoxLayout()
        self.export_selected_btn = QtWidgets.QPushButton("First Time Export", self)
        self.export_selected_btn.setEnabled(False)
        self.export_selected_btn.clicked.connect(self.export_selection)
        export_layout.addWidget(self.export_selected_btn)

        self.export_btn = QtWidgets.QPushButton("Export", self)
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_animations)
        export_layout.addWidget(self.export_btn)
        layout.addLayout(export_layout)

        # Restart Button
        layout.addWidget(self.create_label("Restarting File"))
        self.reopen_btn = QtWidgets.QPushButton("Reopen", self)
        self.reopen_btn.clicked.connect(self.restart_file)
        layout.addWidget(self.reopen_btn)

    def create_label(self, text):
        """Helper function to create a QLabel with center alignment."""
        label = QtWidgets.QLabel(text, self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        return label

    def prepare_scene(self):
        """Prepare the scene for export."""
        mel.eval("file -save;")
        mel.eval('namespace -mergeNamespaceWithRoot -removeNamespace "SKL_robin";')

        all_ref_paths = mc.file(q=True, reference=True) or []

        for ref_path in all_ref_paths:
            if mc.referenceQuery(ref_path, isLoaded=True):
                mc.file(ref_path, importReference=True)
                new_ref_paths = mc.file(q=True, reference=True)
                if new_ref_paths:
                    all_ref_paths.extend([path for path in new_ref_paths if path not in all_ref_paths])

        mc.select("SKL")
        self.move_selection_to_world("DOWN")

        mc.select("GEO")
        self.move_children_to_world()

        mc.select("Root", hi=True)

        self.export_selected_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

        self.prep_btn.setEnabled(False)
        self.min_time_btn.setEnabled(False)
        self.max_time_btn.setEnabled(False)

    def move_selection_to_world(self, direction):
        selected = mc.pickWalk(direction=direction)
        mc.parent(selected, world=True)

    def move_children_to_world(self):
        children = mc.listRelatives(c=True)
        if children:
            mc.parent(children, world=True)

    def export_animations(self):
        mc.select("Root", hi=True)

        filepath = mc.file(q=True, sn=True)
        filename = os.path.basename(filepath)
        path = filepath.replace(filename, "")
        new_filename = filename.replace("ma", "fbx")
        new_path = os.path.join(path, "exportTesting", new_filename)

        min_time = mc.playbackOptions(q=True, min=True)
        max_time = mc.playbackOptions(q=True, max=True)

        mel.eval("FBXResetExport")
        mel.eval("FBXExportBakeComplexAnimation -v 1")
        mel.eval(f"FBXExportBakeComplexStart -v {min_time}")
        mel.eval(f"FBXExportBakeComplexEnd -v {max_time}")
        mel.eval("FBXExportAnimationOnly -v 1")
        mel.eval(f"FBXExport -f \"{new_path}\" -s")

    def restart_file(self):
        filepath = mc.file(q=True, sn=True)
        mc.file(filepath, open=True, force=True)

        self.export_selected_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.prep_btn.setEnabled(True)
        self.min_time_btn.setEnabled(True)
        self.max_time_btn.setEnabled(True)

    def set_min_time(self):
        current_time = mc.currentTime(q=True)
        mc.playbackOptions(min=current_time, ast=current_time)

    def set_max_time(self):
        current_time = mc.currentTime(q=True)
        mc.playbackOptions(max=current_time, aet=current_time)

    def export_selection(self):
        mel.eval("ExportSelection;")

def show_exporter():
    """Show the exporter UI in Maya."""
    global anim_exporter
    try:
        anim_exporter.close()  # Close any existing instance of the exporter
    except:
        pass

    anim_exporter = BfaOpsAnimExporter()
    anim_exporter.show()

if __name__ == "__main__":
    show_exporter()
