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
settings['log-level'] = arcpy.GetParameterAsText(4)
settings['default-edit-by'] = arcpy.GetParameterAsText(5)
settings['default-map-method'] = arcpy.GetParameterAsText(6)
settings['default-originator'] = arcpy.GetParameterAsText(7)
settings['default-constraint'] = arcpy.GetParameterAsText(8)
settings['default-program-collection'] = arcpy.GetParameterAsText(9).rstrip()
settings['trans-nad83-wgs84'] =  arcpy.GetParameterAsText(10)
settings['trans-nad27-wgs84'] =  arcpy.GetParameterAsText(11)

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
            raise Exception("Invalid directory path: {}\n  operation cancelled.".format(d))
        
settings_file = os.path.join(settings['toolbox-location'],"scripts","clitools","config","settings.json")

with open(settings_file, "wb") as out:
    json.dump(settings,out,indent=2)
