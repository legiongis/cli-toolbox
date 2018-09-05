__doc__ =\
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
import os
import shutil
import sys
import traceback
import time
import xlrd
import logging
from .config import settings

from .general import (
    TakeOutTrash,
    MakePathList,
    GetParkTypeDictionary,
    FieldCalculateRegionCode,
    StartLog
    )

from .paths import (
    GDBstandard,
    GDBstandard_link,
    GDBstandard_WGS84,
    NAD83prj,
    BinGDB,
    FeatureLookupTable,
    UnitLookupTable
    )
    
def InspectMXD(map_document):
    """ logs the names and fields of all layers and table views in the mxd"""
    
    log = StartLog(name='InspectMXD')
    log.debug("~~~ INSPECTING MAP DOCUMENT CONTENTS ~~~")
    
    layers = arcpy.mapping.ListLayers(map_document)
    tables = arcpy.mapping.ListTableViews(map_document)
    log.debug("number of layers: "+str(len([l for l in layers if not l.isGroupLayer])))
    log.debug("number of table views: "+str(len(tables)))
    
    log.debug("~~~ LAYER DETAILS ~~~")
    for layer in layers:
        if layer.isGroupLayer:
            continue
        log.debug("LAYER NAME: "+layer.name)
        try:
            log.debug("data source: "+layer.dataSource) 
        except NameError:
            log.debug("data source: n/a") 
        try:
            ct = str(arcpy.management.GetCount(layer).getOutput(0))
        except:
            ct = "n/a"
        log.debug("feature count: "+ct)
        try:
            fields = [f.name for f in arcpy.ListFields(layer)]
            fields.sort()
            log.debug("fields: "+",".join(fields))
        except:
            log.debug("fields: n/a")
        
    
    log.debug("~~~ TABLE VIEW DETAILS ~~~")
    for table in tables:
        log.debug("TABLE VIEW NAME: "+table.name)
        try:
            log.debug("data source: "+table.dataSource) 
        except NameError:
            log.debug("data source: n/a") 
        try:
            ct = str(arcpy.management.GetCount(table).getOutput(0))
            log.debug("row count: "+ct)
        except:
            log.debug("row count: n/a")
        try:
            fields = [f.name for f in arcpy.ListFields(table)]
            fields.sort()
            log.debug("fields: "+",".join(fields))
        except:
            log.debug("fields: n/a")
    
    return
        
def CheckForEnterpriseTables(map_document):
    """ Check the input map document for the three tables that are necessary
    for exporting or analyzing data in the CR Enterprise:
    CLI Feature Table, CR Link Table, and CR Catalog Table

    Returns False if one of the three is missing from table of contents."""

    arcpy.AddMessage("\nChecking for necessary tables...")

    tableviews = arcpy.mapping.ListTableViews(map_document)
    cli_table, cr_link_table, cr_catalog = False,False,False
    for t in tableviews:
        tsource = t.dataSource.upper()
        if "CLI_FEATURE_TABLE" in tsource and "DBO" in tsource:
            cli_table = t
        if "CR_LINK" in tsource and "DBO" in tsource:
            cr_link_table = t
        if "CR_CATALOG" in tsource and "DBO" in tsource:
            cr_catalog = t
    t_list = [cli_table, cr_link_table, cr_catalog]

    if False in [cli_table, cr_link_table, cr_catalog]:
        arcpy.AddError("\nThese three tables must be present in the map "\
            " docmument:\n\nCR LINK TABLE\nCR CATALOG TABLE\n"\
            "CLI FEATURE TABLE(...)\n\nMake you are using the CR_Enterprise_"\
            "Public_Access.mxd map document when you run this tool.\n")
        raise Exception

    arcpy.AddMessage("    all tables present")
    return t_list
    
def GetTableFieldsList(template_table):
    """Returns a dictionary of field names and lengths that can be iterated
    to create a new GDB table"""
    
    fields = []
    for f in arcpy.ListFields(template_table):
        if f.name == "OBJECTID":
            continue
        fields.append((f.name,f.length))
    return fields

