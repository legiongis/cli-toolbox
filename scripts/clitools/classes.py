__doc__ = \
"""Contains a set of classes that are used in many clitools functions.
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
"""

import arcpy
from general import TakeOutTrash
from .config import settings
from paths import FeatureLookupTable
from paths import UnitLookupTable


#small dictionary for region codes and names
region_dict = {
    "AKR":"Alaska Region",
    "IMR":"Intermountain Region",
    "MWR":"Midwest Region",
    "NCR":"National Capital Region",
    "NER":"Northeast Region",
    "PWR":"Pacific West Region",
    "SER":"Southeast Region"
    }

#create reference dictionaries from tables
alpha_and_region_dict = {}
alpha_and_name_dict = {}
cli_num_and_alpha_dict = {}
cli_num_and_region_dict = {}
cli_num_and_name_dict = {}

## new cursor operation (using arcpy.da.SearchCursor)
fields = ["ALPHA_CODE","REGION_NAME","PARK_NAME","CLI_NUM","CLI_NAME"]
sql_clause = (None,"ORDER BY ALPHA_CODE, CLI_NUM")

## use try/except statements in case the sql_clause argument makes trouble
try:
    rows = arcpy.da.SearchCursor(UnitLookupTable,fields,sql_clause=sql_clause)
except:
    rows = arcpy.da.SearchCursor(UnitLookupTable,fields)

for row in rows:
    alpha = row[0]
    region_code = row[1]
    park_name = row[2]
    cli_num = row[3]
    cli_name = row[4].encode('ascii','ignore')

    try:
        alpha_and_region_dict[alpha]
    except KeyError:
        alpha_and_region_dict[alpha] = region_code

    try:
        alpha_and_name_dict[alpha]
    except KeyError:
        alpha_and_name_dict[alpha] = park_name

    try:
        cli_num_and_alpha_dict[cli_num]
    except KeyError:
        cli_num_and_alpha_dict[cli_num] = alpha

    try:
        cli_num_and_region_dict[cli_num]
    except KeyError:
        cli_num_and_region_dict[cli_num] = region_code

    try:
        cli_num_and_name_dict[cli_num]
    except KeyError:
        cli_num_and_name_dict[cli_num] = cli_name

del rows, row

print "regions: {}".format(len(region_dict))
print "parks: {}".format(len(alpha_and_region_dict))
print "landscapes: {}".format(len(cli_num_and_name_dict))


class Landscape(object):
    """This object holds infomation about a Cultural Landscape Inventory
    (CLI) unit.  The input for instantiation is the 6-digit CLI code for
    that landscape unit.  Various properties of the landscape, like its
    name, park location, feature list, etc. are set as immutable attributes.
    """
    def __setattr__(self, *args):
        """Override __setattr__ to prevent attributes of this class from
        being changed."""
        raise AttributeError("Attributes of the %s class cannot be "
                             "changed" % type(self).__name__)
    def __delattr__(self, *args):
        """Override __delattr__ to prevent attributes of this class from
        being deleted."""
        raise AttributeError("Attributes of the %s class cannot be "
                             "deleted" % type(self).__name__)
    def __init__(self,in_code):

        in_code = str(in_code)

        if not in_code in cli_num_and_alpha_dict.keys():
            raise ValueError
        
        object.__setattr__(self, "type", "landscape")
        object.__setattr__(self, "code", in_code)
        object.__setattr__(self, "name", cli_num_and_name_dict[in_code])

        a = cli_num_and_alpha_dict[in_code]
        object.__setattr__(self, "park", (a,alpha_and_name_dict[a]))
        r = cli_num_and_region_dict[in_code]

        object.__setattr__(self, "region", (r,region_dict[r]))
        object.__setattr__(self, "query", ('"CLI_NUM" = \'{0}\''.format(
            in_code)))

    def GetFeatureList(self):
        '''This method creates a cursor on the master table using the query
        for this landscape, and returns a list of CLI_IDs for all features 
        in the landscape.  The list of CLI_IDs is ordered first by Landscape
        Characteristic and then by Resource Name.'''

        #table_query = '"CLI_NUM" = \'' + self.code + "'"
        table_query = self.query

        ## new cursor operation (using arcpy.da.SearchCursor)
        feat_fields = [
            "CLI_ID","REGION_NAME","ALPHA_CODE","LAND_CHAR","RESNAME"]
        tv = "tv"
        TakeOutTrash(tv)
        arcpy.management.MakeTableView(FeatureLookupTable,tv,table_query)
        if int(arcpy.management.GetCount(tv).getOutput(0)) == 0:
            return []
        sql = (None, "ORDER BY REGION_NAME,ALPHA_CODE,LAND_CHAR,RESNAME")
        
        ## use try/except statements in case the sql_clause argument makes trouble
        try:
            rows = arcpy.da.SearchCursor(tv,feat_fields,sql_clause=sql)
            arcpy.AddMessage("~~feature list is sorted~~")
        except:
            rows = arcpy.da.SearchCursor(tv,feat_fields)
            arcpy.AddMessage("~~feature list is not sorted~~")

        f_sort_list = [row[0] for row in rows]
        del rows, row

        return f_sort_list

    def GetFeatureDict(self):
        '''This method creates a cursor on the master table using the query
        for this landscape, and returns a comprehensive dictionary of
        feature info for all features.  The format of the output dictionary:

        {CLI_ID:["RESNAME","CONTRIB_STATUS",
                "LAND_CHAR","CLI_NUM","LCS_ID","HS_ID"]'''

        #table_query = '"CLI_NUM" = \'' + self.code + "'"
        table_query = self.query

        ## new cursor operation (using arcpy.da.SearchCursor)
        f_dict = {}
        feat_fields = ["RESNAME","CONTRIB_STATUS","LAND_CHAR",
            "CLI_NUM","LCS_ID","HS_ID","CLI_ID","REGION_NAME","ALPHA_CODE"]
        for f in feat_fields:
            if not f in [i.name for i in arcpy.ListFields(FeatureLookupTable)]:
                print "error: " + f
        sql = (None, "ORDER BY REGION_NAME,ALPHA_CODE,LAND_CHAR,RESNAME")

        ## use try/except statements in case the sql_clause argument makes trouble
        try:
            rows = arcpy.da.SearchCursor(FeatureLookupTable,feat_fields,table_query,
            sql_clause=sql)
            arcpy.AddMessage("~~feature dictionary is sorted~~")
        except:
            rows = arcpy.da.SearchCursor(FeatureLookupTable,feat_fields,table_query)
            arcpy.AddMessage("~~feature dictionary is not sorted~~")

        for row in rows:
            f_dict[row[6]] = [row[i] for i in range(6)]

        return f_dict

