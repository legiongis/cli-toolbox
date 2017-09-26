# ---------------------------------------------------------------------------
# Title: Set_GCS_NAD83.py
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the SetSpatialReference
#    function that is held in the clitools.mxdops module.
# ---------------------------------------------------------------------------

import arcpy, os, sys
from clitools.mxdops import SetSpatialReference

mxd = arcpy.mapping.MapDocument("CURRENT")

SetSpatialReference(mxd,"GCS","1983")