def ConvertFeatureXLSToGDBTable(input_xls,retain_copy=False,update_local=False):
    """
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
    """
    try:
        ## print initial summary
        arcpy.AddMessage("\nInput MS Excel spreadsheet:")
        arcpy.AddMessage(input_xls)

        ## create workbook object for input workbook.
        bookrd = xlrd.open_workbook(input_xls, formatting_info=True)
        sheet = bookrd.sheet_by_index(0)
        
        ## get field names from workbook (and their index number)
        xls_fields_dict = {}
        for col_x in range(sheet.ncols):
            colname = sheet.cell(0,col_x).value
            xls_fields_dict[colname] = col_x

        expected_fields = ['CLI_ID',
                            'RESNAME',
                            'CONTRIB_STATUS',
                            'LAND_CHAR',
                            'CLI_NUM',
                            'CLI_NAME',
                            'UNIT_CLASS',
                            'LCS_NAME',
                            'LCS_ID',
                            'HS_ID',
                            'ALPHA_CODE',
                            'PARK_NAME',
                            'REGION_NAME',
                            'Type of FMSS Record',
                            'FMSS Record Number',
                            'ASMIS ID',
                            'ASMIS Name'
                            ]
                            
        ## check the fields of the input table
        arcpy.AddMessage("\nChecking fields of input spreadsheet...")
        missing = [i for i in expected_fields if not i in xls_fields_dict.keys()]
        if len(missing) > 0:
            arcpy.AddMessage("  the following expected fields are missing from the XLS file:")
            arcpy.AddMessage("  "+",".join(missing))
            raise Exception("Missing fields in XLS file. Check documentation and correct file before retrying.")
        else:
            arcpy.AddMessage("  all good.")
        
        ## read all the FMSS info into a dictionary for use later
        fmss_dict = {}
        for row in range(1,sheet.nrows):
            cli_id_cell_val = str(sheet.cell(row,0).value)
            cli_id = cli_id_cell_val[:6].rstrip(".")
            fmss_type = sheet.cell(row,xls_fields_dict["Type of FMSS Record"]).value
            fmss_id_raw = sheet.cell(row,xls_fields_dict["FMSS Record Number"]).value
            fmss_id = str(fmss_id_raw).split(".")[0]
            if fmss_id == "":
                continue
            if not cli_id in fmss_dict.keys():
                fmss_dict[cli_id] = {"LOCATION":"","ASSET":""}
            if fmss_type == "Asset":
                fmss_dict[cli_id]["ASSET"] = fmss_id
            elif fmss_type == "Location":
                fmss_dict[cli_id]["LOCATION"] = fmss_id

        ## read all information from table into dictionaries, one for features
        ## and one for boundaries, cast all values as strings.
        arcpy.AddMessage("\nCollecting all values from input table...")
        f_table_dict = {}
        b_table_dict = {}
        for row in range(1,sheet.nrows):
            
            cli_id_cell_val = str(sheet.cell(row,0).value)
            cli_id = cli_id_cell_val[:6].rstrip(".")
            val_dict = {}
            for i in range(1,sheet.ncols):
                colname = sheet.cell(0,i).value
                val = sheet.cell(row,i).value
                try:
                    val2 = val.encode('ascii','ignore').rstrip()
                except:
                    val2 = str(val).split(".")[0]
                
                val_dict[colname] = val2

            ## add the list of values to the correct dictionary, based on
            ## whether it is a feature or a boundary
            land_char_cell_val = str(sheet.cell(row,xls_fields_dict["LAND_CHAR"]).value)
            if land_char_cell_val == "Boundary":
                if cli_id in b_table_dict.keys():
                    arcpy.AddWarning("CLI_NUM {0} encountered twice. Best "\
                "practice is to remake the input XLS file following documentation.")
                b_table_dict[cli_id] = val_dict
            else:
                if cli_id in f_table_dict.keys():
                    arcpy.AddWarning("CLI_ID {0} encountered twice. Best "\
                "practice is to remake the input XLS file following documentation.")
                f_table_dict[cli_id] = val_dict
        arcpy.AddMessage("  all values collected.")

        arcpy.AddMessage("\nWriting all data to new CLI Feature Table...")
        
        TakeOutTrash(r"in_memory\cli_feature_table")
        new_table = arcpy.management.CreateTable("in_memory","cli_feature_table")

        ## add all fields to the new table based on the existing CLIFeatureTable_CREnterprise
        ## in the BinGDB
        new_table_fields = GetTableFieldsList(os.path.join(BinGDB,"CLIFeatureTable_CREnterprise"))
        for f in new_table_fields:
            arcpy.management.AddField(new_table,f[0],"TEXT",
                field_length=f[1])

        ## write all rows from dictionaries to the new table
        type_dict = GetParkTypeDictionary()
        in_curse = arcpy.InsertCursor(new_table)
        for d in [f_table_dict,b_table_dict]:
            for k in d.keys():
                row = in_curse.newRow()
                row.setValue("CLI_ID", k)
                
                ## set all fields that have corresponding names b/t the xls
                ## and the gdb table
                for f in new_table_fields:
                    if f[0] in d[k].keys():
                    
                        ## truncate value if necessary, generally only for RESNAME
                        value = d[k][f[0]][:f[1]]
                        row.setValue(f[0], value)
                    
                ## set PARK_TYPE manually
                if d[k]["ALPHA_CODE"] in type_dict.keys():
                    ptype = type_dict[d[k]["ALPHA_CODE"]]
                else:
                    ptype = ""
                row.setValue("PARK_TYPE",ptype)
                
                ## set FMSS fields manually
                if k in fmss_dict.keys():
                    if fmss_dict[k]["LOCATION"]:
                        row.setValue("FMSS_ID",fmss_dict[k]["LOCATION"])
                    if fmss_dict[k]["ASSET"]:
                        row.setValue("FMSS_Asset_ID",fmss_dict[k]["ASSET"])
                
                in_curse.insertRow(row)

        del in_curse
        
        ## calculating region code field
        FieldCalculateRegionCode(new_table,"REGION_NAME")
        
        arcpy.AddMessage("  all rows written.")
        
        ## if local table should be updated, copy new table there
        if update_local:
            arcpy.AddMessage("\nUpdating local tables...")

            new_cli_table = os.path.join(BinGDB,"CLIFeatureTable_CREnterprise")
            TakeOutTrash(new_cli_table)
            arcpy.management.CopyRows(new_table,new_cli_table)

            ## make new unit table in local table from new feature table
            MakeLocalTablesFromCLIFeatureTable(BinGDB)
            
        if retain_copy:
            
            arcpy.AddMessage("\nSaving a copy of the new CLI Feature Table here:")

            ## make new file geodatabase to hold the retained copy of the table
            gdb_path = os.path.join(settings['cli-gis-directory'],"CLI_InfoTable_" + time.strftime("%m%d%y")+".gdb")
            basename = os.path.basename(gdb_path)
            r = 1
            while os.path.isdir(gdb_path):
                gdb_path = os.path.join(os.path.dirname(gdb_path),basename.rstrip(".gdb")+"_" + str(r) + ".gdb")
                r+=1
            arcpy.management.CreateFileGDB(os.path.dirname(gdb_path),os.path.basename(gdb_path))
            arcpy.AddMessage("  "+gdb_path)

            arcpy.management.CopyRows(new_table,os.path.join(gdb_path,"CLI_Feature_Table_"+time.strftime("%m%d%y")))
            
            arcpy.AddMessage("This table can be used to update the corresponding "\
            "table in the CR Enterprise database.")
        arcpy.AddMessage("\n--process finished--\n")

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

