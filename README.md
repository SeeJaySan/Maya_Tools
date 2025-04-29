# Project Name

## Overview

This project is a toolset for various operations related to animation, modeling, rigging, and scene management. It includes core utilities, modules for specific tasks, and third-party integrations.

## Project Structure

```
__init__.py
.gitattributes
.gitignore
toolset_launcher.py
core/
    __init__.py
    Config.py
    path_utils.py
    toolset_master.py
docs/
    docs_go_here.txt
modules/
    __init__.py
    anim/
        BfaOps_AnimExporter.py
        BfaOps_AnimExportPrep.py
        CopyPasteKeys.py
        export_animation_prep.py
    model/
        createSphere.py
    rig/
        AlwaysDeform.py
        AssumePreferedAngle.py
        auto_rig_unreal.py
        character_rig_template.py
        joint_tools.py
        ...
    scene/
        ...
third_party/
    ...
tools/
    __init__.py
    anim/
    model/
    rig/
    wip/
```

### Core

- `core/Config.py`: Configuration settings for the toolset.
- `core/path_utils.py`: Utility functions for handling file paths.
- `core/toolset_master.py`: Main script for managing the toolset.

### Modules

#### Animation

- `modules/anim/BfaOps_AnimExporter.py`: Script for exporting animations.
- `modules/anim/BfaOps_AnimExportPrep.py`: Preparation steps for animation export.
- `modules/anim/CopyPasteKeys.py`: Utility for copying and pasting animation keys.
- `modules/anim/export_animation_prep.py`: Additional preparation for exporting animations.

#### Modeling

- `modules/model/createSphere.py`: Script for creating a sphere model.

#### Rigging

- `modules/rig/AlwaysDeform.py`: Script for ensuring deformation.
- `modules/rig/AssumePreferedAngle.py`: Script for assuming preferred angles.
- `modules/rig/auto_rig_unreal.py`: Auto rigging script for Unreal Engine.
- `modules/rig/character_rig_template.py`: Template for character rigging.
- `modules/rig/joint_tools.py`: Tools for joint manipulation.

### Tools

- `tools/anim/`: Additional animation tools.
- `tools/model/`: Additional modeling tools.
- `tools/rig/`: Additional rigging tools.
- `tools/wip/`: Work in progress scripts.

### Third Party

- `third_party/`: Contains third-party integrations and dependencies.

## Getting Started

1. Clone the repository:
    ```sh
    git clone <repository-url>
    ```

2. Navigate to the project directory:
    ```sh
    cd <project-directory>
    ```

3. Run the toolset launcher:
    ```sh
    python toolset_launcher.py
    ```

## Documentation

Documentation can be found in the `docs/` directory. Refer to `docs/docs_go_here.txt` for more information.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.