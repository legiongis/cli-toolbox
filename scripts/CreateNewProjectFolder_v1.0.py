#-------------------------------------------------------------------------------
# Title: Create New CLI Project
# Version: 1.0
# Created by Adam Cox
#
# Description:  This is the shell script used to translate the input  
#    parameters from the tool dialogue into appropriate input for the
#    CreateNewProjectFolder function that is held in the clitools.management
# 	 module.
#-------------------------------------------------------------------------------

import os
import arcpy
from clitools.management import CreateNewProjectFolder

drive_letter = arcpy.GetParameterAsText(0)
region_code = arcpy.GetParameterAsText(1)
alpha_code = arcpy.GetParameterAsText(2)
cli_num = arcpy.GetParameterAsText(3)
open_mxd = arcpy.GetParameter(4)

CreateNewProjectFolder(drive_letter,region_code,alpha_code,cli_num,
    open_mxd)

