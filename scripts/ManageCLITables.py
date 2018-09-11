# ---------------------------------------------------------------------------
# Title: ManageCLITables.py
# Created by Adam Cox
#   
# Description:  This is a shell script that only needs to pass the current map document
# 	 object to the function that is held in the clitools.management module. The
# 	 construction must be this way so that the management module is able to locate
# 	 the tables that will be updated.
# ---------------------------------------------------------------------------

import arcpy
import os
from clitools.enterprise import UpdateCLITables
from clitools.enterprise import ConvertFeatureXLSToGDBTable

method = arcpy.GetParameterAsText(0)

if method == "Update Local Tables From CR Enterprise Tables":
    try:
        mxd = arcpy.mapping.MapDocument("CURRENT")
    except:
        arcpy.AddError("You must run this from ArcMap, and you must use the"\
                   "CR Enterprise Access map document.")
    UpdateCLITables(mxd)
elif method == "Process Local Prepared Excel Workbook (.xls)":
    xls = arcpy.GetParameterAsText(1)
    if not xls:
        arcpy.AddError("\nYou must specify a Prepared CLI Feature Table "\
        "Excel Workbook (.xls).\n")
        raise Exception
    ul = arcpy.GetParameter(2)
    retain = arcpy.GetParameter(3)
    if not ul and not retain:
        arcpy.AddError("\nYou must choose to either \"update local lookup "\
        "tables\" or \"create a separate .gdb...\" or both. Otherwise "\
        "the \"Process Local Prepared Excel Workbook (.xls)\" operation does "\
        "nothing.\n")
        raise Exception
    ConvertFeatureXLSToGDBTable(xls,retain_copy=retain,update_local=ul)

