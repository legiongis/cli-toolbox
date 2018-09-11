# ---------------------------------------------------------------------------
# Title: DisplayGeodatabase.py
# Version: 1.0
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the AddToDataFrame function 
#    that is held in the clitools.mxdops module.
# ---------------------------------------------------------------------------

import arcpy
from clitools.mxdops import AddToDataFrame
from clitools.classes import MakeUnit

in_gdb = arcpy.GetParameterAsText(0)
in_unit_code = arcpy.GetParameterAsText(1)
df_name = arcpy.GetParameterAsText(2)

## settings
grp_choice = arcpy.GetParameter(3)
label = arcpy.GetParameter(4)
non_ext = arcpy.GetParameter(5)
omit_mults = arcpy.GetParameter(6)

## output options
feat_class = arcpy.GetParameter(7)
land_char = arcpy.GetParameter(8)
contrib = arcpy.GetParameter(9)
asmis_id = arcpy.GetParameter(10)
fmss_id = arcpy.GetParameter(11)
lcs_id = arcpy.GetParameter(12)
nris_id = arcpy.GetParameter(13)
cli_id = arcpy.GetParameter(14)

if not in_unit_code == '' and MakeUnit(in_unit_code) == False:
    arcpy.AddError("\nERROR: Invalid CLI number or Park Alpha code.\n")

## add error if the user has not specified any output options
all_in = [feat_class,land_char,contrib,asmis_id,fmss_id,lcs_id,nris_id,cli_id]
if not True in all_in:
    arcpy.AddError("\nERROR: You must choose at least one display option.\n")
    raise Exception("You must choose at least one display option.")
    
## create mxd and dataframe objects
mxd = arcpy.mapping.MapDocument('CURRENT')
df = arcpy.mapping.ListDataFrames(mxd,df_name)[0]

if feat_class == True:
    AddToDataFrame(mxd,df,in_gdb,in_unit_code,"FEATCLASS",'',grp_choice,label,
                   non_ext,omit_mults)

if land_char == True:
    AddToDataFrame(mxd,df,in_gdb,in_unit_code,"LANDCHAR",'',grp_choice,label,
                   non_ext,omit_mults)

if contrib == True:
    AddToDataFrame(mxd,df,in_gdb,in_unit_code,"CONTRIB",'',grp_choice,label,
                   non_ext,omit_mults)

id_fields = (("ASMIS_ID",asmis_id),
             ("FMSS_ID",fmss_id),
             ("LCS_ID",lcs_id),
             ("NRIS_ID",nris_id),
             ("CLI_ID",cli_id))

if True in [i[1] for i in id_fields]:
    use_fields = [i[0] for i in id_fields if i[1] == True]
    AddToDataFrame(mxd,df,in_gdb,in_unit_code,"",use_fields,grp_choice,label,
                   non_ext,omit_mults)

