# PRW implementations in Artistoo

Starting point for implementing models as defined in `../schemas` in Artistoo.

## Quick start

If you are using conda (recommended), set up your environment. Navigate to 

```
cd path/to/PersistentCell/implementations/artistoo
```

then create the conda environment:

```
conda env create -f env.yml
```

and activate it:


```
conda activate persistent-cell-artistoo
```

finally, install node packages (locally):

```
npm install
```

now run a simulation using the python wrapper, e.g.:

```
python run.py -s src/persistent-cell.js -f available_runs/model000.json
```

Results will pop up in a newly generated "results" folder with subfolder depending on 
which model you are running.

If not using conda, read on.

## Without conda


### Make and other command line tools:

To use all code, the easiest way to interact with the code is to use the Makefile.
Make sure you have basic command line tools such as 
"make", "awk", "bc" etc. On MacOS, look for xcode CLT. On Linux, look for build-essential. 
On Windows, I am not sure, but you can still run the code manually.

Other tools you may need:
- sed (used to automatically parse input json files for some of the exps)
- ffmpeg (if you want to make videos, see [this page](https://www.ffmpeg.org/download.html) 

### Nodejs, npm, and packages

You'll need Nodejs and its package manager to run Artistoo simulations from the command line. 
See (https://nodejs.org/en/download/)[https://nodejs.org/en/download/].

Standard package managers sometimes install incompatible versions of npm and nodejs. 
To avoid this, you can install both at once using nvm:

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install --lts
nvm use --lts
```

Once node and npm are installed, you can install the necessary packages locally using 

```
npm install
```


### R and packages

Please make sure you have R installed, as well as the required packages:

- jsonlite
- celltrackR
- dplyr
- ggplot2
- patchwork
- ggbeeswarm 

### Python and packages

To use the wrapper script, please make sure you have python installed, as well as the required
packages:

- numpy
- pandas
- argparse
- Naked
- tqdm 



## How to run

### Using make

If you have Make and all other dependencies installed, you can create model outputs simply by running:

```
make model000
```

(or equivalent `modelXXX` for any `modelXXX.json` that is provided in the repo). 
Outputs will automatically be generated in `results/`.


### Using the python wrapper

```
python run.py -s src/persistent-cell.js -f available_runs/model000.json -j 4
```
will run model000 simulations in parallel using 4 cores, and postprocess tracks into 
`/results/something/corrected-tracks.csv`.
