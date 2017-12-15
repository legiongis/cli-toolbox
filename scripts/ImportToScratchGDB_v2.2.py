# ---------------------------------------------------------------------------
# Title: ImportToScratchGDB_v2.2.py
# Version: 2.2
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the ImportToScratchGDB
#    function that is held in the clitools.management module.
# --------------------------------------------------------------------------

import arcpy
import traceback
import time
import sys
import os
from clitools.management import ImportToScratchGDB

#target gdb and input dataset
input_fc = arcpy.GetParameterAsText(0)
target_gdb = arcpy.GetParameterAsText(1)
clip_fc = arcpy.GetParameterAsText(2)
keep_native = arcpy.GetParameter(3)

#1. get source info from parameters
SOURCE = arcpy.GetParameterAsText(6)
SRC_DATE = arcpy.GetParameterAsText(7)
SRC_ACCU = arcpy.GetParameterAsText(8)
SRC_SCALE = arcpy.GetParameterAsText(9)
SRC_COORD = arcpy.GetParameterAsText(10)
VERT_ERROR = arcpy.GetParameterAsText(11)
META_MIDF = arcpy.GetParameterAsText(12)

#2. get creation info
MAP_METHOD = arcpy.GetParameterAsText(14)
MAP_MTH_OT = arcpy.GetParameterAsText(15)
BND_TYPE = arcpy.GetParameterAsText(16)
BND_OTHER = arcpy.GetParameterAsText(17)
CREATEDATE = arcpy.GetParameterAsText(18)
EDIT_DATE = arcpy.GetParameterAsText(19)
EDIT_BY = arcpy.GetParameterAsText(20)
ORIGINATOR = arcpy.GetParameterAsText(21)
CONSTRANT = arcpy.GetParameterAsText(22)

#3. get resource info
RESNAME = arcpy.GetParameterAsText(23)
RESTRICT_ = arcpy.GetParameterAsText(24)
CONTRIBRES = arcpy.GetParameterAsText(25)
IS_EXTANT = arcpy.GetParameterAsText(26)
EXTANT_OTH = arcpy.GetParameterAsText(27)
CR_NOTES = arcpy.GetParameterAsText(28)

Program_Collection = arcpy.GetParameterAsText(29)
fclass = arcpy.GetParameterAsText(30)

#4. get CLI info
CLI_ID = arcpy.GetParameterAsText(31)
CLI_NUM = arcpy.GetParameterAsText(32)
LAND_CHAR = arcpy.GetParameterAsText(33)

#5. get location info
ALPHA_CODE = arcpy.GetParameterAsText(34)
UNIT = arcpy.GetParameterAsText(35)
UNIT_CODEO = arcpy.GetParameterAsText(36)
UNIT_OTHER = arcpy.GetParameterAsText(37)
UNIT_TYPE = arcpy.GetParameterAsText(38)
GROUP_CODE = arcpy.GetParameterAsText(39)
REG_CODE = arcpy.GetParameterAsText(40)

var_dict = {
        "SOURCE":SOURCE,
        "SRC_DATE":SRC_DATE,
        "SRC_SCALE":SRC_SCALE,
        "SRC_ACCU":SRC_ACCU,
        "SRC_COORD":SRC_COORD,
        "VERT_ERROR":VERT_ERROR,
        "META_MIDF":META_MIDF,
        "MAP_METHOD":MAP_METHOD,
        "MAP_MTH_OT":MAP_MTH_OT,
        "BND_TYPE":BND_TYPE,
        "BND_OTHER":BND_OTHER,
        "CREATEDATE":CREATEDATE,
        "EDIT_DATE":EDIT_DATE,
        "EDIT_BY":EDIT_BY,
        "ORIGINATOR":ORIGINATOR,
        "CONSTRANT":CONSTRANT,
        "RESNAME":RESNAME,
        "RESTRICT_":RESTRICT_,
        "CONTRIBRES":CONTRIBRES,
        "IS_EXTANT":IS_EXTANT,
        "EXTANT_OTH":EXTANT_OTH,
        "CR_NOTES":CR_NOTES,
        "CLI_ID":CLI_ID,
        "CLI_NUM":CLI_NUM,
        "LAND_CHAR":LAND_CHAR,
        "ALPHA_CODE":ALPHA_CODE,
        "UNIT":UNIT,
        "UNIT_CODEO":UNIT_CODEO,
        "UNIT_OTHER":UNIT_OTHER,
        "UNIT_TYPE":UNIT_TYPE,
        "GROUP_CODE":GROUP_CODE,
        "REG_CODE":REG_CODE,
        "Program_Collection":Program_Collection,
        "fclass":fclass
        }

ImportToScratchGDB(input_fc,target_gdb,clip_fc,var_dict,keep_native=keep_native)

