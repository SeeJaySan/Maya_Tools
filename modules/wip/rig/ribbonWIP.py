from maya import cmds as mc
from maya import mel

from msc.third_party import zbw_controlShapes as zbw_con

jointLocations = []

def buildControls():
    
    sel = mc.ls(sl = 1)
    
    this = mc.curve(n='{}'.format(sel[0])), d=1, p=zbw_con.shapes['cube'])
    
    mc.select()
    
    
    MatchTransform;
    
   
    
    print(sel)
    
buildControls()