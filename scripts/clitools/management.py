__doc__ = \
"""Contains a variety of functions that are used by the scripts associated
with the tools in the CLI Toolbox.  These functions tend to deal with the
management and analysis of CLI spatial data.

If the clitools package is moved to the user's native Python installation
all of these functions will be available to any python scripting.  Use the
following syntax to import the function:

from clitools.management import <function_name>

To move the clitools package to the Python folder, find your Python
installation folder (e.g. C:\Python27), and then find the 
...\Lib\site-packages directory.  Perform the following actions:

1. Move this clitools folder and all of its contents into the site-packages
directory.
2. From within the clitools folder, move the xlrd and xlwt folders and
their contents into the site-packages folder.
"""

import arcpy
import os
import shutil
import sys
import traceback
import time

from .classes import MakeUnit
from .summarize import MakeSingleLandscapeXLS
from .config import settings

from .general import (
    MakePathList,
    TakeOutTrash,
    GetCRLinkAndCRCatalogPath,
    Print,
    Print3,
    StartLog,
    MakeBlankGDB,
    )

from .paths import (
    GDBstandard,
    GDBscratch,
    MXDtemplate,
    GDBscratch,
    GDBstandard,
    GDBstandard_WGS84,
    WGS84prj,
    NAD83prj,
    )

def ConsolidateCRLinkTable(cr_link_path,fc_cr_id_list=False):
    """ Analyzes a full CR Link table and collapses it down to one row per
    CR_ID.  All program IDs are retained.  Returns a path to a new log file
    if conflicting program IDs have been found."""

    in_gdb = os.path.dirname(cr_link_path)

    ## make new dictionary of unique CR_IDs, consolidating all program ids.
    id_fields = [f.name for f in arcpy.ListFields(cr_link_path)][3:]

    ## augment list
    sf = ["CLI_NUM","LAND_CHAR","RESNAME"]
    for s in sf:
        if s in id_fields:
            id_fields.remove(s)
    id_fields.insert(0,"CR_ID")
    id_fields = tuple(id_fields)

    link_dict = {}
    arcpy.AddMessage("\nCollecting and consolidating all unique CR_IDs "\
                     "and associated program IDs...")
    cr_double_id = []
    with arcpy.da.SearchCursor(cr_link_path,id_fields) as c:
        for row in c:
            cr_id = row[0]

            ## skip empty cr_ids
            if cr_id == None or str(cr_id).rstrip() == "":
                continue

            ## if it's a new cr_id, add to dictionary with all program ids
            if not cr_id in link_dict.keys():
                link_dict[cr_id] = [row[i] for i in range(1,len(id_fields))]

            ## if it's already in the dictionary, compare program ids
            else:
                new_ids = [row[i] for i in range(1,len(id_fields))]
                old_ids = link_dict[cr_id]
                compare = zip(new_ids,old_ids)
                new_list = []
                for i, (x,y) in enumerate(compare):
                    if str(x).rstrip() == '':
                        x = None
                    if str(y).rstrip() == '':
                        y = None
                    if x != None and y == None:
                        val = x
                    elif x == None and y != None:
                        val = y
                    elif x == None and y == None:
                        val = None
                    elif x == y:
                        val = x
                    else:
                        cr_double_id.append((cr_id,id_fields[i+1],x,y,i))
                        val = x
                    new_list.append(val)
                link_dict[cr_id] = new_list

    ## if cr_ids have been found to have multiple values for certain programs
    ## list them and add error
    cr_n = len(link_dict)
    arcpy.AddMessage("  process finished, {0} unique CR_ID{1}".format(
        cr_n,"" if cr_n == 1 else "s"))
    log = False
    if len(cr_double_id) > 0:
        
        #name and create log file
        log_dir = os.path.dirname(in_gdb)
        log_path = os.path.join(log_dir,"CR_ID Multiple Program IDs " +\
                   time.strftime("%m-%d-%Y_%Hh%Mm") + ".txt")
        log = open(log_path, "a")

        ## print error messages and lists of features
        print >> log, "Input Geodatabase:\n{0}".format(str(in_gdb))
        msg1 = "\nThe following CR_IDs have conflicting database IDs."
        msg2 = """
(see bottom of document for a detailed explanation)

LIST OF CONFLICTS:
"""
        msg3 = """
_______________________________________________________________________________                     
EXPLANATION:

Only one row can exist in the CR Link table for each CR_ID, and each CR_ID can
only hold one identifying number for a given database--only one LCS_ID, one
FMSS_ID, etc.  For the cases shown above, there were multiple program IDs
encountered for a single CR_ID.  This is caused when multiple spatial features
that have the same CR_ID have been assigned different program IDs, or if a 
program ID in the spatial feature conflicts with a corresponding CR_ID entry
in the link table.

If the CLI_ID is the culprit, there are two likely causes:

1.  The feature is listed under multiple Landscape Characteristic categories,
    and identical geometries were used (with the same CR_ID) to represent each
    feature.
2.  The feature is listed in more than one landscape, and identical geometries
    were used (with the same CR_ID) to represent each feature.

A careful inspection of the spatial features and corresponding CR_IDs in the
link table will reveal the conflict, and after making the necessary edits to
the spatial features or link table, rerun this tool.  See p. 18 of the "Using
the CLI Toolbox" guide for more information.
_______________________________________________________________________________

"""

        arcpy.AddWarning(msg1)
        print >> log, msg2
        
        lines = []
        for i in cr_double_id:
            line = "{0}: {1}, {2} or {3}? {4} chosen".format(
                i[0],i[1],i[2],i[3],link_dict[i[0]][i[4]])
            if not line in lines:
                arcpy.AddWarning(line)
                lines.append(line)
            
        lines.sort()
        print >> log, "\n".join(lines)
        arcpy.AddWarning("Consult the error log for more information.")

        print >> log, '\nDEFINITION QUERY:\n(can be pasted into a layer\'s '\
            'definition query to only show problem features)\n\n"CR_ID" IN '\
            '(\'{0}\')'.format("','".join(set([e[0] for e in cr_double_id])))
        print >> log, msg3
        log.close()    
        
    ## use update cursor to update program values and delete duplicate cr_ids
    arcpy.AddMessage("\nRemoving all duplicate/null rows and writing program "\
        "IDs...")
    up_curse = arcpy.da.UpdateCursor(cr_link_path,"*")

    covered_cr_ids = []
    removed = 0
    remain = 0
    for row in up_curse:
        cr_id = row[1]
        if fc_cr_id_list:
            if not cr_id in fc_cr_id_list:
                up_curse.deleteRow()
                removed+=1
                continue
        if not cr_id in link_dict.keys() or cr_id in covered_cr_ids\
           or cr_id == None or cr_id == '':
            up_curse.deleteRow()
            removed+=1
        else:
            for i,v in enumerate(link_dict[cr_id]):
                row[i+3] = v
            covered_cr_ids.append(cr_id)
            up_curse.updateRow(row)
            remain+=1  

    arcpy.AddMessage("  {0} row{1} removed from CR Link".format(
            removed,"" if removed == 1 else "s"))
    arcpy.AddMessage("  {0} unique CR_ID{1} remain{2} in CR Link".format(
            remain,"" if remain == 1 else "s","" if not remain == 1 else "s"))

    if not log:
        return False
    else:
        return log_path

