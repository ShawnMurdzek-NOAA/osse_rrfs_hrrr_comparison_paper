#!/bin/sh

# ======================================================
# Make All Figures
# ======================================================

# Must have the proper Python environment (from environment.yml) loaded first

date
echo

# Add root directory to PYTHONPATH
root=`pwd`
export PYTHONPATH=$PYTHONPATH:$root

# Create figs directory
mkdir -p ./figs

# Run plotting scripts
cd plot_code
scripts=( ctrl_verif_sfc_dieoff.py
          ctrl_verif_ua_osse_grid_vprof.py
	  ctrl_verif_ua_pt_vprof.py
	  data_impact_bar_charts.py
	  timeseries_rmse_GFS.py
	  timeseries_rmse_NR.py
	  timeseries_rmse_raob.py
	  uas_osse_verif_lower_atm.py )
for s in ${scripts[@]}; do
  echo
  echo "==================="
  echo "Running ${s}"
  python -u ${s}
done

echo
echo "Done making plots"
date
