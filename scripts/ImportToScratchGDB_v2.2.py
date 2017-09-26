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

#1. get source info from parameters
SOURCE = arcpy.GetParameterAsText(5)
SRC_DATE = arcpy.GetParameterAsText(6)
SRC_ACCU = arcpy.GetParameterAsText(7)
SRC_SCALE = arcpy.GetParameterAsText(8)
SRC_COORD = arcpy.GetParameterAsText(9)
VERT_ERROR = arcpy.GetParameterAsText(10)
META_MIDF = arcpy.GetParameterAsText(11)

#2. get creation info
MAP_METHOD = arcpy.GetParameterAsText(13)
MAP_MTH_OT = arcpy.GetParameterAsText(14)
BND_TYPE = arcpy.GetParameterAsText(15)
BND_OTHER = arcpy.GetParameterAsText(16)
CREATEDATE = arcpy.GetParameterAsText(17)
EDIT_DATE = arcpy.GetParameterAsText(18)
EDIT_BY = arcpy.GetParameterAsText(19)
ORIGINATOR = arcpy.GetParameterAsText(20)
CONSTRANT = arcpy.GetParameterAsText(21)

#3. get resource info
RESNAME = arcpy.GetParameterAsText(22)
RESTRICT_ = arcpy.GetParameterAsText(23)
CONTRIBRES = arcpy.GetParameterAsText(24)
IS_EXTANT = arcpy.GetParameterAsText(25)
EXTANT_OTH = arcpy.GetParameterAsText(26)
CR_NOTES = arcpy.GetParameterAsText(27)

Program_Collection = arcpy.GetParameterAsText(28)
fclass = arcpy.GetParameterAsText(29)

#4. get CLI info
CLI_ID = arcpy.GetParameterAsText(30)
CLI_NUM = arcpy.GetParameterAsText(31)
LAND_CHAR = arcpy.GetParameterAsText(32)

#5. get location info
ALPHA_CODE = arcpy.GetParameterAsText(33)
UNIT = arcpy.GetParameterAsText(34)
UNIT_CODEO = arcpy.GetParameterAsText(35)
UNIT_OTHER = arcpy.GetParameterAsText(36)
UNIT_TYPE = arcpy.GetParameterAsText(37)
GROUP_CODE = arcpy.GetParameterAsText(38)
REG_CODE = arcpy.GetParameterAsText(39)

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

ImportToScratchGDB(input_fc,target_gdb,clip_fc,var_dict)

