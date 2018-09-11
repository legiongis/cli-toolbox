# ---------------------------------------------------------------------------
# Title: GenerateCentroids.py
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the GenerateCentroids
#	 function that is held in the clitools.mxdops module.  Using the input
#    layer, the script looks for a corresponding point fc to hold the new
# 	 centroids and won't work if a feature class can't be found.
# ---------------------------------------------------------------------------

import arcpy
from clitools.mxdops import GenerateCentroids

''' this is the script shell that takes the tool dialogue input and
feeds it to the generate centroid function in the clitools.mxdops module.
'''

in_layer = arcpy.GetParameterAsText(0)

ct = int(arcpy.management.GetCount(in_layer).getOutput(0))

arcpy.AddMessage("\ncreating centroids for {0} feature{1} in {2}.\n".format(
    str(ct),"s" if not ct == 1 else "",in_layer))

layer = arcpy.mapping.Layer(in_layer)

target_layer = layer.dataSource[:-2]+"pt"
if not arcpy.Exists(target_layer):
    arcpy.AddError("\nNo easily found target feature class for centroids.\n")

arcpy.AddMessage("centroids will be appended to:\n" + target_layer)

GenerateCentroids(in_layer,target_layer)

arcpy.AddMessage("\n")
