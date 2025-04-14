import maya.cmds as mc
import maya.mel as mel

currentSel = mc.ls(sl = 1)

rootJoint = 'pelvis'

mel.eval('''
        select -r {0};
        SelectHierarchy;
        select -d {0};
        joint -e -apa -ch;
        select -d;
        '''.format(rootJoint))

mc.select(currentSel)