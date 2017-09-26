# ---------------------------------------------------------------------------
# Title: StandardsToWGS84_v1.0.py
# Version: 1.0
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the StandardsToWGS84
#    function that is held in the clitools.management module.
# ---------------------------------------------------------------------------

import arcpy
from clitools.management import StandardsToWGS84

gdb = arcpy.GetParameterAsText(0)

StandardsToWGS84(gdb)
