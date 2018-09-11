# ---------------------------------------------------------------------------
# Title: SyncCRLinkandCatalogTables.py
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the SyncCRLinkAndCRCatalog
#    function that is held in the clitools.management module.
# ---------------------------------------------------------------------------

import sys
import os
import arcpy
from time import strftime
from clitools.management import SyncCRLinkAndCRCatalog

gdb = arcpy.GetParameterAsText(0)

SyncCRLinkAndCRCatalog(gdb)





