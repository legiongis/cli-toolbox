import os
import json
import arcpy

try:
    from clitools.config import settings
except:
    settings = {}

settings['toolbox-location'] = arcpy.GetParameterAsText(0)
settings['cli-gis-directory'] = arcpy.GetParameterAsText(1)
settings['cache'] = arcpy.GetParameterAsText(2)
settings['default-edit-by'] = arcpy.GetParameterAsText(3)
settings['default-map-method'] = arcpy.GetParameterAsText(4)
settings['default-originator'] = arcpy.GetParameterAsText(5)
settings['default-constraint'] = arcpy.GetParameterAsText(6)
settings['default-program-collection'] = arcpy.GetParameterAsText(7)
settings['trans-nad27-wsg84'] =  arcpy.GetParameterAsText(8)
settings['trans-nad83-wsg84'] =  arcpy.GetParameterAsText(9)

if not os.path.isdir(settings['cli-gis-directory']):
    try:
        os.makedirs(settings['cli-gis-directory'])
    except:
        raise Exception("Invalid CLI GIS Directory path, operation cancelled.")
        
if not os.path.isdir(settings['cache']):
    try:
        os.makedirs(settings['cache'])
    except:
        pass

settings_file = os.path.join(settings['toolbox-location'],"scripts","clitools","config","settings.json")

with open(settings_file, "wb") as out:
    json.dump(settings,out,indent=2)
