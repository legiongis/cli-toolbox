## clitools.enterprise

Contains a set of classes that are used in many clitools functions.
These classes are built to represent each level of broad organizational
entity associated with the CLI progam database.  In ascending order,
1. Landscapes, 2. Parks, and 3. Regions. Each class contains a set of
attributes that can be used to place it within the broader structure of
the park system.

If the clitools package is moved to the user's native Python installation,
all of these functions and classes will be available to any python
scripting, or in the Python shell. Here is an example of using the landscape
class:

from clitools.classes import MakeUnit

landscape = MakeUnit("500003")
print landscape.name
>> Port Oneida Historic District
print landscape.park[0]
>> SLBE
print landscape.GetFeatureList()
>> [list of all cli_ids...]

To move the clitools package to the Python folder, find your Python
installation folder (e.g. C:\Python27), and then find the 
...\Lib\site-packages directory.  Perform the following actions:

1. Move this clitools folder and all of its contents into the site-packages
directory.
2. From within the clitools folder, move the xlrd and xlwt folders and
their contents into the site-packages folder.

### Functions

##### CheckForEnterpriseTables

``CheckForEnterpriseTables(map_document)``

Check the input map document for the three tables that are necessary
for exporting or analyzing data in the CR Enterprise:
CLI Feature Table, CR Link Table, and CR Catalog Table

Returns False if one of the three is missing from table of contents.

##### ConvertFeatureXLSToGDBTable

``ConvertFeatureXLSToGDBTable(input_xls, retain_copy=False, update_local=False)``

Takes an excel workbook that has been created using the "Updating
the CLI Feature Table" guide that is included in the CLI toolbox
documentation. The values from the excel sheet will be read and
written to a new table in a new file geodatabase.

This process is designed to ensure easy and clean updates to the CLI
Feature Table that is served through the NPS CR Enterprise
database. The intention is that the resulting file geodatabase table
can be sent to a regional data editor who will not need to do any QA/QC
before using it to replace the existing CLI Feature Table in the NPS CR
Enterprise database.

##### ExtractFromEnterpriseQuery

``ExtractFromEnterpriseQuery(map_document, query_code, output_location, only_cr_link=False, transform=False, trans_type='NAD_1983_To_WGS_1984_1')``

This function must be used from the CR Enterprise Access map
document.  It will take the input query code and extract all data that
matches it from each layer in the table of contents.  The user may only
download the CR Link table for these records, if desired.

##### ExtractFromEnterpriseSelection

``ExtractFromEnterpriseSelection(map_document, output_location, only_cr_link=False, transform=False, trans_type='NAD_1983_To_WGS_1984_1')``

This function must be used from the CR Enterprise Access map
document.  Any currently selected features are downloaded to a new
geodatabase.  The user can chose to only download the CR Link table
records for all selected features.

##### GetTableFieldsList

``GetTableFieldsList(template_table)``

Returns a dictionary of field names and lengths that can be iterated
to create a new GDB table

##### InspectMXD

``InspectMXD(map_document)``

logs the names and fields of all layers and table views in the mxd

##### MakeLocalTablesFromCLIFeatureTable

``MakeLocalTablesFromCLIFeatureTable(table_geodatabase)``

This function will look in the input table geodatabase for a table
called CLIFeatureTable, which should be created by any function that
includes this function.  From that table, new versions of the
FeatureLookupTable and UnitLookupTable are created to replace the old
versions of those tables, using queries on the LAND_CHAR field.

##### UpdateCLITables

``UpdateCLITables(map_document)``

This tool takes no parameters.  It must be run from the CR Enterprise
Access map document.  It uses the table view in the map document
of the CLI Feature Table to pull information to the local lookup tables
that are used in all of these functions throughout the clitools package.
This tool should be run by the user every time the CR Enterprise
version of the CLI Feature Table is updated.