def CreateGUIDs(geodatabase,subset_query='',cr_guid=False,geom_guid=False,
    overwrite=False):
    """ Makes new GUIDs for all features in geodatabase, or all that match
    a subset query if it is supplied.  Old GUIDs can be overwritten, and
    the user may indicate which GUIDs to make.  The CR Link and Catalog
    tables will not be affected with this tool, just the feature classes.

    If CR GUIDs (CR_IDs) are created, they will be analyzed and transferred
    to match multiple geometry representations of a single physical
    feature."""

    try:
        ## intro print statement
        arcpy.AddMessage("\nInput geodatabase: " + geodatabase)

        ## expression and codeblock for calculate field thing
        ex = "g"
        cb = "Set TypeLib = CreateObject(\"Scriptlet.Typelib\")\n"\
             "g = TypeLib.GUID"

        ## make path list from input geodatabase
        paths = MakePathList(geodatabase)

        ## make sure all feature classes have a CLI_NUM field
        if not subset_query == '':
            arcpy.AddMessage("where clause used: " + subset_query + "\n")
            for path in paths:
                name = os.path.basename(path)
                if not "CLI_NUM" in [f.name for f in arcpy.ListFields(path)]:
                    arcpy.AddError("\nOne of the feature classes ({0}) does "\
                        "not have a CLI_NUM field, which means the the CLI "\
                        "number query cannot be honored.\nProcess aborted.")
                    return
        else:
            arcpy.AddMessage("no where clause used\n")

        ## print summary of settings
        if cr_guid:
            arcpy.AddMessage("  --creating CR_IDs (cultural resource GUIDs)")
        if geom_guid:
            arcpy.AddMessage("  --creating GEOM_IDs (locational GUIDs)")
        if overwrite:
            arcpy.AddMessage("  --existing GUIDs WILL be overwritten")
        else:
            arcpy.AddMessage("  --existing GUIDs WILL NOT be overwritten")
        
        ## iterate through all feature classes
        arcpy.AddMessage("\nCalculating GUIDs in all feature classes...")       
        crtotal = 0
        geomtotal = 0
        for path in paths:
            name = os.path.basename(path)
            arcpy.AddMessage(name)

            fl = "fl"
            TakeOutTrash(fl)
            arcpy.management.MakeFeatureLayer(path,fl,subset_query)
            count = int(arcpy.management.GetCount(fl).getOutput(0))
            if count == 0:
                arcpy.AddMessage("  ...no records")
                continue

            ## make CR_IDs
            if cr_guid:                
                if not overwrite:
                    arcpy.management.SelectLayerByAttribute(fl,"NEW_SELECTION",
                            '"CR_ID" IS NULL OR "CR_ID" = \'\'')
                count = int(arcpy.management.GetCount(fl).getOutput(0))
                crtotal+=count
                arcpy.management.CalculateField(fl, "CR_ID", ex, "VB", cb)
                arcpy.AddMessage("  {0} CR_ID{1} created".format(
                    str(count),"" if count == 1 else "s"))

            ## calculate new GUIDs for all selected records
            if geom_guid:
                if not overwrite:
                    arcpy.management.SelectLayerByAttribute(fl,"NEW_SELECTION",
                            '"GEOM_ID" IS NULL OR "GEOM_ID" = \'\'')
                count = int(arcpy.management.GetCount(fl).getOutput(0))
                geomtotal+=count
                arcpy.management.CalculateField(fl, "CR_ID", ex, "VB", cb)
                arcpy.AddMessage("  {0} GEOM_ID{1} created".format(
                    str(count),"" if count == 1 else "s"))
                
                arcpy.management.CalculateField(fl, "GEOM_ID", ex, "VB", cb)
            TakeOutTrash(fl)                         

        arcpy.AddMessage("\nTotal number of CR_IDs: " + str(crtotal) + "\n")
        arcpy.AddMessage("Total number of GEOM_IDs: " + str(geomtotal) + "\n")

        #transfer new CR_IDs based on geometry
        if cr_guid:

            arcpy.AddMessage("\nTransferring CR_IDs for features with multiple "\
                             "geometries...")
            
            ## iterate through feature class datasets, and transfer CR_IDs
            arcpy.env.workspace = geodatabase
            fcds_list = arcpy.ListDatasets()
            for ds in fcds_list:

                ## skip survey feature class dataset
                if "Survey" in str(ds):
                    continue

                arcpy.AddMessage("\n  " + ds)
                fls = []
                shapes = ["Apolygon","Bpolyline","Cpoint"]            
                for fc in arcpy.ListFeatureClasses("","",ds):
                    for s in shapes:
                        if arcpy.Describe(fc).shapeType.lower() == s[1:]:
                            TakeOutTrash(s)
                            arcpy.management.MakeFeatureLayer(fc,s,subset_query)
                            count = int(arcpy.management.GetCount(s).getOutput(0))
                            if count == 0:
                                arcpy.management.Delete(s)
                                continue
                            fls.append(s)

                print "\n" + ds.replace("_"," ") + ":"
                if len(fls) <= 1:
                    arcpy.AddMessage("  not enough feature classes meet criteria.")
                    continue
                fls.sort()
                if len(fls) == 2:
                    TransferCR_IDs(fls[0],fls[1])
                if len(fls) == 3:
                    TransferCR_IDs(fls[0],fls[1])
                    TransferCR_IDs(fls[0],fls[2])
                    TransferCR_IDs(fls[1],fls[2])
                TakeOutTrash(s)

        del subset_query
        arcpy.AddMessage("\n")

    except:
        
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

        arcpy.AddError(msgs)
        arcpy.AddError(pymsg)

        print msgs

        print pymsg
        
        arcpy.AddMessage(arcpy.GetMessages(1))
        print arcpy.GetMessages(1)

def CreateNewProjectFolder(destination,region_code,alpha_code,cli_num,
    open_mxd=False):
    """Creates a series of new objects to facilitate the creation of data
    for a new cli.  An attempt will be made to create the following:

    1. a scratch geodatabase, named <cli_num>_scratch.gdb
    2. a map document, named <cli_num>.mxd
    3. a spreadsheet, named <cli_num>, <cli_name>.xls

    If any of the above already exist, they will be skipped (no existing
    data will be overwritten.)
    """

    if not len(alpha_code) == 4:
        arcpy.AddError("\nInvalid Alpha Code, check and try again"\
            " (must be 4 letters)")
        return False
    else:
        alpha_code = alpha_code.upper()

    ## make path for new directory and create it if necessary
    region = MakeUnit(region_code)
    region_path = r"{0}\{1}".format(destination,region.name)
    dir_path = r"{0}\{1}\{2}".format(region_path,alpha_code,cli_num)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    ## 1. make scratch geodatabase
    gdb_path = r"{0}\{1}_scratch.gdb".format(dir_path,cli_num)
    if not os.path.isdir(gdb_path):

        os.makedirs(gdb_path)

        #gdbtemplate = os.path.join(bin_dir,"CLI_scratch_template.gdb")
        gdbtemplate = GDBscratch
        for f in os.listdir(gdbtemplate):
            if not f.endswith(".lock"):
                shutil.copy2(gdbtemplate + os.sep + f, gdb_path)

    ## 2. make map document
    new_mxd_path = r"{0}\{1}.mxd".format(dir_path,cli_num)
    if not arcpy.Exists(new_mxd_path):

        ## copy template map document to new folder
        #mxdtemplate_path = os.path.join(bin_dir,"mxd_template.mxd")
        mxdtemplate_path = MXDtemplate
        mxd_template = arcpy.mapping.MapDocument(mxdtemplate_path)
        mxd_template.saveACopy(new_mxd_path)
        new_mxd = arcpy.mapping.MapDocument(new_mxd_path)

        ## add feature classes from geodatabase to table of contents
        df = arcpy.mapping.ListDataFrames(new_mxd)[0]
        arcpy.env.workspace = gdb_path
        for fc in arcpy.ListFeatureClasses():
            arcpy.AddMessage(fc)
            l = arcpy.mapping.Layer(fc)
            arcpy.mapping.AddLayer(df,l)

        ## zoom to park
        nps_lyr = arcpy.mapping.ListLayers(new_mxd,"nps_boundary",df)[0]
        query = "\"UNIT_CODE\" = '" + alpha_code + "'"
        try:
            arcpy.management.SelectLayerByAttribute(nps_lyr,"NEW_SELECTION",query)
            df.zoomToSelectedFeatures()
            arcpy.management.SelectLayerByAttribute(nps_lyr,"CLEAR_SELECTION")
            arcpy.RefreshActiveView()
        except:
            pass

        new_mxd.save()

    ## 3. make new spreadsheet
    landscape = MakeUnit(cli_num)
    if landscape:
        MakeSingleLandscapeXLS(cli_num,gdb_path,dir_path)
    else:
        arcpy.AddMessage("There are no features in the lookup table yet for this "\
            "landscape.  No spreadsheet will be made.")

    if open_mxd:
        os.startfile(new_mxd_path)

def ExtractFromStandards(input_geodatabase,filter_field,input_codes,output_location):
    """Creates a query from the input codes and extracts all matching data
    from the input geodatabase to a new geodatabase in the output_location."""

    log = StartLog(name="ExtractFromStandards",level="DEBUG")
    
    try:

        query = '"{}" IN (\'{}\')'.format(filter_field,"','".join(input_codes))
        log.info("query: "+query)

        ## make new gdb to hold extract

        blank_gdb = GDBstandard_WGS84
        if len(input_codes) == 1:
            new_gdb_suffix = input_codes[0]
        else:
            new_gdb_suffix = input_codes[0]+"_etc"
        new_gdb = os.path.join(output_location,time.strftime(
            "{0}_%Y%b%d_%H%M".format(new_gdb_suffix)))

        ## if gdb already exists, add integer to end of new name
        new_name = new_gdb
        r = 1
        while os.path.isdir(new_name+ ".gdb"):
            new_name = new_gdb+"_"+str(r)
            r+=1

        ## copy template over to new geodatabase
        new_gdb = new_name + ".gdb"
        os.makedirs(new_gdb)
        for f in os.listdir(blank_gdb):
            if not f.endswith(".lock"):
                shutil.copy2(os.path.join(blank_gdb,f), new_gdb)
        new_gdb_paths = MakePathList(new_gdb)

        ## cycle through paths and export features, also get all cr ids
        cr_guids = []
        total = 0
        for path in MakePathList(input_geodatabase,True):
        
            log.debug("processing: "+path)
            
            ## not the most robust solution, but skipping and fcs that don't have
            ## the necessary field. specfically, surv may not have CLI_NUM.
            if not filter_field in [f.name for f in arcpy.ListFields(path)]:
                log.debug(filter_field + " not found, skipping")
                continue
            
            fc_nam = os.path.basename(path)

            fl = "fl"
            TakeOutTrash(fl)
            log.debug("applying query")
            arcpy.management.MakeFeatureLayer(path,fl,query)
            ct = int(arcpy.management.GetCount(fl).getOutput(0))
            if ct == 0:
                continue
            arcpy.AddMessage("{0}, {1} feature{2}".format(
                fc_nam,ct,"" if ct == 1 else "s"))
            for targ_path in new_gdb_paths:
                if targ_path.endswith(fc_nam):
                    break

            arcpy.management.Append(fl,targ_path,"NO_TEST")
            with arcpy.da.SearchCursor(fl,"CR_ID") as cursor:
                for r in cursor:
                    if not r[0] == None:
                        cr_guids.append(r[0])
            total+=ct

        ## cut short if no features were found
        if total == 0:
            arcpy.AddError("\nNo features match this input query code.\n")
            return False

        ## make query for tables
        tbl_qry = '"CR_ID" IN (\'{0}\')'.format("','".join(cr_guids))

        ## append table view to CR_Link
        cr_link = os.path.join(input_geodatabase,"CR_Link")
        tv ='tv'
        TakeOutTrash(tv)
        arcpy.management.MakeTableView(cr_link,tv,tbl_qry)
        arcpy.management.Append(tv,cr_link.replace(input_geodatabase,new_gdb),
            "NO_TEST")

        ## append table view to CR_Catalog
        cr_catalog = os.path.join(input_geodatabase,"CR_Catalog")
        TakeOutTrash(tv)
        arcpy.management.MakeTableView(cr_catalog,tv,tbl_qry)
        arcpy.management.Append(tv,cr_catalog.replace(input_geodatabase,new_gdb),
            "NO_TEST")


    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        print msgs
        print pymsg
        print arcpy.GetMessages(1)
        arcpy.AddMessage(msgs)
        arcpy.AddMessage(pymsg)
        arcpy.AddMessage(arcpy.GetMessages(1))

