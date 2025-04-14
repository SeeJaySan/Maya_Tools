import os
from maya import cmds as mc
from msc.modules import Utils_Directories as Ud

# TODO: Add functionality for multiple meshes

jointList = []
unique_names = []
meshSelected = mc.ls(sl=1)

# Get the current file path of the Maya scene
file_path = mc.file(query=True, sceneName=True)
print(file_path)
# Get the directory of the file
directory = os.path.dirname(file_path)
print(directory)
directorySourceimages = directory.replace('scenes', 'sourceimages')
directorySourceimagesTmp = directory.replace('scenes', 'sourceimages/tmp')


def GetBoneNames():
    """Finds all the joints connected to the selected mesh's skin cluster."""
    descendants = mc.listRelatives(meshSelected, allDescendents=True)
    printed_skin_clusters = set()  # Set to track printed skin clusters

    print('\n|-------------------------------------------------------------------------------------------|')
    print('-----------------------------------Always Deform Readout------------------------------------')
    print('|-------------------------------------------------------------------------------------------|\n')

    for obj in descendants:
        print('\n|-------------------------------------------------------------------------------------------|')
        if mc.objectType(obj) == 'mesh':
            print(f'mesh FOUND! -> {obj}')
            meshConnections = mc.listConnections(obj, type='skinCluster')
            for skin_cluster in meshConnections:
                if skin_cluster not in printed_skin_clusters:  # Check if already printed
                    print(f'\nskinCluster FOUND! -> {skin_cluster}')
                    printed_skin_clusters.add(skin_cluster)  # Add to set to avoid duplicate prints
                jointConnections = mc.listConnections(skin_cluster, type='joint')
                for joint in jointConnections:
                    if mc.objectType(joint) == 'joint':
                        jointList.append(joint)
        else:
            print('NO MESH FOUND!')
        print('|-------------------------------------------------------------------------------------------|\n')

    # Filter unique joint names
    for joint in jointList:
        if joint not in unique_names:
            unique_names.append(joint)
    
    return unique_names, list(printed_skin_clusters)


def ExportSkinCluster(skin_clusters, joint_names):
    """Exports skin weights of the specified skin clusters to a JSON file."""
    if file_path:
        # Ensure necessary directories exist
        Ud.createDirectory(directorySourceimages)
        Ud.createDirectory(directorySourceimagesTmp)

        if skin_clusters:
            for skin_cluster in skin_clusters:
                mc.select(skin_cluster)
                export_name = f'{meshSelected[0]}_skinWeights.json'
                print (directorySourceimagesTmp)
                #export_path = os.path.join(directorySourceimagesTmp, export_name)
                mc.deformerWeights(export_name, ex=True, df=skin_cluster, fm="JSON", p=directorySourceimagesTmp)
                mc.skinCluster(skin_cluster, edit=True, unbind=True)
        
                # Create a new skin cluster with the specified joints and mesh
                new_SC = mc.skinCluster(joint_names, meshSelected[0], 
                                        n=meshSelected[0] + '_SC', 
                                        toSelectedBones=True, bindMethod=0, 
                                        maximumInfluences = 4,
                                        skinMethod=0, normalizeWeights=1)
                import_name = directorySourceimagesTmp + '/' + export_name
                                        
                # Import the deformer weights
                mc.deformerWeights(export_name, im=True, method="index", deformer=new_SC[0], p=directorySourceimagesTmp)
        else:
            print("No skin clusters provided to select.")
    else:
        print("No valid scene file found.")
        

'''
def resetMeshSkinCluster(skin_clusters, joint_names, exportedSkinClusterPath):
    """Rebinds the skin cluster to the mesh and imports the exported weights."""
    for skin_cluster in skin_clusters:
        # Unbind the skin cluster
        mc.skinCluster(skin_cluster, edit=True, unbind=True)
        
        # Create a new skin cluster with the specified joints and mesh
        new_SC = mc.skinCluster(joint_names, meshSelected[0], 
                                n='SC_' + meshSelected[0], 
                                toSelectedBones=True, bindMethod=0, 
                                skinMethod=0, normalizeWeights=1)
                                
        # Import the deformer weights
        export_name = f'{meshSelected[0]}_skinWeights.json'
        mc.deformerWeights(export_name, im=True, method="index", deformer=new_SC[0])  
'''

def run():
    """Main function to run the skin cluster export and reset."""
    # Get joint names and skin cluster names
    joint_names, skin_clusters = GetBoneNames()

    # Display joint list for selected mesh
    if meshSelected:
        print(f'FULL JOINT LIST for mesh -> {meshSelected[0]}')
    else:
        print('No mesh selected.')

    # Display unique joint names and skin clusters found
    if joint_names:
        print(f'UNIQUE JOINT NAMES -> {joint_names}')
    else:
        print('No unique joints found.')

    if skin_clusters:
        print(f'SKIN CLUSTERS FOUND -> {skin_clusters}')
    else:
        print('No skin clusters found.')

    # Export and reset skin cluster
    ExportSkinCluster(skin_clusters, joint_names)


# Execute the script
run()
