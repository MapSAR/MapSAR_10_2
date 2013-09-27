
# Takes an original database and makes a copy reprojecting the database and
# MXD files to the desired spatial reference
#
# Description: Input database and map templates
# Copies and converts them to the desired spatial reference
# Jon Pedder - MapSAR
# version - 9/19/13
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
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, sys, os, distutils, time
from arcpy import env
from os.path import join, abspath
from os import walk
from distutils.core import setup

# Get parameters from user input
# 0. Input folder to walk to look for all mxd files - folder
# 3. Spatial reference selection

sourceStructure = arcpy.GetParameterAsText(0)
targetStructure = arcpy.GetParameterAsText(1)
sr = arcpy.GetParameterAsText(2)

targetDatabase = '{0}\\SAR_Default.gdb'.format(targetStructure)

arcpy.AddMessage('Source Structure is {0}'.format(sourceStructure))
arcpy.AddMessage('Target Structure is {0}'.format(targetStructure))
arcpy.AddMessage('Target Database is {0}'.format(targetDatabase))

# Set Vars and overwrite option to true
arcpy.env.overwriteOutput = True

distutils.dir_util.copy_tree(sourceStructure,targetStructure)
time.sleep(2)

def localizeDatabase():

    arcpy.env.workspace = targetDatabase
    dsList = arcpy.ListDatasets()
    fcList = arcpy.ListFeatureClasses()
    projectList = dsList + fcList

    # Project the datasets and featureclasses and write to target db
    for p in projectList:
        arcpy.AddMessage('Defining Spatial Reference for {0}'.format(p))
        arcpy.DefineProjection_management(p,sr)

def localizeMXD():

    # Walk through the folder structure, look at each mxd, set it's new spatial reference
    # and adjust the source data path to match the new database.
    arcpy.AddMessage('Seting spatial reference on mxd files')
    for root, dirs, files in walk(targetStructure):
         for file in files:
                abspath = (join(root, file))
                if abspath.find(".mxd")>0:
                    arcpy.AddMessage('Setting Spatial Reference on file {0}'.format(abspath))
                    mxd = arcpy.mapping.MapDocument(abspath)
                    for df in arcpy.mapping.ListDataFrames(mxd):
                        df.spatialReference = sr
                        lyr = arcpy.mapping.ListLayers(mxd,'Assignments',df)[0]
                        df.panToExtent(lyr.getSelectedExtent())
                        df.scale = 50000

                    mxd.save()
                    del mxd

def main():
    localizeDatabase()
    localizeMXD()

if __name__ == '__main__':

    main()
