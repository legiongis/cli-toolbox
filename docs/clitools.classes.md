## clitools.classes

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

### Classes

##### __builtin__.object

``__builtin__.object``

Landscape
Park
Region

##### class Landscape

``class Landscape(__builtin__.object)``

|  This object holds infomation about a Cultural Landscape Inventory
|  (CLI) unit.  The input for instantiation is the 6-digit CLI code for
|  that landscape unit.  Various properties of the landscape, like its
|  name, park location, feature list, etc. are set as immutable attributes.
|
|  Methods defined here:
|
|  GetFeatureDict(self)
|      This method creates a cursor on the master table using the query
|      for this landscape, and returns a comprehensive dictionary of
|      feature info for all features.  The format of the output dictionary:
|
|      {CLI_ID:["RESNAME","CONTRIB_STATUS",
|              "LAND_CHAR","CLI_NUM","LCS_ID","HS_ID"]
|
|  GetFeatureList(self)
|      This method creates a cursor on the master table using the query
|      for this landscape, and returns a list of CLI_IDs for all features
|      in the landscape.  The list of CLI_IDs is ordered first by Landscape
|      Characteristic and then by Resource Name.
|
|  __delattr__(self, *args)
|      Override __delattr__ to prevent attributes of this class from
|      being deleted.
|
|  __init__(self, in_code)
|
|  __setattr__(self, *args)
|      Override __setattr__ to prevent attributes of this class from
|      being changed.
|
|  ----------------------------------------------------------------------
|  Data descriptors defined here:
|
|  __dict__
|      dictionary for instance variables (if defined)
|
|  __weakref__
|      list of weak references to the object (if defined)

class Park(__builtin__.object)
|  This object holds information about a park that relates to the
|  cultural landscapes units within it.  Various properties of the park,
|  like its name, list of landscapes within it, etc. are set as immutable
|  attributes.
|
|  Methods defined here:
|
|  __delattr__(self, *args)
|      Override __delattr__ to prevent attributes of this class from
|      being deleted.
|
|  __init__(self, in_code)
|
|  __setattr__(self, *args)
|      Override __setattr__ to prevent attributes of this class from
|      being changed.
|
|  ----------------------------------------------------------------------
|  Data descriptors defined here:
|
|  __dict__
|      dictionary for instance variables (if defined)
|
|  __weakref__
|      list of weak references to the object (if defined)

class Region(__builtin__.object)
|  This object holds information about an NPS region pertaining to
|  the cultural landscapes and parks within it. The input for instantiation
|  is the 3-letter region code.  Various properties of the region, like its
|  name, the parks and landscapes it contains, etc. are set as immutable
|  attributes.
|
|  Methods defined here:
|
|  __delattr__(self, *args)
|      Override __delattr__ to prevent attributes of this class from
|      being deleted.
|
|  __init__(self, in_code)
|
|  __setattr__(self, *args)
|      Override __setattr__ to prevent attributes of this class from
|      being changed.
|
|  ----------------------------------------------------------------------
|  Data descriptors defined here:
|
|  __dict__
|      dictionary for instance variables (if defined)
|
|  __weakref__
|      list of weak references to the object (if defined)

### Functions

##### AllCLINumbers

``AllCLINumbers()``

This function returns a list of all the cli numbers that are in the
master table

##### AllGoodInputs

``AllGoodInputs()``

This function returns a list of all the valid alpha, landscape and
region codes, mainly used as a list to check input against if necessary

##### MakeUnit

``MakeUnit(user_input)``

This function will take any input code and attempt to make a landscape,
park, or region unit out of it.  It returns False if the input is not
a valid park, cli, or region code.  Suggested use for this function in
an interactive script setting:

choice = raw_input(">> ")
while MakeUnit(choice) == False:
choice = raw_input(">> ")
unit = MakeUnit(choice)
print unit.name

The result will be a constant stream of input opportunities until the
user puts in a valid code.  No exceptions will be triggered in this
usage.

