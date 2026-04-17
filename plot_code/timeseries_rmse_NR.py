"""
Plot time series of RMSEs for various simulations using the NR for truth

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
valid_times = {'spring': [dt.datetime(2022, 4, 29, 21) + dt.timedelta(hours=i) for i in range(0, 159)][fcst_lead:],
               'winter': [dt.datetime(2022, 2, 1, 9) + dt.timedelta(hours=i) for i in range(0, 159)][fcst_lead:]}

# Valid times to exclude owing to missing data
valid_times['winter'].remove(dt.datetime(2022, 2, 4, 19))
valid_times['winter'].remove(dt.datetime(2022, 2, 4, 20))
valid_times['winter'].remove(dt.datetime(2022, 2, 4, 21))

# Output file (include {season} placeholder for season and {fl} placeholder for forecast lead)
out_fname = '../figs/RMSEtimeseriesNR{season}{fl:02d}.pdf'


#---------------------------------------------------------------------------------------------------
# Main Program
#---------------------------------------------------------------------------------------------------

start = dt.datetime.now()

# Y axis labels
ylabel = {'TMP': 'T % diff',
          'SPFH': 'Q % diff',
          'UGRD_VGRD': 'winds % diff'}

# Read in simulation and plotting information
with open(yml_fname, 'r') as fptr:
    param = yaml.safe_load(fptr)

plot_vars = ['TMP', 'SPFH', 'UGRD_VGRD']

all_colors = {'RRFS': {150: '#004D40', 35: '#FFC107'},
              'HRRR': {150: '#1E88E5', 35: '#D81B60'}}
all_ls = {'RRFS': {150: '-.', 35: '-.'},
          'HRRR': {150: '-', 35: '-'}}

# Create plots
for season in valid_times.keys():
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(6.5, 3.5))
    plt.subplots_adjust(left=0.1, bottom=0.27, right=0.98, top=0.9, wspace=0.45)
    fontsize = 10
    for j, (v, letter) in enumerate(zip(plot_vars, ['a', 'b', 'c'])):

        ax = axes[j]
        if v in ['TMP', 'SPFH']:
            line_type = 'sl1l2'
            stat = 'RMSE'
        else:
            line_type = 'vl1l2'
            stat = 'VECT_RMSE'

        for model in ['RRFS', 'HRRR']:
            for uas in [35, 150]:
                label = f"{model} {uas}-km UAS"
 
                print(f"Plotting {season} {model} {uas}-km UAS {v}")

                # Loop over each valid time
                all_df = []
                for t in valid_times[season]:

                    # Read in MET output file
                    df_ls = []
                    for name in [f"osse_grid_uas{uas}_dir", "osse_grid_dir"]:
                        path = param['sim_verif'][f"{model}_{season}"][name].format(subtyp='lower_atm_below_sfc_mask')
                        t_str = t.strftime('%Y%m%d_%H%M%S')
                        fname = f"{path}/grid_stat_FV3_TMP_vs_NR_TMP_{fcst_lead:02d}0000L_{t_str}V_{line_type}.txt"
                        df = mt.read_ascii([fname])
                        df = mt.subset_verif_df(df, {'FCST_VAR': v, 'not_VX_MASK': 'FULL'})
                        df_ls.append(df)

                    # Compute vertical average
                    all_df.append(mt.compute_stats_vert_avg(df_ls[0], verif_df2=df_ls[1], 
                                                            diff_kw={'var': [stat], 'pct':True}, line_type=line_type, stats_kw={'agg': True}))

                all_df = pd.concat(all_df)

                # Make plot
                plot_vtimes = [dt.datetime.strptime(s, '%Y%m%d_%H%M%S') for s in all_df['FCST_VALID_BEG'].values]
                ax.plot(plot_vtimes, all_df[stat].values, 
                        ls=all_ls[model][uas], c=all_colors[model][uas], label=label)

        # Plot formatting
        ax.grid()
        ax.set_ylim(top=5)
        ax.set_ylabel(ylabel[v], size=fontsize)
        date_format = mdates.DateFormatter('%d\n%b')
        ax.xaxis.set_major_formatter(date_format)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        ax.tick_params(axis='both', which='major', labelsize=fontsize)
        ax.text(0.05, 0.92, f"{letter})", size=fontsize, weight='bold', transform=ax.transAxes,
                backgroundcolor='white')

        #if v == 'SPFH':
        #    formatter = mticker.FuncFormatter(lambda x, pos: f"{x*1e3:.2f}")
        #    ax.yaxis.set_major_formatter(formatter)

        if j == 0:
            ax.legend(fontsize=fontsize, ncols=2, loc=(0.75, -0.41))

    plt.suptitle(f"{season} {fcst_lead}-hr RMSE % diffs", size=(fontsize+4)) 
    plt.savefig(out_fname.format(season=season, fl=fcst_lead))
    plt.close()

print(f"Done! Elapsed time = {(dt.datetime.now() - start).total_seconds()} s")


"""
End timeseries_rmse_NR.py
"""
