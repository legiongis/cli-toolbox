# ---------------------------------------------------------------------------
# Title: ExtractFromStandards_v1.0.py
# Version: 1.0
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the ExtractFromStandards
#	 function that is held in the clitools.management module.
# ---------------------------------------------------------------------------

import arcpy
from clitools.management import ExtractFromStandards

"""This is a shell script that will pass the parameters from the ArcMap
dialog box to the ExtractFromStandards function in the clitools.management
module."""

input_gdb = arcpy.GetParameterAsText(0)
output_dir = arcpy.GetParameterAsText(1)
incode = arcpy.GetParameterAsText(2)

ExtractFromStandards(input_gdb,incode,output_dir)
