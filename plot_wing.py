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
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import pandas as pd
import scipy.interpolate as spi
import yaml

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


def parse_ic(fname):
    """Parse the Nalu yaml input file for the initial conditions"""
    with open(fname, 'r') as stream:
        try:
            dat = yaml.load(stream)
            u0 = float(dat['realms'][0]['initial_conditions']
                       [0]['value']['velocity'][0])
            rho0 = float(dat['realms'][0]['material_properties']
                         ['specifications'][0]['value'])
            mu = float(dat['realms'][0]['material_properties']
                       ['specifications'][1]['value'])

            return u0, rho0, mu

        except yaml.YAMLError as exc:
            print(exc)


def sort_by_angle(x, y, var):
    """Radial sort of variable on x and y for plotting

    Inspired from:
    http://stackoverflow.com/questions/35606712/numpy-way-to-sort-out-a-messy-array-for-plotting

    """

    # Get the angle wrt the mean of the cloud of points
    x0, y0 = x.mean(), y.mean()
    angle = np.arctan2(y - y0, x - x0)

    # Sort based on this angle
    idx = angle.argsort()

    return x[idx], y[idx], var[idx]


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == '__main__':

    # ========================================================================
    # Parse arguments
    parser = argparse.ArgumentParser(description='A simple plot tool')
    parser.add_argument(
        '-s', '--show', help='Show the plots', action='store_true')
    args = parser.parse_args()

    # ========================================================================
    # Setup
    fdir = os.path.abspath('DES')
    sdir = os.path.join(fdir, 'wing_slices68M')
    pattern = 'output*.1.csv'
    yname = os.path.join(fdir, 'mcalisterWing68M.i')

    ninterp = 100
    mm2ft = 0.003281

    # ========================================================================
    # Read in data

    # simulation setup parameters
    u0, rho0, mu = parse_ic(yname)
    chord = 1

    # wing data
    fnames = sorted(glob.glob(os.path.join(sdir, pattern)))
    df = get_merged_csv(fnames)
    renames = {'Points:0': 'x',
               'Points:1': 'y',
               'Points:2': 'z',
               'pressure': 'p',
               'pressure_force_:0': 'fpx',
               'pressure_force_:1': 'fpy',
               'pressure_force_:2': 'fpz',
               'tau_wall': 'tau_wall',
               'velocity_:0': 'ux',
               'velocity_:1': 'uy',
               'velocity_:2': 'uz'}
    df.columns = [renames[col] for col in df.columns]
    df.loc[df['y'] < 1e-16, 'y'] = 0

    # Calculate the negative of the surface pressure coefficient
    df['cp'] = - df['p'] / (0.5 * rho0 * u0**2)

    # ========================================================================
    # Plot cp in each slice
    yslices = np.unique(df['y'])

    for k, yslice in enumerate(yslices):
        subdf = df[df['y'] == yslice]

        # Sort for a pretty plot
        x, z, cp = sort_by_angle(np.array(subdf['x']),
                                 np.array(subdf['z']),
                                 np.array(subdf['cp']))

        # plot
        plt.figure(0)
        ax = plt.gca()
        polygons = []
        polygons.append(Polygon(np.vstack((x, cp)).transpose()))
        p = PatchCollection(polygons,
                            edgecolors=cmap[k % len(cmap)],
                            linewidths=2,
                            facecolors='none')
        ax.add_collection(p)

    # ========================================================================
    # Save plots
    plt.figure(0)
    ax = plt.gca()
    plt.xlabel(r"$x/c$", fontsize=22, fontweight='bold')
    plt.ylabel(r"$-c_p$", fontsize=22, fontweight='bold')
    plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight='bold')
    plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight='bold')
    plt.xlim([0, chord])
    plt.ylim([-1.5, 2.5])
    plt.tight_layout()
    plt.savefig('cp.png', format='png')

    if args.show:
        plt.show()