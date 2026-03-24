"""
Lower Atmosphere Verification of UAS OSSE Runs

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

import metplus_OSSE_scripts.plotting.metplus_plots as mp


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

# YAML file with simulation and plotting info
yml_fname = 'verif_sim_info.yml'

# Forecast leads
fcst_lead = [0, 6]

# Valid times
valid_times = {'spring': [dt.datetime(2022, 4, 29, 21) + dt.timedelta(hours=i) for i in range(159)],
               'winter': [dt.datetime(2022, 2, 1, 9) + dt.timedelta(hours=i) for i in range(159)]}

# Valid times to exclude owing to missing data
if 6 in fcst_lead:
    valid_times['winter'].remove(dt.datetime(2022, 2, 4, 14))

# Seasons
all_seasons = ['winter', 'spring'] 
#all_seasons = ['winter'] 

# UAS grid spacings
uas_spacing = [150, 35]

# X-axis labels
xlabel_ctrl = {'TMP': 'T (K)',
               'SPFH': 'Q (g kg$^{-1}$)',
               'UGRD_VGRD': 'winds (m s$^{-1}$)'}
xlabel_diff = {'TMP': 'T % diff',
               'SPFH': 'Q % diff',
               'UGRD_VGRD': 'winds % diff'}

# X-axis limits
#xlim = {'TMP': [0.35, 1.7],
#        'SPFH': [0, 1.52e-3],
#        'UGRD_VGRD': [1.6, 6.3]}

# Output file (include {fcst} placeholder)
out_fname = '../figs/UASosseLowerAtmVerifPct{fcst:02d}.pdf'


#---------------------------------------------------------------------------------------------------
# Main Program
#---------------------------------------------------------------------------------------------------

start = dt.datetime.now()

# Read in simulation and plotting information
with open(yml_fname, 'r') as fptr:
    param = yaml.safe_load(fptr)

# Specify verification type
for key in param['sim_verif'].keys():
    for exp in ['osse_grid_dir', 'osse_grid_uas150_dir', 'osse_grid_uas35_dir']:
        param['sim_verif'][key][exp] = param['sim_verif'][key][exp].format(subtyp='lower_atm_below_sfc_mask')

# Extract plotting parameters
plot_dict = param['lower_atm_grid_uas_osse']

# Create plots
for fcst in fcst_lead:
    print(f"\nForecast Lead = {fcst}")
    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(6.5, 7), sharey=True)
    if len(all_seasons) == 2:
        bottom = 0.15
    else:
        bottom = 0.11
    plt.subplots_adjust(left=0.13, bottom=bottom, right=0.99, top=0.98, hspace=0.35, wspace=0.1)
    for i, model in enumerate(['RRFS', 'HRRR']):
        for j, season in enumerate(all_seasons):
            sim_family = param['sim_verif'][f"{model}_{season}"]
            vtimes = valid_times[season]
            for k, n_uas in enumerate(uas_spacing):
                for l, v in enumerate(plot_dict.keys()):

                    print(f"Plotting {season} {model} {v}")

                    # Control plot
                    sim = {f"{model} {season}": {'dir': sim_family[f"osse_grid_dir"],
                                                 'color': sim_family['color'],
                                                 'ls': sim_family['ls'],
                                                 'ctrl':True}}
                    _ = mp.plot_ua_vprof(sim,
                                         vtimes,
                                         fcst_lead=fcst,
                                         plot_stat=plot_dict[v]['plot_stat'],
                                         ax=axes[0, l],
                                         verbose=False,
                                         diffs=False,
                                         include_ctrl=False,
                                         include_zero=False,
                                         **plot_dict[v]['kwargs'])

                    # Percent diff plot
                    diff_sims = {f"ctrl": {'dir': sim_family['osse_grid_dir'],
                                           'ctrl':True},
                                 f"{model} {season}": {'dir': sim_family[f"osse_grid_uas{n_uas}_dir"],
                                                       'color': sim_family['color'],
                                                       'ls': sim_family['ls'],
                                                       'ctrl':False}}
                    _ = mp.plot_ua_vprof(diff_sims,
                                         vtimes,
                                         fcst_lead=fcst,
                                         plot_stat=plot_dict[v]['plot_stat'],
                                         ax=axes[k+1, l],
                                         verbose=False,
                                         diffs=True,
                                         include_ctrl=False,
                                         include_zero=False,
                                         **plot_dict[v]['kwargs'])

    # Formatting
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    fontsize = 11
    for i in range(3):
        for j, v in enumerate(plot_dict.keys()):
            ax = axes[i, j]
            ax.set_title('')
            ax.grid()

            # Subplot labels
            ax.text(0.05, 0.88, f'{letters[3*i+j]})', size=fontsize, weight='bold', transform=ax.transAxes,
                    backgroundcolor='white')

            # Legend
            if (i == 2) and (j == 1):
                if len(all_seasons) == 2:
                    ax.legend(ncols=2, fontsize=fontsize, loc=(-0.3, -0.6))
                else:
                    ax.legend(ncols=2, fontsize=fontsize, loc=(-0.4, -0.45))
            else:
                ax.get_legend().remove()

            # Axes labels and limits
            if i == 0:
                ax.set_xlabel(xlabel_ctrl[v], size=fontsize)
                #ax.set_xlim(xlim[v])
            else:
                ax.set_xlabel(xlabel_diff[v], size=fontsize)
                #ax.set_xlim(xlim[v])

            if (i == 0) and (j == 0):
                ax.set_ylabel(f"Ctrl\npressure (hPa)", size=fontsize)
            elif (i == 1) and (j == 0):
                ax.set_ylabel(f"{uas_spacing[0]}-km UAS\npressure (hPa)", size=fontsize)
            elif (i == 2) and (j == 0):
                ax.set_ylabel(f"{uas_spacing[1]}-km UAS\npressure (hPa)", size=fontsize)
            else:
                ax.set_ylabel('')

            # Ticks
            ax.set_ylim([1000, 530])
            ax.set_yticks(ticks=[1000, 900, 800, 700, 600],
                          labels=['1000', '900', '800', '700', '600'],
                          minor=False)
            ax.tick_params(which='both', labelsize=9)

            # Specific humidity ticks
            if (i == 0) and (j == 1):
                formatter = mticker.FuncFormatter(lambda x, pos: f"{x*1e3:.2f}")
                ax.xaxis.set_major_formatter(formatter)

    plt.savefig(out_fname.format(fcst=fcst))
    plt.close()

print(f"Done! Elapsed time = {(dt.datetime.now() - start).total_seconds()} s")


"""
End uas_osse_verif_lower_atm.py
"""
