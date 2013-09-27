#-------------------------------------------------------------------------------
# Name:        MapSARfunctions
# Purpose:
#
# Author:      Jon Pedder
#
# Created:     3/17/13
# Copyright:   (c) SMSR 2013
# Use:          Often used and useful functions available to be called
# Licence:
#     MapSAR wilderness search and rescue GIS data model and related python scripting
#     Copyright (C) 2012  - Jon Pedder & SMSR
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

# import arcpy
# import os, sys, pythonaddins
# from arcpy import env

def layersOn(mxd, selectedParams):
    """ Requires an mxd as arg 1 and a list of values for arg 2 (to match the dict keys)
    returns no values, just turns on/off selected layers """
    import arcpy
    # layers = arcpy.mapping.ListDataFrames(mxd,'')[0]

    pls = '1 Incident_Group','PLS_Subject_Information'
    found = '1 Incident_Group','Subject_Found'
    assets = '2 Incident_Assets'
    assignments = '3 Assignments_Group','Assignments'
    teamstatus = '5 Resource_Team_Status'
    clues = '6 Clues_Group','Clues_All'
    tracks = '7 GPS_Tracks_And_Routes','Routes'
    Search_Segments = '8 Segments_Group','Search_Segments'
    Search_Segments_Outline = '8 Segments_Group','Search_Segments_Outline'
    Search_Segments_POA = '8 Segments_Group','Search_Segments_POA'
    boundary = '13 Incident_Analysis','Search_Boundary'

    layerDict = {'PLS':pls,'Found':found,'Assets':assets,'Assignments':assignments,'Team_Status':teamstatus,'Clues':clues,'Tracks':tracks,'Segments_Filled':Search_Segments,'Segments_Outline':Search_Segments_Outline,'Segments_POA':Search_Segments_POA,'Boundary':boundary}

    for frame in arcpy.mapping.ListDataFrames(mxd):

    # Strip out base data to avoid issues with layer compatability
        for l in arcpy.mapping.ListLayers(mxd,'',frame):
             if 'Base_Data_Group' in l.name:
                arcpy.mapping.RemoveLayer(frame,l)
             else:
                 # Then set all layers to NOT visible (False)
                l.visible = False

        for sp in selectedParams: # loop through the selection list
            if layerDict.has_key(sp):
                for lyr in arcpy.mapping.ListLayers(mxd,'',frame):
                    currLyr = layerDict[sp]
                    if 'Assignments_DDP' in lyr.name:
                        lyr.visible = False
                    elif 'Assignments_DDP' not in lyr.name:
                        if lyr.name in currLyr:
                            lyr.visible = True

    return

def initializeDcenterOn():
    """ Creates a dictionary of feature class names, field names """
    import arcpy

    # Tuple format - Feature class, display text, Layername, (Optional fields - field 1, field 2)

    # Tuples with one fields - len is 4
    allAssignments = ('Assignments','All Assignments','Assignments','Assignments.Assignment_Number')
    # allAssignments = ('Assignments','All Assignments','hidden_assignments','Assignment_Number')
    allSegments = ('Search_Segments','All Segments','Search_Segments','Area_Name')
    pls = ('PLS','Select Subject Name From List','PLS_Subject_Information','Name')
    segment = ('Search_Segments','Select Segment Name From List','Search_Segments','Area_Name')
    assignment = ('Assignments','Select Assignment Number From List','Assignments','Assignments.Assignment_Number')
    # assignment = ('Assignments','Select Assignment Number From List','hidden_assignments','Assignment_Number')
    # Tuples with two fields - len is 5
    asset = ('Assets','Select Asset From List','2 Incident_Assets','Asset_Number','Description')
    clue = ('Clues_Point','Select Clue from List','Clues_All','Clue_Number','Verbal_Description')

    # Dictionary key:tuple
    DcenterOn={}
    DcenterOn = {'PLS':pls,'Single Asset':asset,'Single Clue':clue,'Single Assignment': assignment, 'Single Segment':segment,'All Assignments':allAssignments,'All Segments':allSegments}
    return(DcenterOn)

