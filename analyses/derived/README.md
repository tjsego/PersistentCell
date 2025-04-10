# Comparing track statistics based on track output

This code allows you to compare different track datasets, e.g. outputs from different
frameworks or different models. See the examples in `plots/`; the outputs can be expanded
at a later stage.

## Dependencies

### Make

The easiest way to interact with the code is to use the Makefile.
Make sure you have basic command line tools such as 
"make", "awk", "bc" etc. On MacOS, look for xcode CLT. On Linux, look for build-essential. 
On Windows, I am not sure, but you can still run the code manually.


### R and packages

To use the analysis code, please make sure you have R installed, and make sure to get the required 
packages by running:

```
make .Rsetup
```

or directly

```
Rscript Rsetup.R Rpackages.txt
```

## Data

The code assumes that you have generated tracks as csv somewhere, where:

- One csv files contains tracks from one or more simulated cells (this can also be pooled 
	single cell replicates with a different random seed)
- One column contains the simulation time
- One column contains a unique identifier for every cell/track
- One column contains the x-coordinate
- and one column contains the y-coordinate

The ordering or naming of the columns does not matter as it can be specified in a 
configuration json file (see below).

## Example

See `example-comparison.json`; you can choose a comparison between different track 
csv files, give them a name that will appear in the figure legends, and specify some
relevant scaling details for the comparison as well as which csv columns contain which
information. In principle you can add as many datasets as you like, but you may wish 
to adjust the height and width of the output plots in the relevant script.

The output plots can be generated via the Makefile or manually, as long as the 
json file is specified. The first step is to read, rescale, and pool the datasets
that are to be compared:

```
mkdir data
Rscript scripts/load-and-preprocess-tracks.R example-comparison.json data/example-comp.rds
```

After this step, all data are in `data/example-comp.rds` and will all be scaled with 
space in microns and time in minutes.

We can then perform various motility comparisons, e.g. speeds:

```
mkdir plots
Rscript scripts/simple-speed.R data/example-comp.rds plots/example-comp.pdf
```

Or MSD:
```
mkdir plots
Rscript scripts/msd.R data/example-comp.rds plots/example-msd.pdf
```

Or autocovariance (in this case only over time lags up to 100 minutes):

```
mkdir plots
Rscript scripts/acov.R data/example-comp.rds 100 plots/example-msd.pdf
```

	


