#-------------------------------------------------------------------------------
# Name:        Viewshed Analysis
# Purpose:     Create viewshed from a point location
#
# Author:      Jon Pedder
#
# Created:     10/02/2013
# Copyright:   (c) SMSR 2013
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

# Import system modules
import arcpy, datetime, os
import time
from arcpy import env
from arcpy.sa import *

# Set enviroment, frames and layers
arcpy.env.workspace
arcpy.env.scratchGDB

scratchdb = arcpy.env.scratchGDB
defaultDB = arcpy.env.workspace
arcpy.env.overwriteOutput = True

# Assure Scratch DB has been written to disk
time.sleep(2)


def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT')
        frame = arcpy.mapping.ListDataFrames(mxd,'MapSAR')[0]

        return(mxd,frame)

    except SystemExit as err:
            pass

def checkSR(inRaster):
    """ Check to see if the raster is GCS or PCS, if GCS it's converted """
    try:
        mxd, frame = getDataframe()

        # Check to see if DEM is projected or geographic
        sr = arcpy.Describe(inRaster).spatialreference
        if sr.PCSName == '':
        # if geographic throw an error and convert to projected to match the dataframe
            inSR = frame.spatialReference
            inPCSName = frame.spatialReference.PCSName
            arcpy.AddWarning('This elevation file (DEM) is NOT projected. Converting DEM to {0}\n'.format(inPCSName))
            inRaster = arcpy.ProjectRaster_management(inRaster, "{0}\DEM_{1}".format(scratchdb,inPCSName),inSR, "BILINEAR", "#","#", "#", "#")

        return(inRaster)

    except SystemExit as err:
            pass

def clipDEM(inRaster,clippedRasterName):
    arcpy.AddMessage('Clipping DEM {0} to the display extent\n'.format(inRaster))
    from arcpy import env
    arcpy.env.extent = 'DISPLAY'

    # Clip the DEM raster to the size of the Buffered_Area
    clipped_raster = arcpy.Clip_management(inRaster,'#',clippedRasterName,'','0', 'ClippingGeometry')

    return(clipped_raster)

def main():

    # Set date and time vars
    timestamp = ''
    now = datetime.datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)

    inFeature = arcpy.GetParameterAsText(0)
    inRaster = arcpy.GetParameterAsText(1)
    inSymbology = arcpy.GetParameterAsText(2)

    # Create a clipped DEM file for faster processing
    clippedRasterName = "{0}\Clipped_Raster_{1}".format(scratchdb,timestamp)
    viewRasterName = "{0}\View_Raster_{1}".format(scratchdb,timestamp)

    # Add Slope Raster to dataframe
    mxd, frame = getDataframe()

    # Clip Raster to display extent
    clippedRaster = clipDEM(inRaster,clippedRasterName)

    clippedRaster = checkSR(clippedRaster)

    # Set local variables
    zFactor = 1
    useEarthCurvature = "FLAT_EARTH"
    refractivityCoefficient = 0.15


    # Execute Viewshed
    arcpy.AddMessage('Analysing Viewshed for {0}\n'.format(inFeature))
    outViewshed = Viewshed(inRaster, inFeature, zFactor,useEarthCurvature, refractivityCoefficient)

    # Save the output
    outViewshed.save(viewRasterName)

    # Define the name of the output Layer
    if inFeature > "":
        if '\\' in inFeature:
            layerLen = len(inFeature.split('\\'))
            layerName = inFeature.split('\\')[layerLen -1]

        elif '\\' not in inFeature:
            layerName = inFeature
    elif inFeature == '':
        if '\\' in inRaster:
            layerLen = len(inRaster.split('\\'))
            layerName = inRaster.split('\\')[layerLen -1]

        elif '\\' not in inRaster:
            layerName = inRaster

    arcpy.AddMessage('Adding layer {0} to Incident Analysis\n'.format(layerName))
    viewLayer = arcpy.MakeRasterLayer_management(viewRasterName, "Slopes for {0}".format(layerName))
    refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Incident_Analysis*',frame)[0]
    arcpy.mapping.AddLayerToGroup(frame,refGroupLayer,viewLayer.getOutput(0),'BOTTOM')

    if inSymbology > '':
        arcpy.AddMessage('adding symbology from {0}\n'.format(inSymbology))
        df = arcpy.mapping.ListDataFrames(mxd,'MapSAR')[0]
        updateLayer = arcpy.mapping.ListLayers(mxd, viewLayer, df)[0]
        sourceLayer = arcpy.mapping.Layer(inSymbology)
        arcpy.mapping.UpdateLayer(df, updateLayer, sourceLayer, True)


if __name__ == '__main__':
    main()
