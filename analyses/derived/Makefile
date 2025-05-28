.SECONDARY:
.DELETE_ON_ERROR:

all : plots/example-comp.pdf plots/example-msd.pdf plots/example-acov.pdf

data : 
	mkdir -p $@
	
plots : 
	mkdir -p $@

.Rsetup : Rsetup.R Rpackages.txt 
	Rscript $^ | tee $@


data/example-comp.rds : scripts/load-and-preprocess-tracks.R example-comparison.json | data .Rsetup
	Rscript $^ $@
	
plots/example-comp.pdf : scripts/simple-speeds.R data/example-comp.rds  | plots
	Rscript $^ $@
	
plots/example-msd.pdf : scripts/msd.R data/example-comp.rds  | plots
	Rscript $^ $@
	
# autocovariance up to time lag 100 min
plots/example-acov.pdf : scripts/acov.R data/example-comp.rds  | plots
	Rscript $^ 100 $@
	

# raw data: square displacements and DAC for all subtracks.
# this won't work very well with the current sampling rate of every 100 MCS though.
data/example-processed.csv : scripts/data-msd-acov.R ../../implementations/artistoo/E0/results/model006-corrected-tracks.csv | data
	Rscript $^ $@
	
plots/example-processed.pdf : scripts/plot-msd-acov.R data/example-processed.csv | plots
	Rscript $^ $@