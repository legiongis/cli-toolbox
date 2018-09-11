# ---------------------------------------------------------------------------
# Title: MergeStandardsGDBs.py
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the StandardsToStandardsGDB
#    function that is held in the clitools.management module.
# ---------------------------------------------------------------------------

import arcpy
from clitools.management import StandardsToStandardsGDB
from clitools.general import BackupGDB

in_gdb = arcpy.GetParameterAsText(0)
target_gdb = arcpy.GetParameterAsText(1)
backup = arcpy.GetParameter(2)
backup_location = arcpy.GetParameter(3)

if backup == True:
    BackupGDB(target_gdb,backup_location,"BEFORE_IMPORT")

StandardsToStandardsGDB(in_gdb,target_gdb)
