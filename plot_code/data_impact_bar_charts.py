"""
Plot Todling (2013) data impact metric using bar charts

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
import pickle
from pathlib import Path
import argparse
import datetime as dt
import copy
import os


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# pickle_detail files from data-impact
rrfs_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/todling_obs_impact'
hrrr_dir = '/work2/noaa/wrfruc/murdzek/HRRR_OSSE/todling_obs_impact'
in_pickles = {'spring': {'RRFS real': f"{rrfs_dir}/real_red_data_rrfs-workflow_orion/spring/data-impact/pickle_detail",
                         'RRFS OSSE': f"{rrfs_dir}/syn_data_rrfs-workflow_orion/spring/data-impact/pickle_detail",
                         'HRRR real': f"{hrrr_dir}/real_red_data_WRF_FCST_OSSE_hercules/spring/data-impact/pickle_detail",
                         'HRRR OSSE': f"{hrrr_dir}/syn_data_WRF_FCST_OSSE_hercules/spring/data-impact/pickle_detail"},
              'winter': {'RRFS real': f"{rrfs_dir}/real_red_data_rrfs-workflow_orion/winter/data-impact/pickle_detail",
                         'RRFS OSSE': f"{rrfs_dir}/syn_data_rrfs-workflow_orion/winter/data-impact/pickle_detail",
                         'HRRR real': f"{hrrr_dir}/real_red_data_WRF_FCST_OSSE_hercules/winter/data-impact/pickle_detail",
                         'HRRR OSSE': f"{hrrr_dir}/syn_data_WRF_FCST_OSSE_hercules/winter/data-impact/pickle_detail"}}

# Datetimes to loop over
dt_list = {'spring': [dt.datetime(2022, 4, 29, 12) + dt.timedelta(hours=i) for i in range(169)],
           'winter': [dt.datetime(2022, 2, 1, 0) + dt.timedelta(hours=i) for i in range(169)]}

# Observation subsets
ob_subsets = {'raob':[120, 122, 132, 220, 221, 222],
              'aircft':[130, 131, 133, 134, 135, 230, 231, 232, 233, 234, 235],
              'sfc':[180, 181, 182, 183, 187, 188, 192, 193, 194, 195, 280, 281, 282, 284, 287, 
                     288, 292, 293, 294, 295],
              'gps':[153]}

# Variables included
ob_vars = ['ps', 't', 'q', 'uv', 'pw']

# Option to enable warnings
enable_warn = False

# Output files (include {cyc} placeholder for "Spinup" or "Prod")
out_fname = '../figs/DataImpact{cyc}.pdf'


#---------------------------------------------------------------------------------------------------
# Main Program
#---------------------------------------------------------------------------------------------------

start = dt.datetime.now()

def read_pickle(file_path):
    """Read a pickle file and return unpacked data."""
    with open(file_path, "rb") as f:
        return pickle.load(f)


for cyc in ['Production', 'Spinup']:
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(6.5, 3.5), sharex=True, sharey=True)
    plt.subplots_adjust(left=0.08, bottom=0.22, right=0.98, top=0.88, wspace=0.05)
    fontsize = 10
    for i, (season, letter) in enumerate(zip(['spring', 'winter'], ['a', 'b'])):
        ax = axes[i]
        for j, (sim, c) in enumerate(zip(in_pickles[season].keys(), ['#004D40', '#FFC107', '#1E88E5', '#D81B60'])): 
        
            print(f"Plotting {cyc} {season} {sim}")

            sum_jo_diffs = np.zeros(len(ob_subsets))

            # Main loop over each datetime
            for t in dt_list[season]:
                t_str = t.strftime('%Y%m%d%H')

                # Loop over each variable
                for v in ob_vars:
                    if cyc == 'Spinup':
                        pkl_file = f"{in_pickles[season][sim]}/{t_str}_conv_{v}_spinup_detail.pkl"
                    else:
                        pkl_file = f"{in_pickles[season][sim]}/{t_str}_conv_{v}_detail.pkl"

                    try:
                        pkl_out = read_pickle(pkl_file)
                    except FileNotFoundError:
                        if enable_warn: print(f"  pickle file for {t_str} and {v} is missing")
                        continue

                    obs = np.unique(pkl_out['observation_type'])
                    if len(obs) == 0:
                        if enable_warn: print(f"  pickle file for {v} at {t_str} is empty. Skipping.")
                        continue

                    # Extract data from pickle file
                    for l, subset in enumerate(ob_subsets.keys()):
                        for typ in ob_subsets[subset]:
                            idx = np.where(pkl_out['observation_type'] == typ)[0]
                            sum_jo_diffs[l] = sum_jo_diffs[l] + np.sum(pkl_out['jo_diff'][idx])

            # Make plot
            width = 0.225
            offset = width * j
            ax.barh(np.arange(len(ob_subsets)) + offset, sum_jo_diffs, width, color=c, label=sim)

        # Plot formatting
        ax.set_title(season, size=fontsize)
        ax.grid(axis='x')
        ax.set_xlabel('total impact (unitless)', size=fontsize)
        ax.text(0.03, 0.92, f'{letter})', size=(fontsize-1), weight='bold', transform=ax.transAxes,
                backgroundcolor='white')
        if i == 0:
            ax.legend(fontsize=fontsize, ncols=4, loc=(0.07, -0.3))
            ax.set_yticks(np.arange(len(ob_subsets)) + (1.5*width), list(ob_subsets.keys()), size=fontsize)

    plt.suptitle(f"{cyc} Cycles", size=(fontsize+2))

    # Save plot
    plt.savefig(out_fname.format(cyc=cyc))
    plt.close()

print(f"\nProgram complete! (elapsed time = {(dt.datetime.now() - start).total_seconds()} s)")


"""
End data_impact_bar_charts.py
"""