def getPrintRange(strValues):
    """ Parser which returns a list of single digit values for input of string separated by commas or dashes """
    import arcpy

    getdash = []
    printrange = []
    splitValues = strValues.split(',')
    # Split string to list with comma delimiter
    for i in splitValues[:]:
        # If a dash, then expand the range
        if '-' in i:
            getdash = (i.split('-'))
            printrange.extend(range(int(getdash[0]),int(getdash[1])+1,1))
        # If no dash, just add the value as an int()
        else:
            printrange.append(int(i))

    # Remove duplicate values in the list
    if printrange:
        printrange.sort()
        last = printrange[-1]
        for d in range(len(printrange)-2,-1,-1):
            if last == printrange[d]:
                del printrange[d]
            else:
                last = printrange[d]
    # Return a list of unique values
    return(printrange)

def populateAnalysisData(mxd):
    """ Saves current Incident_Analysis file to disk, loads lyr file from disk to target mxd"""
    import arcpy
    from arcpy import env

    import os
    arcpy.env.overwriteOutput = True

    # Gather information to copy over base_data

    # Define vars
    mxdlayer = "13 Incident_Analysis"
    LayerFile = "Incident_Analysis"
    LayerName = LayerFile + '.lyr'

    # Save base_data layer file to disk in c:\MapSAR\TempDir from current mxd.
    # If directory does not exist create it
    # TempDir = r'c:\mapsar\Tools\Layer_Templates'
    # baselayer = '{0}\{1}'.format(TempDir,LayerName)

    TempDir = '{0}Base_Data\Layers'.format(env.workspace.rstrip('SAR_Default.gdb'))

    baselayer = '{0}\{1}'.format(TempDir,LayerName)

    arcpy.AddMessage('Analysis layer is {0}'.format(baselayer))

    if os.path.exists(TempDir):
          arcpy.SaveToLayerFile_management(mxdlayer,baselayer,"RELATIVE")
    else:
          os.makedirs(TempDir)
          arcpy.SaveToLayerFile_management(mxdlayer,baselayer,"RELATIVE")

    # Check for existing Incident_Analysis layers in target. If present remove them
    for df in arcpy.mapping.ListDataFrames(mxd):
         for lyr in arcpy.mapping.ListLayers(mxd, "", df):
             if 'Incident_Analysis' in lyr.name:
                  arcpy.mapping.RemoveLayer(df,lyr)

    # Check if the layer exists on disk

    if os.path.isfile(baselayer):
          addLayer = arcpy.mapping.Layer(baselayer)
          arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")
          mxd.save()
    else:
          # If not alert user of an error
          arcpy.AddMessage(baselayer +' does not exist')

def populateBaseData(mxd):
    """ Params are source mxd, Feature Layer name, file layer name
    Saves current base lyr file to disk, loads lyr file from disk to target mxd"""
    import arcpy
    from arcpy import env

    import os
    arcpy.env.overwriteOutput = True

    # Gather information to copy over base_data

    # Define vars
    mxdlayer = "14 Base_Data_Group"
    LayerFile = "Base_Layer"
    LayerName = LayerFile + '.lyr'

    # Save base_data layer file to disk in c:\MapSAR\TempDir from current mxd.
    # If directory does not exist create it
    #TempDir = r'c:\mapsar\Tools\Layer_Templates'
    #baselayer = '{0}\{1}'.format(TempDir,LayerName)

    TempDir = '{0}Base_Data\Layers'.format(env.workspace.rstrip('SAR_Default.gdb'))

    baselayer = '{0}\{1}'.format(TempDir,LayerName)

    arcpy.AddMessage('Base data copied to {0}'.format(TempDir, ))

    if os.path.exists(TempDir):
          arcpy.SaveToLayerFile_management(mxdlayer,baselayer,"RELATIVE")
    else:
          os.makedirs(TempDir)
          arcpy.SaveToLayerFile_management(mxdlayer,baselayer,"RELATIVE")

    # Check for existing Base_Data layers in target. If present remove them
    for df in arcpy.mapping.ListDataFrames(mxd):
         for lyr in arcpy.mapping.ListLayers(mxd, "", df):
             if 'Base_Data' in lyr.name:
                  arcpy.mapping.RemoveLayer(df,lyr)

    # Check if the layer exists on disk

    if os.path.isfile(baselayer):
        arcpy.AddMessage('Base Data Layer Loaded')
        frames = arcpy.mapping.ListDataFrames(mxd)
        for frame in frames:
            addLayer = arcpy.mapping.Layer(baselayer)
            arcpy.mapping.AddLayer(frame, addLayer, "BOTTOM")
        mxd.save()
    else:
          # If not alert user of an error
          arcpy.AddMessage(baselayer +' does not exist')

