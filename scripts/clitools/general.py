__doc__ = \
"""Contains a set of general functions that are reused many times by tool
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
"""

import arcpy
import time
import os
import shutil
import logging

from .paths import BinGDB
from .config import settings

def StartLog(level=settings['log-level'],name="output"):
    ## remove any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    if level=="DEBUG":
        name+=time.strftime("_%m%d%y-%H%M%S")
        
    logpath = os.path.join(settings['log-dir'],name+".log")
    logging.basicConfig(
        filename=logpath,
        format='%(asctime)s|%(levelname)s|%(message)s',
        datefmt='%m-%d-%y %H:%M:%S',
        level=logging.getLevelName(level)
    )
    
    arcpy.AddMessage("log level: {}".format(level))
    arcpy.AddMessage("log file: {}".format(logpath))
    
    log = logging.getLogger()
    return log
    
def Print(message,just_arcpy=False):
    '''This will print the input to the console and also pass the message to
    the arcpy.AddMessage() function. If the arcpy parameter is set to False,
    the AddMessage() function will not be called.  This is useful because 
    AddMessage() also prints to the python terminal, though not to the
    console.
    '''

    arcpy.AddMessage(message)
    if not just_arcpy:
        print message

def ConvertContribStatus(input_status):
    """Takes an input contributing status from the CLI and converts it to
    a value that is supported by the CR Spatial Data Transfer Standards.
    """

    try:
        val = str(input_status).lower().rstrip()
    except:
        contrib = "Unknown"

    if "contributing" in val and "non" in val:
        contrib = "No"
    elif "contributing" in val:
        contrib = "Yes"
    elif "undetermined" in val:
        contrib = "Unknown"
    elif val == "managed as a cultural resource":
        contrib = "No"
    else:
        contrib = "Unknown"

    return contrib
    
def FieldCalculateRegionCode(fc_or_table,field_name):
    """Runs the code block for converting long form region names to
    the corresponding 3-letter code"""
    
    cb = """def get_reg_code(region_name):
    if region_name.lower().startswith("alaska"):
        return "AKR"
    elif region_name.lower().startswith("intermountain"):
        return "IMR"
    elif region_name.lower().startswith("midwest"):
        return "MWR"
    elif region_name.lower().startswith("national"):
        return "NCR"
    elif region_name.lower().startswith("northeast"):
        return "NER"
    elif region_name.lower().startswith("pacific"):
        return "PWR"
    elif region_name.lower().startswith("southeast"):
        return "SER"
    else:
        return "UNK"
    """
    ex = "get_reg_code(!{}!)".format(field_name)
    arcpy.management.CalculateField(fc_or_table,field_name,ex,"PYTHON",cb)
    
def GetParkTypeDictionary():
    """get dictionary of park types from nps_boundary feature class"""
    
    type_dict = {}
    bnds = os.path.join(BinGDB,"nps_boundary")
    c = arcpy.da.SearchCursor(bnds,["UNIT_CODE","UNIT_TYPE"])
    for row in c:
        if not row[0] in type_dict.keys():
            type_dict[row[0]] = row[1]
    del c
    
    return type_dict

def GetCRLinkAndCRCatalogPath(geodatabase):
    """Returns the paths to the CR Link table and CR Catalog table in the
    input geodatabase.  Returns False for a table if it doesn't exist.
    """

    ## get path to cr link and catalog tables
    arcpy.env.workspace = geodatabase

    cr_link_path = False
    cr_cat_path = False
    for t in arcpy.ListTables():
        if t.lower().endswith("cr_link"):
            cr_link_path = os.path.join(geodatabase,t)
        if t.lower().endswith("cr_catalog"):
            cr_cat_path = os.path.join(geodatabase,t)
    return (cr_link_path,cr_cat_path)

def Print3(message,log):
    """Prints the input message to a log, the shell, and the arcpy.AddMessage()
    function."""
    print message
    print >> log, message
    arcpy.AddMessage(message)
        
def TimeDiff(start_time):
    """Prints out a time differential in seconds.  Provide a start time (as
    defined previously by setting a variable to equal time.time()), and that
    time will be subtracted from the current time.  The result is printed
    and returned."""
    current_time = time.time()
    secs = current_time-start_time
    msg = "{0} seconds elapsed".format(secs)
    print msg
    arcpy.AddMessage(msg)
    return secs