def ExtractFromEnterpriseSelection(map_document,output_location,
    only_cr_link=False,transform=False,trans_type='NAD_1983_To_WGS_1984_1'):
    """This function must be used from the CR Enterprise Access map
    document.  Any currently selected features are downloaded to a new
    geodatabase.  The user can chose to only download the CR Link table
    records for all selected features."""

    try:
        InspectMXD(map_document)
        tables = CheckForEnterpriseTables(map_document)
        if not tables:
            return
        else:
            cli_table = tables[0]
            cr_link_table = tables[1]
            cr_catalog = tables[2]

        ## make new gdb to hold extract
        if only_cr_link:
            blank_gdb = GDBstandard_link
            new_gdb = os.path.join(output_location,time.strftime(
                "EntSelect_CRLink_%Y%b%d_%H%M".format(query_code)))
        elif not transform:
            blank_gdb = GDBstandard_WGS84
            new_gdb = os.path.join(output_location,time.strftime(
                "EntSelect_Spatial_%Y%b%d_%H%M".format(query_code)))
        else:
            blank_gdb = GDBstandard
            new_gdb = os.path.join(output_location,time.strftime(
                "EntSelect_Spatial_%Y%b%d_%H%M_NAD83".format(query_code)))
        
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

        arcpy.AddMessage("\nOutput Geodatabase:\n{0}\n".format(new_gdb))
        dest_paths = MakePathList(new_gdb)

        if not only_cr_link:
            arcpy.AddMessage("---DOWNLOADING SPATIAL DATA---\n")
        else:
            arcpy.AddMessage("---DOWNLOADING TABULAR DATA---\n")

        ## make path list for all potential destination feature classes in new gdb
        dest_paths = MakePathList(new_gdb,True)

        ## iterate through layers and export any selected features
        copy = r"in_memory\copy"
        cr_ids_in_fcs = []
        geom_ids_in_fcs = []
        cr_id_resname = {}
        total_feat = 0

        totaltime = 0
        for layer in arcpy.mapping.ListLayers(map_document):

            a = time.time()

            ## get datasource name for layer
            if not layer.supports("DATASOURCE"):
                continue
            lyr_src = layer.dataSource.lower()

            ## print layer name
            arcpy.AddMessage(layer)

            ## skip if there's no selection on feature class
            desc = arcpy.Describe(layer)
            selection = []
            try:
                selection = desc.FIDSet
            except:
                selection = []
            if len(selection) == 0:
                arcpy.AddMessage("    ...no features")
                continue

            ## find appropriate path in destination geodatabase
            out_path = False
            for dpath in dest_paths:
                if lyr_src.find(os.path.basename(dpath)) != -1:
                    out_path = dpath
                    break
            if not out_path:
                arcpy.AddWarning("    there is no appropriate path match "\
                    "for this layer")
                ss = time.time()-a
                sss = str(ss).split(".")[0]
                arcpy.AddMessage("      {0} seconds elapsed".format(sss))
                continue

            ## get cr ids from the layer
            with arcpy.da.SearchCursor(layer,("CR_ID","GEOM_ID","RESNAME")) as curse:
                for r in curse:
                    c = str(r[0])
                    if not c in cr_ids_in_fcs:
                        cr_ids_in_fcs.append(c)
                        cr_id_resname[c] = r[2]
                    g = str(r[1])
                    if not g in geom_ids_in_fcs:
                        geom_ids_in_fcs.append(g)

            ## don't append features if only the cr_link is desired
            if only_cr_link:
                cnt = len(cr_ids_in_fcs)
                arcpy.AddMessage("    {0} cultural resource{1} selected".format(
                    cnt, '' if cnt == 1 else "s"))
                continue

            ## print count of features
            ct = int(arcpy.management.GetCount(layer).getOutput(0))
            arcpy.AddMessage("    {0} spatial feature{1} selected".format(
                    ct, '' if ct == 1 else "s"))

            ## transform feature class if desired
            if transform:
                ## copy features before projecting them
                copy = r"in_memory\copy"
                TakeOutTrash(copy)
                arcpy.management.CopyFeatures(layer,copy)

                ## project copied layer to temporary NAD83 version
                proj = r"{0}\proj".format(new_gdb)
                TakeOutTrash(proj)
                arcpy.management.Project(copy,proj,NAD83prj,trans_type)
                
                src = proj
            
            else:
                src = layer
 
            ## finally, append the features to the destination path
            arcpy.management.Append(src,dpath,"NO_TEST")
            arcpy.AddMessage("    feature{0} exported to {1}".format(
                '' if ct == 1 else "s",os.path.basename(dpath)))
                
            total_feat+=ct

            ss = time.time()-a
            sss = str(ss).split(".")[0]
            arcpy.AddMessage("      {0} seconds elapsed".format(sss))
            totaltime += time.time()-a

        a = totaltime/60
        mins = str(a).split(".")[0]
        decsecs = str(a).split(".")[1]
        secs = str(int(float("0."+decsecs)*60))[:2]
        arcpy.AddMessage(
            "\nTotal time: {0} minute(s), {1} seconds\n".format(mins,secs))

        if not only_cr_link:
            arcpy.AddMessage("\nTotal features exported: " + str(total_feat))
            arcpy.AddMessage("\n---DOWNLOADING TABULAR DATA---")

        arcpy.AddMessage("\nCR Link")

        ## make query from collected cr_ids, apply to cr_link
        cr_id_qry = '"CR_ID" IN (\'{0}\')'.format("','".join(cr_ids_in_fcs))
        arcpy.management.SelectLayerByAttribute(cr_link_table,"NEW_SELECTION",cr_id_qry)

        ## append Link table to new gdb table
        new_cr_link = os.path.join(new_gdb,"CR_Link")
        arcpy.management.Append(cr_link_table,new_cr_link,"NO_TEST")
        arcpy.AddMessage("    {0} row{1} exported".format(len(cr_ids_in_fcs),
            "" if len(cr_ids_in_fcs) == 1 else "s"))

        ## append Catalog table to new gdb table
        if not only_cr_link:
            arcpy.AddMessage("\nCR Catalog")
            new_cr_catalog = os.path.join(new_gdb,"CR_Catalog")

            geom_id_qry = '"GEOM_ID" IN (\'{0}\')'.format(
                "','".join(geom_ids_in_fcs))
            arcpy.management.SelectLayerByAttribute(
                cr_catalog,"NEW_SELECTION",geom_id_qry)
            arcpy.management.Append(cr_catalog,new_cr_catalog,"NO_TEST")
            ct = int(arcpy.management.GetCount(new_cr_catalog).getOutput(0))
            arcpy.AddMessage("    {0} row{1} exported".format(ct,
                "" if ct == 1 else "s"))

        ## print statement
        arcpy.AddMessage("\n---POPULATING CLI FIELDS IN EXPORTED DATA---")
        
        ## get cli_ids from link table
        arcpy.AddMessage("getting list of CLI_IDs from CR Link")
        cli_cr_dict = {}
        curse = arcpy.da.SearchCursor(new_cr_link,["CLI_ID","CR_ID","LCS_ID","FMSS_ID","FMSS_Asset_ID"])
        for row in curse:
            if not row[1] in cli_cr_dict.keys():
                cli_cr_dict[row[1]] = [row[0],row[2],row[3],row[4]]
        cli_id_list = set([v[0] for k,v in cli_cr_dict.iteritems() if not v[0] == None])
        cli_id_qry = '"CLI_ID" IN (\'{0}\')'.format("','".join(cli_id_list))

        ## get cli_info from the feature table
        arcpy.AddMessage("getting CLI_NUM and LAND_CHAR values from CLI"\
                        " Feature Table")
        fields = ["CLI_ID","CLI_NUM","LAND_CHAR","RESNAME"]
        cli_info = {}
        with arcpy.da.SearchCursor(cli_table,fields,cli_id_qry) as cursor:
            for row in cursor:
                if not row[0] in cli_info.keys():
                    cli_info[row[0]] = [row[1],row[2],row[3]]

        ## add CLI information to records in CR Link with CLI_ID
        arcpy.AddMessage("writing RESNAME, CLI_NUM and LAND_CHAR values to CR Link")
        dest_paths_nosurv = MakePathList(new_gdb)
        fields = ["CLI_ID","CLI_NUM","LAND_CHAR","RESNAME","CR_ID"]
        with arcpy.da.UpdateCursor(new_cr_link,fields) as cursor:
            for row in cursor:
                cid = row[0]

                if cid in cli_info.keys():
                    row[1] = cli_info[cid][0]
                    row[2] = cli_info[cid][1]
                    row[3] = cli_info[cid][2]

                else:
                    row[3] = cr_id_resname[row[4]]
                
                cursor.updateRow(row)

        ## finish function if only the cr link table is needed
        if only_cr_link:
            arcpy.AddMessage("\nexport complete\n")
            return

        ## add CLI information to all features in all new feature classes
        arcpy.AddMessage("writing CLI_ID, LCS_ID, FMSS_ID, CLI_NUM and LAND_CHAR values to spatial data")
        dest_paths_nosurv = MakePathList(new_gdb)
        for path in dest_paths_nosurv:
            fields = ["CR_ID","CLI_ID","CLI_NUM","LAND_CHAR","LCS_ID","FMSS_ID","FMSS_Asset_ID"]
            with arcpy.da.UpdateCursor(path,fields) as cursor:
                for row in cursor:
                    if not row[0] in cli_cr_dict.keys():
                        continue

                    ## write to rows
                    cinfo = cli_cr_dict[row[0]]
                    c = cinfo[0]
                    if c in cli_info.keys():
                        row[1] = c
                        row[2] = cli_info[c][0]
                        row[3] = cli_info[c][1]
                    
                    row[4] = cinfo[1]
                    row[5] = cinfo[2]
                    row[6] = cinfo[3]
                    cursor.updateRow(row)

        arcpy.AddMessage("\nexport complete\n")
        return
    
    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        print msgs
        print pymsg
        print arcpy.GetMessages(1)
        arcpy.AddError(msgs)
        arcpy.AddError(pymsg)
        arcpy.AddError(arcpy.GetMessages(1))    

