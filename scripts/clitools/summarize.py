__doc__ = \
"""Contains a variety of functions that are used by the scripts associated
with the tools in the CLI Toolbox.  These functions use the xlrd and xlwt
modules to create a few different forms of MS Excel spreadsheet summaries
of landscape and their features.  The xlrd and xlwt modules were developed
by David Giffin <david@giffin.org>, and are freely distributable under a 
4-clause BSD-style license.

If the clitools package is moved to the user's native Python installation,
all of these functions will be available to any python scripting.  Use the
following syntax to import the function:

from clitools.summarize import <function_name>

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
import traceback, sys
from time import strftime
import xlrd
import xlwt

from .classes import MakeUnit
from .enterprise import CheckForEnterpriseTables
from .config import settings

from general import (
    Print,
    GetDraftedFeatureCounts,
    GetDraftedFeatureCountsScratch,
    TakeOutTrash,
    MakePathList
    )

## This block of code is used to list the landscapes that were included in the
## original scope of work for the project.  These lists of tuples are referenced 
## in the regional spreadsheet function.
ser_sow = [('975192', u'ABLI'), ('550132', u'ABLI'), ('550146', u'ANDE'), ('550147', u'ANDE'), ('550094', u'ANJO'), ('550011', u'BISC'), ('550005', u'BISO'), ('550006', u'BISO'), ('550008', u'BISO'), ('550009', u'BISO'), ('550138', u'BLRI'), ('550140', u'BLRI'), ('550214', u'BLRI'), ('550215', u'BLRI'), ('550216', u'BLRI'), ('550218', u'BLRI'), ('550219', u'BLRI'), ('550145', u'BLRI'), ('550220', u'BLRI'), ('550221', u'BLRI'), ('550222', u'BLRI'), ('550223', u'BLRI'), ('550150', u'CAHA'), ('550155', u'CHAT'), ('550156', u'CHAT'), ('550059', u'CHCH'), ('550060', u'CHCH'), ('550061', u'CHCH'), ('550062', u'CHCH'), ('550063', u'CHCH'), ('550064', u'CHCH'), ('550065', u'CHCH'), ('550066', u'CHCH'), ('550067', u'CHCH'), ('550068', u'CHCH'), ('550069', u'CHCH'), ('550070', u'CHCH'), ('550236', u'CHCH'), ('550018', u'DRTO'), ('550172', u'EVER'), ('975659', u'EVER'), ('975723', u'FODO'), ('550055', u'FOPU'), ('550168', u'FORA'), ('550078', u'GRSM'), ('550118', u'GRSM'), ('550119', u'GRSM'), ('550120', u'GRSM'), ('550121', u'GRSM'), ('550122', u'GRSM'), ('550123', u'GRSM'), ('550124', u'GRSM'), ('550125', u'GRSM'), ('550126', u'GRSM'), ('550127', u'GRSM'), ('550190', u'GRSM'), ('550205', u'GRSM'), ('550198', u'GRSM'), ('550002', u'GUCO'), ('550003', u'GUCO'), ('550020', u'HOBE'), ('550111', u'JELA'), ('550203', u'JELA'), ('550050', u'KEMO'), ('550051', u'KEMO'), ('550047', u'KIMO'), ('550048', u'KIMO'), ('550049', u'KIMO'), ('550176', u'NATC'), ('550193', u'NATR'), ('550021', u'OCMU'), ('550022', u'OCMU'), ('550097', u'STRI'), ('550098', u'STRI'), ('550099', u'STRI'), ('550100', u'STRI'), ('550101', u'STRI'), ('550102', u'STRI'), ('550109', u'STRI'), ('550112', u'STRI'), ('550114', u'STRI'), ('550110', u'TIMU'), ('550185', u'VICK'), ('975474', u'VIIS'), ('550169', u'WRBR')]
ner_sow = [('300123','SHEN'),('300124','SHEN'),('650053','SARA'),('650048','ROWI'),('650043','MIMA'),('650041','MIMA'),('650039','MIMA'),('650041','MIMA'),('650040','MIMA'),('650032','JOFI'),('300173','FRSP'),('300179','FRED'),('975695','EDIS'),('650002','EDIS'),('975707','COLO'),('650021','BOST'),('650017','ADAM'),('650090','ACAD'),('300084','COLO'),('975512','GATE'),('300085','COLO'),('650075','HOFR'),('300089','APCO'),('650077','MORR'),('650060','ACAD'),('300177','FRSP'),('975550','SHEN'),('975558','SAGA'),('300100','RICH'),('650036','MIMA'),('650037','MIMA'),('300118','SHEN'),('650072','CACO'),('300204','NERI'),('300024','DEWA'),('300021','VAFO'),('975560','VAMA'),('650067','ACAD'),('650066','ACAD'),('650064','ACAD'),('650063','SACR'),('650069','ACAD'),('650068','ACAD'),('300018','VAFO'),('300150','GEWA'),('300185','GEWA'),('650096','SARA'),('650097','SARA'),('650095','SARA'),('300087','COLO'),('300115','SHEN'),('300119','SHEN'),('300205','NERI'),('650022','BOST'),('650027','FOST'),('650026','FIIS'),('650024','ELRO'),('650114','CACO'),('650111','CACO'),('650110','CACO'),('650058','VAMA'),('650056','SPAR'),('300216','POGR'),('300015','VAFO'),('300017','VAFO'),('300223','COLO'),('300117','SHEN'),('300116','SHEN'),('650013','WORI'),('650010','MORR'),('650011','MORR'),('650014','WORI'),('650155','MABI'),('650154','GOIS'),('300020','VAFO'),('650124','WORI'),('650089','ACAD'),('650088','ACAD'),('300196','PETE'),('650084','GATE'),('975526','GATE'),('975388','SHEN'),('975386','SHEN'),('300120','APCO'),('300121','SHEN'),('300122','SHEN'),('300125','SHEN'),('300126','SHEN'),('300127','SHEN'),('300129','SHEN'),('975506','ACAD'),('650041','MIMA'),('650045','MIMA'),('650047','MORR'),('650046','MORR'),('300098','RICH'),('300099','RICH'),('975552','SHEN'),('975556','SAGA'),('975554','SHEN'),('300161','ASIS'),('300169','FONE'),('300005','EISE'),('300003','EISE'),('300001','FOMC'),('650020','BOST'),('650003','STLI'),('650004','ELIS'),('650008','FIIS'),('975420','CEBE'),('975390','SHEN'),('300133','GETT')]
pwr_sow = [('725543', u'BIHO'), ('975450', u'CABR'), ('725078', u'CHIS'), ('725083', u'CHIS'), ('725080', u'CHIS'), ('725483', u'CHIS'), ('725485', u'CHIS'), ('400004', u'CIRO'), ('400007', u'CRLA'), ('400249', u'CRLA'), ('400006', u'CRLA'), ('400186', u'CRLA'), ('400189', u'CRLA'), ('975518', u'DEVA'), ('975530', u'DEVA'), ('400250', u'DEVA'), ('725096', u'DEVA'), ('725097', u'DEVA'), ('725105', u'DEVA'), ('725106', u'DEVA'), ('725107', u'DEVA'), ('725109', u'DEVA'), ('725113', u'DEVA'), ('725114', u'DEVA'), ('725115', u'DEVA'), ('725116', u'DEVA'), ('725118', u'DEVA'), ('725119', u'DEVA'), ('725018', u'EUON'), ('400177', u'FOVA'), ('400179', u'FOVA'), ('975379', u'FOVA'), ('975330', u'GOGA'), ('975275', u'GOGA'), ('725240', u'GOGA'), ('725241', u'GOGA'), ('725243', u'GOGA'), ('725249', u'GOGA'), ('725255', u'GOGA'), ('725257', u'GOGA'), ('725123', u'GRBA'), ('975494', u'HALE'), ('975105', u'HALE'), ('975108', u'HAVO'), ('975050', u'HAVO'), ('975082', u'HAVO'), ('400016', u'JODA'), ('725020', u'JOMU'), ('725033', u'JOTR'), ('975444', u'JOTR'), ('725029', u'JOTR'), ('725046', u'JOTR'), ('975012', u'KALA'), ('975016', u'KALA'), ('725048', u'LABE'), ('725265', u'LAKE'), ('400017', u'LARO'), ('725057', u'LAVO'), ('725061', u'LAVO'), ('725063', u'LAVO'), ('725221', u'MANZ'), ('975323', u'MIIN'), ('700002', u'MOJA'), ('700015', u'MOJA'), ('725129', u'MOJA'), ('725541', u'MOJA'), ('400002', u'MORA'), ('400018', u'MORA'), ('400019', u'MORA'), ('400020', u'MORA'), ('400021', u'MORA'), ('400023', u'MORA'), ('400027', u'MORA'), ('400029', u'MORA'), ('400030', u'MORA'), ('400031', u'MORA'), ('400032', u'MORA'), ('400033', u'MORA'), ('400034', u'MORA'), ('400118', u'MORA'), ('400127', u'MORA'), ('725254', u'MUWO'), ('400180', u'NEPE'), ('400162', u'NEPE'), ('400183', u'NOCA'), ('400212', u'NOCA'), ('400086', u'OLYM'), ('400087', u'OLYM'), ('400088', u'OLYM'), ('400089', u'OLYM'), ('400090', u'OLYM'), ('400091', u'OLYM'), ('400233', u'OLYM'), ('725276', u'PARA'), ('725387', u'PARA'), ('725071', u'PINN'), ('700017', u'PINN'), ('725493', u'PINN'), ('725003', u'PORE'), ('725014', u'PORE'), ('725200', u'PORE'), ('725202', u'PORE'), ('725203', u'PORE'), ('725212', u'PORE'), ('725005', u'PORE'), ('725006', u'PORE'), ('725011', u'PORE'), ('725012', u'PORE'), ('725013', u'PORE'), ('725016', u'PORE'), ('725017', u'PORE'), ('725167', u'PORE'), ('725170', u'PORE'), ('725177', u'PORE'), ('725481', u'PORE'), ('725182', u'PORE'), ('725183', u'PORE'), ('725188', u'PORE'), ('725189', u'PORE'), ('975035', u'PUHE'), ('975502', u'PUHO'), ('700003', u'REDW'), ('700005', u'REDW'), ('725358', u'SAFR'), ('400105', u'SAJH'), ('400106', u'SAJH'), ('400174', u'SAJH'), ('725074', u'SAMO'), ('725075', u'SAMO'), ('725076', u'SAMO'), ('725360', u'SEKI'), ('725375', u'SEKI'), ('975116', u'WAPA'), ('725213', u'WHIS'), ('725296', u'YOSE'), ('725297', u'YOSE'), ('725308', u'YOSE'), ('725311', u'YOSE'), ('975546', u'YOSE'), ('725341', u'YOSE'), ('725351', u'YOSE')]
ncr_sow = [('600048', u'ANTC'), ('600030', u'ANTI'), ('600034', u'ANTI'),('600091','NACE'), ('600047', u'ANTI'), ('600284', u'ANTI'), ('975301', u'ANTI'), ('975731', u'ANTI'), ('600049', u'ARHO'), ('600137', u'BATT'), ('600017', u'CATO'), ('600104', u'CATO'), ('600271', u'CHOH'), ('600278', u'CHOH'), ('600279', u'CHOH'), ('600289', u'CHOH'), ('975434', u'CHOH'), ('600098', u'FOWA'), ('600033', u'FRDO'), ('600052', u'GLEC'), ('600170', u'GWMP'), ('600177', u'GWMP'), ('600245', u'GWMP'), ('600247', u'GWMP'), ('600288', u'GWMP'), ('600005', u'HAFE'), ('600062', u'HAFE'), ('600290', u'HAFE'), ('600295', u'HAFE'), ('975428', u'HAFE'), ('600004', u'JEFM'), ('600182', u'MANA'), ('600185', u'MANA'), ('600201', u'MONO'), ('600294', u'MONO'), ('600072', u'NACE'), ('600075', u'NACE'), ('600076', u'NACE'), ('600248', u'NACE'), ('600093', u'NACE'), ('600012', u'NAMA'), ('975436', u'NAMA'), ('600213', u'NAMA'), ('600227', u'NAMA'), ('600228', u'NAMA'), ('600230', u'NAMA'), ('600242', u'NAMA'), ('975261', u'NAMA'), ('600019', u'PRWI'), ('600032', u'ROCR'), ('600108', u'ROCR'), ('600115', u'ROCR'), ('600147', u'ROCR'), ('600165', u'ROCR'), ('600261', u'ROCR'), ('600265', u'ROCR'), ('975381', u'ROCR'), ('975383', u'ROCR'), ('600061', u'TRIS'), ('600016', u'WASH'), ('975602', u'WHHO')]
mwr_sow = [('500989', u'AGFO'), ('501358', u'AGFO'), ('975288', u'AGFO'), ('500303', u'APIS'), ('500358', u'APIS'), ('500359', u'APIS'), ('500360', u'APIS'), ('500362', u'APIS'), ('500363', u'APIS'), ('500364', u'APIS'), ('500365', u'APIS'), ('500366', u'APIS'), ('500368', u'APIS'), ('500826', u'APIS'), ('500850', u'BADL'), ('500006', u'BRVB'), ('500851', u'BUFF'), ('500852', u'BUFF'), ('500856', u'BUFF'), ('500898', u'BUFF'), ('500918', u'BUFF'), ('975514', u'BUFF'), ('501428', u'CEHS'), ('500212', u'CUVA'), ('500273', u'CUVA'), ('500937', u'CUVA'), ('500961', u'CUVA'), ('500964', u'CUVA'), ('500973', u'CUVA'), ('500974', u'CUVA'), ('501202', u'CUVA'), ('501373', u'CUVA'), ('975277', u'CUVA'), ('501388', u'CUVA'), ('500249', u'CUVA'), ('500987', u'CUVA'), ('500379', u'DAAV'), ('501182', u'DAAV'), ('975360', u'EFMO'), ('975361', u'EFMO'), ('450005', u'FOLS'), ('450012', u'FOSC'), ('450013', u'FOSC'), ('500389', u'FOSM'), ('450011', u'FOUS'), ('500390', u'GERO'), ('500927', u'GRPO'), ('500391', u'GWCA'), ('500401', u'HEHO'), ('500393', u'HOCU'), ('501184', u'HOCU'), ('975460', u'HOCU'), ('500423', u'HOME'), ('501364', u'HOME'), ('500341', u'HOSP'), ('975290', u'HOSP'), ('500439', u'HSTR'), ('501438', u'HSTR'), ('500102', u'INDU'), ('500113', u'INDU'), ('500116', u'INDU'), ('500443', u'INDU'), ('500186', u'INDU'), ('501440', u'INDU'), ('500444', u'ISRO'), ('500447', u'ISRO'), ('500482', u'ISRO'), ('500513', u'ISRO'), ('500520', u'ISRO'), ('500568', u'ISRO'), ('501404', u'ISRO'), ('501189', u'JAGA'), ('501075', u'JECA'), ('450002', u'JEFF'), ('450003', u'JEFF'), ('450006', u'JEFF'), ('501432', u'KEWE'), ('501433', u'KEWE'), ('501434', u'KEWE'), ('501435', u'KEWE'), ('501437', u'KEWE'), ('450001', u'KNRI'), ('450007', u'KNRI'), ('450008', u'KNRI'), ('450009', u'KNRI'), ('501366', u'KNRI'), ('500583', u'LIBO'), ('501429', u'MIMI'), ('501430', u'MIMI'), ('501080', u'MORU'), ('500587', u'NICO'), ('500041', u'OZAR'), ('500046', u'OZAR'), ('500059', u'OZAR'), ('500063', u'OZAR'), ('500604', u'OZAR'), ('500613', u'OZAR'), ('500628', u'OZAR'), ('500630', u'OZAR'), ('500631', u'OZAR'), ('500637', u'OZAR'), ('500035', u'OZAR'), ('975524', u'OZAR'), ('975452', u'PERI'), ('500023', u'PEVI'), ('501118', u'PIPE'), ('500318', u'PIRO'), ('501218', u'SACN'), ('501231', u'SACN'), ('501344', u'SACN'), ('975488', u'SACN'), ('500001', u'SCBL'), ('450004', u'SLBE'), ('500003', u'SLBE'), ('500330', u'SLBE'), ('975462', u'SLBE'), ('975538', u'SLBE'), ('975586', u'SLBE'), ('501138', u'TAPR'), ('501139', u'TAPR'), ('500762', u'THRO'), ('501145', u'THRO'), ('501146', u'THRO'), ('975665', u'THRO'), ('500101', u'ULSG'), ('450014', u'VOYA'), ('500068', u'VOYA'), ('500073', u'VOYA'), ('500074', u'VOYA'), ('975365', u'VOYA'), ('975564', u'VOYA'), ('975566', u'VOYA'), ('500791', u'WICR'), ('500721', u'WIHO')]
imr_sow = [('850319', u'ARCH'), ('850225', u'AZRU'), ('850226', u'AZRU'), ('850227', u'AZRU'), ('850015', u'BAND'), ('850366', u'BAND'), ('890238', u'BEOL'), ('890013', u'BICA'), ('850160', u'BITH'), ('850501', u'BRCA'), ('850504', u'BRCA'), ('890148', u'CARE'), ('850216', u'CAVE'), ('850217', u'CAVE'), ('850018', u'CAVO'), ('850138', u'CHIC'), ('850139', u'CHIC'), ('850142', u'CHIC'), ('850143', u'CHIC'), ('850144', u'CHIC'), ('850145', u'CHIC'), ('850146', u'CHIC'), ('850465', u'CHIC'), ('850466', u'CHIC'), ('850467', u'CHIC'), ('975440', u'CHIC'), ('850007', u'CHIR'), ('850020', u'CHIR'), ('850489', u'CORO'), ('890007', u'DINO'), ('975596', u'ELMA'), ('975598', u'ELMA'), ('975600', u'ELMA'), ('850108', u'ELMO'), ('850021', u'FOBO'), ('850276', u'FODA'), ('890191', u'FOLA'), ('850082', u'FOUN'), ('975508', u'FOUN'), ('890108', u'GLAC'), ('890166', u'GLCA'), ('890167', u'GOSP'), ('850112', u'GRCA'), ('850122', u'GRCA'), ('890194', u'GRKO'), ('890242', u'GRKO'), ('850491', u'GRTE'), ('890045', u'GRTE'), ('890046', u'GRTE'), ('890056', u'GRTE'), ('890057', u'GRTE'), ('890136', u'GRTE'), ('975608', u'GRTE'), ('975643', u'GRTE'), ('850071', u'GUMO'), ('850072', u'GUMO'), ('850077', u'GUMO'), ('850109', u'HUTR'), ('850083', u'IMSF'), ('890199', u'LIBI'), ('850133', u'LYJO'), ('850135', u'LYJO'), ('850176', u'LYJO'), ('850177', u'LYJO'), ('850296', u'LYJO'), ('850241', u'MEVE'), ('850242', u'MEVE'), ('850243', u'MEVE'), ('850246', u'MEVE'), ('850025', u'ORPI'), ('850463', u'ORPI'), ('975542', u'PAAL'), ('975544', u'PAAL'), ('850085', u'PAIS'), ('850086', u'PAIS'), ('850087', u'PAIS'), ('850092', u'PECO'), ('850114', u'PEFO'), ('850115', u'PEFO'), ('850116', u'PEFO'), ('850119', u'PEFO'), ('850364', u'PEFO'), ('975168', u'PISP'), ('890200', u'ROMO'), ('975211', u'ROMO'), ('850148', u'SAAN'), ('850149', u'SAAN'), ('850150', u'SAAN'), ('850151', u'SAAN'), ('850152', u'SAAN'), ('850490', u'SAGU'), ('850098', u'SAPU'), ('850099', u'SAPU'), ('850100', u'SAPU'), ('975319', u'SUCR'), ('850103', u'TUMA'), ('850104', u'TUMA'), ('850475', u'WABA'), ('975278', u'WACA'), ('850106', u'WHSA'), ('975279', u'WUPA'), ('890064', u'YELL'), ('890082', u'YELL'), ('890087', u'YELL'), ('890215', u'YELL'), ('890229', u'YELL'), ('975154', u'YELL'), ('850485', u'ZION'), ('850486', u'ZION')]
akr_sow = [('100063','WRST'),('100122','KEFJ'),('100120','DENA'),('100127','KATM'),('100124','LACL'),('100128','KATM'),('975703','KATM'),('100058','WRST'),('100050','KLGO'),('100051','KLGO'),('100046','KLGO'),('100060','WRST'),('975442','WRST'),('975562','BELA'),('100096','WRST'),('100091','SITK'),('975498','DENA'),('975311','WRST'),('975287','WRST'),('100131','GAAR'),('100133','KOVA'),('100132','GAAR'),('975534','WRST'),('975536','WRST'),('975532','WRST'),('100041','KATM'),('100044','DENA'),('100047','KLGO'),('975348','DENA'),('975346','DENA'),('100083','KOVA'),('100082','DENA'),('100030','GLBA'),('100086','YUCH'),('100081','SITK'),('100108','BELA'),('100109','LACL'),('975317','KATM'),('975649','WRST'),('100121','KLGO'),('975468','WRST'),('100035','GLBA'),('100028','GLBA'),('975584','WRST'),('100111','ANIA'),('975392','YUCH')]

reg_sow_lists = {"SER":ser_sow,"NER":ner_sow,"NCR":ncr_sow,
                 "MWR":mwr_sow,"IMR":imr_sow,"AKR":akr_sow,
                 "PWR":pwr_sow}

## the following are xlwt.easyxf styles that are used by more than one function.
## they are set here in variables here for easy reuse.

## 1. group one; primarily used by multiple landscape functions
grey_borders = 'border:  left thin, right thin, top thin, bottom thin,'\
                'left_color grey25, right_color grey25, bottom_color grey25,'\
                'top_color grey25'
title_style_big = xlwt.easyxf('font: name Calibri, bold True, height 350')
summary_style = xlwt.easyxf('font: name Calibri, italic True, height 275') 
header_style_big = xlwt.easyxf('font: name Calibri, bold True, height 220;'\
                           'alignment: horizontal center, vertical center,'\
                           'wrap True; '+ grey_borders)
basic_style = xlwt.easyxf('font: name Calibri, height 220;'\
                'alignment: horizontal center, vertical center; '+ grey_borders)
basic_style_grey = xlwt.easyxf('font: name Calibri, height 220;'\
                'pattern: pattern solid, fore_color grey40;'\
                'alignment: horizontal center, vertical center; '+ grey_borders)
basic_style_grey_left = xlwt.easyxf('font: name Calibri, height 220;'\
                'pattern: pattern solid, fore_color grey40;'\
                'alignment: vertical center; '+ grey_borders)
cli_name_style = xlwt.easyxf('font: name Calibri, height 220;'\
                'alignment: horizontal left, vertical center; '+ grey_borders)
cli_name_style_grey = xlwt.easyxf('font: name Calibri, height 220;'\
                'pattern: pattern solid, fore_color grey40;'\
                'alignment: horizontal left, vertical center; '+ grey_borders)
boundary_yes_style = xlwt.easyxf('font: name Calibri, height 240, bold true;'\
                'alignment: horizontal center, vertical center; '+ grey_borders)
boundary_no_style = xlwt.easyxf('font: name Calibri, height 240, bold true,'\
                'color white; alignment: horizontal center, vertical center;'\
                'pattern: pattern solid, fore_color black; '+ grey_borders)
low_pct_style = xlwt.easyxf('font: name Calibri, height 240, bold true;'\
        'alignment: horizontal center, vertical center;'\
        'pattern: pattern solid, fore_color coral; '+ grey_borders)
mid_pct_style = xlwt.easyxf('font: name Calibri, height 240, bold true;'\
        'alignment: horizontal center, vertical center;'\
        'pattern: pattern solid, fore_color light_orange; '+ grey_borders)
high_pct_style = xlwt.easyxf('font: name Calibri, height 240, bold true;'\
        'alignment: horizontal center, vertical center;'\
        'pattern: pattern solid, fore_color lime; '+ grey_borders)

## 2. group two; primarily used by single landscape functions
header_style_small = xlwt.easyxf('font: bold True, name Calibri;'
                'alignment: horizontal center, wrap True;')
header_style_small_left = xlwt.easyxf('font: bold True, name Calibri;'
                'alignment: wrap True')
feat_style_fn = xlwt.easyxf('font: name Calibri')
feat_style = xlwt.easyxf('font: name Calibri;alignment: horizontal center')
geom_style = xlwt.easyxf('font: name Calibri, bold True;'
                        'alignment: horizontal center, vertical center')
highlight = xlwt.easyxf('font: name Calibri;'
                'alignment: horizontal center, vertical center;'\
                'pattern: pattern solid, fore_color light_yellow')
highlight_fn = xlwt.easyxf('font: name Calibri;'
                'pattern: pattern solid, fore_color light_yellow')
feat_style_fn_aqua = xlwt.easyxf('font: bold True, name Calibri;'\
                'pattern: pattern solid, fore_color aqua; '+grey_borders)
feat_style_fn_lime = xlwt.easyxf('font: bold True, name Calibri;'\
                'pattern: pattern solid, fore_color lime; '+grey_borders)

def MakePercentage(partial_num,whole_num):
    '''Creates a formatted percentage based on two numbers.  It is used to
    deal with 0 value inputs.

    Param1: partial number
    Param2: full number

    The output is a string in this format: %xx.xx
    '''

    if partial_num == whole_num:
        perc = "100.0"
    elif int(partial_num) == 0:
        perc = "00.00"
    else:
        num = float(partial_num)*100/whole_num
        if str(num)[1] == ".":
            perc = "0"+str(num)[:4]
        else:
            perc = str(num)[:str(num).find(".")+3]
    if not len(perc) == 5:
        perc+="0"
    return perc

def ChoosePercStyle(value,low_style,mid_style,high_style):
    '''Chooses a cell format style based on the input value for the cell.
    These styles are defined at the beginning of this module, and are not
    included in this function.'''

    if value == "00.00":
        return low_style

    n = float(value)
    if n < 50:
        return low_style
    elif n >= 50 and n < 75:
        return mid_style
    elif n >= 75:
        return high_style
    else:
        return False

def MakeSingleSummaryXLSHeaders(input_sheet_object):
    '''Takes an input xlwt sheet object and adjusts the columns and
    writes headers to fit the single landscape summary template.'''

    input_sheet_object.col(0).width = int(2.5*260)
    input_sheet_object.col(1).width = int(2.5*260)
    input_sheet_object.col(2).width = int(2.5*260)
    input_sheet_object.col(3).width = 10*261
    input_sheet_object.col(4).width = 40*261
    input_sheet_object.col(5).width = 13*261
    input_sheet_object.col(6).width = 27*261
    input_sheet_object.col(7).width = 9*261
    input_sheet_object.col(8).width = 9*261
    input_sheet_object.col(9).width = 9*261
    input_sheet_object.col(10).width = 9*261
    input_sheet_object.col(11).width = 50*261
    input_sheet_object.col(12).width = 10*261
    input_sheet_object.col(13).width = 10*261
    input_sheet_object.col(14).width = 10*261
    input_sheet_object.col(15).width = 10*261
    input_sheet_object.col(16).width = 10*261
    input_sheet_object.col(17).width = 10*261
    header_row = input_sheet_object.row(0)
    header_row.write(0,"pt",header_style_small)
    header_row.write(1,"ln",header_style_small)
    header_row.write(2,"py",header_style_small)
    header_row.write(3,"CLI_ID",header_style_small)
    header_row.write(4,"Feature Name",header_style_small_left)
    header_row.write(5,"Contributing?",header_style_small)
    header_row.write(6,"Landscape Characteristic",header_style_small)
    header_row.write(7,"Current Dataset",header_style_small)
    header_row.write(8,"Switch to Dataset",header_style_small)
    header_row.write(9,"LCS_ID",header_style_small)
    header_row.write(10,"HS_ID",header_style_small)
    header_row.write(11,"comment",header_style_small_left)
    header_row.write(12,"Need to Revise GIS [Y/N]",header_style_small_left)
    header_row.write(13,"Staff",header_style_small_left)
    header_row.write(14,"Date Revision Completed",header_style_small_left)
    header_row.write(15,"Need to Revise Database [Y/N]",header_style_small_left)
    header_row.write(16,"Staff",header_style_small_left)
    header_row.write(17,"Date Revision Completed",header_style_small_left)

def MakeMultipleSummaryXLSHeaders(input_sheet_object,full=True):
    '''Takes an input xlwt sheet object and adjusts the columns and
    writes headers to fit the single landscape summary template.'''

    input_sheet_object.col(0).width = 10*256
    input_sheet_object.col(1).width = 10*256
    input_sheet_object.col(2).width = 50*256
    input_sheet_object.col(3).width = 11*256
    input_sheet_object.col(4).width = 11*256
    input_sheet_object.col(5).width = 12*256
    input_sheet_object.col(6).width = 11*256
    input_sheet_object.col(7).width = 11*256
    input_sheet_object.col(8).width = 11*256
    input_sheet_object.col(9).width = 11*256
    if full:
        input_sheet_object.col(10).width = 11*256
        input_sheet_object.col(11).width = 11*256
        input_sheet_object.col(12).width = 11*256
        input_sheet_object.col(13).width = 11*256

    header_row = input_sheet_object.row(2)
    header_row.write(0,"PARK ALPHA CODE",header_style_big)
    header_row.write(1,"CLI UNIT NUMBER",header_style_big)
    header_row.write(2,"CLI UNIT NAME",header_style_big)
    header_row.write(3,"BOUNDARY PRESENT?",header_style_big)
    header_row.write(4,"CONTRIB. FEATURES DONE",header_style_big)
    header_row.write(5,"CONTRIB. FEATURES EXPECTED",header_style_big)
    header_row.write(6,"CONTRIB. FEATURES PROGRESS",header_style_big)
    header_row.write(7,"TOTAL FEATURES DONE",header_style_big)
    header_row.write(8,"TOTAL FEATURES EXPECTED",header_style_big)
    header_row.write(9,"TOTAL FEATURES PROGRESS",header_style_big)
    if full:
        header_row.write(10,"CONTRIB. FEATURES EXPECTED IN PARK",header_style_big)
        header_row.write(11,"TOTAL FEATURES EXPECTED IN PARK",header_style_big)
        header_row.write(12,"PARK PROGRESS FOR CONTRIBUTING FEATURES",header_style_big)
        header_row.write(13,"PARK PROGRESS FOR TOTAL FEATURES",header_style_big)

def MakeMultipleLandscapeXLS(input_geodatabase,out_directory,cli_list=[],
                                                        exclude_arch=False):
    """ Creates a spreadsheet with one line per landscape that is included
    in the cli_list.  The output spreadsheet will have percentages, totals,
    and color coding for the GIS feature contents of each landscape."""

    try:

        ## make output book path
        gdb_name = os.path.splitext(os.path.basename(input_geodatabase))[0]
        book_path = os.path.join(out_directory,strftime(
                            "{0}_%Y%b%d_%H%M.xls".format(gdb_name)))
        if exclude_arch:
            book_path = os.path.join(out_directory,strftime(
                            "{0}_NoArch_%Y%b%d_%H%M.xls".format(gdb_name)))

        ## print output path
        arcpy.AddMessage("\nOutput spreadsheet:\n  {0}\n".format(book_path))

        ## make dictionary of cli numbers and park alphas, ordered by alpha
        cli_and_park_dict = {}
        park_list = []
        for cl in cli_list:
            aaa = MakeUnit(cl)
            if not aaa:
                arcpy.AddError("ERROR: {0} is an invalid CLI number.  You may "\
                    "need to update your CLI Info Tables if this is a brand "\
                    "new CLI.  See toolbox documentation for more information.")
            alph = aaa.park[0]
            if not alph in park_list:
                park_list.append(alph)
                cli_and_park_dict[cl] = alph

        clis_in_order = cli_list

        ## this is all the units that are in any parks that are included 
        cli_full_list = []
        for cli in cli_and_park_dict.iterkeys():
            un = MakeUnit(cli)
            pk_cd = un.park[0]
            pk = MakeUnit(pk_cd)
            for ls in [i[0] for i in pk.landscapes]:
                cli_full_list.append(ls)

        ## go through all landscapes and get completed feature counts for each
        ## also go through all that are in the         
        cli_all_feat,cli_contrib_feat,alpha_all_feat,alpha_contrib_feat = \
                                                       {},{},{},{}
        Print("\nGetting counts of features in geodatabase...")
        counter = 1
        prog_count = 1

        boundaries = []
        previous = 0
        for cli in cli_full_list:

            if cli in cli_list:
                Print("  {0} ({1} of {2})".format(cli,prog_count,len(cli_list)))
                prog_count+=1            

            ## get count for features that are in GIS for this unit.
            c_unit = MakeUnit(cli)
            if c_unit == False:
                continue
            cli_id_list = c_unit.GetFeatureList()


            #if gdb_type == "region":
            cli_features_done = GetDraftedFeatureCounts(
                    cli,cli_id_list,input_geodatabase,exclude_arch)

            if cli_features_done[2]:
                boundaries.append(cli)
                
            ## count for features that are in the CLI database for this unit
            landscape_unit = MakeUnit(cli)
            f = landscape_unit.GetFeatureDict()

            if exclude_arch:
                all_in_cli_ct = len([i for i in f.keys() if not f[i][2] ==\
                                                         "Archeological Sites"])
                contrib_in_cli_ct = len([i for i in f.keys() if (f[i][1] == "Contributing"\
                                                    and not f[i][2] == "Archeological Sites")])
            else:
                all_in_cli_ct = len(f.keys())
                contrib_in_cli_ct = len([i for i in f.keys() if f[i][1] == "Contributing"])

            cli_features_total = [all_in_cli_ct,contrib_in_cli_ct]

            #calculate percentages
            total_perc = MakePercentage(cli_features_done[0],cli_features_total[0])
            contrib_perc = MakePercentage(cli_features_done[1],cli_features_total[1])

            #make entries to dictionaries
            cli_all_feat[cli] = [cli_features_total[0],cli_features_done[0],total_perc]
            cli_contrib_feat[cli] = [cli_features_total[1],cli_features_done[1],contrib_perc]

            ## nifty progress bar printing
            percent_int = int(counter * 100./len(cli_full_list))
            
            if not percent_int == previous:
                if percent_int%5 == 0:
                    num = str(percent_int)
                    if len(num) == 1:
                        num = "0"+num
                    print num+"%",
                elif percent_int == 100:
                    print "COMPLETE"
                    break
                elif previous%25 == 0:
                    print "\n*",
                else:
                    print "*",
                previous = percent_int

            counter+=1

        Print("\nCalculating park completion percentages...\n")
        for p in park_list:

            park = MakeUnit(p)

            clis_in_park = [i[0] for i in park.landscapes]

            ## skip if there are no relevant landscapes in this park
            if len([d for d in clis_in_park if d in cli_full_list]) == 0:
                continue

            park_total_feat_ct = 0
            park_contrib_feat_ct = 0
            for l in [i[0] for i in park.landscapes]:
                z = MakeUnit(l)
                park_total_feat_ct += len(z.GetFeatureList())
                y = z.GetFeatureDict()
                park_contrib_feat_ct += len([i for i in y.keys() if\
                    y[i][1] == "Contributing"])

           # park_total_feat_ct = sum([cli_all_feat[i][0] for i in clis_in_park])
            park_done_ct = sum([cli_all_feat[i][1] for i in clis_in_park])

           # park_contrib_feat_ct = sum([cli_contrib_feat[i][0] for i in clis_in_park])
            park_contrib_done_ct = sum([cli_contrib_feat[i][1] for i in clis_in_park])

            ## calculate percentages
            total_park_perc = MakePercentage(park_done_ct,park_total_feat_ct)
            contrib_park_perc = MakePercentage(park_contrib_done_ct,park_contrib_feat_ct)

            ## make entries to dictionaries
            alpha_all_feat[park.code] = [park_total_feat_ct,park_done_ct,total_park_perc]
            alpha_contrib_feat[park.code] = [park_contrib_feat_ct,park_contrib_done_ct,contrib_park_perc]      

        ## make book object and begin writing info to it
        book = xlwt.Workbook(style_compression = 2)
        fsheet = book.add_sheet(gdb_name[:30])

        MakeMultipleSummaryXLSHeaders(fsheet)

        #write cli info to rows
        rownum = 3
        for landscape in clis_in_order:

            #create all of the values to be written from existing dictionaries
            l = MakeUnit(landscape)
            Print("writing {0} - {1} ({2})".format(l.park[0],l.name,l.code))
            cont_done = str(cli_contrib_feat[l.code][1])
            cont_expect = str(cli_contrib_feat[l.code][0])
            cont_perc = str(cli_contrib_feat[l.code][2])
            cont_perc_style = ChoosePercStyle(float(cont_perc),
                                    low_pct_style,mid_pct_style,high_pct_style)
                
            total_done = str(cli_all_feat[l.code][1])
            total_expect = str(cli_all_feat[l.code][0])
            total_perc = str(cli_all_feat[l.code][2])
            total_perc_style = ChoosePercStyle(float(total_perc),
                                    low_pct_style,mid_pct_style,high_pct_style)

            cont_park = alpha_contrib_feat[l.park[0]][0]
            total_park = alpha_all_feat[l.park[0]][0]

            cont_park_perc = alpha_contrib_feat[l.park[0]][2]
            cont_park_perc_style = ChoosePercStyle(float(cont_park_perc),
                                    low_pct_style,mid_pct_style,high_pct_style)
            total_park_perc = alpha_all_feat[l.park[0]][2]
            total_park_perc_style = ChoosePercStyle(float(total_park_perc),
                                    low_pct_style,mid_pct_style,high_pct_style)
               
            writerow = fsheet.row(rownum)
            for colnum in range(0,15):
                if colnum == 0:
                    writerow.set_cell_text(colnum,l.park[0],basic_style)
                elif colnum == 1:
                    writerow.set_cell_text(colnum,l.code,basic_style)
                elif colnum == 2:
                    writerow.set_cell_text(colnum,l.name,cli_name_style)
                if colnum == 3:
                    if l.code in boundaries:
                        writerow.set_cell_text(colnum,"YES",boundary_yes_style)
                    else:
                        writerow.set_cell_text(colnum,"NO",boundary_no_style)
                elif colnum == 4:
                    writerow.set_cell_text(colnum,str(cont_done),basic_style)
                elif colnum == 5:
                    writerow.set_cell_text(colnum,str(cont_expect),basic_style)
                elif colnum == 6:
                    writerow.set_cell_text(colnum,cont_perc+"%",cont_perc_style)
                elif colnum == 7:
                    writerow.set_cell_text(colnum,str(total_done),basic_style)
                elif colnum == 8:
                    writerow.set_cell_text(colnum,str(total_expect),basic_style)
                elif colnum == 9:
                    writerow.set_cell_text(colnum,total_perc+"%",total_perc_style)
                elif colnum == 10:
                    writerow.set_cell_text(colnum,str(cont_park),basic_style)
                elif colnum == 11:
                    writerow.set_cell_text(colnum,str(total_park),basic_style)
                elif colnum == 12:
                    writerow.set_cell_text(colnum,cont_park_perc+"%",cont_park_perc_style)
                elif colnum == 13:
                    writerow.set_cell_text(colnum,total_park_perc+"%",total_park_perc_style)
                
            rownum+=1

        #final step, print top row
        date = strftime("%m-%d-%y")
        title = "{0}, {1}".format(gdb_name,date)
        reg_done_cont_ct = sum([cli_contrib_feat[i][1] for i in cli_contrib_feat.keys()])
        reg_total_cont_ct = sum([cli_contrib_feat[i][0] for i in cli_contrib_feat.keys()])
        reg_perc_cont = MakePercentage(reg_done_cont_ct,reg_total_cont_ct)

        reg_done_all_ct = sum([cli_all_feat[i][1] for i in cli_all_feat.keys()])
        reg_total_all_ct = sum([cli_all_feat[i][0] for i in cli_all_feat.keys()])
        reg_perc_all_ct = MakePercentage(reg_done_all_ct,reg_total_all_ct)

        
        cont_sum_msg = "{0} ({1}%) of {2} Contributing Features Drafted".format(
            reg_done_cont_ct,reg_perc_cont,reg_total_cont_ct)
        total_sum_msg = "{0} ({1}%) of all {2} Features Drafted".format(
            reg_done_all_ct,reg_perc_all_ct,reg_total_all_ct)
        
        fsheet.write(0,0,title,title_style_big)
        fsheet.write(0,3,cont_sum_msg,summary_style)
        fsheet.write(0,9,total_sum_msg,summary_style)

        if exclude_arch:
            fsheet.write(
             1,0,"**COUNTS DO NOT INCLUDE ARCHAEOLOGICAL SITE FEATURES**",
                         cli_name_style)
        fsheet.write(1,3,"0% - 50%",low_pct_style)
        fsheet.write(1,4,"50% - 75%",mid_pct_style)
        fsheet.write(1,5,"75% - 100%",high_pct_style)
        
        #save book to specified location
        try:
            book.save(book_path)
            return book_path
        except:
            arcpy.AddMessage("\nError saving workbook.  Make sure that any "\
                "conflicting spreadsheets are not currently open in MS Excel "\
                "and rerun this operation.")
            return False        
    
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
        book.save(book_path)


def MakeSingleLandscapeXLS(cli_num,input_geodatabase,out_directory,
    get_comments_from='',overwrite=False):
    """This is a flexible spreadsheet creation function that will take an
    input geodatabase and analyize it for features that are in the landscape
    that is indicated by the cli number.  The spreadsheet will list all
    expected features in the landscape.  Those that have geometry in the
    geodatabase will have an indication of what type of geometry (pt/ln/py)
    is being used to represent the feature.  Those features that have no
    geometry will be highlighted.  At the end of the spreadsheet there are
    percentages printed, and the location of the input geodatabase.

    Comments from a previous spreadsheet summary of this landscape can be
    incoporated into the output of this function, by placing the file path
    in the get_comments_from parameter.
    """

    try:
        query = '"CLI_NUM" = \''+cli_num+"'"

        ## create landscape object
        landscape = MakeUnit(cli_num)

        ## get dictionary of all feature info in landscape
        f_dict = landscape.GetFeatureDict()

        ## create version of dictionary with '' instead of null values
        f_dict_no_nulls = {}
        for k, v in f_dict.iteritems():
            new_v = ['' if i==None else i for i in v]
            f_dict_no_nulls[k] = new_v                

        ## get list of all features in landscape
        f_list = landscape.GetFeatureList()

        ## create list of paths in gdb
        path_list = MakePathList(input_geodatabase)

        ## determine if it's a scratch or standards geodatabase
        arcpy.env.workspace = input_geodatabase
        if "Historic_Buildings" in arcpy.ListDatasets():
            gdb_type = "standards"
        else:
            gdb_type = "scratch"

        ## construct book path
        book_name = "{0}, {1}".format(landscape.code,landscape.name)
        book_path = r"{0}\{1}.xls".format(out_directory,book_name)

        if not overwrite:
            new_path = book_path
            counter = 1
            while os.path.isfile(new_path):
                new_path = r"{0} {1}.xls".format(book_path[:-4],counter)
                counter+=1
            book_path = new_path

        ## find existing spreadsheet if it exists, and get all comment info
        comments = {}
        if os.path.isfile(get_comments_from):
            ex_bookrd = xlrd.open_workbook(get_comments_from, formatting_info=True)
            ex_sheet = ex_bookrd.sheet_by_index(0)
            for row_x in range(1,ex_sheet.nrows):

                id_cell = ex_sheet.cell(row_x,3)
                #sometimes the existings ids have been formatted as integers
                #and the . on the end of 5-digit ids must be stripped away
                id_cell_value = str(id_cell.value)[:6].rstrip(".")

                ## make a list of all the comment cell values
                comvalues = []
                for col in range(11,18):
                    com_cell = ex_sheet.cell(row_x,col)
                    comvalues.append(com_cell.value)

                ## if the list is completely empty, continue
                t = [i for i in comvalues if not i == '']
                if len(t) == 0:
                    continue
                
                ## else, enter this list as value for the cli_id in the dict
                comments[id_cell_value] = comvalues
            del ex_bookrd,ex_sheet

        ## delete comment file if desired
        if overwrite:
            os.remove(get_comments_from)
                
        ## create workbook with initial info in it
        fbook = xlwt.Workbook()
        fsheet = fbook.add_sheet(cli_num,cell_overwrite_ok=True)

        ## add header rows
        MakeSingleSummaryXLSHeaders(fsheet)

        ## write basic feature info to sheet straight from cli info dict
        cli_id_row_dict = {}
        for x,f_id in enumerate(f_list):

            row = fsheet.row(x+2)
            cli_id_row_dict[f_id] = x+2
            row.set_cell_text(3,f_id,feat_style)
            row.set_cell_text(4,f_dict_no_nulls[f_id][0],feat_style_fn)
            row.set_cell_text(5,f_dict_no_nulls[f_id][1],feat_style)
            row.set_cell_text(6,f_dict_no_nulls[f_id][2],feat_style)
            row.set_cell_text(9,f_dict_no_nulls[f_id][4],feat_style)
            row.set_cell_text(10,f_dict_no_nulls[f_id][5],feat_style)

        ## make list of lists to hold feature presence info for each cli_id
        geometries = []
        datasets = []
        bound = False
        for path in path_list:

            fc_name = os.path.basename(path)
            
            shape = arcpy.Describe(path).shapetype.lower()
            col_num = ["point","polyline","polygon"].index(shape)

            fclass_dict = {"crsite":"Site",
                           "crothr":"Other",
                           "crstru":"Structure",
                           "crobj_":"Object",
                           "crbldg":"Building",
                           "crsurv":"Survey",
                           "crdist":"District",
                           "crland":"Landscape (deprecated value)"}
            
            query = landscape.query
            TakeOutTrash("fl")
            fl = arcpy.management.MakeFeatureLayer(path,"fl",query)
            if int(arcpy.management.GetCount(fl).getOutput(0)) == 0:
                continue

            rows = arcpy.SearchCursor(fl)
            for row in rows:
                num = row.getValue("CLI_ID")

                ## skip if this is the boundary feature
                if num == landscape.code:
                    bound = True
                    continue

                oid = str(row.getValue("OBJECTID"))

                if gdb_type == "standards":
                    ds = fclass_dict[fc_name[:6]]
                if gdb_type == "scratch":
                    ds = str(row.getValue("fclass"))[:6]

                if not num in f_list:
                    Print("  CLI_ID error: {0} (fc {1}, OID {2})".format(
                            str(num),os.path.basename(path),oid))
                    continue

                if not [num,ds] in datasets:
                    datasets.append((num,ds))
                if not [num,col_num] in geometries:
                    geometries.append((num,col_num))

            del rows

        ## write geometry indicators and dataset values
        for geom in geometries:
            fsheet.write(cli_id_row_dict[geom[0]],geom[1],"x",geom_style)
        for ds in datasets:
            fsheet.write(cli_id_row_dict[ds[0]],7,ds[1],feat_style)

        ## create list of missing feature numbers
        missing_features = [i for i in cli_id_row_dict.iterkeys() if not i in
                            [k[0] for k in geometries]]

        ## highlight rows for missing features
        for miss in missing_features:
            if miss == "":
                continue
            row = fsheet.row(cli_id_row_dict[miss])
            
            ## write cli info with highlighting
            row.set_cell_text(3,miss,highlight)
            row.set_cell_text(4,f_dict_no_nulls[miss][0],highlight_fn)
            row.set_cell_text(5,f_dict_no_nulls[miss][1],highlight)
            row.set_cell_text(6,f_dict_no_nulls[miss][2],highlight)
            row.set_cell_text(9,f_dict_no_nulls[miss][4],highlight)
            row.set_cell_text(10,f_dict_no_nulls[miss][5],highlight)
            row.set_style(highlight)

        ## add comments from previous spreadsheet
        for k,v in cli_id_row_dict.iteritems():
            if k == landscape.code:
                continue
            r = fsheet.row(v)
            if k in comments.keys():
                for i in range(11,17):
                    if k in missing_features:
                        r.set_cell_text(i,comments[k][i-11],highlight_fn)
                    else:
                        r.set_cell_text(i,comments[k][i-11],feat_style_fn)
            else:
                for i in range(11,17):
                    if k in missing_features:
                        r.set_cell_text(i,'',highlight_fn)
                    else:
                        r.set_cell_text(i,'',feat_style_fn)
                
        ## fill in row for boundary
        bound_info = [landscape.code,landscape.name,
                      "Not Applicable","LANDSCAPE BOUNDARY"]
        row = fsheet.row(1)
        for y in range(4):
            col_num = y+3
            if not bound:
                if col_num == 4:
                    row.set_cell_text(col_num,bound_info[y],highlight_fn)
                else:
                    row.set_cell_text(col_num,bound_info[y],highlight)
                #highlight row
                row.set_style(highlight)
            else:
                row.set_cell_text(2,"x",geom_style)
                row.set_cell_text(7,"Landscape",feat_style)
                if col_num == 4:
                    row.set_cell_text(col_num,bound_info[y],feat_style_fn)
                else:
                    row.set_cell_text(col_num,bound_info[y],feat_style)
        if landscape.code in comments.keys():
            if bound:
                for i in range(11,17):
                    row.set_cell_text(i,comments[landscape.code][i-11],feat_style_fn)
            else:
                for i in range(11,17):
                    row.set_cell_text(i,comments[landscape.code][i-11],highlight_fn)
        else:
            if bound:
                row.set_cell_text(11,'',feat_style_fn)
            else:
                row.set_cell_text(11,'',highlight_fn)

        ## print percentages in last row
        geodatabase_msg = input_geodatabase
        fsheet.write(len(f_list)+2,3,geodatabase_msg,feat_style_fn_aqua)
        for r in range(4,7):
            fsheet.write(len(f_list)+2,r,'',feat_style_fn_aqua)

        if gdb_type == "standards":
            gis_feat_sum = GetDraftedFeatureCounts(landscape.code,
            f_list,input_geodatabase)
        else:
            gis_feat_sum = GetDraftedFeatureCountsScratch(landscape.code,
            f_list,input_geodatabase)

        expect_all_feat = len(f_list)
        expect_contrib_feat = len([i for i in f_dict.keys() if f_dict[i][1] ==\
            "Contributing"])

        perc_contrib = MakePercentage(gis_feat_sum[1],expect_contrib_feat)
        perc_all = MakePercentage(gis_feat_sum[0],expect_all_feat)
        
        contrib_msg = "{0}% ({1} of {2}) Contributing Features".format(
            perc_contrib,str(gis_feat_sum[1]),str(expect_contrib_feat))
        full_msg = "{0}% ({1} of {2}) Total Features".format(
            perc_all,str(gis_feat_sum[0]),str(expect_all_feat))

        fsheet.write(len(f_list)+3,3,contrib_msg,feat_style_fn_aqua)
        fsheet.write(len(f_list)+3,4,'',feat_style_fn_aqua)
        fsheet.write(len(f_list)+3,5,full_msg,feat_style_fn_aqua)
        fsheet.write(len(f_list)+3,6,'',feat_style_fn_aqua)

        try:
            fbook.save(book_path)
            Print("  spreadsheet created")
            return book_path
        except:
            arcpy.AddError("  ERROR: Problem saving spreadsheet. Permissions issue.\n"\
                  "         Close previous versions and rerun process.")
            return False
        
    except:
            
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     "\
                + str(sys.exc_type) + ": " + str(sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        arcpy.AddError(msgs)
        arcpy.AddError(pymsg)

        Print(msgs)
        Print(pymsg)
        Print(arcpy.GetMessages(1))

def MakeXLSFromSelectedRecords(in_layer,out_path,out_name,fieldnames=[],open=False):
    """This function will create a spreadsheet with some very basic formatting
    (grey background and bold font in header row) from the attribute table
    of the input layer.  If there is a selection in the layer, only the
    selected features will be included.  The user has the option of defining
    which fields will be included."""

    try:
        if fieldnames == []:
            fieldnames = [i.name for i in arcpy.ListFields(in_layer)]

        fieldnames.sort()
        arcpy.AddMessage("\nCreating MS Excel spreadsheet from features in "\
            "{0}.  The following fields will be included:\n{1}".format(
                in_layer,"\n".join(fieldnames)))

        #read values from input table
        attr = {}
        lyr = in_layer
        for i,row in enumerate(arcpy.SearchCursor(lyr,"",fieldnames)):
            attr[i] = []
            for field in fieldnames:
                attr[i].append(row.getValue(field))

        # write to workbook
        book = xlwt.Workbook(style_compression = 2)
        sheet = book.add_sheet("Sheet 1")

        for col,field in enumerate(fieldnames):
            sheet.write(0,col,field,basic_style_grey_left)        

        for k,v in attr.iteritems():
            for n in range(0,len(v)):
                sheet.write(k+1,n,str(v[n]))

        # save to workbook
        out_workbook = os.path.join(out_path,out_name)
        book.save(out_workbook)

        # open workbook if desired
        if open:
            os.startfile(out_workbook)

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

def CREnterpriseSingleXLS(map_document,input_code,output_dir):
    """ Using the tables available in the map document (only the CR
    Catalog and CLI Feature table are necessary), creates a spreadsheet
    with the progress of each feature in the landscape."""

    ## check for tables in map document
    tables = CheckForEnterpriseTables(map_document)
    if not tables:
        return False
    else:
        cli_table = tables[0]
        cr_link_table = tables[1]
        cr_catalog = tables[2]

    if input_code.isdigit() and len(input_code) == 6:
        query = '"CLI_NUM" = \''+input_code+"'"
        arcpy.AddMessage("\nQuery used: " + query)
    else:
        arcpy.AddError("\nInvalid input code.\n")
        return False

    ## get full list of features in landscape
    arcpy.management.SelectLayerByAttribute(cli_table,"NEW_SELECTION",query)
    ct = int(arcpy.management.GetCount(cli_table).getOutput(0))
    if ct == 0:
        arcpy.AddError("\nNo features found in CLI Feature Table matching "\
            "this query.\n")
        return False

    ## create path for new xls file
    new_xls = os.path.join(output_dir,strftime(
                            "EntXLS_{0}_%Y%b%d_%H%M".format(input_code)))
    new_name = new_xls
    r = 1
    while os.path.isfile(new_name+ ".xls"):
        new_name = new_xls+"_"+str(r)
        r+=1
    new_xls = new_name + ".xls"
    arcpy.AddMessage("Output file: {0}".format(new_xls))

    ## get dictionary of features with indication of geometry presence
    result = GetFeatureDictFromTables(
        input_code,cli_table,cr_link_table,cr_catalog)
    order_cli_ids = result[0]
    feat_dict = result[1]

    ## create workbook with initial info in it
    arcpy.AddMessage("Writing rows to output file...")
    fbook = xlwt.Workbook()
    fsheet = fbook.add_sheet(input_code,cell_overwrite_ok=True)

    ## add header rows
    fsheet.col(0).width = 10*261
    fsheet.col(1).width = 40*261
    fsheet.col(2).width = 15*261
    fsheet.col(3).width = 27*261
    fsheet.col(4).width = 20*261
    header_row = fsheet.row(0)
    header_row.write(0,"CLI_ID",header_style_small)
    header_row.write(1,"Feature Name",header_style_small_left)
    header_row.write(2,"Contributing?",header_style_small)
    header_row.write(3,"Landscape Characteristic",header_style_small)
    header_row.write(4,"Current Dataset",header_style_small)

    ## write data to spreadsheet
    contributing_done = 0
    total_done = 0
    for i,v in enumerate(order_cli_ids):
        row = fsheet.row(i+1)
        info = feat_dict[v]
        if len(info) == 4:
            row.write(0,v,feat_style)
            row.write(1,info[0],feat_style_fn)
            row.write(2,info[1],feat_style)
            row.write(3,info[2],feat_style)
            row.write(4,info[3],feat_style)
            
            ## add to feature counts
            total_done+=1
            if info[1].lower() == "contributing":
                contributing_done+=1
        else:
            #row.set_style(highlight)
            row.write(0,v,highlight)
            row.write(1,info[0],highlight_fn)
            row.write(2,info[1],highlight)
            row.write(3,info[2],highlight)
            row.write(4,'',highlight)

    ## print percentages in last row
    n_of_frows = len(order_cli_ids)
    fsheet.write(n_of_frows+1,0,"CR Enterprise Database",feat_style_fn_aqua)
    for r in range(1,4):
        fsheet.write(n_of_frows+1,r,'',feat_style_fn_aqua)

    expect_all_feat = n_of_frows-1
    expect_contrib_feat = len([i for i in feat_dict.keys() if\
        feat_dict[i][1].lower() == "contributing"])

    perc_contrib = MakePercentage(contributing_done,expect_contrib_feat)
    perc_all = MakePercentage(total_done,expect_all_feat)
    
    contrib_msg = "{0}% ({1} of {2}) Contributing Features".format(
        perc_contrib,contributing_done,str(expect_contrib_feat))
    full_msg = "{0}% ({1} of {2}) Total Features".format(
        perc_all,total_done,str(expect_all_feat))

    fsheet.write(n_of_frows+2,0,contrib_msg,feat_style_fn_aqua)
    fsheet.write(n_of_frows+2,1,'',feat_style_fn_aqua)
    fsheet.write(n_of_frows+2,2,full_msg,feat_style_fn_aqua)
    fsheet.write(n_of_frows+2,3,'',feat_style_fn_aqua)


    fbook.save(new_xls)
    arcpy.AddMessage("\nspreadsheet created\n")
    return new_xls

def GetFeatureDictFromTables(cli_number,cli_table,cr_link,cr_catalog):
    """ Uses the input CLI number to analyze the tables and return a
    dictionary that contains a key per expected landscape feature
    (and boundary) and values as lists of info for that feature.

    key=CLI_ID, value=[RESNAME,CONTRIB_STATUS,LAND_CHAR,{RESOURCE_TYPE}]

    RESOURCE_TYPE is appended to the list of values if that feature
    has a spatial feature to represent it.
    """

    ## make selection on cli feature table
    cli_num_qry = '"CLI_NUM" = \'' + cli_number + "'"
    arcpy.management.SelectLayerByAttribute(cli_table,"NEW_SELECTION",
        cli_num_qry)

    ## create dictionary of all features in landscape with info
    feat_dict = {}
    fields = ["CLI_ID","RESNAME","CONTRIB_STATUS","LAND_CHAR"]
    order_cli_ids = []
    sql = (None,"ORDER BY LAND_CHAR, RESNAME")

    try:
        c = arcpy.da.SearchCursor(cli_table,fields,sql_clause=sql)
        arcpy.AddMessage("~~features are sorted~~")
    except:
        c = arcpy.da.SearchCursor(cli_table,fields)
        arcpy.AddMessage("~~features are not sorted~~")

    for row in c:
        cid = row[0]
        if cid == None or cid in feat_dict.keys():
            continue
        if not row[3] == "Boundary":
            order_cli_ids.append(cid)    
        feat_dict[cid] = [row[1],row[2],row[3]]
    del c

    ## add boundary feature at front of cli id list
    order_cli_ids.insert(0,cli_number)

    ## also, add boundary to dictionary if somehow it's missing...
    if not cli_number in feat_dict.keys():
        feat_dict[cli_number] = ["CLI Boundary for [...]","Not Applicable","Boundary"]

    ## use list of cli_ids to query cr link and get all cr_ids
    cli_id_qry = '"CLI_ID" IN (\'{0}\')'.format("','".join(order_cli_ids))
    arcpy.management.SelectLayerByAttribute(cr_link,"NEW_SELECTION",
        cli_id_qry)
    cli_id_cr_id = {}
    with arcpy.da.SearchCursor(cr_link,("CLI_ID","CR_ID")) as c:
        for r in c:
            if not r[0] in cli_id_cr_id.values():
                cli_id_cr_id[r[1]] = r[0]
    cr_ids = cli_id_cr_id.keys()
    cr_id_qry = '"CR_ID" IN (\'{0}\')'.format("','".join(cr_ids))

    ## use cr catalog to find which features have spatial features
    arcpy.management.SelectLayerByAttribute(cr_catalog,"NEW_SELECTION",
        cr_id_qry)
    with arcpy.da.SearchCursor(cr_catalog,("CR_ID","RESOURCE_TYPE")) as c:
        for row in c:
            cr = row[0]
            if cr in cr_ids:
                restype = row[1]
                cid = cli_id_cr_id[cr]
                if len(feat_dict[cid]) == 4:
                    continue
                else:
                    feat_dict[cid].append(restype)

    return (order_cli_ids,feat_dict)

def CREnterpriseMultipleXLS(map_document,input_code,output_dir):
    """ Using the tables available in the map document (only the CR
    Catalog and CLI Feature table are necessary), creates a spreadsheet
    with the progress of each feature in the landscape."""

    ## check for tables in map document
    tables = CheckForEnterpriseTables(map_document)
    
    arcpy.AddMessage("tables found:")
    for t in tables:
        arcpy.AddMessage(t)
        
    if not tables:
        return False
    else:
        cli_table = tables[0]
        cr_link_table = tables[1]
        cr_catalog = tables[2]

    ## create query from input code
    if input_code.isdigit():
        arcpy.AddError("\nInvalid input code.\n")
        return False
    elif len(input_code) == 3:
        query = '"REGION_NAME" = \'' + input_code.upper() + "'"
    elif len(input_code) == 4:
        query = '"ALPHA_CODE" = \'' + input_code.upper() + "'"  
    else:
        arcpy.AddError("\nInvalid input code.\n")
        return False
    arcpy.AddMessage("\nQuery used: " + query)

    ## create path for new xls file
    new_xls = os.path.join(output_dir,strftime(
                            "EntXLS_{0}_%Y%b%d_%H%M".format(input_code)))
    new_name = new_xls
    r = 1
    while os.path.isfile(new_name+ ".xls"):
        new_name = new_xls+"_"+str(r)
        r+=1
    new_xls = new_name + ".xls"
    arcpy.AddMessage("Output file: {0}".format(new_xls))

    ## get full list of landscapes in the park or region
    arcpy.AddMessage("starting select by attribute process")
    arcpy.AddMessage("  using cli_table")
    arcpy.management.SelectLayerByAttribute(cli_table,"NEW_SELECTION",query)
    arcpy.AddMessage("selection completed")
    ct = int(arcpy.management.GetCount(cli_table).getOutput(0))
    arcpy.AddMessage(str(ct))
    if ct == 0:
        arcpy.AddError("\nNo landscapes found in CLI Feature Table matching "\
            "this query.\n")
        return False
    cli_dict = {}
    cli_list = []
    
    fs = ["CLI_NUM","CLI_NAME","ALPHA_CODE"]
    sql = (None,"ORDER BY ALPHA_CODE,CLI_NUM")

    try:
        c = arcpy.da.SearchCursor(cli_table,fs,sql_clause=sql)
        arcpy.AddMessage("~~features are sorted~~")
    except:
        c = arcpy.da.SearchCursor(cli_table,fs)
        arcpy.AddMessage("~~features are not sorted~~")

    for r in c:
        if not r[0] in cli_dict.keys():
            cli_list.append(r[0])
            cli_dict[r[0]] = (r[1],r[2])
    del c

    ## print list of matching landscapes
    ln = len(cli_list)
    arcpy.AddMessage("\n{0} landscape{1} match query".format(ln,'' if ln == 1\
        else 's'))
 
    ## create workbook with initial info in it
    arcpy.AddMessage("\nWriting landscape summaries to output file...")
    fbook = xlwt.Workbook()
    fsheet = fbook.add_sheet(input_code,cell_overwrite_ok=True)

    ## iterate through all landscapes and get counts and write rows
    all_total, all_total_done = 0,0
    all_contrib, all_contrib_done = 0,0

    MakeMultipleSummaryXLSHeaders(fsheet,False) 
    row_num = 3   
    for cli in cli_list:

        ## get cli name and park alpha
        name = cli_dict[cli][0]
        park = cli_dict[cli][1]

        arcpy.AddMessage("  {0} {1} {2}".format(
            cli_dict[cli][1],cli,cli_dict[cli][0]))

        rslt = GetFeatureDictFromTables(cli,cli_table,cr_link_table,cr_catalog)
        f_dict = rslt[1]

        ## calculate percentages and get styles for percentage cells
        cli_total = len(f_dict.keys())-1
        cli_total_done = len([i for i in f_dict.keys() if len(f_dict[i]) == 4\
            and not f_dict[i][2] == "Boundary"])
        cli_total_perc = MakePercentage(cli_total_done,cli_total)
        cli_total_perc_style = ChoosePercStyle(
            cli_total_perc,low_pct_style,mid_pct_style,high_pct_style)

        cli_contrib = len([i for i in f_dict.keys() if f_dict[i][1].lower()\
            == "contributing"])
        cli_contrib_done = len([i for i in f_dict.keys() if len(f_dict[i]) == 4\
            and f_dict[i][1].lower() == "contributing"\
            and not f_dict[i][2] == "Boundary"])
        cli_contrib_perc = MakePercentage(cli_contrib_done,cli_contrib)
        cli_contrib_perc_style = ChoosePercStyle(
            cli_contrib_perc,low_pct_style,mid_pct_style,high_pct_style)

        ## update total counts
        all_total+=cli_total
        all_total_done+=cli_total_done
        all_contrib+=cli_contrib
        all_contrib_done+=cli_contrib_done

        ## get boundary flag
        bnd = False
        for k,v in f_dict.iteritems():
            if "Boundary" in v:
                if len(v) == 4:
                    bnd = True

        ## write all info to row
        writerow = fsheet.row(row_num)

        for colnum in range(0,15):
            if colnum == 0:
                writerow.set_cell_text(colnum,park,basic_style)
            elif colnum == 1:
                writerow.set_cell_text(colnum,cli,basic_style)
            elif colnum == 2:
                writerow.set_cell_text(colnum,name,cli_name_style)
            if colnum == 3:
                if bnd:
                    writerow.set_cell_text(colnum,"YES",boundary_yes_style)
                else:
                    writerow.set_cell_text(colnum,"NO",boundary_no_style)
            elif colnum == 4:
                writerow.set_cell_text(colnum,str(cli_contrib_done),basic_style)
            elif colnum == 5:
                writerow.set_cell_text(colnum,str(cli_contrib),basic_style)
            elif colnum == 6:
                writerow.set_cell_text(colnum,cli_contrib_perc+"%",cli_contrib_perc_style)
            elif colnum == 7:
                writerow.set_cell_text(colnum,str(cli_total_done),basic_style)
            elif colnum == 8:
                writerow.set_cell_text(colnum,str(cli_total),basic_style)
            elif colnum == 9:
                writerow.set_cell_text(colnum,cli_total_perc+"%",cli_total_perc_style)
        row_num += 1

    #final step, print top row
    date = strftime("%m-%d-%y")
    title = "CLI spatial data for {0} in CR Enterprise, {1}".format(
        input_code,date)

    ## make percentages for total
    all_total_perc = MakePercentage(all_total_done,all_total)
    all_contrib_perc = MakePercentage(all_contrib_done,all_contrib)

    cont_sum_msg = "{0} ({1}%) of {2} Contributing Features Drafted".format(
        all_contrib_done,all_contrib_perc,all_contrib)
    total_sum_msg = "{0} ({1}%) of all {2} Features Drafted".format(
        all_total_done,all_total_perc,all_total)
    
    fsheet.write(0,0,title,title_style_big)
    fsheet.write(1,0,cont_sum_msg,summary_style)
    fsheet.write(1,3,total_sum_msg,summary_style)

    fsheet.write(1,7,"0% - 50%",low_pct_style)
    fsheet.write(1,8,"50% - 75%",mid_pct_style)
    fsheet.write(1,9,"75% - 100%",high_pct_style)

    fbook.save(new_xls)
    arcpy.AddMessage("\nspreadsheet created\n")
    return new_xls