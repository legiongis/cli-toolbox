import sys
if sys.version_info[:2] != (2, 7):
    arcpy.AddError("Sorry, clitools requires Python 2.7 and ArcGIS Desktop 10.1/10.2 (possibly 10.3)")
    print >> sys.stderr, "Sorry, clitools requires Python 2.7 and ArcGIS Desktop 10.1/10.2 (possibly 10.3)"
    sys.exit(1)

__version__ = (1, 0)
