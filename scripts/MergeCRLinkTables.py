# ---------------------------------------------------------------------------
# Title: MergeCRLinkTables.py
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the MergeCRLinkTables
#    function that is held in the clitools.management module.
# ---------------------------------------------------------------------------

import os
from clitools.management import MergeCRLinkTables

in_table = arcpy.GetParameterAsText(0)
target_table = arcpy.GetParameterAsText(1)

MergeCRLinkTables(in_table,target_table)