def GetCLI_IDGUIDs(cr_link_path,cli_id_list):
    """Looks through the CR Link table in the geodatabase holding the input
    feature class, and finds the GEOMETRY_GUIDs for all the features that
    are in the list of CLI_IDs that is provided.
    """

    list_string = ",".join(["'"+str(i)+"'" for i in cli_id_list])
    cli_id_qry = '"CLI_ID" IN ({0})'.format(list_string)

    ## use cursor on cr link table to get guids
    cursor = arcpy.da.SearchCursor(cr_link_path,["CR_ID","CLI_ID"],cli_id_qry)
    all_guids = [row[0] for row in cursor]
    del cursor

    return all_guids

def GetGUIDsFromCatalog(catalog_table,cr_guids):
    """Given a set of input CR GUIDs, or CR_IDs, the function will return all
    of the corresponding GEOM_IDs from the catalog table."""

    query = '"CR_ID" IN (\'{0}\')'.format("','".join(cr_guids))
    cursor = arcpy.da.SearchCursor(catalog_table,("CR_ID","GEOM_ID"),query)
    geom_ids = [row[1] for row in cursor]

    return geom_ids

def GetIDFieldGUIDs(fc_path,id_field,old_query):
    """This function looks through the CR Link table in the geodatabase
    holding the input feature class, and finds the CR GUIDs for all
    the features that have a value in the user specified id field.  That
    full list is then checked against the list of all CR_IDs in the input
    feature class.  The result is a tuple:

    (with_id_guids,without_id_guids)

    """

    try:

        if "EXTANT" in old_query:
            old_query = ''

        ## get path to containing geodatabase
        gdb_path = os.path.dirname(fc_path)
        while not gdb_path.endswith(".gdb") and not gdb_path.endswith(".sde"):
            gdb_path = os.path.dirname(gdb_path)

        ## get path to cr link table 
        cr_link_path = GetCRLinkAndCRCatalogPath(gdb_path)[0]
        if not cr_link_path:
            arcpy.AddError("There is no CR Link table in this geodatabase, so this "\
                "operation cannot be performed.")
            return False

        ## make table view
        tv = "tv"
        TakeOutTrash(tv)
        arcpy.management.MakeTableView(cr_link_path,tv)

        with_id_qry = '"{0}" IS NOT NULL AND "{0}" <> \'\''.format(id_field)
        without_id_qry = '"{0}" IS NULL OR "{0}" = \'\''.format(id_field)
        
        ## get list of those with ids
        arcpy.management.SelectLayerByAttribute(
                    tv,"NEW_SELECTION",with_id_qry)
        with arcpy.da.SearchCursor(tv,"CR_ID") as curse:
            all_with_id_guids = [r[0] for r in curse]

        ## get list of those without ids
        arcpy.management.SelectLayerByAttribute(
                    tv,"NEW_SELECTION",without_id_qry)

        with arcpy.da.SearchCursor(tv,"CR_ID") as curse:
            all_without_id_guids = [r[0] for r in curse]

        ## pare down lists to only have GUIDs that are in this feature class
        guids_in_fc = [i[0] for i in arcpy.da.SearchCursor(fc_path,"CR_ID")]
        with_id_guids = [str(i) for i in all_with_id_guids if i in guids_in_fc]
        without_id_guids = [str(i) for i in all_without_id_guids if i in guids_in_fc]
    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        print msgs
        print pymsg
        print arcpy.GetMessages(1)
        arcpy.AddMessage(msgs)
        arcpy.AddMessage(pymsg)
        arcpy.AddMessage(arcpy.GetMessages(1))

    return (with_id_guids,without_id_guids)

def GetMultiplesGUIDs(fc_path,subset_query):
    """ This function takes a feature class and produces a list
    of GEOM_IDs for the features that are multiple geometries of
    other feature classes.  a subset query can be applied.

    the results is a tuple of lists:
    (bad_guids,good_guids)
    """

    try:

        ## make empty lists so they can be added together later
        list1,list2 = [],[]

        ## get shape of input fc
        shptype = arcpy.Describe(fc_path).shapeType.lower()

        ## compare point to line
        if shptype == "point":

            ln_path = fc_path[:-2]+"ln"
            if arcpy.Exists(ln_path):
                TakeOutTrash("l1")
                TakeOutTrash("l2")

                arcpy.management.MakeFeatureLayer(fc_path,"l1",subset_query)
                arcpy.management.MakeFeatureLayer(ln_path,"l2",subset_query)

                list1 = SpatialAndCLI_IDCompareForGUIDs("l1","l2")

        ## compare point to polygon or line to polygon
        if shptype == "point" or shptype == "polyline":

            py_path = fc_path[:-2]+"py"

            if arcpy.Exists(py_path):
                TakeOutTrash("l1")
                TakeOutTrash("l2")

                arcpy.management.MakeFeatureLayer(fc_path,"l1",subset_query)
                arcpy.management.MakeFeatureLayer(py_path,"l2",subset_query)

                list2 = SpatialAndCLI_IDCompareForGUIDs("l1","l2")

        ## add lists together for final list
        bad_guids = list1+list2
        all_guids = [i[0] for i in arcpy.da.SearchCursor(
            fc_path,"GEOM_ID",subset_query)]
        good_guids = [str(i) for i in all_guids if not i in bad_guids]

        return (bad_guids,good_guids)

    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        print msgs
        print pymsg
        print arcpy.GetMessages(1)
        arcpy.AddMessage(msgs)
        arcpy.AddMessage(pymsg)
        arcpy.AddMessage(arcpy.GetMessages(1))

def ImportKMLToGDB(kml_or_kmz_file,target_gdb):
    """This function just takes the input file and uses the ESRI
    arcpy.conversion.KMLToLayer() tool to place a feature class in
    the target geodatabase.  If run from ArcMap, the new layer will
    be added to the dataframe.  Technically this is against GE license
    agreement if the data is to be used in a final product, so this
    function is not actually used anywhere right now."""

    ## make mxd variables if possible
    try:
        mxd = arcpy.mapping.MapDocument("CURRENT")
        df_list = arcpy.mapping.ListDataFrames(mxd)
        for d in df_list:
            if d.name == mxd.activeView:
                df = d
    except:
        pass

    ## make name for new feature class
    basename = os.path.basename(kml_or_kmz_file)
    in_name = os.path.splitext(basename)[0]
    out_name = in_name


    repl_dict = {" ":"_", "-":"_",
                 "'":"", "\"":"_",
                 ".":""}
    for i,k in repl_dict.iteritems():
        out_name = out_name.replace(i,k)

    ## check to see if outpath already exists
    ## add incrementing numbers on the end of it if it does
    if arcpy.Exists(os.path.join(target_gdb,out_name)):
        endint = 1
        while arcpy.Exists(os.path.join(target_gdb,out_name + str(endint))):
            endint+=1
        out_name = out_name + str(endint)

    if in_name[0].isdigit():
        out_name = "x" + out_name

    out_path = os.path.join(target_gdb,out_name)

    arcpy.AddMessage("\nName used for new feature class:\n  " + out_name)
    arcpy.AddMessage("Final path used for new feature class:\n  " + out_path)

    ## make variables for kml conversion process
    out_dir = os.path.dirname(target_gdb)
    kml_gdb = os.path.join(out_dir,in_name + ".gdb")
    kml_lyr = os.path.join(out_dir,in_name + ".lyr")

    ## delete output if necessary
    try:
        TakeOutTrash(kml_gdb)
        TakeOutTrash(kml_lyr)
    except:
        arcpy.AddError("Unable to delete intermediate data.  Restart "\
            "ArcMap and rerun tool.")
        return

    try:
        ## run kml conversion
        arcpy.conversion.KMLToLayer(kml_or_kmz_file, out_dir)
        
        ## add results to scratch gdb
        arcpy.env.workspace = kml_gdb
        for ds in arcpy.ListDatasets():
            arcpy.env.workspace = ds
            for fc in arcpy.ListFeatureClasses():
                arcpy.management.MakeFeatureLayer(fc, "fl")
                arcpy.management.CopyFeatures("fl", out_path)
                arcpy.management.Delete("fl")
                
                #add new fc to display
                if mxd:
                    lyr = arcpy.mapping.Layer(out_path)
                    arcpy.mapping.AddLayer(df, lyr)
                
        #delete unnecessary intermediate .lyr output from kml conversion
        if arcpy.Exists(kml_lyr):
            arcpy.management.Delete(kml_lyr)

    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo +\
        "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

        arcpy.AddError(msgs)
        arcpy.AddError(pymsg)

        print msgs

        print pymsg
        
        arcpy.AddMessage(arcpy.GetMessages(1))
        print arcpy.GetMessages(1)

