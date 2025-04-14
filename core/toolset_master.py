# toolset_master.py
"""
Main UI module for Maya rigging tools.

A dockable UI for Autodesk Maya designed to streamline rigging workflows.
This script provides a framework for accessing various toolsets for creating,
orienting, and visualizing joint structures, batch renaming, and additional utility widgets.

Features:
    - Enables access to a variety of rigging tools through a tabbed interface
    - Dynamically loads available scripts from configured directories
    - Seamlessly integrates into Maya's workspace as a dockable interface

Author: CJ Nowacek
Version: 2.0.0
License: GPL
"""
import os
import sys
import importlib
from typing import Dict, List, Optional, Any

from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

from maya import cmds
from maya import OpenMayaUI
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from core.Config import Config


def get_maya_main_window() -> QtWidgets.QWidget:
    """
    Return the Maya main window widget as a Python object.

    Returns:
        QtWidgets.QWidget: Maya's main window
    """
    main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def list_modules(script_path: str) -> List[str]:
    """
    Retrieve a list of Python script names from a directory.

    Args:
        script_path: Path to directory containing Python scripts

    Returns:
        List of module names without their .py extension
    """
    if not os.path.exists(script_path):
        cmds.warning(f"Path does not exist: {script_path}")
        return []

    module_names = []
    for file in os.listdir(script_path):
        if file.endswith(".py") and not file.startswith("__"):
            module_names.append(file.split(".")[0])
    return module_names


class ToolsetTab(QtWidgets.QWidget):
    """
    Tab widget for each tool category containing script selection and execution controls.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        """Initialize the tab with basic UI elements."""
        super(ToolsetTab, self).__init__(parent)

        # Create the script selection dropdown and run button
        self.script_combobox = QtWidgets.QComboBox()
        self.run_button = QtWidgets.QPushButton("Run")
        self.parameter_input = QtWidgets.QLineEdit("")

        # Layout configuration
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Select Script:"))
        layout.addWidget(self.script_combobox)

        param_layout = QtWidgets.QHBoxLayout()
        param_layout.addWidget(QtWidgets.QLabel("Parameters:"))
        param_layout.addWidget(self.parameter_input)
        layout.addLayout(param_layout)

        layout.addWidget(self.run_button)
        layout.setAlignment(QtCore.Qt.AlignTop)


class ToolsetMaster(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    """
    Main dockable window containing the ToolsetMaster UI.
    Provides access to various tools through a tabbed interface.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        """Initialize the main ToolsetMaster window."""
        parent = parent or get_maya_main_window()
        super(ToolsetMaster, self).__init__(parent)

        # Get UI configuration
        ui_config = Config.get_ui_config("toolset_master")
        self.setWindowTitle(ui_config.get("title", "Toolset Master"))
        self.setMinimumSize(ui_config.get("width", 400), ui_config.get("height", 125))

        # Adjust window flags for different operating systems
        if cmds.about(ntOS=True):
            self.setWindowFlags(
                self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint
            )
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        # Load available script modules
        self.module_names = {}
        for category, path in Config.TOOL_PATHS.items():
            self.module_names[category] = list_modules(path)

        # Initialize UI elements
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self) -> None:
        """Create UI widgets and populate script selection lists."""
        self.tabs = {
            "Wip": ToolsetTab(),
            "Model": ToolsetTab(),
            "Rig": ToolsetTab(),
            "Anim": ToolsetTab(),
        }

        # Populate script dropdowns for each tab
        for key, tab in self.tabs.items():
            script_list = self.module_names.get(key.lower(), [])
            tab.script_combobox.addItems(script_list)

            # Add placeholder text
            tab.parameter_input.setPlaceholderText("Optional parameters for script")

        # Create a tab widget and add each category as a separate tab
        self.tab_widget = QtWidgets.QTabWidget()
        for name, tab in self.tabs.items():
            self.tab_widget.addTab(tab, name)

    def create_layout(self) -> None:
        """Define and set up the layout for the main window."""
        main_layout = QtWidgets.QVBoxLayout(self)

        # Add info label
        info_label = QtWidgets.QLabel(
            "Select a script from any tab and click 'Run' to execute it."
        )
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(info_label)

        # Add tab widget
        main_layout.addWidget(self.tab_widget)

    def create_connections(self) -> None:
        """Connect button clicks to the script execution function."""
        for category, tab in self.tabs.items():
            tab.run_button.clicked.connect(
                lambda checked=False, cat=category.lower(): self.run_script(cat)
            )

    def run_script(self, category: str) -> None:
        """
        Handle script execution based on the selected category and script.

        Args:
            category: The tool category (model, rig, anim, wip)
        """
        print(f"=== Starting run_script for category: {category} ===")
        
        script_path = Config.get_tool_path(category)
        print(f"Script path: {script_path}")
        print(f"Script path exists: {os.path.exists(script_path)}")
        
        tab = self.tabs[category.capitalize()]
        selected_script = tab.script_combobox.currentText()
        print(f"Selected script: {selected_script}")

        if not selected_script:
            cmds.warning(f"No script selected in {category} tab")
            return

        # Retrieve user-provided input from the text field
        user_input = tab.parameter_input.text()
        print(f"User input: {user_input}")

        # Ensure the script's directory is in the Python path
        if script_path not in sys.path:
            sys.path.append(script_path)
            print(f"Added {script_path} to Python path")

        # Check for script file
        script_file = os.path.join(script_path, f"{selected_script}.py")
        print(f"Looking for script file: {script_file}")
        print(f"Script file exists: {os.path.exists(script_file)}")

        try:
            # Dynamically import or reload the selected script
            print(f"Attempting to import module: {selected_script}")
            
            if selected_script in sys.modules:
                print(f"Module {selected_script} already imported, reloading...")
                importlib.reload(sys.modules[selected_script])
            else:
                print(f"Importing module {selected_script} for the first time...")
                importlib.import_module(selected_script)

            module = sys.modules[selected_script]
            print(f"Module imported: {module}")
            
            # List available attributes in the module
            print("Module attributes:")
            for attr in dir(module):
                if not attr.startswith("__"):
                    print(f"  - {attr}")

            # Try executing the main function with user input
            try:
                if hasattr(module, "main"):
                    print(f"Found main function in {selected_script}, executing...")
                    result = module.main(user_input)
                    print(f"Result from main function: {result}")
                    
                    if result and hasattr(result, "show"):
                        print("Result has show method, calling it...")
                        result.show()
                else:
                    print(f"No main function found in {selected_script}")
                    cmds.warning(f"No main function found in {selected_script}")
            except Exception as e:
                print(f"Error executing {selected_script}: {e}")
                cmds.warning(f"Error executing {selected_script}: {e}")
        except ImportError as e:
            print(f"Import error for {selected_script}: {e}")
            cmds.warning(f"Error importing {selected_script}: {e}")
        except Exception as e:
            print(f"General error: {e}")
            cmds.warning(f"General error: {e}")
            
        print("=== run_script completed ===")
def show_ui() -> ToolsetMaster:
    """
    Display the ToolsetMaster window as a dockable widget in Maya.

    Returns:
        Instance of the ToolsetMaster UI
    """
    # Close any existing instance
    try:
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if isinstance(widget, ToolsetMaster):
                widget.close()
                widget.deleteLater()
    except Exception as e:
        cmds.warning(f"Error closing existing widget: {e}")

    # Create and show new instance
    ui = ToolsetMaster()
    ui.show(dockable=True, floating=True)
    return ui


if __name__ == "__main__":
    show_ui()
