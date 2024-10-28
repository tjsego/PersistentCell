# Comparing stochastic simulation results

This module allows you to test the reproducibility of stochastic simulation results, and to test 
whether two samples of stochastic simulation results are equal in distribution. 
The module uses the [EFECT method](https://arxiv.org/abs/2406.16820) implemented 
in [libSSR](https://github.com/tjsego/libSSR). 

The module provides two tools: 
* `ssr/analyze.py`: generates an EFECT report that describes the reproducibility of stochastic simulation 
results and all necessary information to compare those results to another set of stochastic simulation results.
* `ssr/compare.py`: tests for equality in distribution of stochastic simulation results and those encoded in an EFECT 
report. 

## Installation and setup

The easiest way to use this module is with conda. 
Use the script `setup/env.yml` to install all dependencies in a new or existing conda environment. 

With an activated conda environment that has the module dependencies installed, the module can be 
used by adding the absolute path of the `comparison` directory to the environment variable `PYTHONPATH`.

## Data

The module assumes that data is formatted according to the format of this project. 

## Example

Suppose a dataset `data1.csv` contains the output of an implementation run. 
An EFECT report `efect_report1.json` can be generated for the output with the terminal command:

```commandline
python ssr/analyze.py -r data1.csv -o efect_report1.json
```

See `python ssr/analyze.py -h` for information on additional arguments. 

Now suppose a second dataset `data2.csv` contains the output of another implementation run, and that 
we want to test whether we can show that this output is not equal in distribution to those in `data1.csv`. 
If both outputs are of the same sample size and record results at the same simulation times, then we can 
perform our test using the EFECT report for `data1.csv` (*i.e.*, `efect_report1.json`):

```commandline
python ssr/compare.py -e efect_report1.json -r data2.csv -o compare12.json
```

The output `compare12.json` contains a dictionary with the names of results that were compared and a 
p-value. If the p-value is less than an *a priori* significance (typically 0.05), then the two 
samples are considered not equal in distribution. 
