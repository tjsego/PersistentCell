# PRW implementations in Artistoo

Starting point for implementing models as defined in `../schemas` in Artistoo.

## Preliminaries: install dependencies

### Make

The easiest way to interact with the code is to use the Makefile.
Make sure you have basic command line tools such as 
"make", "awk", "bc" etc. On MacOS, look for xcode CLT. On Linux, look for build-essential. 
On Windows, I am not sure, but you can still run the code manually.

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

Once node and npm are installed, you can install the necessary packages using 

```
make node_modules
```

Or if you don't have make:

```
npm install
```


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

### ffmpeg

If you want to generate video output, make sure to install ffmpeg as described [here](https://www.ffmpeg.org/download.html).


## How to run

### Using make

If you have Make and all other dependencies installed, you can create model outputs simply by running:

```
make model000
```

(or equivalent `modelXXX` for any `modelXXX.json` that is provided in the repo). 
Outputs will automatically be generated in `results/modelXXX/`.

To run simulations in parallel (recommended), try e.g.:

```
make model000 -j 4
```


### Run manually

#### Step 1 : run simulations

If Node.js, npm, and the node modules are installed, you can run a single simulation of the model using:

```
	mkdir -p results/MODEL000/img
	mkdir -p results/MODEL000/tracks
	node persistent-cell.js model000.json 1 > results/MODEL000/tracks/track1.csv
```

Here, the `1` is the random seed used in the simulation, and replicates can be created analogously by using
a different number here. The random seed will be stored as the track identifier in the csv output produced,
so results of multiple simulations can easily be concatenated in a single file `results/MODEL000/combined-tracks.csv`
at the end. 

#### Step 2: example movie output

Running the simulation with seed 1 as described above also creates images, which can be compiled into
a timelapse by running:

```
ffmpeg -r 10 -i results/MODEL000/img/sim1/MODEL000-seed1-t%01d0.png -vcodec libx264 -pix_fmt yuv420p -y results/MODEL000/example.mp4
```

#### Step 3: track analysis using celltrackR

You can run the analysis script on pooled tracks from step 1:

```
Rscript analysis.R results/MODEL000/combined-tracks.csv model000.json results/MODEL000/analysis.pdf 
```