def toggleAssignment():

    import arcpy
    import pythonaddins

    table = "DynamicValue"
    field = "Comments"

    rows = arcpy.UpdateCursor(table)
    iField = arcpy.AddFieldDelimiters(table, field)
    # Comments field in dynamicvalues = AutoAssign
    iQuery = "{0} = '{1}'".format(iField, "AutoAssign")

    rows = arcpy.UpdateCursor("DynamicValue",iQuery)

    for row in rows:
        if row.ON_CREATE == 0:
            row.ON_CREATE = 1
            pythonaddins.MessageBox("Assignment Auto Text - Feature turned ON, Auto text will populate the assignment description","Assignment Auto Text on",0)
        elif row.ON_CREATE == 1:
            row.ON_CREATE = 0
            pythonaddins.MessageBox("Assignment Auto Text - Feature turned OFF","Assignment Auto Text off",0)
        rows.updateRow(row)

    del row
    del rows

def togglePeriods():
    import arcpy
    import pythonaddins

    table = "DynamicValue"
    field = "Comments"

    rows = arcpy.UpdateCursor(table)
    iField = arcpy.AddFieldDelimiters(table, field)
    # Comments field in dynamicvalues = AutoDate
    iQuery = "{0} = '{1}'".format(iField, "AutoDate")

    rows = arcpy.UpdateCursor("DynamicValue",iQuery)
    for row in rows:
        if row.ON_CREATE == 0:
            row.ON_CREATE = 1
            row.ON_CHANGE = 1
            pythonaddins.MessageBox("Operation Periods - Feature turned ON, End Dates will automatically increment by 12 hours. Start Dates will auto populate","Periods Auto Calc on",0)
        elif row.ON_CREATE == 1:
            row.ON_CREATE = 0
            row.ON_CHANGE = 0
            pythonaddins.MessageBox("Operation Periods - Feature turned OFF","Periods Auto Calc off",0)
        rows.updateRow(row)

    del row
    del rows

def getDomainErr(failed):
    """ Process string of error from update domains when a value exists """
    import arcpy

    try:
        errlst = failed[failed.find('[')+1:failed.find(']')].split(',')
        errFieldStart = errlst[0].find(':')+1
        errFieldEnd = len(errlst[0])
        errField = errlst[0][errFieldStart:errFieldEnd]
        errValStart = errlst[1].find(':')+1
        errValEnd = len(errlst[1])
        errVal = errlst[1][errValStart:errValEnd]
        return(errField.strip(), errVal.strip())
    except:
        return('Unknown',failed)

def clearNulls(myList):
    """ Pass in list parameter, clears out NULL values in list items """
    import arcpy
        # Determine item type
    for i in range(len(myList)):
        myType = type(myList[i])
        if myType is str or myType is unicode:
            if 'NULL' in myList[i]:
                myList[i] = ''

        elif myType is int or myType is float or myType is long:
            if not myList[i] > 0:
                myList[i] = None
    return(myList)

