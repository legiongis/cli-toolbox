# How to Create a New Feature Table for the CR Enterprise
*National Center for Preservation Technology and Training | 9-18-2014*

Background: The CLI Feature Table is the master table that is served through the NPS CR Enterprise spatial database. It is crucial for a number of operations that can be performed concerning the enterprise spatial data and the Cultural Landscape Inventory database. For example, by having this table available, the user can figure out what features are still missing from the spatial database for a given cultural landscape. Also, with this table the _Update Fields_ in _Selected Records_ tool can be used to auto-populate a number of CLI related fields. This guide will explain how to create a new version of this table from the online CLI database, and how to prepare that table for inclusion in the enterprise database. This process should be carried out every few months to ensure that an up-to-date version of the table is available to anyone accessing the NPS CR Enterprise database.

Alternatively: If you have just added a new landscape to the CLI and you would like to create spatial data for it, you can follow this procedure to update your local feature tables to include the brand new features. If this is your goal, there is no need to pass the table on to a data editor for inclusion in the Enterprise.


1. **Log on to the CLI online database**
    1. You need at least read-access to the database. http://www.hscl.cli.nps.gov
1. **Query the database and download results**
    1. Go to the “Standard Queries” tab, and locate these two queries (author: Debbie Smith)
        1. *CLI Lookup Table -- Features*
        1. *CLI Lookup Table -- Units*
    1. For both of these queries, run them and download the results
        1. The feature query should return over 50,000 records, the unit query should return approximately 750 (of course, these numbers will grow over time)
        1. To download the results, click on the query name above the records and choose Download
        1. Choose MS Excel as the download format, and be sure to download all records. The feature query results may take a while to download.

1. **Clean up Feature Results in MS Excel**
    1. Open the downloaded results from the *CLI Lookup Table – Features* query in MS Excel. Because of its size, it may take a minute to open. You may get a warning, but click “Yes” or “OK”.
    1. Remove empty rows:
        1. Select the `CLI_ID` column (click on the “B”).
        1. In the Home tab, click on the Sort & Filter button, and choose Smallest to Largest.
        1. Choose “Yes” when prompted to expand selection.
        1. Go to the bottom of the spreadsheet, and you may see rows that only have fragments of entries in them. If this is the case, select the very bottom row, hold shift, and scroll up until you see the first full row and can select everything up to it. Delete all of these empty rows.
    1. Remove duplicates based on `CLI_ID` column. Because there are many instances where multiple rows occur for the same `CLI_ID`, these must be removed.
        1. In the Data tab, select Remove Duplicates.
        1. Choose “Yes” when prompted to expand selection.
        1. Select all columns only the `CLI_ID` column, and remove duplicates
        1. You should now have a clean spreadsheet with over 33,000 rows.

1. **Clean up Unit Results in MS Excel**
    1. Open the downloaded spreadsheet from the CLI Lookup Table – Units query
    1. Sort the entire table based on the H column, `UNIT_CLASS` (Expand Selection when prompted)
    1. All unit types should be either District or Site, however, you may find rows where the `UNIT_CLASS` is blank or “Multiple Property”. If this is the case, consult with the CLI Coordinator for the region that holds the CLI Unit, ask for clarification, update the `UNIT_CLASS` in the spreadsheet, and encourage that the correct value be entered in the CLI.
    1. Continue to step 5 only after all units have a `UNIT_TYPE` that is either “Site” or “District” (case-sensitive).

1. **Add the Unit results to the Features results**
    1. Select and copy all of the data from the Unit spreadsheet. Be sure not to copy the header row.
    1. Paste it into the feature spreadsheet underneath the last feature row. The columns should all line up correctly.
    1. Close the Unit spreadsheet.

1. **Finalize and save spreadsheet**
    1. In the features spreadsheet, delete column A.
    1. Change the name of column I from “IDLCS Number” to “LCS_ID”
    1. Save the workbook with the name “CLI_Feature_Table_mm_dd_yy” where mm_dd_yy should represent today’s date. Save the file as an Excel 97-2003 Workbook (*.xls). It is important to save it in this format.

1. **Use the "Prepare CLI Table for Data Editor" tool in the CR Enterprise Access toolset**
    1. In ArcMap or ArcCatalog look in the CLI Toolbox, in the CR Enterprise Access > Feature Table Update toolset, and use the Prepare CLI Table for Data Editor tool. Refer to the help that is embedded in the tool dialog for more information.
    1. When running this tool, you have the option of updating your own local feature tables. This will accomplish the alternative task described at the top of this document.

*The result of this procedure will be a new file geodatabase containing a table whose rows should be used by a Data Editor to replace the existing CLI Feature Table rows in the CR Enterprise database. If the user is only hoping to update his or her local feature tables, this resulting file geodatabase can be discarded after "Prepare CLI Table for Data Editor" tool has been run with the “Update Local Feature Tables?” box checked.*
