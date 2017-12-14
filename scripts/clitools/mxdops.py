__doc__ = \
"""Contains a set of functions that are intended for use while editing or
viewing CLI data in ArcMap.

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

import os
import arcpy
import traceback
import sys
import string
import time
from classes import MakeUnit

from general import (
    Print,
    TakeOutTrash,
    ConvertContribStatus,
    MakePathList,
    GetCRLinkAndCRCatalogPath
    )

from management import (
    GetMultiplesGUIDs,
    GetIDFieldGUIDs,
    GetCLI_IDGUIDs,
    GetGUIDsFromCatalog
    )

from paths import (
    LayerDir,
    FeatureLookupTable,
    UnitLookupTable,
    SourceLookupTable,
    BinGDB,
    MXDempty,
    WGS84prj,
    NAD83prj,
    NAD27prj,
    UTM83dir,
    UTM84dir,
    UTM27dir,
    SPdir
    )

grplayerpath = os.path.join(LayerDir,"grouplayer.lyr")

def GetZoneID(dataframe,pcs_type):
    """This function makes a polygon out of the input dataframe current,
    extent and using the specified zone shapefile (either UTM or state 
    plane), figures out which zone the current view is in.  It returns
    a warning if more than two zones are in the current view."""

    if pcs_type == "SP":
        shp = os.path.join(BinGDB,"usstpln83")
    elif pcs_type == "UTM":
        shp = os.path.join(BinGDB,"utm")
    else:
        arcpy.AddError("\nInvalid input.\n")
        return False
   
    lyr = "fl"
    TakeOutTrash(lyr)

    dfAsFeature = arcpy.Polygon(arcpy.Array([dataframe.extent.lowerLeft,
         dataframe.extent.lowerRight, dataframe.extent.upperRight,
          dataframe.extent.upperLeft]),dataframe.spatialReference)
    arcpy.management.MakeFeatureLayer(shp, lyr)
    arcpy.SelectLayerByLocation_management(lyr, "INTERSECT",
                                           dfAsFeature, "", "NEW_SELECTION")
    ct = int(arcpy.management.GetCount(lyr).getOutput(0))
    if ct == 1:
        rows = arcpy.SearchCursor(lyr,"","","ZONE")
        for row in rows:
            zoneNum = str(row.getValue("ZONE"))

        return zoneNum
      
    zone_sym = os.path.join(LayerDir,"zones.lyr")
    zone_lyr = arcpy.mapping.Layer(shp)
    arcpy.management.ApplySymbologyFromLayer(zone_lyr,zone_sym)
    zone_lyr.name = pcs_type
    arcpy.mapping.AddLayer(dataframe, zone_lyr)

    if ct > 1:
        arcpy.AddWarning("\nYou are looking at more than one "\
                         "zone right now.  Zone boundaries have been added to "\
                         "the display.  Pick one, zoom in until there are no "\
                         "boundaries visible in the current extent, and rerun "\
                         "tool.\n")
        return False

    else:
        arcpy.AddWarning("\nSome issue with the zone selection process."\
                         "  Zone boundaries have been added to "\
                         "the display.  Pick one, zoom in, and rerun tool.\n")
        return False

    TakeOutTrash(lyr)

def SetSpatialReference(map_document,pcs_or_gcs,datum_year,
                                zone='',pcs_type=''):
    '''Sets the input dataframe to the specified coordinate system, using
    the .prj files in the bin folder.'''

    mxd = map_document
    for d in arcpy.mapping.ListDataFrames(mxd):
        if d.name == mxd.activeView:
            df = d

    oldsr = df.spatialReference
    arcpy.AddMessage("\nCurrent spatial reference:\n{0}".format(
        oldsr.name))

    if pcs_or_gcs == "GCS":
        if datum_year == "1927":
            prj_file = NAD27prj
        elif datum_year == "1983":
            prj_file = NAD83prj
        elif datum_year == "1984":
            prj_file = WGS84prj
        else:
            arcpy.AddError("\ninvalid input\n")
            return

    if pcs_or_gcs == "PCS":

        if pcs_type == "SP":
            sp_dir = SPdir
            for prj in os.listdir(sp_dir):
                if zone in prj:
                    prj_file = os.path.join(sp_dir,prj)
        if pcs_type == "UTM":
            if datum_year == "1927":
                utm_dir = UTM27dir
            elif datum_year == "1983":
                utm_dir = UTM83dir
            elif datum_year == "1984":
                utm_dir = UTM84dir
            else:
                arcpy.AddError("\ninvalid input\n")
                return

            for prj in os.listdir(utm_dir):
                if " " + zone + "N.prj" in prj:
                    prj_file = os.path.join(utm_dir,prj)

    newsr = arcpy.SpatialReference(prj_file)
    if newsr.name == oldsr.name:
        arcpy.AddWarning("\nCurrent spatial reference matches new spatial "\
            "reference\n")
        return

    try:
        df.spatialReference = newsr
        arcpy.RefreshActiveView()
        arcpy.AddMessage("\nNew spatial reference:\n{0}\n".format(
    newsr.name))

    except:
        arcpy.AddError("\nError setting spatial reference, you probably "\
            "need to close an edit session.\n")


def MakeGroupLayerInTOC(map_document,data_frame,name):
    '''This function will create a group layer, place it in the dataframe,
    and return a layer object for that group layer in the table of
    contents. This is TOC layer is need to be able to add stuff to the group
    layer.'''

    topgrplyr = arcpy.mapping.Layer(grplayerpath)
    topgrplyr.name = name
    arcpy.mapping.AddLayer(data_frame,topgrplyr)
    topgrplyrTOC = arcpy.mapping.ListLayers(
        map_document,name,data_frame)[0]
    return topgrplyrTOC

def LayerByIDPresence(geodatabase,id_field,map_document,data_frame,query='',
        place_in_group=False,group_name='',label=False,omit_multiples=False):
    '''This function must use a CLI standards geodatabase, and by using the
    CR_Link table, it will display all of the features in the geodatabase
    in two separate group layers, based on whether or not the feature has
    an associated program id in the indicated field.

    Features can optionally be placed in a new group layer, labeled, or have
    multiple geometries for the same cli_id omitted.'''

    try:

        ## make all group layers and stuff
        if place_in_group:
            topgrplyr_name = "{0}, {1}".format(group_name,id_field)
            topgrplyrTOC = MakeGroupLayerInTOC(map_document,data_frame,topgrplyr_name)

        with_grplayer = arcpy.mapping.Layer(grplayerpath)
        with_grplayer_name = "Yes {0}".format(id_field)
        with_grplayer.name = with_grplayer_name

        without_grplayer = arcpy.mapping.Layer(grplayerpath)
        without_grplayer_name = "No {0}".format(id_field)
        without_grplayer.name = without_grplayer_name

        bnd_grplayer = arcpy.mapping.Layer(grplayerpath)
        bnd_grplayer.name = "Boundary Features"

        if place_in_group:
            arcpy.mapping.AddLayerToGroup(data_frame,topgrplyrTOC,bnd_grplayer)
            arcpy.mapping.AddLayerToGroup(data_frame,topgrplyrTOC,without_grplayer)
            arcpy.mapping.AddLayerToGroup(data_frame,topgrplyrTOC,with_grplayer)

        else:
            arcpy.mapping.AddLayer(data_frame,bnd_grplayer)
            arcpy.mapping.AddLayer(data_frame,without_grplayer)
            arcpy.mapping.AddLayer(data_frame,with_grplayer)
            
        with_layerTOC = arcpy.mapping.ListLayers(
                map_document,with_grplayer_name,data_frame)[0]
        without_layerTOC = arcpy.mapping.ListLayers(
                map_document,without_grplayer_name,data_frame)[0]
        bnd_layerTOC = arcpy.mapping.ListLayers(
                map_document,"Boundary Features",data_frame)[0]

        ## get path to cr link and catalog tables
        crpaths = GetCRLinkAndCRCatalogPath(geodatabase)
        cr_link_path = crpaths[0]
        cr_cat_path = crpaths[1]
        if not cr_link_path:
            arcpy.AddError("There is no CR Link table in this geodatabase, so this "\
                "operation cannot be performed.")
            return False
        if not cr_cat_path:
            arcpy.AddError("There is no CR Catalog table in this geodatabase, so this "\
                "operation cannot be performed.")
            return False

        paths = MakePathList(geodatabase)
        for path in paths:

            fc_name = str(os.path.basename(path).split(".")[-1])
            arcpy.AddMessage("\nFEATURE CLASS: " + fc_name)
            bound_guids = []

            ## get boundary features from dist and site feature classes            
            if fc_name.startswith("crdist") or fc_name.startswith("crsite"):

                ## append guids for boundary feature to bound guid list
                cursor = arcpy.da.SearchCursor(path,["LAND_CHAR","GEOM_ID"])
                bound_guids+=[i[1] for i in cursor if i[0] == "Boundary"]
                del cursor

                ## make layer of only boundary features that match query
                bnd_lyr = arcpy.mapping.Layer(path)
                bnd_lyr.showLabels = label
                bnd_lyr.definitionQuery = '"LAND_CHAR" = \'Boundary\'{0}'.format(
                    " AND " + query if not query == '' else '')

                ## add to data frame if there are boundary features
                ct = int(arcpy.management.GetCount(bnd_lyr).getOutput(0))
                if not ct == 0:
                    sym = os.path.join(LayerDir,"Boundary{0}.lyr".format(
                        arcpy.Describe(path).shapeType.lower()))
                    arcpy.management.ApplySymbologyFromLayer(bnd_lyr,sym)
                    arcpy.mapping.AddLayerToGroup(data_frame,bnd_layerTOC,bnd_lyr)

                    arcpy.AddMessage("  --{0} boundary feature{1}--".format(
                        ct,'' if ct == 1 else 's'))

            ## get list of guids for features with and without id in field
            CR_ID_result = GetIDFieldGUIDs(path,id_field,query)

            with_id_guids = GetGUIDsFromCatalog(cr_cat_path,CR_ID_result[0])
            c1 = len(with_id_guids)
            arcpy.AddMessage("  {0} spatial feature{1} with {2}".format(
                c1,'' if c1 == 1 else 's',id_field))
            
            without_id_guids = GetGUIDsFromCatalog(cr_cat_path,CR_ID_result[1])
            c2 = len(without_id_guids)
            arcpy.AddMessage("  {0} spatial feature{1} without {2}".format(
                c2,'' if c2 == 1 else 's',id_field))

            ## get guids for features that are multiple geometries
            if omit_multiples:

                arcpy.AddMessage("  checking for multiple geometries...")
                bad_guids = GetMultiplesGUIDs(path,query)[0]

            else:
                bad_guids = []

            ## combine list of bad geom guids and boundary guids
            undesirables = bound_guids+bad_guids

            ## pull out guids that are either boundary features or multiple geoms
            with_list = [i for i in with_id_guids if not i in undesirables]
            without_list = [i for i in without_id_guids if not i in undesirables]

            final_with_id_guid_qry = "("+" OR ".join(
                    ['"GEOM_ID" = \'{0}\''.format(str(i)) for i in with_list])+")"        
            final_without_id_guid_qry = "("+" OR ".join(
                    ['"GEOM_ID" = \'{0}\''.format(str(i)) for i in without_list])+")"

            ## little bit of error checking in case there are no good guids
            if final_with_id_guid_qry == "()":
                final_with_id_guid_qry = '("OBJECTID" IS NULL)'
            if final_without_id_guid_qry == "()":
                final_without_id_guid_qry = '("OBJECTID" IS NULL)'
        
            ## append final guid queries to original query to make finals
            if query == '':
                with_qry = final_with_id_guid_qry
            elif final_with_id_guid_qry == '':
                with_qry = query
            else:
                with_qry = ' AND '.join([query,final_with_id_guid_qry])

            if query == '':
                without_qry = final_without_id_guid_qry
            elif final_without_id_guid_qry == '':
                without_qry = query
            else:
                without_qry = ' AND '.join([query,final_without_id_guid_qry])

            ## make new layer and apply the final 'with' query to it
            with_layer = arcpy.mapping.Layer(path)
            with_layer.showLabels = label
            with_layer.definitionQuery = with_qry
            ctwith = int(arcpy.management.GetCount(with_layer).getOutput(0))

            ## if there's something in the layer, add it to the data frame
            if ctwith != 0:
                yes_sym = os.path.join(LayerDir,"yesID_{0}.lyr".format(
                    arcpy.Describe(path).shapeType.lower()))
                arcpy.management.ApplySymbologyFromLayer(with_layer,yes_sym)
                arcpy.mapping.AddLayerToGroup(data_frame,with_layerTOC,with_layer)
                arcpy.AddMessage("  {0} spatial feature{1} with {2}".format(
                ctwith,'' if ctwith == 1 else 's',id_field))
            else:
                arcpy.AddMessage("  0 spatial features with {0}".format(id_field))
            ## make new layer and apply the final 'without' query to it
            without_layer = arcpy.mapping.Layer(path)
            without_layer.showLabels = label
            without_layer.definitionQuery = without_qry
            ctwithout = int(arcpy.management.GetCount(without_layer).getOutput(0))

            ## if there's something in the layer, add it to the data frame
            if ctwithout != 0: 
                no_sym = os.path.join(LayerDir,"noID_{0}.lyr".format(
                    arcpy.Describe(path).shapeType.lower()))
                arcpy.management.ApplySymbologyFromLayer(without_layer,no_sym)
                arcpy.mapping.AddLayerToGroup(data_frame,without_layerTOC,without_layer)
                arcpy.AddMessage("  {0} spatial feature{1} without {2}".format(
                ctwithout,'' if ctwithout == 1 else 's',id_field))
            else:
                arcpy.AddMessage("  0 spatial features without {0}".format(id_field))

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

def LayerByCLIContribStatus(geodatabase_path, map_document, data_frame, query='',
                place_in_group=False, group_name='',label=False,omit_multiples=False):
    """The features in the input paths will be added to the data frame, and
    sorted based on CLI contributing status.  The categories used will be:
    1. Contributing
    2. Non-Contributing
    3. Undetermined
    4. Unknown
    NOTE: The Unknown category will hold any features that do not fit the
    others, as well as any that are marked as unknown.  For example,
    Non-Contributing - compatible will be sorted to Unknown if it occurs.

    Features can optionally be placed in a new group layer, labeled, or have
    multiple geometries for the same cli_id omitted.
    """

    try:
        paths = MakePathList(geodatabase_path)

        ## get path to cr link and catalog tables
        arcpy.env.workspace = geodatabase_path

        cr_link_path = False
        cr_cat_path = False
        for t in arcpy.ListTables():
            if t.lower().endswith("cr_link"):
                cr_link_path = os.path.join(geodatabase_path,t)
            if t.lower().endswith("cr_catalog"):
                cr_cat_path = os.path.join(geodatabase_path,t)
        if not cr_link_path:
            arcpy.AddError("There is no CR Link table in this geodatabase, so this "\
                "operation cannot be performed.")
            return False
        if not cr_cat_path:
            arcpy.AddError("There is no CR Catalog table in this geodatabase, so this "\
                "operation cannot be performed.")
            return False

        ## make top grouplayer if desired
        if place_in_group:
            topgrplyr_name = "{0}, CONTRIB".format(group_name)
            topgrplyrTOC = MakeGroupLayerInTOC(map_document,data_frame,topgrplyr_name)

        ## make group layer to hold boundary features
        bnd_grplayer = arcpy.mapping.Layer(grplayerpath)
        bnd_grplayer.name = "Boundary Features"

        if place_in_group:
            arcpy.mapping.AddLayerToGroup(data_frame,topgrplyrTOC,bnd_grplayer)
        else:
            arcpy.mapping.AddLayer(data_frame,bnd_grplayer)
        bnd_layerTOC = arcpy.mapping.ListLayers(
                map_document,"Boundary Features",data_frame)[0]

        ## take care of boundary features first
        bound_guids = []
        for path in paths:

            fc_name = os.path.basename(path)

            ## get boundary features from dist and site feature classes            
            if fc_name.startswith("crdist") or fc_name.startswith("crsite"):

                ## append guids for boundary feature to bound guid list
                cursor = arcpy.da.SearchCursor(path,["LAND_CHAR","GEOM_ID"])
                bound_guids+=[i[1] for i in cursor if i[0] == "Boundary"]
                del cursor

                ## make layer of only boundary features that match query
                bnd_lyr = arcpy.mapping.Layer(path)
                bnd_lyr.showLabels = label
                bnd_lyr.definitionQuery = '"LAND_CHAR" = \'Boundary\'{0}'.format(
                    " AND " + query if not query == '' else '')

                ## add to data frame if there are boundary features
                ct = int(arcpy.management.GetCount(bnd_lyr).getOutput(0))
                if not ct == 0:
                    sym = os.path.join(LayerDir,"Boundary{0}.lyr".format(
                        arcpy.Describe(path).shapeType.lower()))
                    arcpy.management.ApplySymbologyFromLayer(bnd_lyr,sym)
                    arcpy.mapping.AddLayerToGroup(data_frame,bnd_layerTOC,bnd_lyr)

        ## get all CLI_ID values in all feature classes
        all_cli_ids = []
        for path in paths:

            fc_name = os.path.basename(path)
            cursor = arcpy.da.SearchCursor(path,"CLI_ID",query)
            all_cli_ids+=[row[0] for row in cursor if not row[0] in all_cli_ids]
            del cursor

        ## use the all_cli_ids list to get contributing statuses from the lookup table
        c1ids,c2ids,c3ids,c4ids,c5ids = [],[],[],[],[]
        cursor = arcpy.da.SearchCursor(FeatureLookupTable,["CLI_ID","CONTRIB_STATUS"],
            '"CLI_ID" IN ({0})'.format(",".join(["'"+i+"'" for i in all_cli_ids])))
        for row in cursor:
            try:
                cval = str(row[1]).encode('ascii','ignore')
            except:
                cval = "problem"
            cvallow = cval.lower().rstrip()

            ## sort cli_ids into contribution categories
            if "contributing" in cvallow and "non" in cvallow:
                if not row[0] in c2ids:
                    c2ids.append(row[0])
            elif "contributing" in cvallow:
                if not row[0] in c1ids:
                    c1ids.append(row[0])
            elif "undetermined" in cvallow:
                if not row[0] in c3ids:
                    c3ids.append(row[0])
            elif cvallow == "managed as a cultural resource":
                if not row[0] in c5ids:
                    c5ids.append(row[0])
            else:
                if not row[0] in c4ids:
                    c4ids.append(row[0])
        del cursor

        arcpy.AddMessage("Contributing: " + str(len(c1ids)))
        arcpy.AddMessage("Non-Contributing: " + str(len(c2ids)))
        arcpy.AddMessage("Managed as a Cultural Resource: " + str(len(c5ids)))
        arcpy.AddMessage("Undetermined: " + str(len(c3ids)))
        arcpy.AddMessage("Unknown: " + str(len(c4ids)))

        ## make a new group layer for each contributing status category
        ## ok ok, this is super clumsy...
        ## also, get guids here

        if not len(c4ids) == 0:
            con_group_layer4 = arcpy.mapping.Layer(grplayerpath)
            con_group_layer4.name = "Unknown"
            if place_in_group:
                arcpy.mapping.AddLayerToGroup(data_frame,topgrplyrTOC,con_group_layer4)
            else:
                arcpy.mapping.AddLayer(data_frame,con_group_layer4)
            conlyr4_TOC = arcpy.mapping.ListLayers(map_document,"Unknown",data_frame)[0]

            CR_guids4 = GetCLI_IDGUIDs(cr_link_path,c4ids)
            guids4 = GetGUIDsFromCatalog(cr_cat_path,CR_guids4)

        if not len(c3ids) == 0:
            con_group_layer3 = arcpy.mapping.Layer(grplayerpath)
            con_group_layer3.name = "Undetermined"
            if place_in_group:
                arcpy.mapping.AddLayerToGroup(data_frame,topgrplyrTOC,con_group_layer3)
            else:
                arcpy.mapping.AddLayer(data_frame,con_group_layer3)
            conlyr3_TOC = arcpy.mapping.ListLayers(map_document,"Undetermined",data_frame)[0]

            CR_guids3 = GetCLI_IDGUIDs(cr_link_path,c3ids)
            guids3 = GetGUIDsFromCatalog(cr_cat_path,CR_guids3)

        if not len(c5ids) == 0:
            con_group_layer5 = arcpy.mapping.Layer(grplayerpath)
            con_group_layer5.name = "Managed as a Cultural Resource"
            if place_in_group:
                arcpy.mapping.AddLayerToGroup(data_frame,topgrplyrTOC,con_group_layer5)
            else:
                arcpy.mapping.AddLayer(data_frame,con_group_layer5)
            conlyr5_TOC = arcpy.mapping.ListLayers(map_document,"Managed as a Cultural Resource",data_frame)[0]

            CR_guids5 = GetCLI_IDGUIDs(cr_link_path,c5ids)
            guids5 = GetGUIDsFromCatalog(cr_cat_path,CR_guids5)

        if not len(c2ids) == 0:
            con_group_layer2 = arcpy.mapping.Layer(grplayerpath)
            con_group_layer2.name = "Non-Contributing"
            if place_in_group:
                arcpy.mapping.AddLayerToGroup(data_frame,topgrplyrTOC,con_group_layer2)
            else:
                arcpy.mapping.AddLayer(data_frame,con_group_layer2)
            conlyr2_TOC = arcpy.mapping.ListLayers(map_document,"Non-Contributing",data_frame)[0]

            CR_guids2 = GetCLI_IDGUIDs(cr_link_path,c2ids)
            guids2 = GetGUIDsFromCatalog(cr_cat_path,CR_guids2)

        if not len(c1ids) == 0:
            con_group_layer1 = arcpy.mapping.Layer(grplayerpath)
            con_group_layer1.name = "Contributing"
            if place_in_group:
                arcpy.mapping.AddLayerToGroup(data_frame,topgrplyrTOC,con_group_layer1)
            else:
                arcpy.mapping.AddLayer(data_frame,con_group_layer1)
            conlyr1_TOC = arcpy.mapping.ListLayers(map_document,"Contributing",data_frame)[0]

            CR_guids1 = GetCLI_IDGUIDs(cr_link_path,c1ids)
            guids1 = GetGUIDsFromCatalog(cr_cat_path,CR_guids1)

        ## go through paths, and split each one into the various contrib statuses
        ## this whole process is a little convoluded, and could be structured.

        arcpy.AddMessage("\nProcessing feature classes...")
        for path in paths:

            n = os.path.basename(path)
            arcpy.AddMessage("  --" + n)

            ## get list of GUIDs in this feature class
            fc_guids = [i[0] for i in arcpy.da.SearchCursor(path,"GEOM_ID",query)]

            ## get guids for features that are multiple geometries
            bad_guids = []
            if omit_multiples:

                arcpy.AddMessage("  checking for multiple geometries...")
                bad_guids = GetMultiplesGUIDs(path,query)[0]

            undesirables = bad_guids + bound_guids
            shape = arcpy.Describe(path).shapeType.lower()
            

            if not len(c1ids) == 0:
                
                good_guids = [i for i in guids1 if not i in undesirables and i in fc_guids]
                list_string = "','".join([str(i) for i in good_guids])
                if len(good_guids) == 0:
                        qry = '"OBJECTID" IS NULL'
                else:
                    qry = '"GEOM_ID" IN (\'{0}\'){1}'.format(list_string," AND " + query if 
                            not query == '' else '')
                lyr1 = arcpy.mapping.Layer(path)
                lyr1.definitionQuery = qry
                ct = int(arcpy.management.GetCount(lyr1).getOutput(0))
                if not ct == 0:
                    s = r"{0}\cont1_{1}.lyr".format(LayerDir,shape)
                    arcpy.management.ApplySymbologyFromLayer(lyr1,s)
                    arcpy.mapping.AddLayerToGroup(data_frame,conlyr1_TOC,lyr1)

            if not len(c2ids) == 0:
               
                good_guids = [i for i in guids2 if not i in undesirables and i in fc_guids]
                list_string = "','".join([str(i) for i in good_guids])
                if len(good_guids) == 0:
                        qry = '"OBJECTID" IS NULL'
                else:
                    qry = '"GEOM_ID" IN (\'{0}\'){1}'.format(list_string," AND " + query if 
                            not query == '' else '')
                lyr2 = arcpy.mapping.Layer(path)
                lyr2.definitionQuery = qry
                ct = int(arcpy.management.GetCount(lyr2).getOutput(0))
                if not ct == 0:
                    s = r"{0}\cont2_{1}.lyr".format(LayerDir,shape)
                    arcpy.management.ApplySymbologyFromLayer(lyr2,s)
                    arcpy.mapping.AddLayerToGroup(data_frame,conlyr2_TOC,lyr2)

            if not len(c5ids) == 0:
                
                good_guids = [i for i in guids5 if not i in undesirables and i in fc_guids]
                list_string = "','".join([str(i) for i in good_guids])
                if len(good_guids) == 0:
                        qry = '"OBJECTID" IS NULL'
                else:
                    qry = '"GEOM_ID" IN (\'{0}\'){1}'.format(list_string," AND " + query if 
                            not query == '' else '')
                lyr5 = arcpy.mapping.Layer(path)
                lyr5.definitionQuery = qry
                ct = int(arcpy.management.GetCount(lyr5).getOutput(0))
                if not ct == 0:
                    s = r"{0}\cont5_{1}.lyr".format(LayerDir,shape)
                    arcpy.management.ApplySymbologyFromLayer(lyr5,s)
                    arcpy.mapping.AddLayerToGroup(data_frame,conlyr5_TOC,lyr5)

            if not len(c3ids) == 0:
                
                good_guids = [i for i in guids3 if not i in undesirables and i in fc_guids]
                list_string = "','".join([str(i) for i in good_guids])
                if len(good_guids) == 0:
                        qry = '"OBJECTID" IS NULL'
                else:
                    qry = '"GEOM_ID" IN (\'{0}\'){1}'.format(list_string," AND " + query if 
                            not query == '' else '')
                lyr3 = arcpy.mapping.Layer(path)
                lyr3.definitionQuery = qry
                ct = int(arcpy.management.GetCount(lyr3).getOutput(0))
                if not ct == 0:
                    s = r"{0}\cont3_{1}.lyr".format(LayerDir,shape)
                    arcpy.management.ApplySymbologyFromLayer(lyr3,s)
                    arcpy.mapping.AddLayerToGroup(data_frame,conlyr3_TOC,lyr3)

            if not len(c4ids) == 0:
                
                good_guids = [i for i in guids4 if not i in undesirables and i in fc_guids]
                list_string = "','".join([str(i) for i in good_guids])
                if len(good_guids) == 0:
                        qry = '"OBJECTID" IS NULL'
                else:
                    qry = '"GEOM_ID" IN (\'{0}\'){1}'.format(list_string," AND " + query if 
                            not query == '' else '')
                lyr4 = arcpy.mapping.Layer(path)
                lyr4.definitionQuery = qry
                ct = int(arcpy.management.GetCount(lyr4).getOutput(0))
                if not ct == 0:
                    s = r"{0}\cont4_{1}.lyr".format(LayerDir,shape)
                    arcpy.management.ApplySymbologyFromLayer(lyr4,s)
                    arcpy.mapping.AddLayerToGroup(data_frame,conlyr4_TOC,lyr4)

        arcpy.AddMessage("  completed.")

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

def LayerByLandscapeCharacteristic(paths, map_document, data_frame, query='',
                place_in_group=False, group_name='',label=False,omit_multiples=False):
    '''This function takes a set of input paths (generally, all the paths to
    feature classes in a standards implementation model geodatabase) and
    uses definition queries on these layers to add them to larger group
    layers. The layers are grouped by landscape characteristic, and then a
    standardized color scheme is applied.  The feature classes must have a
    LAND_CHAR field filled out for the operation to work.

    Features can optionally be placed in a new group layer, labeled, or have
    multiple geometries for the same cli_id omitted.'''

    m_list = ['ARCHEOLOGICAL SITES', 'BUILDINGS AND STRUCTURES',
            'CIRCULATION', 'CLUSTER ARRANGEMENT', 'CONSTRUCTED WATER FEATURES',
            'CULTURAL TRADITIONS', 'LAND USE', 'NATURAL SYSTEMS AND FEATURES',
            'SMALL-SCALE FEATURES', 'SPATIAL ORGANIZATION', 'TOPOGRAPHY',
            'VEGETATION', 'VIEWS AND VISTAS', 'SMALL SCALE FEATURES']

    try:

        ## make top grouplayer if desired
        if place_in_group:
            topgrplyr_name = "{0}, LANDCHAR".format(group_name)
            topgrplyrTOC = MakeGroupLayerInTOC(map_document,data_frame,topgrplyr_name)

        ## iterate through all feature classes to make list of land chars
        lc_list = []
        mults = {}

        if omit_multiples:
            arcpy.AddMessage("Analyzing features to omit multiple geometries...")
        for path in paths:

            fc_name = os.path.basename(path)

            ## make list of landscape characteristics that are in this CLI
            srows = arcpy.SearchCursor(path,query,"","LAND_CHAR")
            for srow in srows:
                lc = string.capwords(str(srow.getValue("LAND_CHAR")))
                if not lc in lc_list and str(lc).upper() in m_list:
                    lc_list.append(lc)

            ## also, make dictionary matching feature name with list of
            ## multiple guids if omit multiples == True
            if omit_multiples:

                bad_guids = GetMultiplesGUIDs(path,'')[0]
                mults[fc_name] = bad_guids
       
        ## make the list backwards alphabetical for correct final TOC order
        lc_list.sort()
        lc_list.append("Boundary")
        lc_list.reverse()

        ## make a group layer for each land char
        for lc in lc_list:

            Print("adding " + lc)

            ## first, make group layer, add it to TOC, and make layer object
            ## from it after it's in the TOC
            lc_group_layer = arcpy.mapping.Layer(grplayerpath)
            lc_group_layer.name = lc
            if place_in_group:
                arcpy.mapping.AddLayerToGroup(data_frame,topgrplyrTOC,lc_group_layer)
            else:
                arcpy.mapping.AddLayer(data_frame,lc_group_layer)
            lc_group_layerTOC = arcpy.mapping.ListLayers(
                map_document,lc,data_frame)[0]

            ## make and symbolize a layer for each fc, add to lc group layer
            for path in paths:

                name = os.path.basename(path)

                ## make query for specific landscape characteristic
                qry = '(UPPER("LAND_CHAR") = \'{0}\'{1}{2})'.format(lc.upper(),
                    "" if query == '' else " AND ",query)

                ## get guids for features that are multiple geometries
                if omit_multiples:

                    ## list all guids and pull out those that are bad_guids
                    all_guids = [i[0] for i in arcpy.da.SearchCursor(
                        path,["GEOM_ID","LAND_CHAR","CLI_NUM","ALPHA_CODE"],qry)]
                    good_guids = [i for i in all_guids if not i in mults[name]]
                    if len(good_guids) == 0:
                        qry = '"OBJECTID" IS NULL'
                    else:
                        qry = '"GEOM_ID" IN (\'{0}\')'.format("','".join(
                            [str(i) for i in good_guids]))


                layer = arcpy.mapping.Layer(path)
                layer.definitionQuery = qry
                layer.showLabels = label

                ## skip if layer is empty
                ct = int(arcpy.management.GetCount(layer).getOutput(0))
                if ct == 0:
                    continue

                shape = arcpy.Describe(layer).shapeType.lower()
                sym_path = r'{0}\{1}{2}.lyr'.format(LayerDir,lc.lower(),shape)
                arcpy.management.ApplySymbologyFromLayer(layer,sym_path)
                arcpy.mapping.AddLayerToGroup(data_frame,lc_group_layerTOC,layer)

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

def LayerByFeatureClass(paths, map_document, data_frame, query='',
                place_in_group=False, group_name='',label=False,
                omit_multiples=False):
    '''This function will add a series of paths to the display, and will
    symbolize them in a standard color scheme. They can optionally be placed
    in a new group layer, labeled, or have multiple geometries for the same
    cli_id omitted.'''

    if place_in_group:
        topgrplyr_name = "{0}, FEATCLASS".format(group_name)
        topgrplyrTOC = MakeGroupLayerInTOC(map_document,data_frame,topgrplyr_name)

    Print("\nsymbolizing layers by feature class...")
    arcpy.AddMessage("original query: " + query)

    for path in paths:

        #reset new query on every iteration
        new_query = query

        layer = arcpy.mapping.Layer(path)
        if not layer.supports("DEFINITIONQUERY"):
            continue

        fcname = os.path.basename(path)

        if omit_multiples:
            arcpy.AddMessage(path)
            good_guids = GetMultiplesGUIDs(path,query)[1]
            guid_qry = '"GEOM_ID" IN (\'{0}\')'.format("','".join(good_guids))

            if len(good_guids) == 0:
                new_query = '"OBJECTID" IS NULL'
            elif query == '':
                new_query = guid_qry
            else:
                new_query = ' AND '.join([query,guid_qry])

        layer.definitionQuery = new_query
        count = int(arcpy.management.GetCount(layer).getOutput(0))
        n = 11 - len(fcname)
        if count == 0:
            Print("{0}:{1}...no records".format(fcname," "*n))
            continue
        msg = "{0}:{1}{2} feature{3} added to display".format(
                fcname," "*n,str(count),"" if count == 1 else "s")

        ## apply symbology before adding to data frame
        if not layer.name.startswith("imp_"):
            fcshortname = str(layer.name.split(".")[-1])
            sym_path = r"{0}\{1}.lyr".format(LayerDir,fcshortname)
            arcpy.management.ApplySymbologyFromLayer(layer,sym_path)
        else:
            shp = arcpy.Describe(layer).shapeType.lower()
            if shp == "point":
                sym_path = r"{0}\scratch_pt.lyr".format(LayerDir)
                arcpy.management.ApplySymbologyFromLayer(layer,sym_path)
            elif shp == "polyline":
                sym_path = r"{0}\scratch_ln.lyr".format(LayerDir)
                arcpy.management.ApplySymbologyFromLayer(layer,sym_path)
            elif shp == "polygon":
                sym_path = r"{0}\scratch_py.lyr".format(LayerDir)
                arcpy.management.ApplySymbologyFromLayer(layer,sym_path)
            else:
                pass

        ## turn on labels if desired
        layer.showLabels = label

        ## add to data frame, in premade group layer if desired
        if place_in_group:
            arcpy.mapping.AddLayerToGroup(data_frame,topgrplyrTOC,layer)
        else:
            arcpy.mapping.AddLayer(data_frame,layer)

        Print(msg)
        del layer

def AddToDataFrame(map_document,dataframe,geodatabase_path,unit_code=False,
    layer_scheme='',id_fields=[],place_in_group=False,label=False,
    exclude_non_extant=False,omit_multiples=False):
    '''Complex display function used to show CLI data in a variety of ways.
    This function works on either a scratch geodatabase or a CLI standards
    implementation model geodatabase.  The layer_sheme must be one of the
    following: FEATCLASS, LANDCHAR, CONTRIB, and/or a list of id fields may
    passed through the id_fields argument.

    Features can optionally be placed in a new group layer, labeled, or have
    multiple geometries for the same cli_id omitted.
    '''
    try:
        unit = False
        if unit_code:
            unit = MakeUnit(unit_code)

        gdbname = os.path.splitext(os.path.basename(geodatabase_path))[0]
        
        ## create query, taking into account the geodatabase type 
        if "scratch" in geodatabase_path:
            query = '("fclass" IS NOT NULL)'
            groupname = gdbname
        else:
            if unit:
                query = "("+unit.query+")"
                groupname = unit.code
            else:
                query = ''
                groupname = gdbname

        ## modify query in case non-extant features should be excluded
        if exclude_non_extant:
            ext_qry = '("IS_EXTANT" <> \'False\')'
            if query == '':
                query = ext_qry
            else:
                query = ' AND '.join([query,ext_qry])
        
        paths = MakePathList(geodatabase_path)

        ## filter path list if scratch gdb is used
        if "scratch" in geodatabase_path:
            scratch_fcs = ["scratch_pt","scratch_ln","scratch_py"]
            paths = [i for i in paths if os.path.basename(i) in scratch_fcs\
                        or "imp_" in i]

        if layer_scheme == 'FEATCLASS':
            LayerByFeatureClass(paths,map_document,dataframe,query,place_in_group,
                groupname,label,omit_multiples)

        if layer_scheme == "LANDCHAR":
            try:
                LayerByLandscapeCharacteristic(paths,map_document,dataframe,query,
                    place_in_group,groupname,label,omit_multiples)
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

        if layer_scheme == "CONTRIB":
            LayerByCLIContribStatus(geodatabase_path,map_document,dataframe,query,
                    place_in_group,groupname,label,omit_multiples)

        for id_field in id_fields:
            LayerByIDPresence(geodatabase_path,id_field,map_document,dataframe,query,
                place_in_group,groupname,label,omit_multiples)

        dataframe.zoomToSelectedFeatures()

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

def MakeKMZ(input_gdb,output_dir,subset_unit_code='',layer_scheme='',
            id_fields=[],label=False,exclude_non_extant=False,omit_multiples=False):
    """Uses the AddToDataFrame function to add data to a blank mxd.  The mxd
    is then converted to a KMZ file using arcpy.conversion.MapToKML."""

    try:
        ## get map document and remove any existing layers
        #mxd_path = os.path.join(bin_dir,"blank.mxd")
        mxd_path = MXDempty
        mxd = arcpy.mapping.MapDocument(mxd_path)
        for d in arcpy.mapping.ListDataFrames(mxd):
            if d.name == mxd.activeView:
                df = d
        for l in arcpy.mapping.ListLayers(mxd,"",df):
            arcpy.mapping.RemoveLayer(df,l)

        ## use the add to dataframe function to display the data in the mxd.
        ## (I know this is a cumbersome way of passing arguments, but don't
        ## have time to restructure these functions.)
        arcpy.AddMessage("\nAdding features to blank map document...")
        AddToDataFrame(mxd,df,input_gdb,subset_unit_code,layer_scheme,id_fields,
            True,label,exclude_non_extant,omit_multiples)
        arcpy.AddMessage("  completed.")

        arcpy.RefreshTOC()

        out_name = time.strftime("KMZ Export %b%d %H%M")
        out_file = output_dir + os.sep + out_name + ".kmz"
        
        
        df.name = out_name
        mxd.save()

        arcpy.AddMessage("\nConverting map document to KMZ file...")
        arcpy.conversion.MapToKML(mxd.filePath, df.name, out_file, 1000)
        arcpy.AddMessage("  completed.")

        Print("\noutput file: " + out_file)

        return out_file
        
    except:
                
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

        Print(msgs)

        Print(pymsg)
        Print(arcpy.GetMessages(1))

def GenerateCentroids(input_featureclass, target_featureclass):
    '''Takes the input features, create centroids from them and then appends
    those features to target_feature class, which must be a
    point feature class. Only works with the ArcInfo product license. '''

    if not arcpy.ProductInfo() == "ArcInfo":
        Print("you must have the ArcInfo or \"Advanced\" license"\
            " level to use this tool.")
        Print(arcpy.ProductInfo())
        return False

    temp_pts = r'in_memory\centroids'
    TakeOutTrash(temp_pts)

    TakeOutTrash("fl1")
    fl1 = arcpy.management.MakeFeatureLayer(input_featureclass,"fl1")

    arcpy.management.FeatureToPoint(fl1,temp_pts, "INSIDE")

    ## update some field values
    rows = arcpy.UpdateCursor(temp_pts)
    for row in rows:
        if "fclass" in [f.name for f in arcpy.ListFields(temp_pts)]:
            fclass = row.getValue("fclass")
            if not str(fclass) == "None":
                new_fclass = fclass[:-2] + "pt"
                row.setValue("fclass",new_fclass)
        row.setValue("MAP_METHOD","Derived by XY event point or centroid"\
            " generation")
        row.setValue("BND_TYPE","Derived point")
        row.setValue("MAP_MTH_OT","centroid generated from digitized polygon")
        rows.updateRow(row)

    ## calculate new geometry GUID
    ex = "g"
    cb = "Set TypeLib = CreateObject(\"Scriptlet.Typelib\")\ng = TypeLib.GUID"
    arcpy.management.CalculateField(temp_pts,"GEOM_ID",ex,code_block=cb)

    ## append to target feature class
    arcpy.management.Append(temp_pts,target_featureclass,'NO_TEST')

    TakeOutTrash(temp_pts)

def ZoomTo(input_code,map_document,data_frame_object):
    '''Uses a region, park, or landscape code as input, and zooms to any
    features that match this code.  The order in which the feature classes
    are searched is as follows: "crland","crdist","crsite_py","crstru",
    "crbldg","crobj","crothr".  This function works by selecting features
    and zooming to the selection, so it may work incorrectly if there are
    existing selections in any layers.
    '''

    if len(input_code) == 6:
        query = '"CLI_NUM" = \'' + input_code + "'"
    elif len(input_code) == 4:
        query = '"ALPHA_CODE" = \'' + input_code.upper() + "'"
    elif len(input_code) == 3:
        query = '"REG_CODE" = \'' + input_code.upper() + "'"
    else:
        arcpy.AddError("\ninvalid input.\n")
        return False

    arcpy.AddMessage("query used: " + query + "\n")

    search_order = ["crland","crdist","crsite_py","crstru","crbldg",
                    "crobj","crothr"]

    layers = arcpy.mapping.ListLayers(map_document,'',data_frame_object)
    filter_layers = [i for i in layers if i.supports("DATASOURCE")]
    for fc in search_order:

        for layer in [l for l in filter_layers if fc in l.dataSource]:

            Print("looking for features in: {}".format(layer.name))
            arcpy.management.SelectLayerByAttribute(layer,"NEW_SELECTION",query)
            ct = int(arcpy.management.GetCount(layer).getOutput(0))
            Print("  found {}".format(ct))
            if ct == 0:
                continue
            Print("  zooming to features.")
            data_frame_object.zoomToSelectedFeatures()
            arcpy.management.SelectLayerByAttribute(layer,'CLEAR_SELECTION')
            arcpy.RefreshTOC()
            return True
    return False

def ListAllVisibleFeatureLayers(map_document,data_frame):
    '''this function will return a list of the visible layers in a given
    data frame, excluding any that are not visible in the map display.
    It is designed to exclude layers that are visible, but the group layers
    that they reside in are not.

    NOTE: THIS IS UNTESTED AND SUSPECT, AND NOT USED IN ANY SCRIPTS 9-22-14
    however, this would be a useful function to add to the UpdateFieldsIn
    SelectedRecords tool, because it would allow for multiple layers with
    the same name to be present, one would just have to be turned off.'''
    try:

        ## first get list of all visible layers that are not in group layers
        vis_layers = []
        for layer in arcpy.mapping.ListLayers(map_document):
            
            if not layer.supports("LONGNAME") or not layer.supports("VISIBLE"):
                continue
            if layer.isRasterLayer:
                continue
            try:
                if layer.isGroupPlayer:
                    continue
            except:
                continue
            if layer.name == layer.longName and layer.visible:
                arcpy.AddMessage(layer.name)
                arcpy.AddMessage(layer.longName)
                vis_layers.append(layer)
            print layer


        print "stand alone layers"
        print [l.name for l in vis_layers]

        ## start with list of visible top group layers
        top_group_layers = []
        for layer in arcpy.mapping.ListLayers(map_document):
            if not layer.supports("LONGNAME"):
                continue
            if layer.isRasterLayer:
                continue
            if layer.isGroupLayer and layer.longName.split("\\")[0] == layer.name\
               and layer.visible:
                top_group_layers.append(layer)
                print type(layer)

        ## iterate visible group layers and everything inside them that is visible
        vis_layers_in_groups = []
        for group_layer in top_group_layers:
            contents = arcpy.mapping.ListLayers(group_layer)
            for layer in contents:
                if layer.isRasterLayer:
                    continue
                if layer.isGroupLayer and layer.visible:
                    contents2 = arcpy.mapping.ListLayers(layer)
                    for lyr in contents2:
                        if lyr.isRasterLayer:
                            continue
                        if lyr.visible:
                            vis_layers_in_groups.append(lyr)
                elif layer.visible:
                    vis_layers_in_groups.append(layer)
                else:
                    pass

        print "visible layers in groups"
        print vis_layers_in_groups

        all_vis_layers = vis_layers + vis_layers_in_groups
        return all_vis_layers

    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

        Print(msgs)

        Print(pymsg)
        Print(arcpy.GetMessages(1))

def UpdateCLIFieldsInLayer(layer):
    """This function will iterate through the input rows, collect all
    CLI_IDs from the input layer, use those for a query on the
    FeatureInfoLookup table, and them pull all necessary information
    from that table and write it to the input layer.

    Based on the existing value in the CLI_ID field, a feature will have
    the following attributes filled:
    RESNAME, LAND_CHAR, CLI_NUM, and CONTRIBRES"""

    try:

        ## do some initial prep field work
        layer_fields = [f.name for f in arcpy.ListFields(layer)]
        if not "CLI_ID" in layer_fields:
            arcpy.AddError("\nNo CLI_ID field in this layer.  Make sure "\
                " there are no joins on the layer and try again.")
            return
            
        core_fields = ["CLI_ID","CLI_NUM","LAND_CHAR","RESNAME"]
        
        m = [i for i in core_fields if not i in layer_fields]
        if len(m) > 0:
            arcpy.AddError("\nMissing these necessary fields:\n"+",".join(m))
            return
            
        ## make query
        cli_ids = [i[0] for i in arcpy.da.SearchCursor(layer,"CLI_ID")]
        if len(cli_ids) == 0:
            arcpy.AddError("\nNo CLI_IDs in input layer\n")
            return
        qry = '"CLI_ID" IN (' + ",".join(['\'{0}\''.format(i) for i in cli_ids]) + ")"
        
        ## access feature table to get field names
        tv = "tv"
        TakeOutTrash(tv)
        arcpy.management.MakeTableView(FeatureLookupTable,tv,qry)
        table_fields = [g.name for g in arcpy.ListFields(tv)]
        
        ## more field checking and dealing with different names in different tables
        p_id_fields = ["LCS_ID","FMSS_ID","FMSS_Asset_ID","ASMIS_ID","ASMIS_Name","HS_ID","NRIS_ID","NHL_ID","NAB_ID"]
        id_fields = [i for i in p_id_fields if i in layer_fields and i in table_fields]
        p_park_fields = ["ALPHA_CODE","PARK_NAME","UNIT"]
        park_fields = [i for i in p_park_fields if i in layer_fields and i in table_fields]
        
        l_cur_fields = core_fields+id_fields+park_fields
        l_cur_fields.append("CONTRIBRES")
        t_cur_fields = core_fields+id_fields+park_fields
        t_cur_fields.append("CONTRIB_STATUS")
        
        if "REG_CODE" in layer_fields:
            l_cur_fields.append("REG_CODE")
            t_cur_fields.append("REGION_CODE")
        
        if "UNIT_TYPE" in layer_fields:
            l_cur_fields.append("UNIT_TYPE")
            t_cur_fields.append("PARK_TYPE")

        ## make dictionary from table
        info = {}
        for row in arcpy.da.SearchCursor(tv,t_cur_fields):
            for ind,nm in enumerate(t_cur_fields):
                val = row[ind]
                if nm == "CONTRIB_STATUS":
                    val = ConvertContribStatus(val)
                if nm == "CLI_ID":
                    info[row[0]] = []
                else:
                    info[row[0]].append(val)

        ## check to see if any of the rows are boundaries
        ds = layer.dataSource.lower()
        if "dist" in ds or "site_py" in ds:
            arcpy.AddMessage("    --checking for boundary features--")
            tv = "tv"
            TakeOutTrash(tv)
            qry2 = '"CLI_NUM" IN (' + ",".join(['\'{0}\''.format(i) for i in cli_ids]) + ")"
            arcpy.management.MakeTableView(UnitLookupTable,tv,qry2)
            nums = []
            if int(arcpy.management.GetCount(tv).getOutput(0)) > 0:
                for row in arcpy.da.SearchCursor(tv,t_cur_fields):
                    cli_num = row[0]
                    if cli_num in nums:
                        continue
                    for ind,nm in enumerate(t_cur_fields):
                        val = row[ind]
                        if nm == "CONTRIB_STATUS":
                            val = "Not Applicable"
                        if nm == "RESNAME":
                            val = "CLI Boundary for " + val
                        if nm == "LAND_CHAR":
                            val = "Boundary"
                        if nm == "CLI_NUM":
                            val == cli_num
                        if nm == "CLI_ID":
                            info[cli_num] = []
                        else:
                            info[cli_num].append(val)
                    nums.append(cli_num)

        ## write data from cli info dictionary to layer
        rows = arcpy.da.UpdateCursor(layer,l_cur_fields)
        ct = 0
        cli_nums_present = []
        for row in rows:
            cliid = row[0]
            if cliid == None:
                continue
            if not cliid in info.keys():
                arcpy.AddMessage("    CLI_ID: {0} not found in master table"\
                    .format(cliid))
                continue
            c_num = info[cliid][1]
            if not c_num in cli_nums_present:
                cli_nums_present.append(c_num) 
            for i in range(len(info[cliid])):
                row[i+1] = info[cliid][i]
            rows.updateRow(row)
            ct+=1

        return ct

        if len(cli_nums_present) > 1:
            arcpy.AddWarning("\nWarning: CLI_IDs from multiple landscapes were "\
                "entered.  This may mean that incorrect CLI_IDs were entered."\
                "\n\nThe multiple landscapes are:\n" + "\n".join(cli_nums_present))

    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        Print(msgs)
        Print(pymsg)
        Print(arcpy.GetMessages(1))

def UpdateRowsInLayer(layer,variable_dictionary,overwrite=False):
    """This function will take the input dictionary and use it to apply
    new values to the rows in the input layer.  If a field in the
    dictionary does not exist in the layer, it will be skipped without
    any trouble.

    The variable_dictionary must be formatted this way:

    {"field_name":"new_value"}

    The overwrite option dictates whether old values in the layer will be
    overwritten if there is a new value provided for that field.
    """

    ## update rows
    ct = 0
    rows = arcpy.UpdateCursor(layer)
    for row in rows:
        for field, value in variable_dictionary.iteritems():
            if not field in [i.name for i in arcpy.ListFields(layer)]:
                continue
            try:
                if not overwrite:
                    v = row.getValue(field)
                    if str(v) == "<Null>" or str(v) == "None"\
                       or str(v).rstrip() == "":
                        row.setValue(field,value)
                        rows.updateRow(row)
                else:
                    row.setValue(field,value)
                    rows.updateRow(row)
            except:
                arcpy.AddMessage("  some problem updating {0}".format(field))
        ct+=1

    return ct

def SaveSourceInfoToTable(variable_dictionary):
    """This function will save the values in the input variable dictionary
    to the master table that holds source info."""

    ## write variable dictionary info to all fields in the source table
    rows = arcpy.InsertCursor(SourceLookupTable)
    row = rows.newRow()
    for v, k in variable_dictionary.iteritems():
        if v in [i.name for i in arcpy.ListFields(SourceLookupTable)]:
            row.setValue(v, k)
    rows.insertRow(row)
