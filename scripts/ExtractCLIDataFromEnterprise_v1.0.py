# ---------------------------------------------------------------------------
# Title: ExtractCLIDataFromEnterprise_v1.0.py
# Version: 1.0
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the two extract functions 
#    that are made to access the CR Enterprise database, and are held in the 
#    clitools.management module.
# ---------------------------------------------------------------------------

import arcpy
import os
from clitools.enterprise import ExtractFromEnterpriseSelection
from clitools.enterprise import ExtractFromEnterpriseQuery
from clitools.general import StartLog

## start logging messages now
start = datetime.now()
log = StartLog(level="DEBUG",name="ExtractCLIDataFromEnterprise")
log.debug("starting extract")

"""this is a shell script that takes the arguments from the ArcMap tool
dialog and passes them to the function in the clitools.management module."""

extract_method = arcpy.GetParameterAsText(0)
in_code = arcpy.GetParameterAsText(1)
output_location = arcpy.GetParameterAsText(2)
only_link = arcpy.GetParameter(3)
trans = arcpy.GetParameter(4)
trans_type = arcpy.GetParameterAsText(5)

try:
    mxd = arcpy.mapping.MapDocument("CURRENT")
except:
    errmsg = "This tool must be run from ArcMap, "\
            "using the CR Enterprise Access document that is included "\
            "in this toolbox folder."
    arcpy.AddError(errmsg)
    log.error(errmsg)

if len(in_code) == 3:
    query_code = in_code.upper()
elif len(in_code) == 4:
    query_code = in_code.upper()
elif len(in_code) == 6:
    query_code = in_code
else:
    query_code = False

log.debug("extract method: "+extract_method)
log.debug("query_code: "+str(query_code))

if extract_method == "unit code" and not query_code == False:
    ExtractFromEnterpriseQuery(mxd,query_code,output_location,only_link,trans,trans_type)
elif extract_method == "selected features":
    ExtractFromEnterpriseSelection(mxd,output_location,only_link,trans,trans_type)
else:
    arcpy.AddError("\nInvalid query code.\n")

log.debug("completed extract {}".format(datetime.now()-start))