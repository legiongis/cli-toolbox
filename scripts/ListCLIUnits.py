from clitools.classes import MakeUnit

region_code = raw_input("enter region code: ")

region = MakeUnit(region_code)

for i in region.landscapes:
    print i

raw_input()
