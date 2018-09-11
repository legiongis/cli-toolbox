# ---------------------------------------------------------------------------
# Title: ExcelFileMultipleLandscapes.py
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the MakeMultipleLandscapeXLS
#    function that is held in the clitools.summarize module.
# ---------------------------------------------------------------------------

import arcpy
import os
from clitools.summarize import MakeMultipleLandscapeXLS
from clitools.classes import MakeUnit

in_gdb = arcpy.GetParameterAsText(0)
out_dir = arcpy.GetParameterAsText(1)
use_one_region = arcpy.GetParameterAsText(2)
landscapes = arcpy.GetParameterAsText(3)
exclude_arch = arcpy.GetParameter(4)
of = arcpy.GetParameter(5)

if len(landscapes) == 0 and use_one_region == "--no, choose from landscapes in "\
   "input geodatabase (use list below)--":
    arcpy.AddWarning("\nNo landscapes were selected.\n")
    exit()

if not use_one_region == "--no, choose from landscapes in "\
   "input geodatabase (use list below)--":
    region = MakeUnit(use_one_region)
    cli_nums = [i[0] for i in region.landscapes]
    arcpy.AddMessage("\nProcessing all landscapes in the "+ region.name)
    
else:
    cli_nums = [i[7:13] for i in landscapes.split(";")]
    arcpy.AddMessage("\nProcessing the following landscapes:")
    arcpy.AddMessage(landscapes.replace(";","\n"))
  
path = MakeMultipleLandscapeXLS(in_gdb,out_dir,cli_nums,exclude_arch)
if of == True:
    os.startfile(path)
