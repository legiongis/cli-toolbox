# ---------------------------------------------------------------------------
# Title: CheckMandatoryFields.py
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input  
#    parameters from the tool dialogue into appropriate input for the
#    CheckGeodatabaseForNulls function that is held in the clitools.general
# 	 module.
# ---------------------------------------------------------------------------

from clitools.general import CheckGeodatabaseForNulls

gdb = arcpy.GetParameterAsText(0)
guids = arcpy.GetParameter(1)

CheckGeodatabaseForNulls(gdb,guids)
