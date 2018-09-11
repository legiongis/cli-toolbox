# ---------------------------------------------------------------------------
# Title: MakeGoogleEarthFile.py
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the MakeKMZ
#    function that is held in the clitools.mxdops module.
# ---------------------------------------------------------------------------

import arcpy
import os
from clitools.mxdops import MakeKMZ
from clitools.classes import MakeUnit

"""this is a shell script that takes the arguments from the arcmap tool
dialog box and passes them to the MakeKMZ function in the clitools.mxdops
module."""

input_gdb = arcpy.GetParameterAsText(0)
out_directory = arcpy.GetParameterAsText(1)
in_unit_code = arcpy.GetParameter(2)
layer_scheme = arcpy.GetParameter(3)

## settings
non_ext = arcpy.GetParameter(4)
omit_mults = arcpy.GetParameter(5)

if not in_unit_code == '' and MakeUnit(in_unit_code) == False:
    arcpy.AddError("\nERROR: Invalid CLI number or park alpha code.\n")

id_field = []

## make layer scheme name from input
if layer_scheme == "Feature Class":
    ls = "FEATCLASS"
elif layer_scheme == "Landscape Characteristic":
    ls = "LANDCHAR"
elif layer_scheme == "CLI Contributing Status":
    ls = "CONTRIB"
else:
    ls = ''
    id_field = [layer_scheme]

result_path = MakeKMZ(input_gdb,out_directory,in_unit_code,ls,
        id_field,False,non_ext,omit_mults)

try:
    os.startfile(result_path)
except:
    arcpy.AddWarning("Can't open file, make sure Google Earth is installed "\
                     "on this computer.")
