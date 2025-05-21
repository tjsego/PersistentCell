.SECONDARY:
.DELETE_ON_ERROR:

all : allA allB allC

allA : model000a model003a model005a model006a
allB : model000b model003b model005b model006b
allC : model000c model003c model005c model006c



# Directories
results :
	mkdir -p $@


NSIM=1000
THIS_DIR=E1
MAX_PROC=4

# Copy/edit input jsons
# ===============================
#MODELXXXA : default Artistoo.
#MODELXXXB : substitute Math.Random prng
#MODELXXXC : repeat default artistoo.


input :
	mkdir -p $@
	
input/model%a.json : ../available_runs/model%.json | input
	cat $< | sed 's/"num_sims": 100/"num_sims": $(NSIM)/g' | sed 's/"output_name": "model$*",/"output_name": "model$*a",/g'> $@

input/model%b.json : input/model%a.json | input
	cat $< | sed 's/MersenneTwister/MathRandom/g'  | sed 's/model$*a/model$*b/g' > $@

input/model%c.json : input/model%a.json | input
	cat $< | sed 's/model$*a/model$*c/g' > $@


# Run models
# ===============================

model000a : results/model000a_artistoo/corrected-tracks.csv
model000b : results/model000b_artistoo/corrected-tracks.csv
model000c : results/model000c_artistoo/corrected-tracks.csv

model003a : results/model003a_artistoo/corrected-tracks.csv
model003b : results/model003b_artistoo/corrected-tracks.csv
model003c : results/model003c_artistoo/corrected-tracks.csv

model005a : results/model005a_artistoo/corrected-tracks.csv
model005b : results/model005b_artistoo/corrected-tracks.csv
model005c : results/model005c_artistoo/corrected-tracks.csv

model006a : results/model006a_artistoo/corrected-tracks.csv
model006b : results/model006b_artistoo/corrected-tracks.csv
model006c : results/model006c_artistoo/corrected-tracks.csv


results/model%a_artistoo/corrected-tracks.csv : ../run.py ../src/persistent-cell.js input/model%a.json 
	rm -f results/model%*a_artistoo && \
	python $< -s ../src/persistent-cell.js -f input/model$*a.json -j $(MAX_PROC)

results/model%b_artistoo/corrected-tracks.csv : ../run.py ../src/persistent-cell.js input/model%b.json 
	rm -f results/model%*b_artistoo && \
	python $< -s ../src/persistent-cell.js -f input/model$*b.json -j $(MAX_PROC)

results/model%c_artistoo/corrected-tracks.csv : ../run.py ../src/persistent-cell.js input/model%c.json 
	rm -f results/model%*c_artistoo && \
	python $< -s ../src/persistent-cell.js -f input/model$*c.json -j $(MAX_PROC) -i $(NSIM)





# # MODEL003D test
# # ===============================
# model003d : results/model003d-corrected-tracks.csv
# 
# results/MODEL003D/tracks/track%.csv : ../persistent-cell-test.js model003.json | results/MODEL003D/tracks \
# 	results/MODEL003D/img
# 	node $< E0/model003.json $* > $@
# 
# # combine tracks of independently simulated cells	
# results/MODEL003D/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL003D/tracks/track$(s).csv)
# 	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@
# 
# results/model003d-corrected-tracks.csv : correct-torus.R results/MODEL003D/combined-tracks.csv model003.json
# 	Rscript $^ $@
# 
