# ---------------------------------------------------------------------------
# Title: ScratchToStandards_v1.0.py
# Version: 1.0
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the ScratchToStandardsGDB
#    function that is held in the clitools.management module.
# ---------------------------------------------------------------------------

import arcpy
import os
from clitools.general import BackupGDB
from clitools.management import ScratchToStandardsGDB

input_gdb = arcpy.GetParameterAsText(0)
fc_list = arcpy.GetParameter(1)
target = arcpy.GetParameterAsText(2)
backup = arcpy.GetParameter(3)
backup_dir = arcpy.GetParameterAsText(4)

scratch_fcs = ["scratch_pt","scratch_ln","scratch_py"]
path_list = [i for i in fc_list if i in scratch_fcs or i.startswith("imp")]

if target == '':
    target = False

if backup == True:
    BackupGDB(target,backup_dir,"BEFORE_SCRATCH_IMPORT")

ScratchToStandardsGDB(input_gdb,path_list,target)         


