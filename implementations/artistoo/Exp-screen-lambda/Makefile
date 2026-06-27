.SECONDARY:
.DELETE_ON_ERROR:

all :model003a model005a model006a



# Directories
results :
	mkdir -p $@


NSIM=100
MAX_PROC=4
LAMBDAS=0 100 5

# Copy/edit input jsons
# ===============================
#MODELXXXA : default Artistoo.
#MODELXXXB : substitute Math.Random prng
#MODELXXXC : repeat default artistoo.

input :
	mkdir -p $@
	
input/model%a.json : make-json.R ../available_runs/model%.json | input
	Rscript $^ '$(LAMBDAS)' $@


# Run models
# ===============================

model003a : results/model003a_artistoo/lambda-screen.pdf
model005a : results/model005a_artistoo/lambda-screen.pdf
model006a : results/model006a_artistoo/lambda-screen.pdf

MODELS=003 005 006

results/model%a_artistoo/corrected-tracks.csv : ../run.py ../src/screen-lambda-persistent-cell.js input/model%a.json 
	rm -f results/model%*a_artistoo && \
	python $< -s ../src/screen-lambda-persistent-cell.js -f input/model$*a.json -j $(MAX_PROC)

results/lambda-screen.pdf : plot-speed.R $(foreach m, $(MODELS), results/model$(m)a_artistoo/corrected-tracks.csv)
	Rscript $^ $@

