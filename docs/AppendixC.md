### _APPENDIX C: Using CLI Tools Outside of CLI Data_

A number of the tools in this toolbox can be used outside of any CLI data/functions that the toolbox was initially designed for. Below are examples of some such uses. Please note that here, as in the rest of this document, “geodatabase” refers to an ESRI file geodatabase (\*.gdb), not a personal geodatabase (\*.mdb). Many of the tools below *may* work on personal geodatabases, but that has not been tested at all.

<p align= "center">ACCESSING THE CR ENTERPRISE DATABASE</p>

**_Extract Data From Enterprise:_**
Though this tool is designed to support the download of CLI-specific data from the CR Enterprise database, the user can also download non-CLI-specific data by choosing to download selected features and selecting arbitrary features from anywhere in the CR Enterprise. A user could download all features that fall within a given state or city boundary, for example.

<p align= "center">SPECIFICALLY SUPPORTING THE NPS CR SPATIAL DATA TRANSFER STANDARDS</p>

**_Check Mandatory Fields:_**
Creates a summary of all Null or empty (“”) values that occur in any of the NPS CR Spatial Data Transfer Standards required fields. Analyzes all feature classes in a geodatabase.
     
**_Import to Scratch GDB:_**
The input dataset can be placed into any geodatabase, and its new copy will be augmented with all of the NPS CR Spatial Data Transfer Standards fields, with the option to prepopulate each one. Use this tool for general conversion of a feature class or shapefile to a feature class version that is compliant with the NPS CR Spatial Data Transfer Standards.

<p align= "center">SUPPORTING GENERAL OPERATIONS IN ANY ENVIRONMENT</p>

**_Backup GDB:_**
Backs up any geodatabase, even during an open edit session (unsaved edits will not be reflected in the backup copy). Best used with a default backup location set in the tool parameter properties. (Definitely won’t work on a personal geodatabase.)

**_Check Values Against Domains:_**
Checks the values of all fields that have a domain assigned against the values in that domain. Works on any geodatabase.

**_Excel File From Features:_**
Used in ArcMap, will create an MS Excel workbook out of the selected features in any input layer. Should work anywhere there is a layer with a selection applied to it.

**_Export GDB to Shapefiles:_**
Exports all feature classes from an input geodatabase to separate shapefiles in the output folder. Works on any geodatabase.

**_Fix Field in GDB:_**
Allows user to change a set of values that occur in a specific field in all feature classes to a new value. Works on any geodatabase.

**_Spatial Reference Tools:_**
All of the tools in the Editing > Spatial Reference toolset will work for any map document. They must be used in data view.
