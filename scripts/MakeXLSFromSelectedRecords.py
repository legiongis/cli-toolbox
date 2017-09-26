# ---------------------------------------------------------------------------
# Title: MakeXLSFromSelectedRecords.py
# Version: 1.2
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the MakeXLSFromSelectedRecords
#    function that is held in the clitools.summarize module.
# ---------------------------------------------------------------------------

import arcpy
import arcpy.mapping
import os,sys,traceback
from clitools.summarize import MakeXLSFromSelectedRecords

layer = arcpy.GetParameter(0)
out_dir = arcpy.GetParameterAsText(1)
out_name = arcpy.GetParameterAsText(2)
field_list = arcpy.GetParameter(3)
open_file = arcpy.GetParameter(4)

MakeXLSFromSelectedRecords(layer,out_dir,out_name,field_list,open_file)

