import os
import json
import arcpy

from clitools.config import settings
if not settings:
    settings = {}

settings['toolbox-location'] = arcpy.GetParameterAsText(0)
settings['cli-gis-directory'] = arcpy.GetParameterAsText(1)
settings['cache'] = arcpy.GetParameterAsText(2)
settings['log-dir'] = arcpy.GetParameterAsText(3)
settings['default-edit-by'] = arcpy.GetParameterAsText(4)
settings['default-map-method'] = arcpy.GetParameterAsText(5)
settings['default-originator'] = arcpy.GetParameterAsText(6)
settings['default-constraint'] = arcpy.GetParameterAsText(7)
settings['default-program-collection'] = arcpy.GetParameterAsText(8).rstrip()
settings['trans-nad83-wsg84'] =  arcpy.GetParameterAsText(9)
settings['trans-nad27-wsg84'] =  arcpy.GetParameterAsText(10)

dirs = (
    settings['cli-gis-directory'],
    settings['cache'],
    settings['log-dir']
)

for d in dirs:
    if not os.path.isdir(d):
        try:
            os.makedirs(d)
        except WindowsError:
            raise Exception("Invalid CLI GIS Directory path, operation cancelled.")
        
settings_file = os.path.join(settings['toolbox-location'],"scripts","clitools","config","settings.json")

with open(settings_file, "wb") as out:
    json.dump(settings,out,indent=2)