def ImportToScratchGDB(input_fc,gdb_path,clip_features='',
    variable_dictionary={},keep_native=False):
    """Imports the input features to a target geodatabase, and adds all NPS
    CR spatial data transfer standards fields during the process.  They will
    be prepopulated with the attributes provided in the variable dictionary.
    """

    # try:
    #create the variable "shrtName" used to name the output
    fcName = os.path.basename(input_fc)
    int_name = os.path.splitext(fcName)[0]
    bad_char = ["(",")","'",'"',"\\","/","*","#","&","+"]
    for char in bad_char:
        int_name = int_name.replace(char,"")
    shrtName = int_name.replace(" ", "_")
    shrtName = shrtName.replace("-", "_")
    arcpy.AddMessage("\nInput Feature Class: "+shrtName)

    #get path of specific standards fc based on input_fc shapetype
    shapetype = arcpy.Describe(input_fc).shapeType.lower()
    if shapetype == "point":
        standards_match_fc = "Historic_Objects\\crobj_pt"
    elif shapetype == "polyline":
        standards_match_fc = "Historic_Objects\\crobj_ln"
    elif shapetype == "polygon":
        standards_match_fc = "Historic_Objects\\crobj_py"
    else:
        arcpy.AddError("\nInput feature class shape type is "+\
            shapetype.upper()+".  Only POINT, POLYLINE, and POLYGON "\
            "are supported by the NPS standards.")
        return

    standards_match_gdb = GDBstandard
    standards_match = os.path.join(standards_match_gdb,standards_match_fc)

    #name and create log file
    cli_dir = os.path.dirname(gdb_path)
    log_dir = cli_dir + "\\logs"
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    log_file = log_dir + "\\ImportToScratchGDB Results " +\
               time.strftime("%m-%d-%Y %Hh %Mm %Ss") + ".txt" 
    log = open(log_file, "a")

    arcpy.AddMessage("\ntool results stored in log file:\n" + log_file +\
                     "\n\n----------\n")
    print >> log, "Results of \"Import to Standards GDB\""\
          "\n\nStart Time: " + time.strftime("%H:%M:%S") + "\n\n----------\n"
    
    #create all new domains if necessary
    domains = arcpy.Describe(gdb_path).domains

    #dictionary of new domains and their values
    new_domain_dict = {
    "LAND_CHAR":["Archeological Sites", "Boundary", "Buildings and Structures",
               "Circulation", "Cluster Arrangement", "Constructed Water Features",
               "Cultural Traditions", "Land Use", "Natural Systems and Features",
               "Small-Scale Features", "Spatial Organization", "Topography",
               "Vegetation", "Views and Vistas"],
    "fclass_pt":["crsite_pt", "crothr_pt", "crbldg_pt",
                  "crstru_pt", "crobj_pt","crsurv_pt", "crethn_pt"],
    "fclass_ln":["crsite_ln", "crothr_ln", "crstru_ln",
                  "crobj_ln", "crsurv_ln", "crethn_ln"],
    "fclass_py":["crsite_py", "crothr_py", "crbldg_py",
                  "crstru_py", "crobj_py", "crsurv_py",
                  "crethn_py", "crdist_py"],
    "BND_TYPEpt":["Center point","Derived point","Random point","Vicinity point",
                  "Vicinity point","Other point"],
    "BND_TYPEln":["Center line","Derived line","Edge line","Perimeter line",
                  "Random line","Other line"],
    "BND_TYPEpy":["Buffer polygon","Circumscribed polygon","Derived polygon",
                  "Perimeter polygon","Other polygon"]
                  }
    
    #make new domains if necessary
    for k,v in new_domain_dict.iteritems():
        if not k in domains:
            arcpy.management.CreateDomain(gdb_path,k,k, "TEXT", "CODED", "", "")
            for dval in v:
                arcpy.management.AddCodedValueToDomain(gdb_path,k, dval, dval)
    del domains

    #temporary fc used to merge
    intermediate = r"in_memory\import_tmp"
    TakeOutTrash(intermediate)
    
    #clip if clip feature is provided
    if clip_features:
        clip_int = r"in_memory\import_clip"
        TakeOutTrash(clip_int)
        arcpy.analysis.Clip(input_fc, clip_features, clip_int, "1 meter")
        input_fc = clip_int
        Print3("Input dataset clipped to input:",log)

    ## cache dir definition/creation should be refactored to settings
    ## but it's here for now..
    cache_dir = os.path.join(settings['cli-gis-directory'],'_cache')
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)
        
    # project input dataset to WGS84 (this should happen by default)
    def get_trans(in_sr_name):
        if "1927" in in_sr_name:
            trans = settings['trans-nad27-wgs84']
        elif "1983" in in_sr_name:
            trans = settings['trans-nad83-wgs84']
        elif "1984" in in_sr_name:
            return False
        else:
            arcpy.AddError("problem finding transformation between "\
                "these geographic coordinate systems. try manually "\
                "projecting this dataset to a NAD83- or WGS84-based spatial "\
                "reference, and rerun this tool.\n")
            
    if keep_native:
        arcpy.AddMessage("keeping native spatial reference:\n{}\n".format(in_sr.name))
    else:
        in_sr = arcpy.Describe(input_fc).spatialReference
        trans = get_trans(in_sr.name)
        if trans:
            arcpy.AddMessage("projecting input dataset to WGS 84, using "\
                            "transformation: "+trans+"\n")
            proj_int = os.path.join(os.path.join(cache_dir,"import_wgs84.shp"))
            TakeOutTrash(proj_int)
            arcpy.management.Project(input_fc,proj_int,WGS84prj,trans)
            input_fc = proj_int
        else:
            arcpy.AddMessage("input dataset is already in GCS WGS84, "\
                "no reprojection needed.\n")

    arcpy.management.CopyFeatures(input_fc, intermediate)
    Print3("Input dataset copied:",log)
    
    # TakeOutTrash(clip_int)
    # TakeOutTrash(proj_int)

    ct1 = int(arcpy.management.GetCount(intermediate).getOutput(0))
    ct2 = int(arcpy.management.GetCount(input_fc).getOutput(0))
    Print3("{0} feature{1} in the original feature layer, {2} will be "\
        "added to the scratch geodatabase.".format(
            str(ct2),"" if ct2==1 else "s",str(ct1)),log)

    #MERGE WITH BLANK STANDARDS FEATURE CLASS

    #check to see if any of the fields that will be added in the merge
    #process already exist in the input feature dataset.  If one does
    #exist, it will cause a problem.
    Print3("\nFIELD MAPPING DETAILS:\nmaking sure no original field names"\
        " will cause problems...",log)
    info_printed = False
    
    a = arcpy.ListFields(intermediate)
    bfields = ["OBJECTID","FID"]
    int_fields = [f for f in a if not f.required and not f.name in bfields]
    stan_fields = arcpy.ListFields(standards_match)      

    dropFields = []

    for intf in int_fields:
        fname = intf.name
        ftype = intf.type
        flen = intf.length

        for stanf in stan_fields:
            sfname = stanf.name
            sftype = stanf.type
            sflen = stanf.length

            if fname != sfname:
                break
            elif ftype == sftype and flen <= sflen:
                Print3("-- Values from field {0} will be carried over from "\
                      "original dataset".format(fname),log)
                info_printed = True
                break
            else:
                usename = fname + "_OLD"
                counter = 1
                while not usename in [i.name for i in int_fields]:
                    usename = fname + "_OLD" + str(counter)
                    counter+=1
                arcpy.management.AddField(intermediate, usename, ftype)
                info_printed = True
                try:
                    arcpy.management.CalculateField(intermediate,
                        usename,'[' + fname + ']')
                    Print3("-- Values from field {0} were transferred to new "\
                           "field {1}".format(fname,usename),log)
                except:
                    Print3("-- There was an error while transferring values "\
                           "from field {0} to new field {1}".format(
                               fname,usename),log)
                dropFields.append(fname)

    if not info_printed:
        Print3("  no field mapping required",log)
            
    #merge newly created temporary file with selected standards fc
    output_dataset = os.path.join(gdb_path,"imp_" + shrtName)
    TakeOutTrash(output_dataset)
    arcpy.management.Merge([intermediate, standards_match], output_dataset)
    Print3("\nnew feature class named \"imp_" + shrtName + "\".",log)

    #ADD FIELDS/ASSIGN DOMAINS, IF NECESSARY:
    shapetype = arcpy.Describe(output_dataset).shapeType.lower()

    #remove domain from bndtype field and assign all inclusive bnd_type domain
    arcpy.management.RemoveDomainFromField(output_dataset,"BND_TYPE")
    if shapetype == "point":
        arcpy.management.AssignDomainToField(
            output_dataset,"BND_TYPE","BND_TYPEpt")
    if shapetype == "polyline":
        arcpy.management.AssignDomainToField(
            output_dataset,"BND_TYPE","BND_TYPEln")
    if shapetype == "polygon":
        arcpy.management.AssignDomainToField(
            output_dataset,"BND_TYPE","BND_TYPEpy")
    
    #"fclass" field used to sort each record into the appropriate standards fc
    #and assign appropriate domain, depending on shape type
    f_names = [f.name.upper() for f in arcpy.ListFields(output_dataset)]
    
    shape_dict = {"point":"fclass_pt",
                  "polyline":"fclass_ln",
                  "polygon":"fclass_py"}
    for shape, domain in shape_dict.iteritems():
        if shape == shapetype:
            if not "FCLASS" in f_names:
                arcpy.management.AddField(
                    output_dataset, "fclass","TEXT","","",50,"","","",domain)
                Print3("New field \"fclass\" has been added "\
                    "and domain \"" + domain + "\" has been assigned to it.\n",log)
            else:
                arcpy.management.AssignDomainToField(
                    output_dataset,"fclass",domain)
                        
    ## update attributes based on input variable dictionary
    arcpy.AddMessage("\n...populating fields based on user input:\n")

    ## print summary
    keys = variable_dictionary.keys()
    keys.sort()
    for k in keys:
        if variable_dictionary[k] == "":
            continue
        Print3("{0} = {1}".format(k,variable_dictionary[k]),log)
 
    ## make list of fields for update cursor
    all_input_fields = [i for i,v in variable_dictionary.iteritems() if (not\
                            v.startswith("code: ") and not v == '')]
    reduced_fields = [i for i in all_input_fields if i.upper() in f_names]

    for fi in arcpy.ListFields(output_dataset):
        if fi.name == "OBJECTID" and fi.required:
            oidfield = "OBJECTID"
        elif fi.name == "OBJECTID_1" and fi.required:
            oidfield = "OBJECTID_1"
        else:
            pass
    reduced_fields.insert(0,oidfield)

    urows = arcpy.da.UpdateCursor(output_dataset,reduced_fields)
    for urow in urows:
        OID = urow[0]
        for index in range(1,len(reduced_fields)):
            urow[index] = variable_dictionary[reduced_fields[index]]
        try:
            urows.updateRow(urow)
        except:
            arcpy.AddWarning("  in field: " + reduced_fields[index])
            arcpy.AddWarning("    problem updating OID: " + str(OID))
    del urows

    #calculate any fields that had a "code: " value entered
    arcpy.AddMessage(" ")
    for field, value in variable_dictionary.iteritems():
        if value[:6] == "code: ":
            exp = value[6:]
            arcpy.AddMessage("using field calculator to interpret input for "+field)
            arcpy.AddMessage("  "+value)
            try:
                arcpy.management.CalculateField(output_dataset, field,
                                            exp, "PYTHON")
            except:
                Print3("New values for " + field + " were not " +\
                        "calculated correctly. Expression entered was:\n"\
                           + exp + "\n\nRemember, the expression will be "\
                           "parsed as Python.",log)

    #delete intermediate clip fc
    TakeOutTrash(intermediate)

    log.close()

    # except:

        # tb = sys.exc_info()[2]
        # tbinfo = traceback.format_tb(tb)[0]
        # pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                # + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        # msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

        # arcpy.AddMessage(msgs)
        # arcpy.AddMessage(pymsg)
        # arcpy.AddMessage(arcpy.GetMessages(1))

        # log.close()

