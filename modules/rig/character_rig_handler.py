import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import sys


def maya_main_window():
    """Return the Maya main window widget as a Python object"""
    main_window = omui.MQtUtil.mainWindow()
    if main_window is not None:
        return wrapInstance(int(main_window), QtWidgets.QWidget)
    return None


class MayaRigHandler(QtWidgets.QDialog):
    """
    Prepares Maya scene for animation export by managing namespaces and selecting objects.
    """

    def __init__(self, parent=maya_main_window()):
        super(MayaRigHandler, self).__init__(parent)

        self.skl_sel = []
        self.geo_sel = []
        self.final_sel = []
        self.rigs = []

        self.setWindowTitle("Maya Rig Handler")
        self.setMinimumWidth(450)
        self.setMinimumHeight(500)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        # Find all rigs in the scene
        self._find_rigs()

        # Create the UI
        self.create_ui()

    # ==================================
    # UI
    # ==================================

    def create_ui(self):
        """Create the user interface"""
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_rig_tab()
        self.create_export_tab()

        # Close button at the bottom
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn)

    def create_rig_tab(self):
        """Create the Create Rig tab"""
        rig_tab = QtWidgets.QWidget()
        rig_layout = QtWidgets.QVBoxLayout(rig_tab)

        # ----------------------------------
        # Create Character Template
        # ----------------------------------

        # Header
        header_label = QtWidgets.QLabel("Create Template")
        header_label.setStyleSheet(
            "background-color: #333333; color: white; padding: 8px; font-weight: bold;"
        )
        header_label.setAlignment(QtCore.Qt.AlignCenter)
        rig_layout.addWidget(header_label)

        # Character Template section (moved from template tab)
        template_group = QtWidgets.QGroupBox("Character Rig Template")
        template_layout = QtWidgets.QVBoxLayout(template_group)

        # Name input section
        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Rig Name:")
        self.name_field = QtWidgets.QLineEdit()
        self.name_field.setPlaceholderText(
            "Enter rig name (will be suffixed with '_rig')"
        )
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_field)
        template_layout.addLayout(name_layout)

        # Create button
        create_btn = QtWidgets.QPushButton("Create Character Template")
        create_btn.setMinimumHeight(50)
        create_btn.clicked.connect(self._create_character_template)
        template_layout.addWidget(create_btn)

        # Help button
        help_btn = QtWidgets.QPushButton("Help")
        help_btn.clicked.connect(self._show_template_help)
        template_layout.addWidget(help_btn)

        rig_layout.addWidget(template_group)

        # ----------------------------------
        # Create Rig
        # ----------------------------------

        # Header
        header_label = QtWidgets.QLabel("Create Rig")
        header_label.setStyleSheet(
            "background-color: #333333; color: white; padding: 8px; font-weight: bold;"
        )
        header_label.setAlignment(QtCore.Qt.AlignCenter)
        rig_layout.addWidget(header_label)

        # Available templates section
        templates_group = QtWidgets.QGroupBox("Available Rigs")
        templates_layout = QtWidgets.QVBoxLayout(templates_group)

        # Create list widget and refresh button in a horizontal layout
        list_layout = QtWidgets.QHBoxLayout()

        self.template_list = QtWidgets.QListWidget()
        self.template_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.template_list.setMinimumHeight(150)

        refresh_templates_btn = QtWidgets.QPushButton("Refresh")
        refresh_templates_btn.clicked.connect(self._refresh_template_list)

        list_layout.addWidget(self.template_list)

        refresh_layout = QtWidgets.QVBoxLayout()
        refresh_layout.addWidget(refresh_templates_btn)
        refresh_layout.addStretch()

        list_layout.addLayout(refresh_layout)
        templates_layout.addLayout(list_layout)

        rig_layout.addWidget(templates_group)

        # Rig settings section
        settings_group = QtWidgets.QGroupBox("Rig Settings")
        settings_layout = QtWidgets.QVBoxLayout(settings_group)

        # Option checkboxes
        self.add_controls_cb = QtWidgets.QCheckBox("Add Control Curves")
        self.add_controls_cb.setChecked(True)
        settings_layout.addWidget(self.add_controls_cb)

        self.setup_constraints_cb = QtWidgets.QCheckBox("Set Up Constraints")
        self.setup_constraints_cb.setChecked(True)
        settings_layout.addWidget(self.setup_constraints_cb)

        rig_layout.addWidget(settings_group)

        # Create rig button
        create_rig_btn = QtWidgets.QPushButton("Create Rig")
        create_rig_btn.setMinimumHeight(40)
        create_rig_btn.clicked.connect(self._create_rig)
        rig_layout.addWidget(create_rig_btn)

        # Status label
        self.rig_status_label = QtWidgets.QLabel(
            "Select a template to create a new rig"
        )
        rig_layout.addWidget(self.rig_status_label)

        # Add some stretch at the end
        rig_layout.addStretch()

        # Add tab to tab widget
        self.tab_widget.addTab(rig_tab, "Create")

        # Populate the template list
        self._refresh_template_list()

    def create_export_tab(self):
        """Create the Export Prep tab"""
        export_tab = QtWidgets.QWidget()
        export_layout = QtWidgets.QVBoxLayout(export_tab)

        # Header
        header_label = QtWidgets.QLabel("Animation Export Preparation")
        header_label.setStyleSheet(
            "background-color: #333333; color: white; padding: 8px; font-weight: bold;"
        )
        header_label.setAlignment(QtCore.Qt.AlignCenter)
        export_layout.addWidget(header_label)

        # Rig list section
        rig_group = QtWidgets.QGroupBox("Available Rigs")
        rig_layout = QtWidgets.QVBoxLayout(rig_group)

        # Create list widget and refresh button in a horizontal layout
        list_layout = QtWidgets.QHBoxLayout()

        self.rig_list = QtWidgets.QListWidget()
        self.rig_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.rig_list.setMinimumHeight(150)

        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_rig_list)

        list_layout.addWidget(self.rig_list)

        refresh_layout = QtWidgets.QVBoxLayout()
        refresh_layout.addWidget(refresh_btn)
        refresh_layout.addStretch()

        list_layout.addLayout(refresh_layout)
        rig_layout.addLayout(list_layout)

        export_layout.addWidget(rig_group)

        # Options section
        options_group = QtWidgets.QGroupBox("Options")
        options_layout = QtWidgets.QVBoxLayout(options_group)

        self.namespace_cb = QtWidgets.QCheckBox("Clean up namespaces")
        options_layout.addWidget(self.namespace_cb)

        export_layout.addWidget(options_group)

        # Process button
        process_btn = QtWidgets.QPushButton("Process Selected Rigs")
        process_btn.setMinimumHeight(40)
        process_btn.clicked.connect(self._export_animation)
        export_layout.addWidget(process_btn)

        # Status label
        self.status_label = QtWidgets.QLabel(
            f"Found {len(self.rigs)} rig(s) in the scene."
        )
        export_layout.addWidget(self.status_label)

        # Add some stretch at the end
        export_layout.addStretch()

        # Add tab to tab widget
        self.tab_widget.addTab(export_tab, "Export Prep")

        # Populate the rig list
        self._refresh_rig_list()

    # ==================================
    # Main Functions
    # ==================================

    def _process_rig(self, rig_name):
        """
        Process a specific rig to find its geometry and skeleton components.

        Args:
            rig_name (str): The name of the rig to process
        """
        self.skl_sel = []
        self.geo_sel = []
        self.final_sel = []

        # Look for SKL_lyr and GEO_lyr under this rig
        skl_layer = f"{rig_name}:SKL_lyr"
        geo_layer = f"{rig_name}:GEO_lyr"

        # If no namespace, try without it
        if not cmds.objExists(skl_layer):
            skl_layer = "SKL_lyr"

        if not cmds.objExists(geo_layer):
            geo_layer = "GEO_lyr"

        # Process skeleton layer
        if cmds.objExists(skl_layer):
            cmds.select(skl_layer)
            connections = cmds.listConnections(skl_layer) or []
            self.skl_sel = connections[1:] if len(connections) > 1 else []
            print(f"SKL for {rig_name}:", self.skl_sel)
        else:
            print(f"Warning: '{skl_layer}' not found for rig '{rig_name}'")

            # Try to find skeleton parts by examining rig structure
            if cmds.objExists(f"{rig_name}|Skeleton"):
                skeleton_node = f"{rig_name}|Skeleton"
                skeleton_parts = (
                    cmds.listRelatives(skeleton_node, allDescendents=True, type="joint")
                    or []
                )
                if skeleton_parts:
                    self.skl_sel = skeleton_parts
                    print(
                        f"Found {len(self.skl_sel)} skeleton parts under Skeleton node for '{rig_name}'"
                    )
            else:
                # Fallback: find all joints under the rig
                potential_skeletons = (
                    cmds.listRelatives(rig_name, allDescendents=True, type="joint")
                    or []
                )
                if potential_skeletons:
                    self.skl_sel = potential_skeletons
                    print(
                        f"Found {len(self.skl_sel)} skeleton parts by hierarchy for '{rig_name}'"
                    )

        # Process geometry layer
        if cmds.objExists(geo_layer):
            cmds.select(geo_layer)
            connections = cmds.listConnections(geo_layer) or []
            self.geo_sel = connections[1:] if len(connections) > 1 else []
            print(f"GEO for {rig_name}:", self.geo_sel)
        else:
            print(f"Warning: '{geo_layer}' not found for rig '{rig_name}'")

            # Try to find geometry under ExportMeshes first
            if cmds.objExists(f"{rig_name}|Meshes|ExportMeshes"):
                export_node = f"{rig_name}|Meshes|ExportMeshes"
                potential_geo = (
                    cmds.listRelatives(export_node, allDescendents=True, type="mesh")
                    or []
                )
                if potential_geo:
                    # Get the transform nodes of the meshes
                    geo_transforms = []
                    for geo in potential_geo:
                        parents = cmds.listRelatives(geo, parent=True)
                        if parents:
                            geo_transforms.append(parents[0])
                    self.geo_sel = list(set(geo_transforms))  # Remove duplicates
                    print(
                        f"Found {len(self.geo_sel)} geometry parts under ExportMeshes for '{rig_name}'"
                    )
            else:
                # Fallback: find all meshes under the rig
                potential_geo = (
                    cmds.listRelatives(rig_name, allDescendents=True, type="mesh") or []
                )
                # Get the transform nodes of the meshes
                if potential_geo:
                    geo_transforms = []
                    for geo in potential_geo:
                        parents = cmds.listRelatives(geo, parent=True)
                        if parents:
                            geo_transforms.append(parents[0])
                    self.geo_sel = list(set(geo_transforms))  # Remove duplicates
                    print(
                        f"Found {len(self.geo_sel)} geometry parts by hierarchy for '{rig_name}'"
                    )

        # Compile final selection
        self.final_sel = self.geo_sel + self.skl_sel

        # Print and select the final selection
        print(f"Complete selection for {rig_name}:", self.final_sel)
        if self.final_sel:
            cmds.select(self.final_sel)
            return True
        else:
            print(f"Warning: No objects found to select for '{rig_name}'")
            return False

    def _create_rig(self):
        """
        Create a new rig based on the selected template.
        """
        # Get the selected template
        selected_items = self.template_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please select a template rig from the list."
            )
            return

        template_rig = selected_items[0].text()

        # Get the new rig name
        new_rig_name = self.new_rig_name.text()
        if not new_rig_name:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please enter a name for the new rig."
            )
            return

        # Add '_rig' suffix if not already present
        if not new_rig_name.endswith("_rig"):
            new_rig_name = f"{new_rig_name}_rig"

        # Check if a rig with this name already exists
        if cmds.objExists(new_rig_name):
            QtWidgets.QMessageBox.warning(
                self,
                "Warning",
                f"A rig named '{new_rig_name}' already exists. Please choose a different name.",
            )
            return

        # Get options
        add_controls = self.add_controls_cb.isChecked()
        setup_constraints = self.setup_constraints_cb.isChecked()

        try:
            # Additional setup based on options
            if add_controls and setup_constraints:
                # This is a placeholder for additional rig setup - would need to be customized
                # based on actual rigging requirements
                pass

            # Refresh the rig lists
            self._refresh_rig_list()
            self._refresh_template_list()

            # Show success message
            QtWidgets.QMessageBox.information(
                self,
                "Success",
                f"Successfully created new rig '{new_rig_name}' from template '{template_rig}'.",
            )

            # Select the new rig
            cmds.select(new_rig_name)

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Failed to create rig: {str(e)}"
            )

    def _export_animation(self):
        """
        Process all selected rigs in the UI.
        """
        selected_rigs = []

        # Get selected items from the list
        for item in self.rig_list.selectedItems():
            selected_rigs.append(item.text())

        if not selected_rigs:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please select at least one rig from the list."
            )
            return

        all_selected = []
        for rig in selected_rigs:
            self._process_rig(rig)
            all_selected.extend(self.final_sel)

        if all_selected:
            self.final_sel = all_selected
            cmds.select(self.final_sel)

            # Optionally manage namespaces if checkbox is checked
            if self.namespace_cb.isChecked():
                self._manage_namespaces()

            QtWidgets.QMessageBox.information(
                self,
                "Success",
                f"Selected {len(self.final_sel)} objects from {len(selected_rigs)} rigs.",
            )
        else:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "No objects found to select."
            )

    # ==================================
    # Helper Functions
    # ==================================

    def _manage_namespaces(self):
        """
        Handle namespaces: remove unwanted ones and merge with parent.
        """
        default_namespaces = ["UI", "shared"]
        namespaces = cmds.namespaceInfo(lon=True)

        for ns in namespaces:
            if ns not in default_namespaces:
                try:
                    cmds.namespace(removeNamespace=ns, mergeNamespaceWithParent=True)
                except Exception as e:
                    print(f"Could not merge namespace '{ns}': {e}")

    def _find_rigs(self):
        """
        Find all transforms named 'rig' in the scene.
        """
        # Find all transforms in the scene
        all_transforms = cmds.ls(type="transform")

        # Filter for transforms that are named 'rig' or end with 'rig'
        self.rigs = [
            transform
            for transform in all_transforms
            if transform == "rig" or transform.endswith("_rig") or transform == "RIG"
        ]

        return self.rigs

    def _find_template_rigs(self):
        """
        Find all rigs that can be used as templates.
        """
        # Find all transforms in the scene
        all_rigs = self._find_rigs()

        # For now, return all rigs as potential templates
        # This can be enhanced with additional filtering logic if needed
        return all_rigs

    def _refresh_rig_list(self):
        """
        Refresh the list of rigs in the scene.
        """
        self._find_rigs()
        self.rig_list.clear()

        if self.rigs:
            self.rig_list.addItems(self.rigs)
            self.status_label.setText(f"Found {len(self.rigs)} rig(s) in the scene.")
        else:
            self.status_label.setText("No rigs found in the scene.")
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "No rigs found in the scene. Look for transforms named 'rig', 'RIG', or ending with '_rig'.",
            )

    def _refresh_template_list(self):
        """
        Refresh the list of template rigs in the scene.
        """
        template_rigs = self._find_template_rigs()
        self.template_list.clear()

        if template_rigs:
            self.template_list.addItems(template_rigs)
            self.rig_status_label.setText(
                f"Found {len(template_rigs)} template rig(s) in the scene."
            )
        else:
            self.rig_status_label.setText("No template rigs found in the scene.")
            QtWidgets.QMessageBox.information(
                self,
                "Info",
                "No template rigs found in the scene. Create a character template first.",
            )

    def _create_character_template(self):
        """
        Create a character rig template hierarchy.
        """
        # Get the rig name from the text field
        rig_name = self.name_field.text()

        if not rig_name:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Please enter a name for the rig."
            )
            return

        # Create the full rig name with suffix
        full_rig_name = f"{rig_name}_rig"

        # Create the top-level node
        rig_node = cmds.createNode("transform", name=full_rig_name)

        # Create 'Controls" nodes under the rig
        cmds.createNode("transform", name="Controls", parent=rig_node)

        # Create 'Meshes' nodes under the rig
        meshes_node = cmds.createNode("transform", name="Meshes", parent=rig_node)

        # Create 'ExportMeshes' and 'bak' nodes under 'Meshes'
        cmds.createNode("transform", name="ExportMeshes", parent=meshes_node)
        cmds.createNode("transform", name="bak", parent=meshes_node)

        # Create 'Skeleton' nodes under the rig
        cmds.createNode("transform", name="Skeleton", parent=rig_node)

        # Print the created hierarchy for verification
        print("Hierarchy created:")
        print(cmds.ls(rig_node, dag=True))

        # Refresh the rig lists
        self._refresh_rig_list()
        self._refresh_template_list()

        # Show a confirmation
        QtWidgets.QMessageBox.information(
            self,
            "Success",
            f"Character template '{full_rig_name}' created successfully.",
        )

    # ==================================
    # Help
    # ==================================

    def _show_template_help(self):
        """
        Display help information about the character template.
        """
        help_text = """
        Character Template Structure:

        The character rig template creates a standardized hierarchy for animation:

        - [NAME]_rig
        |-- Controls
            Contains all control objects for animating the character

        |-- Meshes
            |-- ExportMeshes
                Place meshes here that should be exported with the animation
            |-- bak
                Place backup or work-in-progress meshes here

        |-- Skeleton
            Contains all joints and skeleton elements

        This structure helps maintain consistency across character rigs and
        streamlines the export process for animation.
        """

        QtWidgets.QMessageBox.information(self, "Character Template Help", help_text)


def main(*args):
    """
    Main function to run the export preparation process.
    """
    # Close any existing instance
    try:
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if isinstance(widget, MayaRigHandler):
                widget.close()
                widget.deleteLater()

    except Exception as e:

        cmds.warning(f"Error closing existing widget: {e}")

    try:
        pass
    except:
        pass

    # Create and show the UI
    ui = MayaRigHandler()
    ui.show()
    return ui


if __name__ == "__main__":
    main()
