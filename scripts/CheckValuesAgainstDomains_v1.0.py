# ---------------------------------------------------------------------------
# Title: CheckValuesAgainstDomains_v1.0.py
# Version: 1.0
# Created by Adam Cox
#   
# Description:  This is the shell script used to translate the input  
#    parameters from the tool dialogue into appropriate input for the
#    CheckValuesAgainstDomains function that is held in the clitools.general
# 	 module.
# ---------------------------------------------------------------------------

import arcpy
import os

from clitools.general import CheckValuesAgainstDomains

gdb = arcpy.GetParameterAsText(0)

CheckValuesAgainstDomains(gdb)
                
        
        
    

    
