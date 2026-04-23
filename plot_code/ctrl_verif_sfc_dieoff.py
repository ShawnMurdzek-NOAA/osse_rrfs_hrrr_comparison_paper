"""
Surface Verification of Real-Data and OSSE Control Runs

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
fcst_lead = [0, 1, 2, 3, 6, 12]

# Valid times
valid_times_spring = [dt.datetime(2022, 4, 29, 21) + dt.timedelta(hours=i) for i in range(159)]
valid_times_winter = [dt.datetime(2022, 2, 1, 9) + dt.timedelta(hours=i) for i in range(159)]

# Valid times to exclude owing to missing data
valid_times_winter.remove(dt.datetime(2022, 2, 4, 14))

# Y-axis labels
ylabel_real = {'TMP': 'T (K)',
               'SPFH': 'Q (g kg$^{-1}$)',
               'UGRD_VGRD': 'winds (m s$^{-1}$)'}
ylabel_diff = {'TMP': 'T % diff',
               'SPFH': 'Q % diff',
               'UGRD_VGRD': 'winds % diff'}

# Y-axis limits
ylim_real = {'TMP': [1.3, 2.7],
             'SPFH': [0.2e-3, 1.35e-3],
             'UGRD_VGRD': [1.95, 3.2]}
ylim_pct = [-40, 10]

# Output file
out_fname = '../figs/CtrlSfcPtVerif.pdf'


#---------------------------------------------------------------------------------------------------
# Main Program
#---------------------------------------------------------------------------------------------------

start = dt.datetime.now()

# Read in simulation and plotting information
with open(yml_fname, 'r') as fptr:
    param = yaml.safe_load(fptr)

# Specify verification type (sfc)
for key in param['sim_verif'].keys():
    for sim in ['real_pt_dir', 'osse_pt_dir']:
        param['sim_verif'][key][sim] = param['sim_verif'][key][sim].format(subtyp='sfc')

# Extract plotting parameters
plot_dict = param['sfc_pt']

# Create plots
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(6.5, 4), sharex=True)
plt.subplots_adjust(left=0.11, bottom=0.23, right=0.99, top=0.99, hspace=0.12, wspace=0.42)
for i, model in enumerate(['RRFS', 'HRRR']):
    for j, (season, valid_times) in enumerate(zip(['winter', 'spring'], 
                                                  [valid_times_winter, valid_times_spring])):
        sim_family = param['sim_verif'][f"{model}_{season}"]
        for k, v in enumerate(plot_dict.keys()):

            print(f"Plotting {season} {model} {v}")

            # Real-data runs
            real_sim = {f"{season} {model}": {'dir': sim_family['real_pt_dir'],
                                              'color': sim_family['color'],
                                              'ls': sim_family['ls']}}
            _ = mp.plot_sfc_dieoff(real_sim,
                                   valid_times,
                                   fcst_lead=fcst_lead,
                                   plot_stat=plot_dict[v]['plot_stat'],
                                   ax=axes[0, k],
                                   verbose=False,
                                   **plot_dict[v]['kwargs'])

            # OSSE runs
            diff_sims = {f"{season} {model} real": {'dir': sim_family['real_pt_dir'],
                                                    'color': 'k',
                                                    'ctrl':True},
                         f"{season} {model}": {'dir': sim_family['osse_pt_dir'],
                                               'color': sim_family['color'],
                                               'ls': sim_family['ls'],
                                               'ctrl':False}}
            _ = mp.plot_sfc_dieoff(diff_sims,
                                   valid_times,
                                   fcst_lead=fcst_lead,
                                   plot_stat=plot_dict[v]['plot_stat'],
                                   ax=axes[1, k],
                                   verbose=False,
                                   diffs=True,
                                   include_ctrl=False,
                                   include_zero=True,
                                   **plot_dict[v]['kwargs'])

# Formatting
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
fontsize = 9
for i, desc in enumerate(['real', 'OSSE $-$ real']):
    for j, v in enumerate(plot_dict.keys()):
        ax = axes[i, j]
        ax.set_title('')
        ax.grid()

        # Subplot labels
        ax.text(0.85, 0.07, f'{letters[3*i+j]})', size=fontsize, weight='bold', transform=ax.transAxes,
                backgroundcolor='white')

        # Legend
        if (i == 1) and (j == 1):
            ax.legend(ncols=2, fontsize=fontsize, loc=(-0.38, -0.58))
        else:
            ax.get_legend().remove()

        # Axes labels and limits
        if i == 0:
            ax.set_xlabel('')
            if j == 0:
                ax.set_ylabel(f"{desc}\n{ylabel_real[v]}", size=fontsize)
            else:
                ax.set_ylabel(ylabel_real[v], size=fontsize)
            ax.set_ylim(ylim_real[v])
        elif i == 1:
            ax.set_xlabel('lead time (hr)', size=fontsize)
            if j == 0:
                ax.set_ylabel(f"{desc}\n{ylabel_diff[v]}", size=fontsize)
            else:
                ax.set_ylabel(ylabel_diff[v], size=fontsize)
            ax.set_ylim(ylim_pct)

        # Ticks
        ax.tick_params(which='both', labelsize=fontsize)

        # Specific humidity ticks
        if (i == 0) and (j == 1):
            formatter = mticker.FuncFormatter(lambda x, pos: f"{x*1e3:.2f}")
            ax.yaxis.set_major_formatter(formatter)

plt.savefig(out_fname)
plt.close()

print(f"Done! Elapsed time = {(dt.datetime.now() - start).total_seconds()} s")


"""
End ctrl_verif_sfc_dieoff.py
"""
