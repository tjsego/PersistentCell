.SECONDARY:
.DELETE_ON_ERROR:


data : 
	mkdir -p $@
	
plots : 
	mkdir -p $@

data/example-comp.rds : scripts/load-and-preprocess-tracks.R example-comparison.json | data
	Rscript $^ $@
	
plots/example-comp.pdf : scripts/simple-speeds.R data/example-comp.rds  | plots
	Rscript $^ $@
	
plots/example-msd.pdf : scripts/msd.R data/example-comp.rds  | plots
	Rscript $^ $@
	
# autocovariance up to time lag 100 min
plots/example-acov.pdf : scripts/acov.R data/example-comp.rds  | plots
	Rscript $^ 100 $@