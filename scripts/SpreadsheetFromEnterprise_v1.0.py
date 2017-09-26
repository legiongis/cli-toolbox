# ---------------------------------------------------------------------------
# Title: SpreadsheetFromEnterprise_v1.0.py
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input parameters 
#    from the tool dialogue into appropriate input for the two functions in the
#	 summarize module that will create spreadsheets from the data in the CR
#	 Enterprise database.
# ---------------------------------------------------------------------------

import arcpy
import os
from clitools.summarize import CREnterpriseSingleXLS,CREnterpriseMultipleXLS

sum_type = arcpy.GetParameterAsText(0)
cli_code = arcpy.GetParameterAsText(1)
other_code = arcpy.GetParameterAsText(2)
out_dir = arcpy.GetParameterAsText(3)

mxd = arcpy.mapping.MapDocument("CURRENT")

if sum_type == "Single Landscape":
    path = CREnterpriseSingleXLS(mxd,cli_code,out_dir)
elif sum_type == "Multiple Landscapes":
    path = CREnterpriseMultipleXLS(mxd,other_code,out_dir)
else:
    pass
    
if path:
    os.startfile(path)
