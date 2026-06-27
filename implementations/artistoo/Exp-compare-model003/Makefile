.SECONDARY:
.DELETE_ON_ERROR:

all : model003-tracks model005-tracks model006-tracks

# Directories
results :
	mkdir -p $@


MAX_PROC=4
FORCE_MODES=extension retraction reciprocal
UPDATE_DIR=source-to-target-norm source-to-target-unnorm cell-mass-displacement

# Copy/edit input jsons
# ===============================

input :
	mkdir -p $@
	
	
input/model003%.json : make-json.R ../available_runs/model003.json | input
	Rscript $^ $* input/model003$*.json

input/model005%.json : make-json.R ../available_runs/model005.json | input
	Rscript $^ $* input/model005$*.json

input/model006%.json : make-json.R ../available_runs/model006.json | input
	Rscript $^ $* input/model006$*.json



# Run models
# ===============================


model003-tracks : $(foreach var1, $(FORCE_MODES), $(foreach var2, $(UPDATE_DIR),  results/model003$(var1)_$(var2)_artistoo/corrected-tracks.csv )) 
	touch $@
	
model005-tracks : $(foreach var1, $(FORCE_MODES), $(foreach var2, $(UPDATE_DIR),  results/model005$(var1)_$(var2)_artistoo/corrected-tracks.csv )) 
	touch $@

model006-tracks : $(foreach var1, $(FORCE_MODES), $(foreach var2, $(UPDATE_DIR),  results/model006$(var1)_$(var2)_artistoo/corrected-tracks.csv )) 
	touch $@


results/model003%_artistoo/corrected-tracks.csv : ../run.py ../src/persistent-cell.js input/model003%.json 
	rm -rf results/model003$* && \
	python $< -s ../src/persistent-cell.js -f input/model003$*.json -j $(MAX_PROC)

results/model005%_artistoo/corrected-tracks.csv : ../run.py ../src/persistent-cell.js input/model005%.json 
	rm -rf results/model005$* && \
	python $< -s ../src/persistent-cell.js -f input/model005$*.json -j $(MAX_PROC)

results/model006%_artistoo/corrected-tracks.csv : ../run.py ../src/persistent-cell.js input/model006%.json 
	rm -rf results/model006$* && \
	python $< -s ../src/persistent-cell.js -f input/model006$*.json -j $(MAX_PROC)

results/comparison.pdf : plot-comparison.R model003-tracks
	Rscript $< $@

results/all-model-comparison.pdf : plot-all-comparison.R model003-tracks model006-tracks model005-tracks
	Rscript $< $@



# 
# 
# results/model%a_artistoo/corrected-tracks.csv : ../run.py ../src/screen-lambda-persistent-cell.js input/model%a.json 
# 	rm -f results/model%*a_artistoo && \
# 	python $< -s ../src/screen-lambda-persistent-cell.js -f input/model$*a.json -j $(MAX_PROC)
# 
# results/lambda-screen.pdf : plot-speed.R $(foreach m, $(MODELS), results/model$(m)a_artistoo/corrected-tracks.csv)
# 	Rscript $^ $@