class Park(object):
    """This object holds information about a park that relates to the
    cultural landscapes units within it.  Various properties of the park,
    like its name, list of landscapes within it, etc. are set as immutable
    attributes."""
    def __setattr__(self, *args):
        """Override __setattr__ to prevent attributes of this class from
        being changed."""
        raise AttributeError("Attributes of the %s class cannot be "
                             "changed" % type(self).__name__)
    def __delattr__(self, *args):
        """Override __delattr__ to prevent attributes of this class from
        being deleted."""
        raise AttributeError("Attributes of the %s class cannot be "
                             "deleted" % type(self).__name__)

    def __init__(self,in_code):

        in_code_up = in_code.upper()
        if not in_code_up in alpha_and_region_dict.keys():
            raise ValueError

        object.__setattr__(self, "type", "park")
        object.__setattr__(self, "code", in_code_up)
        object.__setattr__(self, "name", alpha_and_name_dict[in_code_up])

        ## make and sort list of tuples for landscapes
        land_list = [i for i in cli_num_and_region_dict.keys()\
                           if cli_num_and_alpha_dict[i] == in_code_up]
        land_tuples = [(i,cli_num_and_name_dict[i]) for i in land_list]
        land_tuples.sort(key=lambda tup: tup[0])
        object.__setattr__(self, "landscapes", land_tuples)

        r = alpha_and_region_dict[in_code_up]
        object.__setattr__(self, "region", (r,region_dict[r]))
        object.__setattr__(self, "query", '"ALPHA_CODE" = \'{0}\''.format(
            in_code_up))

class Region(object):
    """ This object holds information about an NPS region pertaining to 
    the cultural landscapes and parks within it. The input for instantiation
    is the 3-letter region code.  Various properties of the region, like its
    name, the parks and landscapes it contains, etc. are set as immutable
    attributes."""
    def __setattr__(self, *args):
        """Override __setattr__ to prevent attributes of this class from
        being changed."""
        raise AttributeError("Attributes of the %s class cannot be "
                             "changed" % type(self).__name__)
    def __delattr__(self, *args):
        """Override __delattr__ to prevent attributes of this class from
        being deleted."""
        raise AttributeError("Attributes of the %s class cannot be "
                             "deleted" % type(self).__name__)

    def __init__(self,in_code):

        in_code_up = in_code.upper()

        if not in_code_up in region_dict.keys():
            raise ValueError

        object.__setattr__(self, "type", "region")
        object.__setattr__(self, "code", in_code_up)
        object.__setattr__(self, "name", region_dict[in_code_up])

        ## this is a redundant property, but useful in some situations
        object.__setattr__(self, "region", (in_code,region_dict[in_code_up]))

        ## make and sort list of tuples for parks
        park_list = [i for i in alpha_and_region_dict.keys()\
                           if alpha_and_region_dict[i] == in_code_up]
        park_tuples = [(i,alpha_and_name_dict[i]) for i in park_list]
        park_tuples.sort(key=lambda tup: tup[0])
        object.__setattr__(self, "parks", park_tuples)
        object.__setattr__(self, "query", '"REGION_CODE" = \'{0}\''.format(
            in_code_up))

        ## make and sort list of tuples for landscapes
        land_list = []
        park_list.sort()
        for p in park_list:
            p_unit = MakeUnit(p)
            land_list+=[i[0] for i in p_unit.landscapes]
        land_tuples = [(i,cli_num_and_name_dict[i]) for i in land_list if\
                         i in cli_num_and_name_dict.keys()]
        #land_tuples.sort(key=lambda tup: tup[0])
        object.__setattr__(self, "landscapes", land_tuples)

def AllCLINumbers():
    '''This function returns a list of all the cli numbers that are in the
    master table'''
    return cli_num_and_name_dict.keys()

def AllGoodInputs():
    '''This function returns a list of all the valid alpha, landscape and 
    region codes, mainly used as a list to check input against if necessary'''

    return cli_num_and_name_dict.keys() + alpha_and_name_dict.keys() + region_dict.keys()

def MakeUnit(user_input):
    '''This function will take any input code and attempt to make a landscape,
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
    usage.'''

    try:
        if len(str(user_input)) == 3:
            return Region(str(user_input))

        elif len(str(user_input)) == 4:
            return Park(str(user_input))

        elif len(str(user_input)) == 6:
            return Landscape(str(user_input))
        
        else:
            return False
            
    except:
        return False