def TakeOutTrash(trash):
    """Quick little function to delete a dataset if it already exists.
    code is:    
    if arcpy.Exists(trash):
        arcpy.management.Delete(trash)"""
    if arcpy.Exists(trash):
        arcpy.management.Delete(trash)

def MakePathList(in_gdb,include_survey_fcs=False):
    """Makes list of paths to all feature classes in a gdb (including 
    those nested in feature class datasets).  By default, Survey feature
    classes are excluded, but they may be included if desired."""
    arcpy.env.workspace = in_gdb
    path_list = []
    for fds in arcpy.ListDatasets('','feature') + ['']:
        for fc in arcpy.ListFeatureClasses('','',fds):
            if not include_survey_fcs:
                if not "surv" in fc:
                    path_list.append(os.path.join(arcpy.env.workspace, fds, fc))
            else:
                path_list.append(os.path.join(arcpy.env.workspace, fds, fc))
    return path_list

def MakeDateAndTimeVar():
    """Makes the date and time variable formatted just the way you like it."""

    clock = time.strftime("%I:%M%p")
    date = time.strftime("%m-%d-%y")
    dateandtime = "date: {0}\ntime: {1}".format(
        date,clock.lower().lstrip("0"))
    return dateandtime

def AskYesOrNo(question):
    """Quick function to standardize the request for a yes or no answer
    output is a boolean True or False value, input is a string question."""

    answer = raw_input(question + "\n  --> ")
    while not answer.lower().startswith("y") and\
          not answer.lower().startswith("n"):
        answer = raw_input("  --> ")
    if answer.lower().startswith("y"):
        return True
    if answer.lower().startswith("n"):
        return False

def GetDirPath(unit,walk_path):
    """Finds the location of a landscape folder within the standardized
    directory structure.  Must be provided a regional folder and a CLI
    unit number."""

    dir_choice = raw_input("  place on DESKtop or in"\
                           " appropriate DIRectory?\n  --> ").lower()
    while not dir_choice == "desk" and not\
          dir_choice == "dir":
        dir_choice = raw_input("  --> ").lower()
    if dir_choice == "desk":
        userhome = os.path.expanduser('~')
        dir_path = os.path.join(userhome,"Desktop")
    if dir_choice == "dir":
        if unit.type == "region":
            dir_path = walk_path
        if unit.type == "park":
            dir_path = os.path.join(walk_path, unit.code)
        if unit.type == "landscape":
            dir_path = os.path.join(walk_path, unit.park[0], unit.code)
    return dir_path

def GetDraftedFeatureCountsScratch(cli_number,cli_ids,scratch_gdb,
                exclude_arch=False):
    """Iterates through all of the features in a scratch geodatabase, 
    and returns a count of all cli_ids that are included, a count of how
    many are contributing, and a boolean indicating whether or not a
    boundary has been created."""

    ## set query for features that will be included, modify if arch sites
    ## should be excluded
    qry = '"fclass" IS NOT NULL'
    if exclude_arch:
        qry = qry + ' AND UPPER("LAND_CHAR") <> \'ARCHEOLOGICAL SITES\''

    all_feat = []
    contrib_feat = []
    boundary = False

    fc_list = MakePathList(scratch_gdb)
    for p in [i for i in fc_list if "imp_" in i or "scratch_" in i]:

        TakeOutTrash("fl")
        arcpy.management.MakeFeatureLayer(p,"fl",qry)
        if int(arcpy.management.GetCount("fl").getOutput(0)) == 0:
            continue

        for row in arcpy.da.SearchCursor(p,["CLI_ID","CONTRIBRES"],qry):
            if row[0] in all_feat:
                continue
            if row[0] in cli_ids:
                all_feat.append(row[0])
            if row[0] in cli_ids and row[1] == "Yes":
                contrib_feat.append(row[0])
            if row[0] == cli_number:
                boundary = True

    ct_all = len(all_feat)
    ct_contrib = len(contrib_feat)
        
    return [ct_all,ct_contrib,boundary]

