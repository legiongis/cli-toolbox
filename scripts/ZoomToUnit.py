# ---------------------------------------------------------------------------
# Title: ZoomToUnit.py
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the ZoomTo
#    function that is held in the clitools.mxdops module.
# ---------------------------------------------------------------------------

import arcpy
from clitools.mxdops import ZoomTo

in_code = arcpy.GetParameterAsText(0)
df_name = arcpy.GetParameterAsText(1)

mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd,df_name)[0]

result = ZoomTo(in_code,mxd,df)

if result == False:
    arcpy.AddMessage("...nothing was found to zoom to.\n")
else:
    arcpy.AddMessage(" ")
