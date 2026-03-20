"""
Upper-Air Verification of OSSE Control Runs

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
valid_times_spring = [dt.datetime(2022, 4, 29, 21) + dt.timedelta(hours=i) for i in range(159)]
valid_times_winter = [dt.datetime(2022, 2, 1, 9) + dt.timedelta(hours=i) for i in range(159)]

# Valid times to exclude owing to missing data
if 6 in fcst_lead:
    valid_times_winter.remove(dt.datetime(2022, 2, 4, 14))

# Option to plot pct diff relative to RRFS
pct_diff = False

# X-axis labels
if pct_diff:
    xlabel = {'TMP': 'T % diff',
              'SPFH': 'Q % diff',
              'UGRD_VGRD': 'winds % diff'}
else:
    xlabel = {'TMP': 'T (K)',
              'SPFH': 'Q (g kg$^{-1}$)',
              'UGRD_VGRD': 'winds (m s$^{-1}$)'}

# X-axis limits
#xlim = {'TMP': [0.35, 1.7],
#        'SPFH': [0, 1.52e-3],
#        'UGRD_VGRD': [1.6, 6.3]}

# Output file
if pct_diff:
    out_fname = '../figs/CtrlUAosseVerifPct.pdf'
else:
    out_fname = '../figs/CtrlUAosseVerif.pdf'


#---------------------------------------------------------------------------------------------------
# Main Program
#---------------------------------------------------------------------------------------------------

start = dt.datetime.now()

# Read in simulation and plotting information
with open(yml_fname, 'r') as fptr:
    param = yaml.safe_load(fptr)

# Specify verification type (sfc)
for key in param['sim_verif'].keys():
    param['sim_verif'][key]['osse_grid_dir'] = param['sim_verif'][key]['osse_grid_dir'].format(subtyp='upper_air_below_sfc_mask')

# Extract plotting parameters
plot_dict = param['ua_grid_osse']

# Create plots
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(6.5, 4.5), sharey=True, sharex='col')
if pct_diff:
    plt.subplots_adjust(left=0.13, bottom=0.18, right=0.99, top=0.98, hspace=0.1, wspace=0.1)
else:
    plt.subplots_adjust(left=0.13, bottom=0.22, right=0.99, top=0.98, hspace=0.1, wspace=0.1)
for i, model in enumerate(['RRFS', 'HRRR']):
    for j, (season, valid_times) in enumerate(zip(['winter', 'spring'], 
                                                  [valid_times_winter, valid_times_spring])):
        sim_family = param['sim_verif'][f"{model}_{season}"]
        for k, v in enumerate(plot_dict.keys()):

            print(f"Plotting {season} {model} {v}")

            for l, fcst in enumerate(fcst_lead):

                if pct_diff:
                    if model == 'RRFS': continue
                    diff_sims = {f"{season} RRFS": {'dir': param['sim_verif'][f"RRFS_{season}"]['osse_grid_dir'],
                                                    'ctrl':True},
                                 f"{season}": {'dir': sim_family['osse_grid_dir'],
                                               'color': sim_family['color'],
                                               'ls': sim_family['ls'],
                                               'ctrl':False}}
                    _ = mp.plot_ua_vprof(diff_sims,
                                         valid_times,
                                         fcst_lead=fcst,
                                         plot_stat=plot_dict[v]['plot_stat'],
                                         ax=axes[l, k],
                                         verbose=False,
                                         diffs=True,
                                         include_ctrl=False,
                                         include_zero=True,
                                         **plot_dict[v]['kwargs'])


                else:
                    sim = {f"{season} {model}": {'dir': sim_family['osse_grid_dir'],
                                                 'color': sim_family['color'],
                                                 'ls': sim_family['ls']}}
                    _ = mp.plot_ua_vprof(sim,
                                         valid_times,
                                         fcst_lead=fcst,
                                         plot_stat=plot_dict[v]['plot_stat'],
                                         ax=axes[l, k],
                                         verbose=False,
                                         **plot_dict[v]['kwargs'])

# Formatting
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
fontsize = 11
for i, fcst in enumerate(fcst_lead):
    for j, v in enumerate(plot_dict.keys()):
        ax = axes[i, j]
        ax.set_title('')
        ax.grid()

        # Subplot labels
        ax.text(0.05, 0.88, f'{letters[3*i+j]})', size=fontsize, weight='bold', transform=ax.transAxes,
                backgroundcolor='white')

        # Legend
        if (i == 1) and (j == 1):
            if pct_diff:
                ax.legend(ncols=2, fontsize=fontsize, loc=(-0.1, -0.45))
            else:
                ax.legend(ncols=2, fontsize=fontsize, loc=(-0.4, -0.6))
        else:
            ax.get_legend().remove()

        # Axes labels and limits
        if i == 1:
            ax.set_xlabel(xlabel[v], size=fontsize)
            #ax.set_xlim(xlim[v])
        else:
            ax.set_xlabel('')
        if j == 0:
            ax.set_ylabel(f"{fcst}-hr\npressure (hPa)", size=fontsize)
        else:
            ax.set_ylabel('')

        # Ticks
        ax.set_ylim([1050, 80])
        ax.set_yticks(ticks=[1000, 700, 500, 300, 200, 100],
                      labels=['1000', '700', '500', '300', '200', '100'],
                      minor=False)
        ax.tick_params(which='both', labelsize=9)

        # Specific humidity ticks
        if (i == 0) and (j == 1) and not pct_diff:
            formatter = mticker.FuncFormatter(lambda x, pos: f"{x*1e3:.2f}")
            ax.xaxis.set_major_formatter(formatter)

plt.savefig(out_fname)
plt.close()

print(f"Done! Elapsed time = {(dt.datetime.now() - start).total_seconds()} s")


"""
End ctrl_verif_ua_osse_grid_vprof.py
"""