def GetDraftedFeatureCounts(cli_number,cli_ids,gdb_path,
                  exclude_arch=False):
    """Iterates through all of the features in a the provided geodatabase,
    and returns a count of all cli_ids that are included, a count of how
    many are contributing, and a boolean indicating whether or not a
    boundary has been created."""
    
    ## set query to empty, modify if arch sites should be excluded
    qry = '"CLI_NUM" = \'' + cli_number +"'"
    if exclude_arch:
        qry = qry + 'AND UPPER("LAND_CHAR") <> \'ARCHEOLOGICAL SITES\''

    all_feat = []
    contrib_feat = []
    boundary = False

    for p in MakePathList(gdb_path):

        for row in arcpy.da.SearchCursor(p,["CLI_ID","CONTRIBRES"],qry):
            if row[0] in all_feat:
                continue
            if row[0] in cli_ids:
                all_feat.append(row[0])
            if row[0] in cli_ids and row[1] == "Yes":
                contrib_feat.append(row[0])
            if row[0] == cli_number:
                boundary = True

    ct_all = len(all_feat)
    ct_contrib = len(contrib_feat)

    return [ct_all,ct_contrib,boundary]

def CheckFeatureClassForNulls(feature_class,check_guids=False):
    '''Checks for NULL values in any of the mandatory NPS CR Spatial
    Data Transfer Standards fields.'''

    lines = []
    ct = int(arcpy.management.GetCount(feature_class).getOutput(0))

    lines.append(os.path.basename("{0} | {1} total feature{2}".format(
        feature_class,str(ct),"s" if not ct == 1 else "")))

    mand_fields = ["BND_TYPE","IS_EXTANT","CONTRIBRES","RESTRICT_","SOURCE",
    "SRC_DATE","SRC_SCALE","SRC_ACCU","SRC_COORD","MAP_METHOD","CREATEDATE",
    "EDIT_DATE","ORIGINATOR","CONSTRANT","VERT_ERROR"]

    if "othr" in feature_class:
        mand_fields.append("TYPE")

    if check_guids:
        mand_fields.append("CR_ID")
        mand_fields.append("GEOM_ID")

    for f in mand_fields:
        if not f in [i.name for i in arcpy.ListFields(feature_class)]:
            return "operation aborted because field {0} is missing".format(f)

    field_dict = {}
    for f in mand_fields:
        field_dict[f] = 0

    cursor_fields = ";".join(mand_fields + ["OBJECTID","RESNAME"])

    for row in arcpy.SearchCursor(feature_class,"","",cursor_fields):
        
        for field in mand_fields:
            val = row.getValue(field)
            if val == None or str(val).encode('ascii','ignore').rstrip() == "":
                field_dict[field] += 1       

    for k in field_dict.keys():
        string = "OK"
        if not field_dict[k] == 0:
            string = "needs help ({0} feature{1})".format(
                str(field_dict[k]), "s" if not field_dict[k] == 1 else "")
        lines.append("  {0}{1}{2}".format(k,(12-len(k))*" ",string))
    lines.append("\n")
    output = "\n".join(lines)
    return output

def CheckGeodatabaseForNulls(geodatabase,check_guids=False):
    '''Checks an entire geodatabase for NULL values in any of the 
    mandatory NPS CR Spatial Data Transfer Standards fields.  All of the 
    feature classes in the input geodatabase are expected to contain all
    of the fields that will be checked.'''

    dir_path = os.path.dirname(geodatabase)
    name = os.path.basename(geodatabase).rstrip(".gdb")

    log_path = os.path.join(dir_path,"StandardsCheck {0}.txt".format(name))
    Print("\nresults stored in " + log_path + '\n')

    log = open(log_path,"w")

    for path in MakePathList(geodatabase):
        print >> log, CheckFeatureClassForNulls(path,check_guids)

    log.close()
    os.startfile(log_path)

def BackupGDB(geodatabase,backup_location,comment=''):
    """Simple function to back up a geodatabase.  Option to add
    a comment that will be incorporated into the name, like 
    'BEFOREGUIDS', etc. The shutil.copy2 function is used on the files
    within the geodatabase folder.  No arcpy functions are used."""

    gdb_name = os.path.splitext(os.path.basename(geodatabase))[0]

    ##optional comment to add a note to the name of the gdb, needs an
    ##underscore added to it to work correctly.
    if not comment == '':
        comment = "_"+comment

    bu_gdb = "{0}\{1}_{2}{3}.gdb".format(
        backup_location,gdb_name,time.strftime("%b%d_%H%M"),comment)

    os.makedirs(bu_gdb)

    for f in os.listdir(geodatabase):
        if not f.endswith(".lock"):
            shutil.copy2(geodatabase + os.sep + f, bu_gdb)

