"""
Plot time series of RMSEs for various simulations using raobs for truth

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

# YAML file with simulation and plotting info
yml_fname = 'verif_sim_info.yml'

# Forecast lead
fcst_lead = 1

# Valid times
valid_times = {'spring': [dt.datetime(2022, 4, 30, 0) + dt.timedelta(hours=i) for i in range(0, 145, 12)],
               'winter': [dt.datetime(2022, 2, 1, 12) + dt.timedelta(hours=i) for i in range(0, 145, 12)]}

# Valid times to exclude owing to missing data

# Output file (include {season} placeholder for season and {fl} placeholder for forecast lead)
out_fname = '../figs/RMSEtimeseriesRAOB{season}{fl:02d}.pdf'


#---------------------------------------------------------------------------------------------------
# Main Program
#---------------------------------------------------------------------------------------------------

start = dt.datetime.now()

# Y axis labels
ylabel = {'TMP': 'T (K)',
          'SPFH': 'Q (g kg$^{-1}$)',
          'UGRD_VGRD': 'winds (m s$^{-1}$)'}

# Read in simulation and plotting information
with open(yml_fname, 'r') as fptr:
    param = yaml.safe_load(fptr)

# Specify observation type (upper_air)
all_sims = param['RRFS_app_orion']
for s in all_sims.keys():
    for season in ['spring', 'winter']:
        all_sims[s][f"{season}_dir"] = all_sims[s][f"{season}_dir"].format(subtyp='upper_air')

plot_vars = ['TMP', 'SPFH', 'UGRD_VGRD']

# Create plots
for season in valid_times.keys():
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(6.5, 3))
    plt.subplots_adjust(left=0.08, bottom=0.28, right=0.98, top=0.92, wspace=0.42)
    fontsize = 9
    for j, (v, letter) in enumerate(zip(plot_vars, ['a', 'b', 'c'])):

        ax = axes[j]
        if v in ['TMP', 'SPFH']:
            line_type = 'sl1l2'
            stat = 'RMSE'
        else:
            line_type = 'vl1l2'
            stat = 'VECT_RMSE'

        for sim in all_sims.keys():

            print(f"Plotting {season} {sim} {v}")

            # Loop over each valid time
            all_df = []
            for t in valid_times[season]:

                # Read in MET output file
                path = all_sims[sim][f"{season}_dir"]
                t_str = t.strftime('%Y%m%d_%H%M%S')
                fname = f"{path}/point_stat_{fcst_lead:02d}0000L_{t_str}V_{line_type}.txt"
                df = mt.read_ascii([fname])
                df = mt.subset_verif_df(df, {'FCST_VAR': v})

                # Compute vertical average
                all_df.append(mt.compute_stats_vert_avg(df, line_type=line_type, stats_kw={'agg': True}))

            all_df = pd.concat(all_df)

            # Make plot
            plot_vtimes = [dt.datetime.strptime(s, '%Y%m%d_%H%M%S') for s in all_df['FCST_VALID_BEG'].values]
            ax.plot(plot_vtimes, all_df[stat].values, ls=all_sims[sim]['ls'], c=all_sims[sim]['color'], label=sim)

        # Plot formatting
        ax.grid()
        ax.set_ylabel(ylabel[v], size=fontsize)
        date_format = mdates.DateFormatter('%d\n%b')
        ax.xaxis.set_major_formatter(date_format)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        ax.tick_params(axis='both', which='major', labelsize=fontsize)
        ax.text(0.05, 0.9, f"{letter})", size=fontsize, weight='bold', transform=ax.transAxes,
                backgroundcolor='white')

        if v == 'SPFH':
            formatter = mticker.FuncFormatter(lambda x, pos: f"{x*1e3:.2f}")
            ax.yaxis.set_major_formatter(formatter)

        if j == 0:
            ax.legend(fontsize=fontsize, ncols=2, loc=(0.85, -0.42))

    plt.suptitle(f"{season} {fcst_lead}-hr RMSEs", size=(fontsize+2)) 
    plt.savefig(out_fname.format(season=season, fl=fcst_lead))
    plt.close()

print(f"Done! Elapsed time = {(dt.datetime.now() - start).total_seconds()} s")


"""
End timeseries_rmse_raob.py
"""
