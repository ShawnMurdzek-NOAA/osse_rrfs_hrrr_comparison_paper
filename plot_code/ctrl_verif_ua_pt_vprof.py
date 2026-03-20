"""
Upper-Air Verification of Real-Data and OSSE Control Runs

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
valid_times_winter.remove(dt.datetime(2022, 2, 4, 14))

# X-axis labels
xlabel_real = {'TMP': 'T (K)',
               'SPFH': 'Q (g kg$^{-1}$)',
               'UGRD_VGRD': 'winds (m s$^{-1}$)'}
xlabel_diff = {'TMP': 'T % diff',
               'SPFH': 'Q % diff',
               'UGRD_VGRD': 'winds % diff'}

# X-axis limits
xlim_real = {0: {'TMP': [0.35, 1.7],
                 'SPFH': [0, 1.52e-3],
                 'UGRD_VGRD': [1.6, 6.3]},
             6: {'TMP': [0.5, 1.8],
                 'SPFH': [0, 1.7e-3],
                 'UGRD_VGRD': [2, 7.2]}}
#xlim_pct = [-50, 15]

# Output file (include {fcst} and {verif} placeholders) 
out_fname = '../figs/CtrlUA{fcst}hVerif.pdf'


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
        param['sim_verif'][key][sim] = param['sim_verif'][key][sim].format(subtyp='upper_air')

# Extract plotting parameters
plot_dict = param['ua_pt']

# Create plots
for fcst in fcst_lead:

    print()
    print(f"Fcst lead = {fcst}")

    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(6.5, 4.5), sharey=True)
    plt.subplots_adjust(left=0.13, bottom=0.22, right=0.99, top=0.93, hspace=0.37, wspace=0.1)
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
                _ = mp.plot_ua_vprof(real_sim,
                                     valid_times,
                                     fcst_lead=fcst,
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
                _ = mp.plot_ua_vprof(diff_sims,
                                     valid_times,
                                     fcst_lead=fcst,
                                     plot_stat=plot_dict[v]['plot_stat'],
                                     ax=axes[1, k],
                                     verbose=False,
                                     diffs=True,
                                     include_ctrl=False,
                                     include_zero=True,
                                     **plot_dict[v]['kwargs'])

    # Formatting
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    fontsize = 11
    for i, desc in enumerate(['real', 'OSSE $-$ real']):
        for j, v in enumerate(plot_dict.keys()):
            ax = axes[i, j]
            ax.set_title('')
            ax.grid()

            # Subplot labels
            ax.text(0.05, 0.85, f'{letters[3*i+j]})', size=fontsize, weight='bold', transform=ax.transAxes,
                    backgroundcolor='white')

            # Legend
            if (i == 1) and (j == 1):
                ax.legend(ncols=2, fontsize=fontsize, loc=(-0.4, -0.71))
            else:
                ax.get_legend().remove()

            # Axes labels and limits
            if i == 0:
                ax.set_xlabel(xlabel_real[v], size=fontsize)
                ax.set_xlim(xlim_real[fcst][v])
            elif i == 1:
                ax.set_xlabel(xlabel_diff[v], size=fontsize)
                #ax.set_xlim(xlim_pct)
            if j == 0:
                ax.set_ylabel(f"{desc}\npressure (hPa)", size=fontsize)
            else:
                ax.set_ylabel('')

            # Ticks
            ax.set_ylim([1050, 80])
            ax.set_yticks(ticks=[1000, 700, 500, 300, 200, 100],
                          labels=['1000', '700', '500', '300', '200', '100'],
                          minor=False)
            ax.tick_params(which='both', labelsize=9)

            # Specific humidity ticks
            if (i == 0) and (j == 1):
                formatter = mticker.FuncFormatter(lambda x, pos: f"{x*1e3:.2f}")
                ax.xaxis.set_major_formatter(formatter)

    plt.suptitle(f"{fcst}-hr RMSEs", size=14)
    plt.savefig(out_fname.format(fcst=fcst))
    plt.close()

print(f"Done! Elapsed time = {(dt.datetime.now() - start).total_seconds()} s")


"""
End ctrl_verif_ua_pt_vprof.py
"""