def CheckValuesAgainstDomains(geodatabase):
    '''This function introspects all of the values in each feature class in
    the input geodatabase.  The values in any field that has a domain are
    checked against all the values in the domain for that field.  Messages
    are printed whenever a value is out of line.'''

    arcpy.AddMessage("\nAnalyzing feature classes...")

    ## make path for log file
    dir_path = os.path.dirname(geodatabase)
    name = os.path.basename(geodatabase).rstrip(".gdb")
    log_path = os.path.join(dir_path,"DomainCheck {0}.txt".format(name))
    log = open(log_path,"w")
    
    ## first make dictionary of all domains
    desc = arcpy.Describe(geodatabase)
    domains = desc.domains

    val_dict = {}

    for domain in domains:
        temp_tv = "in_memory\\fl"
        TakeOutTrash(temp_tv)
        arcpy.DomainToTable_management(geodatabase, domain, temp_tv,
            'field','description','#')
        code_list = [i.getValue("field") for i in arcpy.SearchCursor(temp_tv)]
        val_dict[domain] = code_list

    for path in MakePathList(geodatabase):
        
        bad = False

        fc_name = os.path.basename(path)
        arcpy.AddMessage(fc_name)
        
        print >> log, fc_name

        for f in arcpy.ListFields(path):
            if f.domain == "":
                continue
            if f.name == "UNIT_CODEO" or f.name == "GROUP_CODE":
                continue
            bad_vals = []
            for row in arcpy.SearchCursor(path,"","",f.name):
                val = str(row.getValue(f.name)).encode('ascii','ignore')
                if val == "None":
                    val = "<Null>"
                if not val in val_dict[f.domain]:
                    if not val in bad_vals:
                        bad = True
                        if len(bad_vals) == 0:
                            print >> log, "    " + f.name
                        bad_vals.append(val)
                        print >> log, "        bad value(s): {0}".format(val)
        if not bad:
            arcpy.AddMessage("    ALL FIELD VALUES MATCH DOMAIN VALUES")
            print >> log, "    ALL FIELD VALUES MATCH DOMAIN VALUES"
        else:
            arcpy.AddMessage("    see log for problems")
        
        print >> log, '\n'+'-'*40+'\n'

    arcpy.AddMessage("\nProcess finished.")
    log.close()
    os.startfile(log_path)

def ExportGDBToShapefiles(input_gdb,output_location):
    """ Exports all feature classes in the input geodatabase to
    shapefiles."""

    arcpy.AddMessage("Exporting contents of:\n{0}\n\nTo destination"\
        " folder:\n{1}\n".format(
        input_gdb,output_location))

    paths = MakePathList(input_gdb,True)
    for path in paths:
        name = os.path.basename(path)
        arcpy.AddMessage(name)

        ct = int(arcpy.management.GetCount(path).getOutput(0))
        if ct == 0:
            arcpy.AddMessage("  ...no features")
            continue

        arcpy.AddMessage("  {0} feature{1}".format(ct,"s" if not\
            ct == 1 else ''))
        out_file = os.path.join(output_location,name+".shp")
        arcpy.management.CopyFeatures(path,out_file)

    arcpy.AddMessage("\nExport Complete.")
    
def MakeBlankGDB(template_path,output_gdb_path):
    """creates a blank geodatabase from the input template. If a gdb of the
    same name as the desired output already exists, then ascending numbers will
    be suffixed as necessary"""
    
    new_gdb = os.path.splitext(output_gdb_path)[0]
    new_name = new_gdb
    r = 1
    while os.path.isdir(new_name+ ".gdb"):
        new_name = new_gdb+"_"+str(r)
        r+=1
    new_gdb = new_name + ".gdb"
    os.makedirs(new_gdb)
    for f in os.listdir(template_path):
        if not f.endswith(".lock"):
            shutil.copy2(os.path.join(template_path,f), new_gdb)
    
    return new_gdb
