import os
import sys

## set path to modules directory and add to sys.path
importpath = os.path.join("..","scripts")
sys.path.append(os.path.realpath(importpath))

from clitools import management
from clitools import enterprise
from clitools import summarize
from clitools import paths
from clitools import mxdops
from clitools import classes
from clitools import general

climods = [
    management,
    enterprise,
    summarize,
    paths,
    mxdops,
    classes,
    general,
]

headers = ["FUNCTIONS","CLASSES"]

for mod in climods:
    name = mod.__name__
    
    tempfilename = "{}_temp.md".format(name)
    outfilename = tempfilename.replace("_temp","")
    
    with open(tempfilename,"wb") as f:
        sys.stdout = f
        help(mod)
        sys.stdout = sys.__stdout__

    in_section = False
    lastline = ""
    cur_indent = 0
    use_section = False
    with open(tempfilename,"rb") as r:
        lines = r.readlines()
        outlines = ["## "+name+"\n\n"]
        outlines.append(mod.__doc__+"\n")
        for line in lines:
            line = line.rstrip()
            
            if line == "":
                if use_section:
                    outlines.append("\n")
                    lastline = line
                continue
                
            if line[0] != " ":
                if line in headers:
                    cur_indent = 0
                    
                    use_section = True
                    outlines.append("### "+line[0].upper()+line[1:].lower()+"\n\n")
                    lastline = line
                    
                else:
                    use_section = False
                    
                continue
                
            if line[:8].rstrip() == "" and use_section:
                cur_indent = 2
                outlines.append(line.lstrip()+"\n")
                lastline = line
                continue
                
            if line[:4].rstrip() == "" and use_section:
                if cur_indent != 1:
                    fname = line.split("(")[0].lstrip()
                    outlines.append("##### "+fname+"\n\n")
                    outlines.append("``"+line.lstrip()+"``\n\n")
                else:
                    outlines.append(line.lstrip()+"\n")
                cur_indent = 1
                lastline = line

    with open(outfilename,"wb") as out:
        out.writelines(outlines)
        
    os.remove(tempfilename)
