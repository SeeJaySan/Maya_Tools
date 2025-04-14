import os
import sys
import maya.cmds as cmds
from core.Config import Config

def main(args=None):
    """
    Main function that will be called by ToolsetMaster.
    """
    # Print arguments received
    print(f"Test script main function executed with args: {args}")
    
    # Create a dialog to make sure it's working
    cmds.confirmDialog(
        title="Test Script",
        message=f"{Config.desktop_path}",
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