# ---------------------------------------------------------------------------
# Title: BackupGDB_v1.2.py
# Version: 1.2
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the BackupGDB function 
#    that is held in the clitools.general module.
# ---------------------------------------------------------------------------

from clitools.general import BackupGDB

in_gdb = arcpy.GetParameterAsText(0)
com = arcpy.GetParameterAsText(1)
bu_path = arcpy.GetParameterAsText(2)

BackupGDB(in_gdb,bu_path,com)
