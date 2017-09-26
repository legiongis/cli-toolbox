# ---------------------------------------------------------------------------
# Title: FixFieldInGDB_v1.2.py
# Version: 1.2
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the ExportGDBToShapefiles
#	 function that is held in the clitools.management module.
# ---------------------------------------------------------------------------

from clitools.general import ExportGDBToShapefiles

in_gdb = arcpy.GetParameterAsText(0)
out_dir = arcpy.GetParameterAsText(1)

ExportGDBToShapefiles(in_gdb,out_dir)
