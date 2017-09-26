# ---------------------------------------------------------------------------
# Title: XLSSingleLandscape_v1.0.py
# Version: 1.0
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the MakeSingleLandscapeXLS
#    function that is held in the clitools.summarize module.
# ---------------------------------------------------------------------------

import arcpy
import os
from clitools.summarize import MakeSingleLandscapeXLS

in_gdb = arcpy.GetParameterAsText(0)
cli_num = arcpy.GetParameterAsText(1)
out_dir = arcpy.GetParameterAsText(2)
comment_xls = arcpy.GetParameterAsText(3)
ow = arcpy.GetParameter(4)
of = arcpy.GetParameter(5)

path = MakeSingleLandscapeXLS(cli_num,in_gdb,out_dir,comment_xls,ow)

if of == True:
    os.startfile(path)