def ExtractFromEnterpriseQuery(map_document,query_code,output_location,
    only_cr_link=False,transform=False,trans_type="NAD_1983_To_WGS_1984_1"):
    """This function must be used from the CR Enterprise Access map
    document.  It will take the input query code and extract all data that
    matches it from each layer in the table of contents.  The user may only
    download the CR Link table for these records, if desired."""

    try:
        log = StartLog(name='ExtractFromEnterpriseQuery')
        ## make feature table queries based on input query code
        if len(query_code) == 3:
            tbl_query = '"REGION_NAME" = \''+query_code.upper()+"'"
            qry_lvl = "region"
        elif len(query_code) == 4:
            tbl_query = '"ALPHA_CODE" = \''+query_code.upper()+"'"
            qry_lvl = "park"
        elif len(query_code) == 6:
            tbl_query = '"CLI_NUM" = \''+query_code+"'"
            qry_lvl = "landscape"
        else:
            arcpy.AddError("\nThis input code is invalid.  Double check and try "\
                "again.\n")
            return False
        
        log.debug("tbl_query:" + tbl_query)
        log.debug("qry_lvl:" + qry_lvl)

        ## check for tables
        InspectMXD(map_document)
        tables = CheckForEnterpriseTables(map_document)
        if not tables:
            return
        else:
            cli_table = tables[0]
            cr_link_table = tables[1]
            cr_catalog = tables[2]
            
        log.debug("cli_table: " + str(tables[0]))
        log.debug("fields: " + ",".join([f.name for f in arcpy.ListFields(tables[0])]))
        log.debug("cr_link_table: " + str(tables[1]))
        log.debug("fields: " + ",".join([f.name for f in arcpy.ListFields(tables[1])]))
        log.debug("cr_catalog: " + str(tables[2]))
        log.debug("fields: " + ",".join([f.name for f in arcpy.ListFields(tables[2])]))

        ## print query
        arcpy.AddMessage("\nQuery Used: {0}".format(tbl_query))

        ## make new gdb to hold extract
        if only_cr_link:
            blank_gdb = GDBstandard_link
            new_gdb = os.path.join(output_location,time.strftime(
                "Ent{0}_CRLink_%Y%b%d_%H%M".format(query_code)))
        elif not transform:
            blank_gdb = GDBstandard_WGS84
            new_gdb = os.path.join(output_location,time.strftime(
                "Ent{0}_Spatial_%Y%b%d_%H%M".format(query_code)))
        else:
            blank_gdb = GDBstandard
            new_gdb = os.path.join(output_location,time.strftime(
                "Ent{0}_Spatial_%Y%b%d_%H%M_NAD83".format(query_code)))
        
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
                
        log.debug("blank output gdb created: "+new_gdb)
        arcpy.AddMessage("\nOutput Geodatabase:\n{0}".format(new_gdb))

        ## make path list for all potential destination feature classes in new gdb
        dest_paths = MakePathList(new_gdb,True)
        
        ## get set of cli_ids and info from the feature table
        arcpy.AddMessage("\nGetting list of CLI_IDs matching query...")
        log.debug("getting list of cli_ids matching query")
        
        id_dict = {}
        arcpy.management.SelectLayerByAttribute(cli_table,"NEW_SELECTION",
            tbl_query)
        
        feat_ct = str(arcpy.management.GetCount(cli_table).getOutput(0))
        log.debug(feat_ct+" rows selected in cli table")
        log.debug("now collecting CLI_ID and CLI_NUM info from cli table")
        fields = ["CLI_ID","CLI_NUM","LAND_CHAR","ALPHA_CODE",
                    "REGION_NAME","RESNAME"]
        log.debug("cursor fields: "+",".join(fields))
        with arcpy.da.SearchCursor(cli_table,fields) as cursor:
            for row in cursor:
                if not row[0] in id_dict.keys():
                    id_dict[row[0]] = [row[i] for i in range(1,len(fields))]
                else:
                    arcpy.AddWarning("    {0}, this CLI_ID occurs TWICE "\
                        "in the CLI Feature Table!!".format(row[0]))

        ## make list from dictionary keys
        id_list = id_dict.keys()
        n = len(id_list)
        arcpy.AddMessage("    {0} CLI_ID{1} found".format(
            n,'' if n == 1 else 's'))
        log.debug("cli_ids collected: "+str(n))

        arcpy.AddMessage("\n---DOWNLOADING TABULAR DATA---\n")
        log.debug("DOWNLOADING TABULAR DATA")

        ## download CR Link table new gdb table
        arcpy.AddMessage("CR Link")
        new_cr_link = os.path.join(new_gdb,"CR_Link")
        cli_id_qry = '"CLI_ID" IN (\'{0}\')'.format("','".join(id_list))
        log.debug("cli_id_qry: "+cli_id_qry)
        log.debug(len(cli_id_qry))
        log.debug("selecting from the cr link table based on cli_id_query")
        arcpy.management.SelectLayerByAttribute(cr_link_table,"NEW_SELECTION",
            cli_id_qry)
        log.debug("selection made. appending cr_link_table to new_cr_link table.")
        arcpy.management.Append(cr_link_table,new_cr_link,"NO_TEST")
        log.debug("append completed")
        ct = int(arcpy.management.GetCount(new_cr_link).getOutput(0))
        arcpy.AddMessage("    {0} row{1} exported".format(ct,
            "" if ct == 1 else "s"))
        log.debug("append completed")
        log.debug("fields in new CR Link table:")
        for field in arcpy.ListFields(new_cr_link):
            log.debug(field.name)

        ## add CLI information to records in CR Link with CLI_ID
        arcpy.AddMessage("    writing CLI_NUM and LAND_CHAR values to CR Link")
        fields = ["CLI_ID","CLI_NUM","LAND_CHAR","RESNAME"]
        with arcpy.da.UpdateCursor(new_cr_link,fields) as cursor:
            for row in cursor:
                cid = row[0]

                if cid in id_dict.keys():
                    row[1] = id_dict[cid][0]
                    row[2] = id_dict[cid][1]
                    row[3] = id_dict[cid][4]
                cursor.updateRow(row)

        ## stop early if only CR Link is needed
        if only_cr_link:
            arcpy.AddMessage("\nexport finished\n")
            return
        
        ## get list of cr_ids from the cr link table
        arcpy.AddMessage("\nCR Catalog")
        arcpy.AddMessage("    getting list of CR_IDs for all CLI_IDs...") 
        cr_id_cli_id_dict = {}
        fields = ["CR_ID","CLI_ID","LCS_ID","FMSS_ID","FMSS_Asset_ID"]
        with arcpy.da.SearchCursor(cr_link_table,fields) as cursor:
            for row in cursor:
                cr = str(row[0])
                ci = str(row[1])
                ## don't mess with null values
                if ci == "None" or cr == "None" or not ci in id_list:
                    continue
                if not cr in cr_id_cli_id_dict.keys():
                    cr_id_cli_id_dict[cr] = [ci,row[2],row[3],row[4]]
        cr_id_list = cr_id_cli_id_dict.keys()
        cr_id_list.sort()
        n = len(cr_id_list)
        arcpy.AddMessage("    {0} CR_ID{1} found".format(
            n,'' if n == 1 else 's'))

        ## sanitize cr_id_list
