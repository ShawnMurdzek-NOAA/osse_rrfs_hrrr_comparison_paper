"""
Plot time series of RMSDs between GFS and NR

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import yaml
import copy
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import pandas as pd

import metplus_OSSE_scripts.plotting.metplus_tools as mt


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# Verification information
all_sims = {'spring' : {'dir': '/work2/noaa/wrfruc/murdzek/nature_run_spring/compare_to_GFS/ua_GFS_nearest/output/GridStat',
                        'color': 'r',
                        'ctrl': True},
            'winter' : {'dir': '/work2/noaa/wrfruc/murdzek/nature_run_winter/compare_to_GFS/ua_GFS_nearest/output/GridStat',
                        'color': 'r',
                        'ctrl': True}}

# Forecast lead
fcst_lead = 3

# Valid times
valid_times = {'spring': [dt.datetime(2022, 4, 29, 15) + dt.timedelta(hours=i) for i in range(0, 168, 12)],
               'winter': [dt.datetime(2022, 2, 1, 3) + dt.timedelta(hours=i) for i in range(0, 168, 12)]}

# Output file (include {season} placeholder for season and {fl} placeholder for forecast lead)
out_fname = '../figs/RMSDtimeseriesGFS{season}.pdf'


#---------------------------------------------------------------------------------------------------
# Main Program
#---------------------------------------------------------------------------------------------------

start = dt.datetime.now()

# Y axis labels
ylabel = {'TMP': 'T (K)',
          'RH': 'RH (%)',
          'UGRD_VGRD': 'winds (m s$^{-1}$)'}

plot_vars = ['TMP', 'RH', 'UGRD_VGRD']

# Create plots
for season in valid_times.keys():
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(6.5, 2.5))
    plt.subplots_adjust(left=0.08, bottom=0.17, right=0.99, top=0.9, wspace=0.32)
    fontsize = 9
    for j, (v, letter) in enumerate(zip(plot_vars, ['a', 'b', 'c'])):

        ax = axes[j]
        if v in ['TMP', 'RH']:
            line_type = 'sl1l2'
            stat = 'RMSE'
        else:
            line_type = 'vl1l2'
            stat = 'VECT_RMSE'

        print(f"Plotting {season} {v}")

        # Loop over each valid time
        all_df = []
        for t in valid_times[season]:

            # Read in MET output file
            path = all_sims[season]['dir']
            t_str = t.strftime('%Y%m%d_%H%M%S')
            fname = f"{path}/grid_stat_GFS_vs_NR_{fcst_lead:02d}0000L_{t_str}V_{line_type}.txt"
            df = mt.read_ascii([fname])
            df = mt.subset_verif_df(df, {'FCST_VAR': v})

            # Compute vertical average
            all_df.append(mt.compute_stats_vert_avg(df, line_type=line_type, stats_kw={'agg': True}))

        all_df = pd.concat(all_df)

        # Make plot
        plot_vtimes = [dt.datetime.strptime(s, '%Y%m%d_%H%M%S') for s in all_df['FCST_VALID_BEG'].values]
        ax.plot(plot_vtimes, all_df[stat].values, ls='-', c=all_sims[season]['color'])

        # Plot formatting
        ax.grid()
        ax.set_ylabel(ylabel[v], size=fontsize)
        date_format = mdates.DateFormatter('%d\n%b')
        ax.xaxis.set_major_formatter(date_format)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        ax.tick_params(axis='both', which='major', labelsize=fontsize)
        ax.text(0.05, 0.9, f"{letter})", size=fontsize, weight='bold', transform=ax.transAxes,
                backgroundcolor='white')

    plt.suptitle(f"{season} {fcst_lead}-hr GFS vs. NR RMSDs", size=(fontsize+2)) 
    plt.savefig(out_fname.format(season=season, fl=fcst_lead))
    plt.close()

print(f"Done! Elapsed time = {(dt.datetime.now() - start).total_seconds()} s")


"""
End timeseries_rmse_GFS.py
"""
