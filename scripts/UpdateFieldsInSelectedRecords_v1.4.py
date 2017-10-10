# ---------------------------------------------------------------------------
# Title: UpdateFieldsInSelectedRecords_v1.4.py
# Version: 1.4
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into  a variable dictionary and then use that
#    dictionary on every layer that currently has a selection on it.
# ---------------------------------------------------------------------------


import arcpy, traceback, os, sys
from arcpy.mapping import *
from clitools.general import TakeOutTrash
from clitools.mxdops import SaveSourceInfoToTable
from clitools.mxdops import UpdateCLIFieldsInLayer
from clitools.mxdops import UpdateRowsInLayer

class DataView(Exception):
    pass
class duplicateLayers(Exception):
    pass

#get field inputs from parameters
#1. source info
SOURCE = arcpy.GetParameterAsText(5)
SRC_DATE = arcpy.GetParameterAsText(6)
SRC_ACCU = arcpy.GetParameterAsText(7)
SRC_SCALE = arcpy.GetParameterAsText(8)
SRC_COORD = arcpy.GetParameterAsText(9)
VERT_ERROR = arcpy.GetParameterAsText(10)
META_MIDF = arcpy.GetParameterAsText(11)

#2. creation info
MAP_METHOD = arcpy.GetParameterAsText(14)
MAP_MTH_OT = arcpy.GetParameterAsText(15)
BND_OTHER = arcpy.GetParameterAsText(16)
CREATEDATE = arcpy.GetParameterAsText(17)
EDIT_DATE = arcpy.GetParameterAsText(18)
EDIT_BY = arcpy.GetParameterAsText(19)
ORIGINATOR = arcpy.GetParameterAsText(20)
CONSTRANT = arcpy.GetParameterAsText(21)
PROGRAM_COLLECTION = arcpy.GetParameterAsText(22)

#3. resource info
RESNAME = arcpy.GetParameterAsText(23)
RESTRICT_ = arcpy.GetParameterAsText(24)
CONTRIBRES = arcpy.GetParameterAsText(25)
IS_EXTANT = arcpy.GetParameterAsText(26)
EXTANT_OTH = arcpy.GetParameterAsText(27)
CR_NOTES = arcpy.GetParameterAsText(28)
fclass = arcpy.GetParameterAsText(29)

#4. cli info
CLI_ID = arcpy.GetParameterAsText(30)
CLI_NUM = arcpy.GetParameterAsText(31)
LAND_CHAR = arcpy.GetParameterAsText(32)

#5. location info
ALPHA_CODE = arcpy.GetParameterAsText(33)
UNIT = arcpy.GetParameterAsText(34)
UNIT_CODEO = arcpy.GetParameterAsText(35)
UNIT_OTHER = arcpy.GetParameterAsText(36)
UNIT_TYPE = arcpy.GetParameterAsText(37)
GROUP_CODE = arcpy.GetParameterAsText(38)
REG_CODE = arcpy.GetParameterAsText(39)

#additional parameter inputs
overwrite = arcpy.GetParameter(0)
save = arcpy.GetParameter(12)

get_cli_info = arcpy.GetParameter(1)
cli_info_table = arcpy.GetParameterAsText(2)

info_layer = arcpy.GetParameterAsText(3)

var_dict = {
"RESNAME": RESNAME,
"BND_OTHER": BND_OTHER,
"IS_EXTANT": IS_EXTANT,
"EXTANT_OTH": EXTANT_OTH,
"CONTRIBRES": CONTRIBRES,
"RESTRICT_": RESTRICT_,
"SOURCE": SOURCE,
"SRC_DATE": SRC_DATE,
"SRC_SCALE": SRC_SCALE,
"SRC_ACCU": SRC_ACCU,
"VERT_ERROR": VERT_ERROR,
"SRC_COORD": SRC_COORD,
"MAP_METHOD": MAP_METHOD,
"MAP_MTH_OT": MAP_MTH_OT,
"CREATEDATE": CREATEDATE,
"EDIT_DATE": EDIT_DATE,
"EDIT_BY": EDIT_BY,
"ORIGINATOR": ORIGINATOR,
"CONSTRANT": CONSTRANT,
"CR_NOTES": CR_NOTES,
"ALPHA_CODE": ALPHA_CODE,
"UNIT_CODEO": UNIT_CODEO,
"UNIT": UNIT,
"UNIT_OTHER": UNIT_OTHER,
"UNIT_TYPE": UNIT_TYPE,
"GROUP_CODE": GROUP_CODE,
"REG_CODE": REG_CODE,
"LAND_CHAR": LAND_CHAR,
"CLI_NUM": CLI_NUM,
"CLI_ID": CLI_ID,
"META_MIDF":META_MIDF,
"fclass":fclass,
"Program_Collection":PROGRAM_COLLECTION
}

