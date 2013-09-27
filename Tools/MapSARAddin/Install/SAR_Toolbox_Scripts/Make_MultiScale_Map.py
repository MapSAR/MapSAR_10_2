
# Name:        Make_Map.py
# Purpose:     Make a single Map suitable for briefing, plans etc.
#              Not for creating DDP maps, see assignments script.
#
# Author:      Jon Pedder
#
# Created:     03/17/2013
# Copyright:   (c) SMSR 2013
# Use:          Run using Toolbox
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

# Import modules
import arcpy, os
import MapSARfunctions as mapsar
import SetMapElements as mapElms

# Set enviroment
from arcpy import env

arcpy.env.overwriteOutput = True

# Gather input parameters from user
# 0. TargetFile mxd - string
# 1. Folder to store pdf product - string
# 2. Name of saved map - string
# 3. Title of the Map - string
# 4. Map Scale MAIN - from value list- string
# 5. Map Scale INSET - from value list- string
# 6. Center map on - from value list - string
# 7. Values - from value list - string
# 8. PDF Quality - from value list - string
# 9. PDF Print speed - from value lilst - string
# 10. Use base data in current map - boolean
# 11. Layers to make visible

TargetFile = arcpy.GetParameterAsText(0)
PDFlocation = arcpy.GetParameterAsText(1)
aMapName = arcpy.GetParameterAsText(2)
aMapTitle = arcpy.GetParameterAsText(3)
aMapScaleMain = arcpy.GetParameterAsText(4)
aMapScaleInset = arcpy.GetParameterAsText(5)
aKeyvalue = arcpy.GetParameterAsText(6)
aSelectedvalue = arcpy.GetParameterAsText(7)
aDPI = arcpy.GetParameterAsText(8)
aQuality = arcpy.GetParameterAsText(9)
aBase_Data = arcpy.GetParameterAsText(10)
aLayers = arcpy.GetParameterAsText(11)


# BASE DATA COPY STARTS HERE#
 ############################
Targetmxd = arcpy.mapping.MapDocument(TargetFile)

if('multiscale' in Targetmxd.tags):
    # Set visable layers first, then populate base data
    selectedParams = aLayers.split(';')
    arcpy.AddMessage(selectedParams)
    mapsar.layersOn(Targetmxd,selectedParams)

    if 'Analysis' in selectedParams:
        mapsar.populateAnalysisData(Targetmxd)

    # Use parameters from user input
    MapTitle = aMapTitle
    MapName = aMapName
    MapLocation = PDFlocation + "/" + aMapName + ".pdf"

    # Populate the current base data to target mxd and frames
    if aBase_Data == "true":
       mapsar.populateBaseData(Targetmxd)

    # Add text elements to the map
    for elm in arcpy.mapping.ListLayoutElements(Targetmxd, "TEXT_ELEMENT","MapTitle"):
    	elm.text = "<BOL> " + MapTitle + "</BOL>"

    for elm in arcpy.mapping.ListLayoutElements(Targetmxd, "TEXT_ELEMENT","MapName"):
    	elm.text = MapName

    # Set Team Logo, Declination and Scale Bar
    mapElms.setMapElements(Targetmxd)

    # Load dictionary of fetaure and field names
    # DcenterOn = mapsar.initializeDcenterOn()
    DcenterOn = mapsar.initializeDcenterOn()

    # Build SQL query to get selection to center map around
    # Keys = PLS,Single Asset,Single Clue,Single Assignment,Single Segment,All Assignments,All Segments
    intList = ['Single Asset','Single Clue','Single Assignment','All Assignments']
    strList = ['Single Segment','PLS','All Segments']

    # Determine Featureclass and field name
    # Tuple format - Feature class, display text, Layername, (Optional fields - field 1, field 2)
    fc = DcenterOn[aKeyvalue][0]
    MapFC = DcenterOn[aKeyvalue][2]
    MapField = DcenterOn[aKeyvalue][3]

    arcpy.AddMessage("Generating Map {0}".format(MapName))

    # arcpy.Addfieldelimiters here. Code revised for 10.2 compatability
    # qField = arcpy.AddFieldDelimiters(MapFC, MapField)
    if MapFC != 'Assignments':
        qField = arcpy.AddFieldDelimiters(MapFC, MapField)
    else:
        qField = MapField


    # Check if the selection is all features or single feature
    # If it's all features
    if aKeyvalue.startswith('All'):
        # Check if the selection is an number or string
        if aKeyvalue in intList:
            iQuery = ('{0} > 0').format(qField)
        elif aKeyvalue in strList:
            iQuery = ("{0} > ''").format(qField)
    # If it's a single feature
    elif not aKeyvalue.startswith('All'):
        # Check if the selection is an number or...
        if aKeyvalue in intList:
            # Pull search value from selection
             if '-' in aSelectedvalue:
                queryVal = aSelectedvalue.split('-')
                iQuery = ('{0} = {1}').format(qField,int(queryVal[0]))
             elif '-' not in aSelectedvalue:
                iQuery = ('{0} = {1}').format(qField,int(aSelectedvalue))
        # Check if the selection is an number or string
        elif aKeyvalue in strList:
            # Pull search value from selection
            if '-' in aSelectedvalue:
                queryVal = aSelectedvalue.split('-')
                iQuery = ("{0} = '{1}'").format(qField,queryVal[0])
            elif '-' not in aSelectedvalue:
                iQuery = ("{0} = '{1}'").format(qField,aSelectedvalue)

    # Zoom to the selected features
    # Use the SelectLayerByAttribute tool to select the center and zoom to the selection

    # center and set scales
    frames = arcpy.mapping.ListDataFrames(Targetmxd)
    # Set map scale
    for df in frames:
        lyr = arcpy.mapping.ListLayers(Targetmxd,MapFC,df)[0]
        arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION",iQuery)

        result = int(arcpy.GetCount_management(fc).getOutput(0))
        if result == 0:
            arcpy.AddError('No Features Found, invalid query')
        elif result == 1:

            df.panToExtent(lyr.getSelectedExtent())

            if 'Main' in df.name:
                df.scale = aMapScaleMain
            elif 'Inset' in df.name:
                df.scale = aMapScaleInset

        # clear selection so highlights don't print
        arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")

    # Export the map to a .pdf
    Targetmxd.save()
    arcpy.mapping.ExportToPDF(Targetmxd,MapLocation, resolution = aDPI, image_quality = aQuality,georef_info = "false")

    # Clear vars
    del Targetmxd, lyr, MapFC, MapField
else:
    arcpy.AddError('\nPlease select a map from the Multi_Scale_Maps templates\n')