##        arcpy.AddMessage("double-checking CR IDs...")
##        cr_ids_in_cat = [r[0] for r in arcpy.da.SearchCursor(cr_catalog,
##                                                        "CR_ID")]
##        for x in cr_id_list:
##            if not x in cr_ids_in_cat:
##                arcpy.AddMessage("ERROR: CR_ID "+str(x))
##        cr_id_list = [i for i in cr_id_list if i in cr_ids_in_cat]
##        arcpy.AddMessage("CR ID list sanitized")

        if qry_lvl == "region":
            cr_id_qry = '"REG_CODE" = \''+query_code.upper()+"'"
        elif qry_lvl == "park":
            cr_id_qry = tbl_query
        else:
            cr_id_qry = '"CR_ID" IN (\'{0}\')'.format("','".join(cr_id_list))
            
        log.debug("cr_id_qry: "+cr_id_qry)
        
        arcpy.management.SelectLayerByAttribute(cr_catalog,
            "NEW_SELECTION",cr_id_qry)
        with arcpy.da.SearchCursor(cr_catalog,"FEATURE_CLASS_NAME") as c:
            fclasses = [row[0] for row in c]
        unique_fcs = set(fclasses)
        log.debug("pulling from these fclasses: "+",".join(unique_fcs))
        ct = int(arcpy.management.GetCount(cr_catalog).getOutput(0))
        arcpy.AddMessage("    {0} GEOM_ID{1} found".format(ct,
            "" if ct == 1 else "s"))

        ## download CR Catalog table new gdb table
        new_cr_catalog = os.path.join(new_gdb,"CR_Catalog")
        arcpy.management.Append(cr_catalog,new_cr_catalog,"NO_TEST")
        arcpy.AddMessage("    {0} row{1} exported".format(ct,
            "" if ct == 1 else "s"))

        arcpy.AddMessage("\n---DOWNLOADING SPATIAL DATA---\n")

        ## iterate through layers and apply cr_id query
        log.debug("iterating through layers and apply cr_id query")
        totaltime = 0
        for layer in arcpy.mapping.ListLayers(map_document):

        ## get datasource name for layer
            if not layer.supports("DATASOURCE"):
                continue
            lyr_src = layer.dataSource.lower()
           
            ## skip the feature class if no cli features are in it.
            log.debug(layer.name)
            arcpy.AddMessage(layer)
            a = time.time()
            skip = True           
            for f in unique_fcs:
                if lyr_src.find(f) != -1:
                    skip = False
            if skip:
                log.debug("    ...no features")
                arcpy.AddMessage("    ...no features")
                continue

            ## find appropriate path in destination geodatabase
            out_path = False
            for dpath in dest_paths:
                if lyr_src.find(os.path.basename(dpath)) != -1:
                    out_path = dpath
                    break
            if not out_path:
                arcpy.AddWarning("    there is no appropriate path match "\
                    "for this layer")
                ss = time.time()-a
                sss = str(ss).split(".")[0]
                arcpy.AddMessage("      {0} seconds elapsed".format(sss))
                continue

            ## make selection on layer based on cr id query
            
            arcpy.management.SelectLayerByAttribute(layer,"NEW_SELECTION",cr_id_qry)
            ct = int(arcpy.management.GetCount(layer).getOutput(0))
            arcpy.AddMessage("    {0} feature{1}".format(ct,'' if ct == 1 else 's'))
            
            ## transform feature class if desired
            if transform:
                ## copy features before projecting them
                copy = r"in_memory\copy"
                TakeOutTrash(copy)
                arcpy.management.CopyFeatures(layer,copy)

                ## project copied layer to temporary NAD83 version
                proj = r"{0}\proj".format(new_gdb)
                TakeOutTrash(proj)
                arcpy.management.Project(copy,proj,NAD83prj,trans_type)
                
                src = proj
            
            else:
                src = layer
 
            ## finally, append the features to the destination path
            arcpy.management.Append(src,dpath,"NO_TEST")
            arcpy.AddMessage("    feature{0} exported to {1}".format(
                '' if ct == 1 else "s",os.path.basename(dpath)))

            ss = time.time()-a
            sss = str(ss).split(".")[0]
            arcpy.AddMessage("      {0} seconds elapsed".format(sss))
            totaltime += time.time()-a

        a = totaltime/60
        mins = str(a).split(".")[0]
        decsecs = str(a).split(".")[1]
        secs = str(int(float("0."+decsecs)*60))[:2]
        arcpy.AddMessage(
            "\nTotal time: {0} minute(s), {1} seconds\n".format(mins,secs))

        ## add CLI information to all features in all new feature classes
        ## make new list of paths that excludes survey feature classes
        a = time.time()
        arcpy.AddMessage("\nwriting CLI_ID, FMSS_ID, LCS_ID, LAND_CHAR and CLI_NUM values to "\
            "exported features...")
        dest_paths_nosurv = MakePathList(new_gdb)
        for path in dest_paths_nosurv:
            fields = ["CR_ID","CLI_ID","CLI_NUM","LAND_CHAR","LCS_ID","FMSS_ID","FMSS_Asset_ID"]
            with arcpy.da.UpdateCursor(path,fields) as cursor:
                for row in cursor:
                    if not row[0] in cr_id_list:
                        continue

                    ## write to rows
                    cinfo = cr_id_cli_id_dict[row[0]]
                    c = cinfo[0]
                    row[1] = c
                    row[2] = id_dict[c][0]
                    row[3] = id_dict[c][1]
                    row[4] = cinfo[1]
                    row[5] = cinfo[2]
                    row[6] = cinfo[3]
                    cursor.updateRow(row)

        arcpy.AddMessage("\nexport finished\n")
        return

    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        print msgs
        print pymsg
        print arcpy.GetMessages(1)
        log.error(msgs)
        log.error(pymsg)
        log.error(arcpy.GetMessages(1))
        arcpy.AddError(msgs)
        arcpy.AddError(pymsg)
        arcpy.AddError(arcpy.GetMessages(1))

