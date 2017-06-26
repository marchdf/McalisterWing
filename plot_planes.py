#!/usr/bin/env python3

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import sys
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.interpolate as spi

# ========================================================================
#
# Some defaults variables
#
# ========================================================================
plt.rc('text', usetex=True)
plt.rc('font', family='serif', serif='Times')
cmap_med = ['#F15A60', '#7AC36A', '#5A9BD4', '#FAA75B',
            '#9E67AB', '#CE7058', '#D77FB4', '#737373']
cmap = ['#EE2E2F', '#008C48', '#185AA9', '#F47D23',
        '#662C91', '#A21D21', '#B43894', '#010202']
dashseq = [(None, None), [10, 5], [10, 4, 3, 4], [
    3, 3], [10, 4, 3, 4, 3, 4], [3, 3], [3, 3]]
markertype = ['s', 'd', 'o', 'p', 'h']


# ========================================================================
#
# Function definitions
#
# ========================================================================
def get_merged_csv(fnames, **kwargs):
    lst = []
    for fname in fnames:
        try:
            df = pd.read_csv(fname, **kwargs)
            lst.append(df)
        except pd.errors.EmptyDataError:
            pass
    return pd.concat(lst, ignore_index=True)


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == '__main__':

    # ========================================================================
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='A simple plot tool')
    parser.add_argument(
        '-s', '--show', help='Show the plots', action='store_true')
    args = parser.parse_args()

    # ========================================================================
    # Setup
    ninterp = 100

    # ========================================================================
    # Read in data
    fdir = os.path.abspath('HybridWALE')
    pattern = '*99.csv'
    fnames = sorted(glob.glob(os.path.join(fdir, pattern)))
    df = get_merged_csv(fnames)
    renames = {'Points:0': 'x',
               'Points:1': 'y',
               'Points:2': 'z',
               'pressure': 'p',
               'velocity_:0': 'ux',
               'velocity_:1': 'uy',
               'velocity_:2': 'uz'}
    df.columns = [renames[col] for col in df.columns]

    # ========================================================================
    # Lineout through vortex core in each slice
    xslices = np.unique(df['x'])
    for k, xslice in enumerate(xslices):
        subdf = df[df['x'] == xslice]
        idx = subdf['p'].idxmin()
        ymin, ymax = np.min(subdf['y']), np.max(subdf['y'])
        zmin, zmax = np.min(subdf['z']), np.max(subdf['z'])

        # vortex center location
        yc = np.array([subdf['y'].loc[idx]])
        zc = np.array([subdf['z'].loc[idx]])

        # interpolate across the vortex core
        yline = np.linspace(ymin, ymax, ninterp)
        zline = np.linspace(zmin, zmax, ninterp)
        ux_zc = spi.griddata((subdf['y'], subdf['z']), subdf['ux'],
                             (yline[None, :], zc[:, None]), method='cubic')
        uz_zc = spi.griddata((subdf['y'], subdf['z']), subdf['uz'],
                             (yline[None, :], zc[:, None]), method='cubic')

        plt.figure(k)
        plt.plot(yline, ux_zc[0, :])

        plt.figure(k + 10)
        plt.plot(yline, uz_zc[0, :])

    # ========================================================================
    # Operate on each slice
    xslices = np.unique(df['x'])
    for k, xslice in enumerate(xslices):
        subdf = df[df['x'] == xslice]
        ymin, ymax = np.min(subdf['y']), np.max(subdf['y'])
        zmin, zmax = np.min(subdf['z']), np.max(subdf['z'])
        yi = np.linspace(ymin, ymax, ninterp)
        zi = np.linspace(zmin, zmax, ninterp)

        pi = spi.griddata((subdf['y'], subdf['z']), subdf['p'],
                          (yi[None, :], zi[:, None]), method='cubic')

        plt.figure(k + 100)
        CS = plt.contourf(yi, zi, pi, 15, cmap=plt.cm.jet)
        plt.colorbar()
        plt.xlim(ymin, ymax)
        plt.ylim(zmin, zmax)

    if args.show:
        plt.show()
