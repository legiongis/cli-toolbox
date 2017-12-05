### APPENDIX A: Glossary of Selected GIS Terminology


**attribute table:** The table of attributes, or field values, that are attached to the features in a spatial dataset.

**ArcCatalog:** The ArcGIS software used to browse and manage spatial datasets.

**ArcGIS:** A suite of software developed by Environmental Systems Research Institute (ESRI) for creating, analyzing, and managing spatial data.

**ArcMap:** The ArcGIS software used to create and edit map documents.

**data frame:** A container within a map document that can contain many layers, which represent spatial datasets.

**dataset/spatial dataset:** General term for a collection of spatial data, like a feature class or a shapefile. In ArcGIS, a spatial dataset contains a collection of spatial features that all have the same geometry type. A spatial dataset is a combination of geometry (the coordinates for each feature) and attributes which are stored in the attribute table and associated with each geometry.

**definition query:** A definition query may be applied to a layer in order to reduce the layer to only a subset of its original features. For example, the definition query “LAND_CHAR” = ‘Vegetation’ will show only features whose LAND_CHAR field value is ‘Vegetation’.

**geometry:** The set of coordinates attached to each feature in a spatial dataset. In ArcGIS, there are many different types of geometry, but in the NPS Spatial Data Transfer Standards, only point, line, and polygon geometry types are used.

**feature:** Generally, “feature” refers to a single piece of spatial data—a point or polygon for example. However, throughout the documentation, cultural resources that are listed in the CLI are also referred to as “features”, or “CLI features”.

**feature class:** In more general GIS contexts, any collection of spatial data (or features) is considered a feature class. However, throughout this documentation, feature class refers specifically to a spatial dataset that is stored in a file geodatabase.

**feature class dataset:** This is a somewhat confusing term for a grouping of feature classes inside of a geodatabase. The CLI Standard geodatabase contains a feature class dataset for each cultural resource type, inside of which is a feature class for each acceptable geometry type (point, line, or polygon).

**field:**  A column in any table, either an attribute table for a spatial dataset, or a non-spatial table such as the CR Link.

**field value:**  Used to refer to a value for a feature that is stored in the attribute table, synonymous with “attribute”.

**geodatabase:** There are two types of geodatabase, file geodatabases (*.gdb) and personal (*.mdb). Throughout the entire documentation and CLI Toolbox, only file geodatabases are used, so any reference to a geodatabase should be interpreted thusly. Viewed in Windows, a file geodatabase is a folder whose name ends with “.gdb” (inside of which are many tiny, nonsense files), and a personal geodatabase is an MS Access database.

**GUID:** A Globally Unique Identifier (GUID) is a long string of characters and numbers that is unique within a given database. In the CR Spatial Data Transfer Standards, GUIDs are used as cultural resource IDs (`CR_ID`) and geometry IDs (`GEOM_ID`).

**layer:** In this document, the term layer is reserved to mean a visual representation of a spatial dataset, such as a feature class or a shapefile. Layers exist in data frames within a map document, or can be saved to a \*.lyr file.

**map document:** A document that is used to display, edit, and analyze spatial data.

**parameter:** A parameter is a value that is passed to a function. In the CLI Toolbox, each tool dialog is a list of parameters that the user enters to guide the process that the tool is about to carry out.

**program ID:** All other IDs for various cultural resource database, like the List of Classified Structures and the National Register, are referred to generally as program IDs through this documentation. Also, even though the facilities management system is not technically a cultural resource database, FMSS IDs are considered program IDs as well.

**Python:** An open-source programming language that is well-integrated into ArcGIS software, and can carry out tasks beyond ArcGIS as well. All of the code for the tools is written in Python, version 2.7.

**shapefile:** A shapefile is a common spatial data format. It is analogous to a feature class, but a feature class exists only within a geodatabase. Technically, a shapefile is a collection of three to seven files that work together. In ArcMap or ArcCatalog, a shapefile will have the extension “.shp”.

**spatial data:** This is a general term for data that has a spatial component, e.g. coordinates or relational geometry.

**tool:** A tool is really two components: a dialog box into which the user will enter parameters, and the script behind it which takes the input parameters to carry out various operations.

**toolbox:** A collection of tools and/or toolsets.

**toolset:** A subset of tools within a toolbox, a purely organizational grouping.
