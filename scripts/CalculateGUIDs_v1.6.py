# ---------------------------------------------------------------------------
# Title: CalculateGUIDs_v1.6.py
# Version: 1.6
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the CreateGUIDs function 
#    that is held in the clitools.management module.
# ---------------------------------------------------------------------------

import arcpy, traceback, os, sys
from arcpy.mapping import *

from clitools.management import CreateGUIDs

#get location of standards gdb, CLI number, and values for fields
gdb = arcpy.GetParameterAsText(0)
cli_num = arcpy.GetParameterAsText(1)
cr = arcpy.GetParameter(2)
loca = arcpy.GetParameter(3)
overwrite = arcpy.GetParameter(4)

## make query with input cli_number
if cli_num:
    query = "\"CLI_NUM\" = \'" + cli_num + "\'"
else:
    query = ''

CreateGUIDs(gdb,query,cr,loca,overwrite)
