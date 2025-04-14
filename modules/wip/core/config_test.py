import os
import sys
import maya.cmds as cmds
from core.Config import Config

def main(args=None):
    """
    Main function that will be called by ToolsetMaster.
    """
    # First, make sure paths are updated
    Config.update_paths()
    
    # Print arguments received
    print(f"Test script main function executed with args: {args}")
    
    # Print path information
    print(f"The file path is: {Config.filepath}")
    print(f"The file name is: {Config.filename}")
    print(f"The raw name is: {Config.raw_name}")
    print(f"The extension is: {Config.extension}")
    
    # Now set desktop_path since it's not set in update_paths()
    if not Config.desktop_path:
        Config.desktop_path = os.path.join("C:\\", f"{Config.raw_name}")
    
    print(f"The desktop path is: {Config.desktop_path}")
    
    # Create a dialog to show the values
    cmds.confirmDialog(
        title="Config Values",
        message=f"File path: {Config.filepath}\n"
               f"Filename: {Config.filename}\n"
               f"Raw name: {Config.raw_name}\n"
               f"Desktop path: {Config.desktop_path}",
        button=["OK"],
        defaultButton="OK"
    )
    
    # Optional: Return a value for debugging
    return f"Test completed with args: {args}"

# The following will execute when the module is imported
print("Test module imported")

if __name__ == "__main__":
    # This only runs when executed directly
    print("Running test.py directly")
    result = main("direct")
    print(f"Result: {result}")