def updateAAvalues():
    """ Manually updates values created with Attribute Assistant """
    import arcpy

    # Team Members
    fc = 'Team_Members'
    fields = ['Total_Weight', 'Body_Weight','Gear_Weight']
    arcpy.AddMessage('Updating {0} values'.format(fc))
    with arcpy.da.UpdateCursor(fc,fields ) as rows:
        for row in rows:
            if row[2] != None and row[2] != None:
                row[0] = row[1] + row[2]
            rows.updateRow(row)

    # Teams
    fc = 'Teams'
    fields = ['Status', 'Team_Available','Team_Name']
    arcpy.AddMessage('Updating {0} values'.format(fc))
    with arcpy.da.UpdateCursor(fc,fields ) as rows:
        for row in rows:
            if row[0] != 'Unavailable':
                row[1] = row[2]
            else:
                row[1] = '<NULL>'
            rows.updateRow(row)


    # Periods
    fc = 'Operation_Period'
    fields = ['PeriodText', 'Period']
    arcpy.AddMessage('Updating {0} values'.format(fc))
    with arcpy.da.UpdateCursor(fc,fields ) as rows:
        for row in rows:
            row[0] = row[1]
            rows.updateRow(row)

    # Clues
    fc = 'Clues_Point'
    fields = ['Clue_Number', 'Clue_NumText']
    arcpy.AddMessage('Updating {0} values'.format(fc))
    with arcpy.da.UpdateCursor(fc,fields ) as rows:
        for row in rows:
            if row[0] > 0:
                row[1] = str(row[0])
            else:
                row[1] = '<NULL>'
            rows.updateRow(row)

    # Assignments
    fc = 'hidden_assignments'
    arcpy.AddMessage('Updating {0} values'.format(fc))
    rows = arcpy.UpdateCursor(fc)
    for row in rows:

        row.AssignNumText = str(row.Assignment_Number)
        row.Mileage = (row.SHAPE_Length * 0.00062137119) / 2
        rows.updateRow(row)


def updateValueLists(launched):
    """ UpdateValueLists populates all db domains with data. pass launched = 'script' or 'tool' to change error message delivery """
    import arcpy
    import pythonaddins

    # Set enviroment
    from arcpy import env
    workspace = arcpy.env.workspace

    try:
        # Define FC's
        Search_Segments = workspace+"\\Search_Segments"
        Teams = workspace+"\\Teams"
        Operation_Period = workspace+"\\Incident\\Operation_Period"
        Incident = workspace+"\\Incident\\Incident"
        PLS = workspace+"\\Incident\\PLS"
        Clues_Point = workspace+"\\Resources_Clues_Routes\\Clues_Point"
        Assignments = workspace+"\\Assignments"

        errorString = ''
        # Process: Table To Domain
        fc = 'Search_Segments'
        arcpy.TableToDomain_management(Search_Segments, "Area_Name", "Area_Name", workspace, "Areas", "Areas", "REPLACE")
        fc = 'Teams'
        arcpy.TableToDomain_management(Teams, "Team_Name", "Team_Name", workspace, "Teams", "Teams", "REPLACE")
        fc = 'Operation_Period'
        arcpy.TableToDomain_management(Operation_Period, "Period", "PeriodText", workspace, "Period", "PeriodText", "REPLACE")
        fc = 'PLS'
        arcpy.TableToDomain_management(PLS, "Victim_Number", "Name", workspace, "Victim_Number", "Victim_Number", "REPLACE")
        fc = 'Incident'
        arcpy.TableToDomain_management(Incident, "Incident_Name", "Incident_Name", workspace, "Incident_Name", "Incident_Name", "REPLACE")
        fc = 'Clues_Point'
        arcpy.TableToDomain_management(Clues_Point, "Clue_Number", "Clue_NumText", workspace, "Clue_Number", "Clue_NumText", "REPLACE")
        fc = 'Assignments'
        arcpy.TableToDomain_management(Assignments, "Assignment_Number", "AssignNumText", workspace, "Assignment_Number", "AssignNumText", "REPLACE")

        if launched == 'script': arcpy.AddMessage('Values Have Been Updated')

    except:
        errors = arcpy.GetMessages(2)
        # Does not have exclusive access to the database
        if 'ERROR 000464' in errors:
            arcpy.AddError('UPDATE ERROR: There is an active editing session, editing MUST be stopped to update values')
        # Duplicate values exist
        elif 'ERROR 999999' in errors:
            a, b = getDomainErr(errors)
            if a == 'unknown':
                errorString = b
            else:
                errorString = "\nThe process failed because the field '{0}' in {1} already has a value of '{2}', all values must be unique! \n\nCorrect the entry and run again.\n".format(a,fc,b)
            if launched == 'script':
                arcpy.AddMessage(errorString)
            if launched == 'tool':
                pythonaddins.MessageBox(errorString,'ERROR in {0}'.format(fc),0)