def MergeCRLinkTables(input_table,target_table):
    """ Merges two CR Link tables, and makes sure that no progam IDs
    are lost in the process.  If conflicting IDs are found for certain
    programs in the same CR_ID, a log is created."""

    ## append input table to target table
    arcpy.management.Append(input_table,target_table,"NO_TEST")

    ## consolite table
    ConsolidateCRLinkTable(target_table)

def ProcessFeatureClass(feature_class,target_gdb):
    '''Takes the features from the input feature class and sorts them based
    on the fclass field value into the appropriate feature class in the
    provided target_gdb.'''

    Print(feature_class)

    stan_fcs = ["crsite_pt","crsite_ln","crsite_py",
                "crstru_pt","crstru_ln","crstru_py",
                "crothr_pt","crothr_ln","crothr_py",
                "crbldg_pt","crbldg_py",
                "crobj_pt","crobj_ln","crobj_py",
                "crsurv_pt","crsurv_ln","crsurv_py",
                "crland_py","crdist_py"]

    ## get all of the unique fclass values in the input feature class
    rows = arcpy.SearchCursor(feature_class,"","","fclass")
    targets = [i.getValue('fclass') for i in rows if not i == "None"]

    ## return function if there are no features with fclass values
    if len(targets) == 0:
        Print('  ...no features with an "fclass" value in this feature class.')
        return

    for fclass in targets:

        ## skip if there is a value value from the fclass field
        if not fclass in stan_fcs:
            Print("  bad fclass value: " + fclass)
            Print("  (any feature with this value will be skipped)" )
            continue

        TakeOutTrash("fl")
        fl = arcpy.management.MakeFeatureLayer(
                            feature_class,"fl",'"fclass" = \'' + fclass + '\'')
        ct = int(arcpy.management.GetCount(fl).getOutput(0))

        for path in MakePathList(target_gdb):
            if path.endswith(fclass):
                arcpy.management.Append(fl,path,"NO_TEST")

        Print("  {0} feature{1} appended to {2}".format(
                                str(ct),'' if ct == 1 else 's',fclass))

def ProjectGDBtoNAD83(geodatabase,gdbtype,transformation):
    """takes a standards gdb or scratch gdb (this must be specified) and
    "reprojects" all of the feature classes into a NAD83 version"""
    if gdbtype == "Standards":
        NAD83_gdb = GDBstandard
    elif gdbtype == "Scratch":
        arcpy.AddMessage("WARNING: The contents of a 'Scratch' geodatabase can"\
        "vary significantly, and this tool is not designed to handle every"\
        "possible situation. Be sure to inspect the output geodatabase carefully"\
        "and be ready to make some further changes if necessary.")
        NAD83_gdb = GDBscratch
    else:
        raise Exception("geodatabase type must either be 'Scratch' or 'Standards'")
    
    arcpy.AddMessage("\nPROJECTING TO NAD83 and APPENDING FEATURE CLASSES")

    ## make new file geodatabase to hold the new table
    output_location = os.path.dirname(geodatabase)
    output_name = os.path.basename(geodatabase)[:-4] + "_NAD83"
    new_NAD83_gdb = os.path.join(output_location,output_name)
    new_name = new_NAD83_gdb

    r = 1
    while os.path.isdir(new_name + ".gdb"):
        new_name = new_NAD83_gdb+"_"+str(r)
        r+=1

    new_NAD83_gdb = new_name + ".gdb"
    os.makedirs(new_NAD83_gdb)
    for f in os.listdir(WGS84_gdb):
        if not f.endswith(".lock"):
            shutil.copy2(os.path.join(WGS84_gdb,f), new_NAD83_gdb)

    trans = settings['trans-nad83-wgs84']
    arcpy.AddMessage("\nOutput geodatabase: "+new_NAD83_gdb)
    arcpy.AddMessage("\nTransformation used: "+trans)


    a83paths = MakePathList(geodatabase,True)
    a84paths = MakePathList(new_NAD83_gdb,True)

    for path in a83paths:

        fcname = os.path.basename(path)
        arcpy.AddMessage("\n"+fcname)
        if fcname == "crland_py":
            continue

        ## skip if there are no features in the feature class
        ct = int(arcpy.management.GetCount(path).getOutput(0))
        if ct == 0:
            arcpy.AddMessage("  ...no features")
            continue
        else:
            arcpy.AddMessage("  {0} feature{1}".format(
                ct,'' if ct ==1 else "s"))

        ## project to temporary shapefile in the CLI_GIS directory
        temp = r"{0}\temp.shp".format(settings['cli-gis-directory'])
        TakeOutTrash(temp)
        arcpy.management.Project(path,temp,wgs84,trans)
        arcpy.AddMessage("  projected to WGS84")
        
        ## append to appropriate feature class
        for p in a84paths:
            if p.endswith(fcname):

                arcpy.management.Append(temp,p,"NO_TEST")
                arcpy.AddMessage("    ...appended")
        TakeOutTrash(temp)

    ## append link and catalog tables to new geodatabase
    if gdb_type == "Standards":
        arcpy.AddMessage("\nAPPENDING TABLES\n")

        old_cr_link = os.path.join(geodatabase,"CR_Link")
        old_cr_catalog = os.path.join(geodatabase,"CR_Catalog")

        new_cr_link = old_cr_link.replace(geodatabase,new_NAD83_gdb)
        new_catalog_link = old_cr_catalog.replace(geodatabase,new_NAD83_gdb)

        for x,y in [(old_cr_link,new_cr_link),(old_cr_catalog,new_catalog_link)]:
            arcpy.AddMessage("  "+os.path.basename(x))
            arcpy.management.Append(x,y,"NO_TEST")

    arcpy.AddMessage("\n--process finished--")
    
    pass
                                
