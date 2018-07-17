# ---------------------------------------------------------------------------
# Title: CLI TERMINAL.py
# Version: 0.1
# Created by Adam Cox
#   
# Description:  This script is a model for what can be done by using the
#    Python console as an interactive way to access the functions in the
#    clitools Python package.  It is dysfunctional at present, as it was 
#    originally built using old clitools functions, but could be revamped
#    to work with the current versions of the functions.  When stored here
#    in the scripts folder, it can access the clitools package.  If that
#    package has been moved to the local Python installation, this script
#    would work wherever it is located.
# ---------------------------------------------------------------------------

print "initializing..."
import os, sys, traceback
import arcpy
from time import strftime
from clitools.general import AskYesOrNo, GetDirPath
from clitools.classes import MakeUnit, AllGoodInputs
# from clitools.management import MakeSpreadsheet

intro = """
~~CLI TERMINAL~~

Type 'help' for more information.
Use CTRL + C to exit.

To choose a unit, enter one of the following:
3-letter region code
4-letter alpha code
6-digit landscape number"""

help = """
Commands: xls, mxd, pdf, jpg, sum, help
Any combination of commands is valid.
"""

print intro

need_prompt = True

while True:

    prompt = "--> "

    if need_prompt == True:
        print ""
        choice = raw_input(prompt)
        
    if "help" in choice.lower():
        print help
        choice = False

    while MakeUnit(choice) == False:
        choice = raw_input(prompt)

    unit = MakeUnit(choice)
    
    ##set walk path and regional gdb path based on region input
    walk_path = os.path.join(r"C:\CLI_GIS",unit.region[1])
    stan_gdb = r"{0}\{1}_standardsGDB.gdb".format(walk_path,unit.region[0])

    print "-"*80
    print "{0}, {1}".format(unit.code, unit.name)

    if unit.type == "park":
        ls = unit.landscapes
        ct = len(ls)
        print "\n  {0} landscape{1}:".format(ct,"s" if ct!=1 else '')
        for l in ls:
            print "    {0}, {1}".format(l[0],l[1])

    if unit.type == "region":
        ls = unit.parks
        ct = len(ls)
        print "\n  {0} parks with landscape{1}".format(
            ct,"s" if ct!=1 else '')
        print "  (type 'list' for a complete list)"


    if unit.type == "region":
        prompt = "{0} --> ".format(unit.code)
    elif unit.type == "park":
        prompt = "{0} > {1} --> ".format(unit.region[0],unit.code)
    elif unit.type == "landscape":
        prompt = "{0} > {1} > {2} --> ".format(
            unit.region[0],unit.park[0],unit.code)

    print ""
    
    next_task = raw_input(prompt).lower()

    while (next_task or next_task == ""):

        good_input = False
        out_path = False
        list_names = False

        if "list" in next_task:
            if unit.type == "region":
                print ""
                for p in unit.parks:
                    print "~~", p[0], p[1]  
            elif unit.type == "park":
                print ""
                for cl in unit.landscapes:
                    print "~~", cl[0], cl[1]          
            else:
                pass

        if "sum" in next_task:
            if unit.type == "region":
                print "you may as well make a spreadsheet for this region."
                
            else:
                good_input = True
                list_names = AskYesOrNo(
                    "  list names of missing contributing features? y/n ")
                make_file = AskYesOrNo("  create text file output? y/n ")
                if make_file == True:
                    out_path = GetDirPath(unit,walk_path)                
                MakeTextSummary(walk_path,unit.code,unit.type,make_file,
                                list_names,out_path)

        if "xls" in next_task:
            good_input = True
            if unit.type == "landscape":
                
                if out_path == False:
                    out_path = GetDirPath(unit,walk_path)

                gdb_type = raw_input(
                    "  analyze SCRATCH .gdb or REGION .gdb?"\
                    "\n  --> ")
                while not gdb_type.lower() in ["scratch","region"]:
                    gdb_type = raw_input("  --> ")
                    
                if gdb_type.lower() == "scratch":
                    openxls = MakeSpreadsheetScratch(unit.code,walk_path,out_path)
                else:
                    openxls = MakeSpreadsheetFinal(unit.code,stan_gdb,out_path)
                if not openxls == False:
                    os.startfile(openxls)
                else:
                    pass

            elif unit.type == "region":
                if out_path == False:
                    out_path = GetDirPath(unit,walk_path)
                arch = AskYesOrNo(
                    "  exclude archeological features from counts? y/n ")
                gdb_type = raw_input(
                    "  analyze SCRATCH .gdb or REGION .gdb?"\
                    "\n  --> ")
                while not gdb_type.lower() in ["scratch","region"]:
                    gdb_type = raw_input("  --> ")
                use_list = []
                
                openxls = MakeSpreadsheetRegion(
                        unit.code,stan_gdb,out_path,gdb_type,use_list,arch)
                if not openxls == False:
                    os.startfile(openxls)
                else:
                    pass
                  
            else:
                for l in unit.landscapes:
                    print l[0]
                    land = MakeUnit(l[0])
                    out_path = GetDirPath(land,walk_path)
                    openxls = MakeSpreadsheetScratch(land.code,walk_path,out_path)
                    if not openxls == False:
                        os.startfile(openxls)

        if "pdf" in next_task:
            if unit.type == "landscape":
                pdf_path = r"{0}\{1}\{2}\CrystalReportViewer.pdf".format(
                    walk_path,unit.park[0],unit.code)
                print "  expected park report path:"
                print " ", pdf_path
                if os.path.isfile(pdf_path):
                    os.startfile(pdf_path)
                else:
                    print "park report does not exist for this landscape yet."
                
            else:
                print "not gonna open multiple park reports."

        if "mxd" in next_task:
            if unit.type == "landscape":
                mxd_path = r"{0}\{1}\{2}\{2}.mxd".format(
                    walk_path,unit.park[0],unit.code)
                print "  expected map document path:"
                print " ", mxd_path
                if os.path.isfile(mxd_path):
                    os.startfile(mxd_path)
                else:
                    print "  map document does not exist for this landscape yet."
                
            else:
                print "  not gonna open multiple landscape map documents."

        if "jpg" in next_task:
            if unit.type == "landscape":
                cli_number = unit.code
                alpha_code = unit.park[0]
                cli_dir_path = r"{0}\{1}\{2}".format(walk_path,alpha_code,cli_number)
                sp = False
                print ""
                print "  available site plan graphics:"
                for f in os.listdir(cli_dir_path):
                    if f.lower().endswith(".jpg") or f.lower().endswith(".tif"):
                        if sp == False:
                            os.startfile(cli_dir_path + os.sep + f)
                        print "   ", f
                        sp = True                        
                        
                if sp == False:
                    print "  no .jpg site plans in cli folder"

                sp = False
                
            else:
                print "  not gonna open site plans for multiple landscapes."

        ## done with actions tasks
        print ""

        if next_task.upper() in AllGoodInputs():
            good_input = True
            need_prompt = False
            choice = next_task
            break

        next_task = raw_input(prompt).lower()

    del walk_path

