import maya.cmds as mc
import maya.mel as mel
from maya import OpenMaya as om

def main(*args):
    RigOps_CreateRollJoints(*args)


class RigOps_CreateRollJoints(object):

    clstr = mc.cluster()
    mc.select(cl=1)
    jnt = mc.joint()
    mc.select(cl=1)
    const = mc.parentConstraint(clstr, jnt, mo=0)
    mc.delete(const, clstr)
