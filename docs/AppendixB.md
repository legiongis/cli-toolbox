### _APPENDIX B: Full List of CLI tools (with page references)_

The following is a full list of all the tools in the CLI Toolbox and short description of each. Also, page number references are given for the tools that are described elsewhere in this document. See each tool’s Item Description and embedded help for more detailed information.


CR Enterprise Access:

  - *Feature Table Update* > **_Prepare CLI Table for Data Editor_** **(p.7)**
      - After following the instructions in ‘Updating the CLI Feature Table’, use this tool to convert the resulting MS Excel workbook into a geodatabase table whose rows can be used to replace the CLI Feature Table on the CR Enterprise.
      
  - *Feature Table Update* > **_Update Local CLI Tables_** **(p. 7)**
     - Updates local toolbox tables using the CLI Feature Table that is stored in the CR Enterprise Database. Must be used from the CR Enterprise Access map document.
     
  - **_Extract Data From CR Enterprise_** **(pp. 29-30)**
     - Export data from the CR Enterprise database. Must be used from the CR Enterprise Access map document.
     
  - **_Summarize CLI Data In Enterprise_** **(p. 28)**
     - Creates a spreadsheet summary of the features that have GIS data for a given landscape, park, or region. Must be used from the CR Enterprise Access map document.


Editing Tools

  - *Spatial Reference* > **_Set To GCS NAD83_** **(p. 12)**
     - Sets the active data frame coordinate system to a geographic coordinate system using North American Datum 1983.
     
  - *Spatial Reference* > **_Set To State Plane (NAD83)_** **(p. 12)**
     - Uses the current extent of the active data frame to find the appropriate State Plane zone, and sets the data frame coordinate system to that projected coordinate system, using North American Datum 1983 (NAD83).
     
  - *Spatial Reference* > **_Set To UTM (NAD83)_** **(p. 12)**
     - Uses the current extent of the active data frame to find the appropriate UTM (Universal Transverse Mercator) zone, and sets the data frame coordinate system to that projected coordinate system, using North American Datum 1983 (NAD83).
     
  - **_Excel File From Features_**
     - Converts rows in the attribute table for currently selected features in a given layer into an MS Excel workbook (\*.xls).

  - **_Generate Centroids_** **(p. 13, 17)**
     - Takes the input polygon or polyline features, creates a centroid for each one, and appends the centroid to the appropriate point feature class.
     
  - **_Update Fields in Selected Records_** **(pp. 14-15, 17)**
     - Batch populate fields in all currently selected features
     
  - **_Zoom To Unit_** **(p. 13, 17)**
     - Enter a CLI number, Alpha Code, or Region Code and zoom to features that match the code.

   
Review Tools

  - **_Display Geodatabase_** **(p. 23)**
     - Choose from a number of predefined symbology schemes to display a CLI Standards or Scratch geodatabase.
     
  - **_Excel File Multiple Landscapes_** **(p. 27)**
     - Create a summary spreadsheet showing feature progress percentages for multiple landscapes.
     
  - **_Excel File Single Landscape_** **(p. 25)**
     - Create a summary spreadsheet showing progress for all features in a single landscape.
     
  - **_Make Google Earth File_** **(p. 25)**
     - Convert the spatial data in a geodatabase into a Google Earth file (\*.kmz) using the symbology schemes available in the Display Geodatabase tool.

  
Scratch GDB

  - **_Create New Project Folder_** **(pp. 6, 10)**
     - Create a new project folder for a landscape. New folder contains scratch geodatabase and blank map document setup for data import, creation, and editing.
     
  - **_Import To Scratch GDB_** **(p. 11)**
     - Import an existing spatial dataset (shapefile, feature class, etc.) into a geodatabase, and prepare it for NPS Spatial Data Transfer Standards fields.
     
  - **_Sort Scratch Into Standards_** **(p. 12, 16-17)**
     - Sort multiple feature classes from a Scratch geodatabase into a CLI Standards geodatabase.

   
Standards GDB

  - _Maintenance_ > **_Check Mandatory Fields_** **(p. 17-18)**
     - Checks for Null or empty (“”) values in all of the NPS Spatial Data Transfer Standards fields in a geodatabase.

  - _Maintenance_ > **_Check Values Against Domains_** **(pp. 17, 19)**
     - For any field with a domain assigned, checks all values in that field against the values in its assigned domain.
     
  - *Maintenance* > **_Create GUIDs_** **(pp. 17, 19, 21)**
     - Create Globally Unique Identifiers (GUIDs) for features in a CLI Standards geodatabase.
     
  - _Maintenance_ > **_Fix Field in GDB_** **(pp. 17, 20-22)**
     - Change all occurrences of a given value in a given field across all feature classes in a geodatabase.
     
  - _Maintenance_ > **_Sync CR Link and Catalog Tables_** **(pp. 18-19)**
     - Synchronizes the CR Link and CR Catalog tables in a CLI Standards geodatabase.
     
  - _Management_ > **_Backup GDB_**
     - Quickly copy a geodatabase to a backup location.
     
  - _Management_ > **_Copy Standards GDB To WGS84_**
     - Make a copy of a CLI Standards geodatabase with all feature classes projected to a geographic coordinate system using datum World Geodetic System 1984 (WGS84).
     
  - _Management_ > **_Create Subset of Standards GDB_**
     - Export a subset geodatabase from a larger geodatabase.
     
  - _Management_ > **_Export GDB To Shapefiles_**
     - Converts all feature classes in a geodatabase into shapefiles.
     
  - _Management_ > **_Merge CR Link Tables_**
     - Merge one CR Link table into another.
     
  - _Management_ > **_Merge Standards GDBs_** **(p. 17)**
     - Merge one CLI Standards geodatabase into another.
