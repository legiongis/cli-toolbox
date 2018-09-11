# ---------------------------------------------------------------------------
# Title: CreateSubsetofStandardsGDB.py
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
filter_by = arcpy.GetParameterAsText(2)
incodes = arcpy.GetParameter(3)

if filter_by == "CLI Number":
    filter_field = "CLI_NUM"
elif filter_by == "Alpha Code":
    filter_field = "ALPHA_CODE"
elif filter_by == "Region":
    filter_field = "REG_CODE"
else:
    exit()

ExtractFromStandards(input_gdb,filter_field,incodes,output_dir)
