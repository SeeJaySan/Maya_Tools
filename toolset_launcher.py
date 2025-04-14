import os
import sys
import importlib
import traceback

# Print a start marker to confirm the launcher is running
print("=== TOOLSET LAUNCHER STARTING ===")

# Get the current directory where the launcher is located
try:
    # If running as a file
    launcher_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # If running in Script Editor
    launcher_dir = r"C:\Dropbox\Developement\Git\Maya_Rigging_Tools"  # UPDATE THIS PATH
    print("Running in Script Editor, using hardcoded path")

# Set project root (same as launcher_dir if launcher is at root)
project_root = launcher_dir
print(f"Project root: {project_root}")

# Add the project root to sys.path if not already there
if project_root not in sys.path:
    sys.path.append(project_root)
    print(f"Added {project_root} to Python path")

# Also add core and modules directories to ensure imports work
core_path = os.path.join(project_root, "core")
modules_path = os.path.join(project_root, "modules")
tools_path = os.path.join(project_root, "tools")

for path in [core_path, modules_path, tools_path]:
    if path not in sys.path:
        sys.path.append(path)
        print(f"Added {path} to Python path")

# Reload modules if they exist in sys.modules
for module_name in list(sys.modules.keys()):
    top_module = module_name.split(".")[0]
    if top_module in ["core", "modules", "tools"]:
        try:
            importlib.reload(sys.modules[module_name])
            print(f"Reloaded {module_name}")
        except Exception as e:
            print(f"Failed to reload {module_name}: {e}")

# Try importing the main UI with robust error handling
try:
    print("Attempting to import toolset_master...")
    from core import toolset_master
    print("Successfully imported toolset_master")
except Exception as e:
    print(f"Error importing toolset_master: {e}")
    traceback.print_exc()
    # Exit if we can't import the main module
    print("Cannot continue without toolset_master. Exiting.")
    sys.exit(1)

# Main execution
if __name__ == "__main__":
    print("Initializing UI...")
    
    # Attempt to close any existing instance
    try:
        TM.close()
        TM.deleteLater()
    except NameError:
        pass  # Ignore if TM is not defined
    
    # Initialize and display the UI
    try:
        TM = toolset_master.show_ui()  # Using the show_ui function is better
        print("UI displayed successfully")
    except Exception as e:
        print(f"Error showing UI: {e}")
        traceback.print_exc()

print("=== TOOLSET LAUNCHER COMPLETED ===")