## clitools.general

Contains a set of general functions that are reused many times by tool
scripts or other modules in the clitools package.

If the clitools package is moved to the user's native Python installation,
all of these functions will be available to any python scripting.  Use the
following syntax to import the function:

from clitools.general import <function_name>

To move the clitools package to the Python folder, find your Python
installation folder (e.g. C:\Python27), and then find the 
...\Lib\site-packages directory.  Perform the following actions:

1. Move this clitools folder and all of its contents into the site-packages
directory.
2. From within the clitools folder, move the xlrd and xlwt folders and
their contents into the site-packages folder.

### Functions

##### AskYesOrNo

``AskYesOrNo(question)``

Quick function to standardize the request for a yes or no answer
output is a boolean True or False value, input is a string question.

##### BackupGDB

``BackupGDB(geodatabase, backup_location, comment='')``

Simple function to back up a geodatabase.  Option to add
a comment that will be incorporated into the name, like
'BEFOREGUIDS', etc. The shutil.copy2 function is used on the files
within the geodatabase folder.  No arcpy functions are used.

##### CheckFeatureClassForNulls

``CheckFeatureClassForNulls(feature_class, check_guids=False)``

Checks for NULL values in any of the mandatory NPS CR Spatial
Data Transfer Standards fields.

##### CheckGeodatabaseForNulls

``CheckGeodatabaseForNulls(geodatabase, check_guids=False)``

Checks an entire geodatabase for NULL values in any of the
mandatory NPS CR Spatial Data Transfer Standards fields.  All of the
feature classes in the input geodatabase are expected to contain all
of the fields that will be checked.

##### CheckValuesAgainstDomains

``CheckValuesAgainstDomains(geodatabase)``

This function introspects all of the values in each feature class in
the input geodatabase.  The values in any field that has a domain are
checked against all the values in the domain for that field.  Messages
are printed whenever a value is out of line.

##### ConvertContribStatus

``ConvertContribStatus(input_status)``

Takes an input contributing status from the CLI and converts it to
a value that is supported by the CR Spatial Data Transfer Standards.

##### ExportGDBToShapefiles

``ExportGDBToShapefiles(input_gdb, output_location)``

Exports all feature classes in the input geodatabase to
shapefiles.

##### FieldCalculateRegionCode

``FieldCalculateRegionCode(fc_or_table, field_name)``

Runs the code block for converting long form region names to
the corresponding 3-letter code

##### GetCRLinkAndCRCatalogPath

``GetCRLinkAndCRCatalogPath(geodatabase)``

Returns the paths to the CR Link table and CR Catalog table in the
input geodatabase.  Returns False for a table if it doesn't exist.

##### GetDirPath

``GetDirPath(unit, walk_path)``

Finds the location of a landscape folder within the standardized
directory structure.  Must be provided a regional folder and a CLI
unit number.

##### GetDraftedFeatureCounts

``GetDraftedFeatureCounts(cli_number, cli_ids, gdb_path, exclude_arch=False)``

Iterates through all of the features in a the provided geodatabase,
and returns a count of all cli_ids that are included, a count of how
many are contributing, and a boolean indicating whether or not a
boundary has been created.

##### GetDraftedFeatureCountsScratch

``GetDraftedFeatureCountsScratch(cli_number, cli_ids, scratch_gdb, exclude_arch=False)``

Iterates through all of the features in a scratch geodatabase,
and returns a count of all cli_ids that are included, a count of how
many are contributing, and a boolean indicating whether or not a
boundary has been created.

##### GetParkTypeDictionary

``GetParkTypeDictionary()``

get dictionary of park types from nps_boundary feature class

##### MakeBlankGDB

``MakeBlankGDB(template_path, output_gdb_path)``

creates a blank geodatabase from the input template. If a gdb of the
same name as the desired output already exists, then ascending numbers will
be suffixed as necessary

##### MakeDateAndTimeVar

``MakeDateAndTimeVar()``

Makes the date and time variable formatted just the way you like it.

##### MakePathList

``MakePathList(in_gdb, include_survey_fcs=False)``

Makes list of paths to all feature classes in a gdb (including
those nested in feature class datasets).  By default, Survey feature
classes are excluded, but they may be included if desired.

##### Print

``Print(message, just_arcpy=False)``

This will print the input to the console and also pass the message to
the arcpy.AddMessage() function. If the arcpy parameter is set to False,
the AddMessage() function will not be called.  This is useful because
AddMessage() also prints to the python terminal, though not to the
console.

##### Print3

``Print3(message, log)``

Prints the input message to a log, the shell, and the arcpy.AddMessage()
function.

##### StartLog

``StartLog(level=u'INFO', name='output')``


TakeOutTrash(trash)
Quick little function to delete a dataset if it already exists.
code is:
if arcpy.Exists(trash):
arcpy.management.Delete(trash)

##### TimeDiff

``TimeDiff(start_time)``

Prints out a time differential in seconds.  Provide a start time (as
defined previously by setting a variable to equal time.time()), and that
time will be subtracted from the current time.  The result is printed
and returned.

