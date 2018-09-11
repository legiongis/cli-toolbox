# ---------------------------------------------------------------------------
# Title: FixFieldInGDB.py
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the UpdateFieldInGDB
#	 function that is held in the clitools.management module.
# ---------------------------------------------------------------------------

import arcpy, os, sys, traceback

from clitools.general import MakePathList
from clitools.management import UpdateFieldInGDB

stan_gdb = arcpy.GetParameterAsText(0)
field = arcpy.GetParameterAsText(1)
old_val_list = arcpy.GetParameter(2)
new_val = arcpy.GetParameterAsText(4)

UpdateFieldInGDB(stan_gdb,field,old_val_list,new_val)
