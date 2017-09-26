# ---------------------------------------------------------------------------
# Title: PrepareXLSForDataEditor_v1.0.py
# Version: 1.0
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the ConvertFeatureXLSToGDBTable
#    function that is held in the clitools.management module.
# ---------------------------------------------------------------------------

import arcpy
import os
from clitools.enterprise import ConvertFeatureXLSToGDBTable

xls_path = arcpy.GetParameterAsText(0)
out_dir = arcpy.GetParameterAsText(1)
update_local = arcpy.GetParameter(2)

ConvertFeatureXLSToGDBTable(xls_path,out_dir,update_local)
