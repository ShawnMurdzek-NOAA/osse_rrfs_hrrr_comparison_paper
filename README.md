# Figures for Manuscript Comparing HRRR and RRFS in a Regional OSSE Framework

## Organization

- `plot_code`: Scripts used to create figures. Note that most of the output data actually required to create these figures is not included.

### Submodules

- [metplus_OSSE_scripts](https://github.com/ShawnMurdzek-NOAA/metplus_OSSE_scripts)

## Creating figures

*These steps assume that you are working on a Linux machine*

1. Recursively clone this directory so that submodules are also cloned:

```
git clone --recurse-submodules https://github.com/ShawnMurdzek-NOAA/osse_rrfs_hrrr_comparison_paper.git
cd osse_rrfs_hrrr_comparison_paper
```

2. Load a Python environment. An existing Python environment you have might already work. You can also create a new environment using the `environment.yml` file included here. This can be done using conda:

```
conda env create -f python_environment.yml --prefix {ENV_PREFIX}
conda activate {ENV_PREFIX}
```

3. Untar and unzip the required data:

```
cd data
bash untar_link_MET_output.sh
cd UAS_obs
tar xvzf uas_obs.tar.gz
cd ../../
```

4. Create plots.

```
bash make_all_plots.sh
```

## Other repos used in this project

- RRFSv1-like source code (tag v1.0.0): <https://github.com/ShawnMurdzek-NOAA/rrfs-workflow/tree/UAS_OSSE>
- HRRR-like source code (tag v1.0.0): <https://github.com/ShawnMurdzek-NOAA/WRF_FCST_OSSE>
- Code for computing Todling (2013) observation impact metric: <https://github.com/ShawnMurdzek-NOAA/data-impact/tree/osse_impact>