def ScratchToStandardsGDB(scratch_gdb,feature_classes,target_gdb=False):
    """Converts a scratch geodatabase into a CLI Standards geodatabase.  If
    the user supplies a target geodatabase, the features from the scratch
    gdb will be appended to the feature classes in the target. At present
    time, this function does not deal with the CR_link table at all, so the
    user will have to Make GUIDs in the new geodatabase (or target), and
    also will have to Sync CR_Link to get everything updated."""

    if not target_gdb:
        
        new_gdb_path = scratch_gdb.replace("scratch","standards")
        new_gdb = MakeBlankGDB(GDBstandard_WGS84,new_gdb_path)

    else:
        new_gdb = target_gdb
        
    arcpy.AddMessage(new_gdb)

    arcpy.AddMessage("\nFeatures will be migrated to:\n{0}".format(new_gdb))

    ## make list of all possible paths
    paths = MakePathList(new_gdb)

    ## iterate through the input feature classes
    scratch_fcs = ["scratch_pt","scratch_ln","scratch_py"]
    for fc in feature_classes:
        if not fc in scratch_fcs and not fc[:4] == "imp_":
            continue
        
        arcpy.AddMessage("\n"+fc)
        
        fc_path = os.path.join(scratch_gdb,fc)
        total = 0

        cursor = arcpy.da.SearchCursor(fc_path,"fclass")
        fvals = [s[0] for s in cursor if not s[0] == None]
        del cursor
        if len(fvals) == 0:
            arcpy.AddMessage("--no features to migrate--")
            continue

        ## trim down full path list to only include the necessary ones.
        trimlist = []
        for fv in fvals:
            for p in paths:
                if p.endswith(fv) and not p in trimlist:
                    trimlist.append(p)

        ## iterate through each potential target feature classes, append any
        ## features whose fclass values match that target feature class
        for path in trimlist:

            name = os.path.basename(path)
            query = '"fclass" = \'' + name + "'"
            fl = "fl"
            TakeOutTrash(fl)
            arcpy.management.MakeFeatureLayer(fc_path,fl,query)
            ct = int(arcpy.management.GetCount(fl).getOutput(0))
            if ct == 0:
                continue
                
            arcpy.AddMessage("  {0} feature{1} to be added to {2}".format(
                ct,'' if ct == 1 else 's',name))
            
            src_sr = arcpy.Describe(fc_path).spatialReference
            src_epsg = src_sr.GCS.GCScode
            targ_sr = arcpy.Describe(path).spatialReference
            targ_epsg = targ_sr.GCS.GCScode
            both_epsgs = [src_epsg,targ_epsg]
            
            if src_epsg == targ_epsg:
                pass
            ## transform between NAD27 and NAD83
            if 4267 in both_epsgs and 4269 in both_epsgs:
                transformation = 'NAD_1927_To_NAD_1983_NADCON'
                
            ## transform between NAD27 and WGS84
            elif 4267 in both_epsgs and 4326 in both_epsgs:
                transformation = settings['trans-nad27-wgs84']
                
            ## transform between NAD83 and WGS84
            elif 4269 in both_epsgs and 4326 in both_epsgs:
                transformation = settings['trans-nad83-wgs84']
            else:
                arcpy.AddMessage("Not prepared to project/transform to or from one"\
                "or both of the spatial references involved:\nsource: {}\n target:{}"\
                "\nPlease manually project to a spatial reference that uses NAD83"\
                " (EPSG:4269), NAD27 (EPSG:4267), or WGS84 (EPSG:4326), and then"\
                "re-run this tool")
                exit()
                
            ## if the target and source match, all good!
            if not src_epsg == targ_epsg:
                arcpy.AddMessage("    projecting from {} to {}".format(src_sr.name,targ_sr.name))
                arcpy.AddMessage("    transformation: {}".format(transformation))
                
                temp_fc = os.path.join(settings['cache'],"temp.shp")
                TakeOutTrash(temp_fc)
                arcpy.management.Project(fc_path,temp_fc,targ_sr,transformation)
                arcpy.management.Append(temp_fc,path,"NO_TEST")
                TakeOutTrash(temp_fc)
            
            else:
                arcpy.management.Append(fl,path,"NO_TEST")

            arcpy.AddMessage("      ...done")
            total+=ct

        arcpy.AddMessage("  --{0} total feature{1} migrated".format(
                total,'' if total == 1 else 's'))

    arcpy.AddMessage("\nProcessing finished.\n")

def SpatialAndCLI_IDCompareForGUIDs(featurelayer1='',featurelayer2=''):
    """This function will return a list of GEOM_IDs from featurelayer1
    that are multiple representations of CLI features in featurelayer2.
    The GUIDs returned will be for those features in  that overlap a
    "larger" representation of the same CLI feature (i.e. have the same
    CLI_ID). It is intended that 1 will be a "smaller" feature class shape
    than 2, e.g. 1 will be a point feature class, and 2 is a line or
    polygon feature class.

    This function is similar to the TransferCR_IDs function.
    """

    ## skip if one of the inputs is empty
    ct1a = int(arcpy.management.GetCount(featurelayer1).getOutput(0))
    ct2a = int(arcpy.management.GetCount(featurelayer2).getOutput(0))
    if ct1a == 0 or ct2a == 0:
        return []

    ## make selection on 1st input
    arcpy.management.SelectLayerByAttribute(featurelayer1,"CLEAR_SELECTION")
    arcpy.management.SelectLayerByLocation(
        featurelayer1, "INTERSECT", featurelayer2)
    cnt1 = int(arcpy.management.GetCount(featurelayer1).getOutput(0))
    
    xshape = arcpy.Describe(featurelayer1).shapeType.lower()
    yshape = arcpy.Describe(featurelayer2).shapeType.lower()
    Print("    comparing {0}s to {1}s".format(xshape,yshape))
    if cnt1 == 0:
        return []
    
    ## create list of cli_ids in second layer
    all_cli_ids = [i[0] for i in arcpy.da.SearchCursor(featurelayer2,"CLI_ID")]

    ## if any of the selected features in featurelayer1 have a cli_id
    ## in the all_cli_ids list, get the GEOM_ID from it because it's a multiple
    guid_list = []
    for row in arcpy.da.SearchCursor(featurelayer1,["CLI_ID","GEOM_ID"]):
        if row[0] in all_cli_ids:
            guid_list.append(row[1])
    guid_list = [str(i) for i in guid_list]

    return guid_list

def StandardsToStandardsGDB(in_geodatabase,target_gdb):
    '''This function will take an input geodatabase and merge with an existing
    target geodatabase.  The input and target must both already be in the
    CLI Standard format.
    '''

    all_paths = MakePathList(in_geodatabase,True)
    dest_paths = MakePathList(target_gdb,True)

    ## check for CR Catalog and CR Link tables
    cr_cat = os.path.join(in_geodatabase,"CR_Catalog")
    cr_link = os.path.join(in_geodatabase,"CR_Link")
    crtables = [cr_cat,cr_link]
    for t in crtables:
        if not arcpy.Exists(t):
            arcpy.AddWarning("\nThe input geodatabase is missing its "\
                "CR Link or CR Catalog table.\nCreate these tables using "\
                "the 'Sync CR Link and Catalog' tool.\n")

    for path in all_paths:

        if not arcpy.Exists(path):
            continue

        ct = int(arcpy.management.GetCount(path).getOutput(0))
        Print("{0}: {1} input feature{2}".format(os.path.basename(path),
            str(ct),"s" if not ct == 1 else ""))
        if ct == 0:
            continue

        ## if the feature class already exists in the target gdb, use append
        name = os.path.basename(path)

        ap = False
        for p in dest_paths:
            if p.endswith(os.path.basename(path)):
                arcpy.management.Append(path,p,"NO_TEST")
                Print(" appended to " + name)
                ap = True
        if ap:
            continue
       
        ## if the feature class doesn't exist, copy it.
        target_path = path.replace(in_geodatabase,target_gdb)
        arcpy.management.CopyFeatures(path,target_path)
        Print(" copied to " + name)
            
    ## append CR Catalog
    cr_cat_new = cr_cat.replace(in_geodatabase,target_gdb)
    arcpy.management.Append(cr_cat,cr_cat_new,"NO_TEST")

    ## merge CR Link tables
    cr_link_new = cr_link.replace(in_geodatabase,target_gdb)
    MergeCRLinkTables(cr_link,cr_link_new)

def StandardsToWGS84(geodatabase):
    """ Creates a version of the input standards geodatabase with all of the
    feature classes projected to WGS84."""

    arcpy.AddMessage("\nPROJECTING TO WSG84 and APPENDING FEATURE CLASSES")

    ## get path to template WGS84 version of GDB, and prj file
    ## WGS84_gdb = os.path.join(bin_dir,"CLI_standard_template_WGS84.gdb")
    ## wgs84 = os.path.join(bin_dir,'projection data','WGS 1984.prj')
    WGS84_gdb = GDBstandard_WGS84
    wgs84 = WGS84prj

    ## make new file geodatabase to hold the new table
    output_location = os.path.dirname(geodatabase)
    output_name = os.path.basename(geodatabase)[:-4] + "_WGS84"

    new_WGS84_gdb = os.path.join(output_location,output_name)
    new_name = new_WGS84_gdb

    r = 1
    while os.path.isdir(new_name + ".gdb"):
        new_name = new_WGS84_gdb+"_"+str(r)
        r+=1

    new_WGS84_gdb = new_name + ".gdb"
    os.makedirs(new_WGS84_gdb)
    for f in os.listdir(WGS84_gdb):
        if not f.endswith(".lock"):
            shutil.copy2(os.path.join(WGS84_gdb,f), new_WGS84_gdb)

    trans = settings['trans-nad83-wgs84']
    arcpy.AddMessage("\nOutput geodatabase: "+new_WGS84_gdb)
    arcpy.AddMessage("\nTransformation used: "+trans)
    arcpy.AddMessage("(transformation can be changed with the Configure Toolbox tool)")

    a83paths = MakePathList(geodatabase,True)
    a84paths = MakePathList(new_WGS84_gdb,True)

    for path in a83paths:

        fcname = os.path.basename(path)
        arcpy.AddMessage("\n"+fcname)
        if fcname == "crland_py":
            continue

        ## skip if there are no features in the feature class
        ct = int(arcpy.management.GetCount(path).getOutput(0))
        if ct == 0:
            arcpy.AddMessage("  ...no features")
            continue
        else:
            arcpy.AddMessage("  {0} feature{1}".format(
                ct,'' if ct ==1 else "s"))

        ## project to temporary shapefile in the CLI_GIS directory
        drive_letter = geodatabase[0]
        temp = r"{0}\temp.shp".format(settings['cli-gis-directory'])
        TakeOutTrash(temp)
        arcpy.management.Project(path,temp,wgs84,trans)
        arcpy.AddMessage("  projected to WGS84")
        
        ## append to appropriate feature class
        for p in a84paths:
            if p.endswith(fcname):

                arcpy.management.Append(temp,p,"NO_TEST")
                arcpy.AddMessage("    ...appended")
        TakeOutTrash(temp)

    ## append link and catalog tables to new geodatabase
    arcpy.AddMessage("\nAPPENDING TABLES\n")

    old_cr_link = os.path.join(geodatabase,"CR_Link")
    old_cr_catalog = os.path.join(geodatabase,"CR_Catalog")

    new_cr_link = old_cr_link.replace(geodatabase,new_WGS84_gdb)
    new_catalog_link = old_cr_catalog.replace(geodatabase,new_WGS84_gdb)

    for x,y in [(old_cr_link,new_cr_link),(old_cr_catalog,new_catalog_link)]:
        arcpy.AddMessage("  "+os.path.basename(x))
        try:
            arcpy.management.Append(x,y,"NO_TEST")
        except:
            arcpy.AddMessage("  ~~error encountered, skipping~~")

    arcpy.AddMessage("\n--process finished--")