#if indicated, add new source data to source info table
if save == True:
    SaveSourceInfoToTable(var_dict)

try:
    #make mxd and dataframe variables
    mxd = arcpy.mapping.MapDocument("CURRENT")
    for d in arcpy.mapping.ListDataFrames(mxd):
        if mxd.activeView == "PAGE_LAYOUT":
            raise DataView
        if mxd.activeView == d.name:
            df = d

    #iterate through relevant layers, and check for duplicate layers
    lyr_list = []
    problem_lyrs = []
    for lyr in arcpy.mapping.ListLayers(mxd,"",df):
        if lyr.supports("DATASETNAME"):
            if lyr.name in lyr_list:
                problem_lyr = problem_lyrs.append(lyr.name)
            else:
                lyr_list.append(lyr.name)
    if len(problem_lyrs) > 0:
        raise duplicateLayers

    ## sanitize the input dictionary: no blank values, and make Nulls
    del_list = []
    for k,v in var_dict.iteritems():
        if v == "":
            del_list.append(k)
        if v == "code: None":
            var_dict[k] = None
    for k in del_list:
        del var_dict[k]

    #print update options input
    arcpy.AddMessage(" ")
    if overwrite:
        arcpy.AddMessage("Overwrite existing values: YES")
    else:
        arcpy.AddMessage("Overwrite existing values: NO")
        
    if get_cli_info:
        arcpy.AddMessage("Update CLI values: YES")
    else:
        arcpy.AddMessage("Update CLI values: NO")
        
    key_sort = var_dict.keys()
    key_sort.sort()
    if len(key_sort) == 0:
        arcpy.AddMessage("User input values: NO")
    else:
        arcpy.AddMessage("User input values: YES")
        arcpy.AddMessage("\nThe following values will be written to all "\
                         "currently selected records:")
        for k in key_sort:
            arcpy.AddMessage("{0}: {1}".format(k,str(var_dict[k])))

    ct = 0
    
    #iterate through relevant layers, and update fields in selected rows    
    for lyr in arcpy.mapping.ListLayers(mxd,"",df):

        ## skip the layer that was entered to transfer field values
        if lyr.name == info_layer:
            continue

        #only process layers with an existing selection
        try:
            desc = arcpy.Describe(lyr)
            if not desc.FIDSet:
                continue
        except:
            continue
        
        arcpy.AddMessage("\nupdating selected rows in " + lyr.name + "...")

        count = 0
        ## write var_dict data to all fields
        if not len(key_sort) == 0:
            arcpy.AddMessage("  adding user input values...")
            count = UpdateRowsInLayer(lyr,var_dict,overwrite)
            arcpy.AddMessage("    {0} row{1} updated.".format\
                         (count,"" if count == 1 else "s"))

        ## pull cli info from table and write to each field
        if get_cli_info == True:
            arcpy.AddMessage("  adding CLI values...")
            count = UpdateCLIFieldsInLayer(lyr)
            arcpy.AddMessage("    {0} row{1} updated.".format\
                         (count,"" if count == 1 else "s"))
        ct += 1    

    if ct == 0:
        arcpy.AddError("\nNo layers were updated.  Make sure a selection is "\
                         " made and try again.\n")

    arcpy.AddMessage(" ")

except DataView:
    arcpy.AddError("\nERROR:\nThis tool must be run from Data View, "\
                     "not Layout View.\n")

except duplicateLayers:
    arcpy.AddError("\nERROR:\nThere are layers with identical names in the "\
                     "table of contents:\n\n" + "\n".join(problem_lyrs) + \
                   "\n\nRemove or rename any these layers and run the "\
                   "tool again.  It may be helpful to remove all layers "\
                   "and run the Display Geodatabase using the Feature Class "\
                   "display option.\n")
    
except:
    
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
            + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
    msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

    arcpy.AddError(msgs)
    arcpy.AddError(pymsg)

    print msgs

    print pymsg
    
    arcpy.AddMessage(arcpy.GetMessages(1))
    print arcpy.GetMessages(1)
