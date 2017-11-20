APPENDIX B: Full List of CLI tools (with page references)
The following is a full list of all the tools in the CLI Toolbox and short description of each. Also, page number references are given for the tools that are described elsewhere in this document. See each tool’s Item Description and embedded help for more detailed information.
CR Enterprise Access:
• Feature Table Update > Prepare CLI Table for Data Editor (p.7)
 After following the instructions in ‘Updating the CLI Feature Table’, use this tool to convert the resulting MS Excel workbook into a geodatabase table whose rows can be used to replace the CLI Feature Table on the CR Enterprise.
• Feature Table Update > Update Local CLI Tables (p. 7)
 Updates local toolbox tables using the CLI Feature Table that is stored in the CR Enterprise Database. Must be used from the CR Enterprise Access map document.
• Extract Data From CR Enterprise (pp. 29-30)
 Export data from the CR Enterprise database. Must be used from the CR Enterprise Access map document.
• Summarize CLI Data In Enterprise (p. 28)
 Creates a spreadsheet summary of the features that have GIS data for a given landscape, park, or region. Must be used from the CR Enterprise Access map document.
Editing Tools
• Spatial Reference > Set To GCS NAD83 (p. 12)
 Sets the active data frame coordinate system to a geographic coordinate system using North American Datum 1983.
• Spatial Reference > Set To State Plane (NAD83) (p. 12)
 Uses the current extent of the active data frame to find the appropriate State Plane zone, and sets the data frame coordinate system to that projected coordinate system, using North American Datum 1983 (NAD83).
• Spatial Reference > Set To UTM (NAD83) (p. 12)
 Uses the current extent of the active data frame to find the appropriate UTM (Universal Transverse Mercator) zone, and sets the data frame coordinate system to that projected coordinate system, using North American Datum 1983 (NAD83).
• Excel File From Features
 Converts rows in the attribute table for currently selected features in a given layer into an MS Excel workbook (*.xls).
- 34 -
• Generate Centroids (p. 13, 17)
 Takes the input polygon or polyline features, creates a centroid for each one, and appends the centroid to the appropriate point feature class.
• Update Fields in Selected Records (pp. 14-15, 17)
 Batch populate fields in all currently selected features
• Zoom To Unit (p. 13, 17)
 Enter a CLI number, Alpha Code, or Region Code and zoom to features that match the code.
Review Tools
• Display Geodatabase (p. 23)
 Choose from a number of predefined symbology schemes to display a CLI Standards or Scratch geodatabase.
• Excel File Multiple Landscapes (p. 27)
 Create a summary spreadsheet showing feature progress percentages for multiple landscapes.
• Excel File Single Landscape (p. 25)
 Create a summary spreadsheet showing progress for all features in a single landscape.
• Make Google Earth File (p. 25)
 Convert the spatial data in a geodatabase into a Google Earth file (*.kmz) using the symbology schemes available in the Display Geodatabase tool.
Scratch GDB
• Create New Project Folder (pp. 6, 10)
 Create a new project folder for a landscape. New folder contains scratch geodatabase and blank map document setup for data import, creation, and editing.
• Import To Scratch GDB (p. 11)
 Import an existing spatial dataset (shapefile, feature class, etc.) into a geodatabase, and prepare it for NPS Spatial Data Transfer Standards fields.
• Sort Scratch Into Standards (p. 12, 16-17)
 Sort multiple feature classes from a Scratch geodatabase into a CLI Standards geodatabase.
Standards GDB
• Maintenance > Check Mandatory Fields (p. 17-18)
 Checks for Null or empty (“”) values in all of the NPS Spatial Data Transfer Standards fields in a geodatabase.
- 35 -
• Maintenance > Check Values Against Domains (pp. 17, 19)
 For any field with a domain assigned, checks all values in that field against the values in its assigned domain.
• Maintenance > Create GUIDs (pp. 17, 19, 21)
 Create Globally Unique Identifiers (GUIDs) for features in a CLI Standards geodatabase.
• Maintenance > Fix Field in GDB (pp. 17, 20-22)
 Change all occurrences of a given value in a given field across all feature classes in a geodatabase.
• Maintenance > Sync CR Link and Catalog Tables (pp. 18-19)
 Synchronizes the CR Link and CR Catalog tables in a CLI Standards geodatabase.
• Management > Backup GDB
 Quickly copy a geodatabase to a backup location.
• Management > Copy Standards GDB To WGS84
 Make a copy of a CLI Standards geodatabase with all feature classes projected to a geographic coordinate system using datum World Geodetic System 1984 (WGS84).
• Management > Create Subset of Standards GDB
 Export a subset geodatabase from a larger geodatabase.
• Management > Export GDB To Shapefiles
 Converts all feature classes in a geodatabase into shapefiles.
• Management > Merge CR Link Tables
 Merge one CR Link table into another.
• Management > Merge Standards GDBs (p. 17)
 Merge one CLI Standards geodatabase into another.