def SyncCRLinkAndCRCatalog(in_gdb):
    """Analyzes a geodatabase, and creates or updates the
    CR Link table and CR Catalog.  
    """

    arcpy.AddMessage("\nInput Geodatabase:\n{0}".format(in_gdb))

    ## Check for edit session
    for f in os.listdir(in_gdb):
        if f.endswith("ed.lock"):
            arcpy.AddError("\nERROR: Close edit session in geodatabase.\n")
            return

    ## Make CR_Link table if necessary
    cr_link = os.path.join(in_gdb,"CR_Link")

    in_link_fields = ("CR_ID","SURVEY_ID","LCS_ID","NRIS_ID","NHL_ID",
        "HABS_HAER_ID","ASMIS_ID","NADB_ID","CLI_ID","CWSS_ID","TAX_ID",
        "ANCS_ID","ERI_ID","FMSS_ID","RESNAME","CLI_ID","LAND_CHAR")
    link_fields = {
        "CR_ID":50,
        "SURVEY_ID":50,
        "LCS_ID":50,
        "NRIS_ID":50,
        "NHL_ID":50,
        "HABS_HAER_ID":50,
        "ASMIS_ID":50,
        "NADB_ID":50,
        "CLI_ID":50,
        "CWSS_ID":50,
        "TAX_ID":50,
        "ANCS_ID":50,
        "ERI_ID":50,
        "FMSS_ID":50,
        "RESNAME":250,
        "CLI_ID":50,
        "LAND_CHAR":50
        }

    if arcpy.Exists(cr_link):
        arcpy.AddMessage("\nCR Link table found in geodatabase.")
        ## make sure it has the right fields
        missing = []
        for f in in_link_fields:
            if not f in [i.name for i in arcpy.ListFields(cr_link)]:
                missing.append(f)
        if missing:
            arcpy.AddError("ERROR: The CR Link table is missing fields:"\
            "\n"+"\n".join(missing)+"\n\nAdd these fields (field type = "\
            "TEXT, field length = 100) and rerun the tool.")
            return
    else:
        ##add table and fields
        arcpy.management.CreateTable(in_gdb,"CR_Link")
        for name in in_link_fields:
            arcpy.management.AddField(cr_link,name,"TEXT",'','',link_fields[name])
        arcpy.AddMessage("\nCreated new CR Link table.")

    ## make CR Catalog table if necessary
    cr_catalog = os.path.join(in_gdb,"CR_Catalog")
    
    in_cat_fields = ("CR_ID","SURVEY_ID","GEOM_ID","RESNAME","RESTRICT_","ORIGINATOR",
        "REG_CODE","ALPHA_CODE","FEATURE_CLASS_NAME","RESOURCE_TYPE","PROGRAM_COLLECTION")
    cat_fields = {
        "CR_ID":50,
        "SURVEY_ID":50,
        "GEOM_ID":50,
        "RESNAME":250,
        "RESTRICT_":50,
        "ORIGINATOR":250,
        "REG_CODE":50,
        "ALPHA_CODE":50,
        "FEATURE_CLASS_NAME":50,
        "RESOURCE_TYPE":50,
        "PROGRAM_COLLECTION":50
        }

    if arcpy.Exists(cr_catalog):
        arcpy.AddMessage("CR_Catalog table found in geodatabase.")
        ## make sure it has the right fields
        current_fields = [i.name for i in arcpy.ListFields(cr_catalog)]
        missing = [i for i in in_cat_fields if not i in current_fields]
        if len(missing) > 0:
            arcpy.AddError("\nERROR: The CR Catalog table is missing fields:"\
            "\n"+"\n".join(missing)+"\n\nBest idea is to delete the table "\
            "and rerun tool. Back up the geodatabase first, just in case.")
            return
    else:
        ##add table and fields
        arcpy.management.CreateTable(in_gdb,"CR_Catalog")
        for name in in_cat_fields:
            arcpy.management.AddField(cr_catalog,name,"TEXT",'','',cat_fields[name])
        arcpy.AddMessage("Created new CR Catalog.")

    ## make list of feature classes
    feature_classes = MakePathList(in_gdb)
  
    ## iterate through all feature classes and create dictionary of all guids
    ## and info for the catalog table
    arcpy.AddMessage("\nCollecting information from all feature classes...")
    catalog_info = {}
    for fc in feature_classes:
        print os.path.basename(fc)
        
        fields = ["SURVEY_ID","GEOM_ID","RESNAME","RESTRICT_","ORIGINATOR",
        "REG_CODE","ALPHA_CODE","Program_Collection","CR_ID"]

        ## modify field list for survey feature classes so error isn't thrown
        if "SURV" in fc.upper():
            fields = ["SURVEY_ID","GEOM_ID","RESNAME","RESTRICT_","ORIGINATOR",
        "REG_CODE","ALPHA_CODE","Program_Collection"]

        ## make fc_name and resource type values
        desc = arcpy.Describe(fc)
        
        shape = desc.shapeType.lower()
        if shape == "point":
            suf = "pt"
        elif shape == "polyline":
            suf = "ln"
        elif shape == "polygon":
            suf = "py"
        else:
            suf = "xx"

        if "BLDG" in fc.upper():
            fc_name = "crbldg_" + suf
            restype = "Historic Building"
        elif "OBJ" in fc.upper():
            fc_name = "crobj_"+suf
            restype = "Historic Object"
        elif "SURV" in fc.upper():
            fc_name = "crsurv_"+suf
            restype = "Surveyed Area"
        elif "OTHR" in fc.upper():
            fc_name = "crothr_"+suf
            restype = "Other Cultural Resource"
        elif "DIST" in fc.upper():
            fc_name = "crdist_"+suf
            restype = "Historic District"
        elif "SITE" in fc.upper():
            fc_name = "crsite_"+suf
            restype = "Historic Site"
        elif "STRU" in fc.upper():
            fc_name = "crstru_"+suf
            restype = "Historic Structure"
        else:
            fc_name = "xxxxxx_"+suf
            restype = "XXXXXX"
            arcpy.AddMessage(fc + ": problem")
            print fc + ": problem"
            
        for row in arcpy.da.SearchCursor(fc,fields):
            
            g_id = row[1]
            
            ## skip if it's a null guid or empty string
            if g_id == None or str(g_id).rstrip() == '':
                continue
            
            surv_id = row[0]
            resname = row[2]
            restrict = row[3]
            orig = row[4]
            r_code = row[5]
            a_code = row[6]
            prog_coll = row[7]
            if "SURV" in fc.upper():
                cr_id = ''
            else:
                cr_id = row[8]

            catalog_info[g_id] = [cr_id,surv_id,resname,restrict,orig,
                                  r_code,a_code,fc_name,restype,prog_coll]

    arcpy.AddMessage("  total number of features in feature classes: "\
                     +str(len(catalog_info.keys())))

    ## get existing GEOM_IDs from CR_Catalog
    ex_geo_guids = [r[0] for r in arcpy.da.SearchCursor(cr_catalog,"GEOM_ID")]
    ex_num = len(ex_geo_guids)

    ## print number of existing rows if there are any
    if not ex_num == 0:
        arcpy.AddMessage("  {0} row{1} already in CR Catalog".format(
            ex_num,"" if ex_num == 1 else "s"))

        ## remove any existing rows from catalog if they are not in fcs
        remove_guids = [i for i in ex_geo_guids if not i in catalog_info.keys()]
        n_remove_guids = len(remove_guids)
        if not n_remove_guids == 0:
            tv = "tv"
            TakeOutTrash(tv)
            query = '"GEOM_ID" IN (\'{0}\')'.format("','".join(remove_guids))
            arcpy.management.MakeTableView(cr_catalog,tv,query)
            arcpy.management.DeleteRows(tv)
            arcpy.AddMessage("  {0} row{1} removed that are not in feature "\
        "classes".format(n_remove_guids,"" if n_remove_guids == 1 else "s"))

    ## write new rows to catalog if their GEOM_ID is not already in there      
    arcpy.AddMessage("\nWriting new rows to CR_Catalog...")
    cursor = arcpy.da.InsertCursor(cr_catalog,in_cat_fields)
    counter = 0
    for k,v in catalog_info.iteritems():
        if not k in ex_geo_guids:
            cursor.insertRow((v[0],v[1],k,v[2],v[3],v[4],v[5],v[6],v[7],v[8],v[9]))
            counter+=1

    arcpy.AddMessage("  {0} row{1} written".format(counter,
                           '' if counter == 1 else 's'))
    del cursor

    ## update preexisting rows in catalog
    cursor = arcpy.da.UpdateCursor(cr_catalog,in_cat_fields)
    counter = 0
    for row in cursor:
        if row[2] in ex_geo_guids:
            v = catalog_info[row[2]]
            row[0] = v[0]
            row[1] = v[1]
            row[3] = v[2]
            row[4] = v[3]
            row[5] = v[4]
            row[6] = v[5]
            row[7] = v[6]
            row[8] = v[7]
            row[9] = v[8]
            row[10] = v[9]
            cursor.updateRow(row)
            counter+=1
    del cursor
    arcpy.AddMessage("  {0} row{1} updated".format(counter,
                           '' if counter == 1 else 's'))
    
    ## update CR Link table
    fc_cr_ids = [catalog_info[i][0] for i in catalog_info.keys()]
    
    ## append all features to the CR Link table
    arcpy.AddMessage("\nAppending all feature classes to the CR Link table...")
    try:
        for path in feature_classes:
            temp = r"in_memory\temp"
            TakeOutTrash(temp)
            arcpy.management.CopyRows(path,temp)
            arcpy.management.Append(temp,cr_link,"NO_TEST")
            ct = int(arcpy.management.GetCount(temp).getOutput(0))
            arcpy.AddMessage("  {0}, {1} feature{2}".format(
                os.path.basename(path),ct,"" if ct == 1 else "s"))
    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

        arcpy.AddError(msgs)
        arcpy.AddError(pymsg)

        print msgs

        print pymsg
        
        arcpy.AddMessage(arcpy.GetMessages(1))
        print arcpy.GetMessages(1)

    ## consolidate cr link table
    log = ConsolidateCRLinkTable(cr_link,fc_cr_ids)
    
    arcpy.AddMessage("\nAll processes finished.\n")

    ## open log file so user can't ignore it
    if log:
        os.startfile(log)

