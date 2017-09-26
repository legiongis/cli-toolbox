__doc__ = \
"""Holds the paths to the lookup tables, files, and folders within the bin
directory.  All paths in all functions that reference data in the bin folder
use these variables.
"""

import os
from clitools.config import settings

BinDir = os.path.join(settings['toolbox-location'],'scripts','clitools','bin')
LayerDir = os.path.join(BinDir,"layer files")
BinGDB = os.path.join(BinDir,"CLI_InfoTables.gdb")
FeatureLookupTable = os.path.join(BinGDB,"FeatureInfoLookup")
UnitLookupTable = os.path.join(BinGDB,"UnitInfoLookup")
SourceLookupTable = os.path.join(BinGDB,"SourceInfo")
MXDempty = os.path.join(BinDir,"blank.mxd")
MXDtemplate = os.path.join(BinDir,"mxd_template.mxd")
GDBscratch = os.path.join(BinDir,"CLI_scratch_template.gdb")
GDBscratch_WGS84 = os.path.join(BinDir,"CLI_scratch_template_WGS84.gdb")
GDBstandard = os.path.join(BinDir,"CLI_standard_template.gdb")
GDBstandard_link = os.path.join(BinDir,"CLI_standard_template_JustLink.gdb")
GDBstandard_WGS84 = os.path.join(BinDir,"CLI_standard_template_WGS84.gdb")
ProjDir = os.path.join(BinDir,"projection data")
WGS84prj = os.path.join(ProjDir,"WGS 1984.prj")
NAD83prj = os.path.join(ProjDir,"NAD 1983.prj")
NAD27prj = os.path.join(ProjDir,"NAD 1927.prj")
UTM83dir = os.path.join(ProjDir,"UTM NAD 1983")
UTM84dir = os.path.join(ProjDir,"UTM WGS 1984")
UTM27dir = os.path.join(ProjDir,"UTM NAD 1927")
SPdir = os.path.join(ProjDir,"SP NAD 1983 (US Feet)")