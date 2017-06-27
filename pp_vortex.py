#
# Run this script on NERSC Edison with something like:
#    start_pvbatch.sh 4 4 00:10:00 default debug `pwd`/pp_vortex.py
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
    '/global/cscratch1/sd/marchdf/McalisterWing/DES/output68M')
pattern = '*.e.*'
fnames = sorted(glob.glob(os.path.join(fdir, pattern)))

odir = os.path.abspath(
    '/global/cscratch1/sd/marchdf/McalisterWing/DES/vortex_slices68M')
shutil.rmtree(odir)
oname = os.path.join(odir, 'output.csv')

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'ExodusIIReader'
exoreader = ExodusIIReader(FileName=fnames)
exoreader.PointVariables = ['pressure', 'velocity_']
exoreader.SideSetArrayStatus = []
exoreader.ElementBlocks = ['upstream-hex',
                           'tipvortex-hex',
                           'testsection-tetra',
                           'testsection-pyramid',
                           'wingbox-9-hex',
                           'wingbox-9-tetra',
                           'wingbox-9-wedge',
                           'wingbox-9-pyramid']

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# create a new 'Slice'
slice1 = Slice(Input=exoreader)
slice1.SliceType = 'Plane'
slice1.SliceOffsetValues = [0.0, 0.1, 0.2, 0.5, 1.0, 2.0, 4.0, 6.0]

# init the 'Plane' selected for 'SliceType'
slice1.SliceType.Origin = [1.0, 0.0, 0.0]

# create a new 'Clip'
clip1 = Clip(Input=slice1)
clip1.ClipType = 'Plane'
clip1.Scalars = ['POINTS', 'pressure']

# init the 'Plane' selected for 'ClipType'
clip1.ClipType.Origin = [0.0, 1.0, 0.0]
clip1.ClipType.Normal = [0.0, -1.0, 0.0]

# create a new 'Clip'
clip2 = Clip(Input=clip1)
clip2.ClipType = 'Plane'
clip2.Scalars = ['POINTS', 'pressure']

# init the 'Plane' selected for 'ClipType'
clip2.ClipType.Origin = [0.0, -1.0, 0.0]
clip2.ClipType.Normal = [0.0, 1.0, 0.0]

# create a new 'Clip'
clip3 = Clip(Input=clip2)
clip3.ClipType = 'Plane'
clip3.Scalars = ['POINTS', 'pressure']

# init the 'Plane' selected for 'ClipType'
clip3.ClipType.Origin = [0.0, 0.0, 1.0]
clip3.ClipType.Normal = [0.0, 0.0, -1.0]

# create a new 'Clip'
clip4 = Clip(Input=clip3)
clip4.ClipType = 'Plane'
clip4.Scalars = ['POINTS', 'pressure']

# init the 'Plane' selected for 'ClipType'
clip4.ClipType.Origin = [0.0, 0.0, -1.0]
clip4.ClipType.Normal = [0.0, 0.0, 1.0]


# ----------------------------------------------------------------
# save data
# ----------------------------------------------------------------
SaveData(oname,
         proxy=clip4,
         Precision=5,
         UseScientificNotation=0,
         WriteAllTimeSteps=1,
         FieldAssociation='Points')
