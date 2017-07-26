#!/usr/bin/env python3
#
# This makes a dataframe containing a temporal average of navg last vortex slices
#
# Run this in the data directory, e.g. from /scratch/mhenryde/McalisterWing/DES/vortex_slices64M:
#    > /path/to/script/avg_vortex_slices.py
#

# ========================================================================
#
# Imports
#
# ========================================================================
import sys
import os
import re
import glob
import numpy as np
import pandas as pd


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
        except pd.io.common.EmptyDataError:
            pass
    return pd.concat(lst, ignore_index=True)


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == '__main__':

    # ========================================================================
    # Setup
    fdir = os.getcwd()
    oname = os.path.join(fdir, 'avg_slice.csv')
    prefix = 'output'
    suffix = '.csv'

    # average over these time steps
    navg = 20

    # Get time steps, keep only last navg steps
    pattern = prefix + '*' + suffix
    fnames = sorted(glob.glob(os.path.join(fdir, pattern)))
    times = []
    for fname in fnames:
        times.append(int(re.findall(r'\d+', fname)[-1]))
    times = np.unique(sorted(times))[-navg:]

    # Loop over each time step and get the dataframe
    lst = []
    for time in times:
        pattern = prefix + '*.' + str(time) + suffix
        fnames = sorted(glob.glob(os.path.join(fdir, pattern)))
        df = get_merged_csv(fnames)
        lst.append(df)
        df['time'] = time
    df = pd.concat(lst, ignore_index=True)

    # Average
    avgdf = df.groupby(['Points:0', 'Points:1', 'Points:2'],
                       as_index=False).mean()

    # Output to file
    avgdf.to_csv(oname, index=False)