def TransferCR_IDs(x,y):
    """This function takes two input feature classes.  The features from
    the first feature class will be compared to those in the second,
    and if they overlap and have the same CLI_ID, the CR_ID from the first
    will be transferred to the second."""
    
    xshape = arcpy.Describe(x).shapeType.lower()
    yshape = arcpy.Describe(y).shapeType.lower()
    no_cliid = '"CLI_ID" IS NOT NULL'

    if not "CLI_ID" in [f.name for f in arcpy.ListFields(x)] or\
       not "CLI_ID" in [f.name for f in arcpy.ListFields(y)]:
       arcpy.AddWarning("Transfer process cannot be carried out if "\
        "either feature class does not have CLI_ID field.")
       return

    try:
        arcpy.management.SelectLayerByAttribute(x,"CLEAR_SELECTION")
        arcpy.management.SelectLayerByAttribute(y,"CLEAR_SELECTION")
        arcpy.management.SelectLayerByLocation(x,"INTERSECT",y,"","")
        arcpy.management.SelectLayerByLocation(y,"INTERSECT",x,"","")
        cnt1 = int(arcpy.management.GetCount(x).getOutput(0))
        arcpy.AddMessage("    comparing {0}s to {1}s...".format(xshape,yshape))
        if cnt1 == 0:
            arcpy.AddMessage(
                "      no overlapping features between feature classes.")
            return
        
        #create necessary lists/dictionary
        all_cli_ids = []
        
        srows = arcpy.da.SearchCursor(x,"CLI_ID",no_cliid)
        for srow in srows:
            cli_id = srow[0]
            all_cli_ids.append(cli_id)
        del srows, srow, cli_id
        problem_cli_ids = {}
        good_cli_ids = []
        srows = arcpy.da.SearchCursor(x,["CLI_ID","CR_ID","OBJECTID"],no_cliid)
        for srow in srows:
            oid = srow[2]
            cr_id = srow[1]
            cli_id = srow[0]
            if all_cli_ids.count(cli_id) > 1:
                problem_cli_ids[oid] = cr_id
            else:
                good_cli_ids.append(cli_id) 
        del srows, srow, cli_id, oid, cr_id
        
        #update all cr_ids that have only one geometry in the x argument
        #i.e. those with cli_ids in the good_cli_ids list
        singles = 0
        srows = arcpy.da.SearchCursor(x,["CR_ID","CLI_ID"],no_cliid)
        for srow in srows:
            cid = srow[1]
            cr = srow[0]
            if cid in good_cli_ids:
                q = "CLI_ID = '" + cid + "'"
                urows = arcpy.da.UpdateCursor(y,["CR_ID","CLI_ID"],q)
                for urow in urows:
                    singles += 1
                    urow[0] = cr
                    urows.updateRow(urow)
        del cid, cr, srow, srows
        if not singles == 0:
            arcpy.AddMessage("      {0} single geometry feature{1} updated.".format(
                str(singles),"" if singles == 1 else "s"))

        #update all cr_ids with multiple geometries, those in the problem list
        #by cycling through each individual feature (using the oid as a selection
        #query)
        multiples = 0
        for oid,cr_id in problem_cli_ids.iteritems():
            qx = "OBJECTID = " + str(oid)
            arcpy.management.SelectLayerByAttribute(x,"",qx)
            arcpy.management.SelectLayerByLocation(y,"INTERSECT",x,"","")
            srows = arcpy.da.SearchCursor(x,"CLI_ID",no_cliid)
            for srow in srows:
                cidx = srow[0]
                if cidx == None:
                    continue
                urows = arcpy.da.UpdateCursor(y,["CLI_ID","CR_ID","OBJECTID"],no_cliid)
                for urow in urows:
                    cidy = urow[0]
                    if cidx == cidy:
                        multiples += 1
                        urow[1] = cr_id
                        urows.updateRow(urow)
            del srow, srows, urow, urows, cidx, cidy   
        if multiples > 0:
            arcpy.AddMessage("      {0} multiple geometry feature{1} updated.".format(
                str(multiples),"" if multiples == 1 else "s"))

        #final default print statement
        if multiples == 0 and singles == 0:
            arcpy.AddMessage("      no overlapping features between feature classes.")
    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

        arcpy.AddError(msgs)
        arcpy.AddError(pymsg)

        print msgs

        print pymsg
        
        arcpy.AddMessage(arcpy.GetMessages(1))
        print arcpy.GetMessages(1)

def UpdateFieldInGDB(input_geodatabase,field,old_val_list,new_val):
    """Takes a list of old values that (presuambly) already exist in the
    input field somewhere within the input geodatabase.  It cycles through
    the entire input geodatabase and replaces any occurrences of the old
    values with the supplied new value."""

    #make list of paths in gdb
    path_list = MakePathList(input_geodatabase)

    arcpy.AddMessage("\nFor field \"{0}\", changing...\n\n{1}\n\nto '{2}'\n".format(
        field, "\n".join(old_val_list), new_val))

    #add NoneType to list if null values should be updated
    if "<Null>" in old_val_list:
        old_val_list.append(None)

    try:
        #iterate through all paths
        for path in path_list:
            rec_count = int(arcpy.management.GetCount(path).getOutput(0))
            if rec_count == 0:
                continue
            #only update feature classes that contain the field to be updated
            f_list = []
            for f in arcpy.ListFields(path):
                if str(f.name) not in f_list:
                    f_list.append(str(f.name))
            if field in f_list:
                update_count = 0
                arcpy.AddMessage("Updating {0}:".format(os.path.basename(path)))
                rows = arcpy.UpdateCursor(path,"","",field + ";OBJECTID")
                for row in rows:
                    a = row.getValue(field)
                    try:
                        value = str(a).encode('ascii','ignore')
                    except:
                        oid = str(row.getValue("OBJECTID"))
                        arcpy.AddWarning("ERROR: problem with OID: {0}".format(oid))
                        del a
                        continue
                            
                    #make sure the string "None" is not misinterpreted as null
                    if value == "None":
                        value = "<Null>"

                    #set "" values to null, just because it's useful
                    if value == "":
                        row.setValue(field, None)
                        continue
                    
                    if value in old_val_list:
                        update_count += 1
                        if new_val == "code: Null":
                            row.setValue(field, None)
                        else:
                            row.setValue(field, new_val)

                    try:
                        rows.updateRow(row)
                    except:
                        arcpy.AddWarning("\nERROR: problem writing " + new_val)
                arcpy.AddMessage("  {0} records updated (of {1})".format(
                        str(update_count),str(rec_count)))
        arcpy.AddMessage("\n")
        
    except:
        
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

        arcpy.AddError(msgs)
        arcpy.AddError(pymsg)

        print msgs

        print pymsg
        
        arcpy.AddMessage(arcpy.GetMessages(1))
        print arcpy.GetMessages(1)


