#
# Run this script on NERSC Edison with something like:
#    start_pvbatch.sh 4 4 00:10:00 default debug `pwd`/pp_wing.py
#


# ----------------------------------------------------------------
# imports
# ----------------------------------------------------------------
# import the simple module from the paraview
from paraview.simple import *
# disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

import os
import glob
import shutil

# ----------------------------------------------------------------
# setup
# ----------------------------------------------------------------

# Get file names
fdir = os.path.abspath(
    '/scratch/mhenryde/McalisterWing/DES/outputRC64M')
pattern = '*.e.*'
fnames = sorted(glob.glob(os.path.join(fdir, pattern)))

odir = os.path.abspath(
    '/scratch/mhenryde/McalisterWing/DES/wing_slicesRC64M')
shutil.rmtree(odir, ignore_errors=True)
os.makedirs(odir)
oname = os.path.join(odir, 'output.csv')

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'ExodusIIReader'
exoreader = ExodusIIReader(FileName=fnames)
exoreader.PointVariables = ['pressure',
                            'pressure_force_',
                            'tau_wall',
                            'velocity_']
exoreader.NodeSetArrayStatus = []
exoreader.SideSetArrayStatus = ['wing']
exoreader.ElementBlocks = []

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# wing properties
wing_length = 3.3

# create a new 'Slice'
# at span location corresponding to McAlister paper Fig 6.
# [0.994, 0.984, 0.974, 0.974, 0.959, 0.944, 0.899, 0.843, 0.773, 0.692, 0.597, 0.491, 0.370, 0.238, 0.094]
slice1 = Slice(Input=exoreader)
slice1.SliceType = 'Plane'
slice1.SliceOffsetValues = [0.0, 0.0198, 0.0528, 0.0858, 0.0858, 0.1353,
                            0.1848, 0.3333, 0.5181, 0.7491, 1.0164, 1.3299,
                            1.6797, 2.079, 2.5146, 2.9898]

# init the 'Plane' selected for 'SliceType'
slice1.SliceType.Origin = [0.0, 0.0, 0.0]
slice1.SliceType.Normal = [0.0, 1.0, 0.0]

# ----------------------------------------------------------------
# save data
# ----------------------------------------------------------------
SaveData(oname,
         proxy=slice1,
         Precision=5,
         UseScientificNotation=0,
         WriteAllTimeSteps=1,
         FieldAssociation='Points')
