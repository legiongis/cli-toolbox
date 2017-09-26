# ---------------------------------------------------------------------------
# Title: Set_PCS_StatePlane.py
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the SetSpatialReference
#    function that is held in the clitools.mxdops module.
# ---------------------------------------------------------------------------

import arcpy, os, traceback, sys
from clitools.mxdops import SetSpatialReference,GetZoneID

mxd = arcpy.mapping.MapDocument("CURRENT")
for d in arcpy.mapping.ListDataFrames(mxd):
    if d.name == mxd.activeView:
        df = d

pcs = "SP"

zone = GetZoneID(df,pcs)

if not zone == False:
    SetSpatialReference(mxd,"PCS","1983",zone,pcs)