def MakeLocalTablesFromCLIFeatureTable(table_geodatabase):
    """This function will look in the input table geodatabase for a table
    called CLIFeatureTable, which should be created by any function that
    includes this function.  From that table, new versions of the
    FeatureLookupTable and UnitLookupTable are created to replace the old
    versions of those tables, using queries on the LAND_CHAR field.
    """

    try:
        ## intro print statement
        arcpy.AddMessage("\nCreating UnitLookupTable and FeatureLookupTable"\
        "tables from CLIFeatureTable...")

        ## locate existing feature info table
        cli_table = os.path.join(table_geodatabase,"CLIFeatureTable_CREnterprise")

        if not arcpy.Exists(cli_table):
            arcpy.AddError("\nThere is no CLIFeatureTable_CREnterprise in the input "\
                "geodatabase.  Run the Update Local CLI Tables tool from the"\
                "CR Enterprise Access map document.\n")
            return

        ## make table view of just the features rows in the cli table
        feat_qry = '"LAND_CHAR" <> \'Boundary\''
        feat_tv = "tv1"
        TakeOutTrash(feat_tv)
        arcpy.management.MakeTableView(cli_table,feat_tv,feat_qry)
        ct1 = int(arcpy.management.GetCount(feat_tv).getOutput(0))
        arcpy.AddMessage("  {0} features in the new "\
            "FeatureLookupTable".format(ct1))

        ## replace FeatureLookupTable with table view
        try:
            TakeOutTrash(FeatureLookupTable)
        except:
            arcpy.AddError("\nSome problem removing existing FeatureLookup"\
                "Table (can't get exclusive schema lock).  Make sure "
                "ArcCatalog is closed and try the process again.\n")
            return
        arcpy.management.CopyRows(feat_tv,FeatureLookupTable)

        ## make table view of just the boundary rows in the cli table
        bound_qry = '"LAND_CHAR" = \'Boundary\''
        bound_tv = "tv2"
        TakeOutTrash(bound_tv)
        arcpy.management.MakeTableView(cli_table,bound_tv,bound_qry)
        ct2 = int(arcpy.management.GetCount(bound_tv).getOutput(0))
        arcpy.AddMessage("  {0} features in the new "\
            "UnitLookupTable".format(ct2))

        ## replace FeatureLookupTable with table view
        TakeOutTrash(UnitLookupTable)
        arcpy.management.CopyRows(bound_tv,UnitLookupTable)

        ## remove the table views
        TakeOutTrash(feat_tv)
        TakeOutTrash(bound_tv)

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

def UpdateCLITables(map_document):
    """This tool takes no parameters.  It must be run from the CR Enterprise
    Access map document.  It uses the table view in the map document
    of the CLI Feature Table to pull information to the local lookup tables
    that are used in all of these functions throughout the clitools package.
    This tool should be run by the user every time the CR Enterprise
    version of the CLI Feature Table is updated."""

    result = CheckForEnterpriseTables(map_document)
    cli_table = result[0]

    if not cli_table:
        arcpy.AddError("The CLI Feature Table is not present in the current "\
            "map document, make sure you are using the CR_Enterprise_Public_"\
            "Access.mxd map document when you run this tool.")
        return False

    ## copy table to local geodatabase
    arcpy.AddMessage("\nCopying CLI Feature Table from CR Enterprise to "\
        "local toolbox geodatabase...")

    new_table = os.path.join(BinGDB,"CLIFeatureTable_CREnterprise")
    TakeOutTrash(new_table)
    arcpy.management.CopyRows(cli_table, new_table)
    arcpy.AddMessage("  table copied.")

    ## make local tables from newly downloaded table
    MakeLocalTablesFromCLIFeatureTable(BinGDB)

    arcpy.AddMessage("\n--process finished--\n")
