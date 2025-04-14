import maya.cmds as cmds

def create_JNT_LOC():
    #create a jnt and locator at point of selected object

    sel = cmds.ls (sl = 1)
    print (sel)
    
    LOC = cmds.spaceLocator ( p=(0,0,0))
    
    cmds.select(sel, LOC)
    
    constLoc = cmds.pointConstraint (sel, LOC, o = (0,0,0), w = 1)
    cmds.delete(constLoc)
    cmds.select(cl = 1)
    
    JNT = cmds.joint(p = (0,0,0))
    
    constJNT = cmds.pointConstraint (LOC, JNT, o = (0,0,0), w = 1)
    cmds.delete(constJNT)
    cmds.parent(JNT, LOC)
    cmds.select(LOC)

create_JNT_LOC()