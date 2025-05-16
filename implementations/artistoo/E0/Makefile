.SECONDARY:
.DELETE_ON_ERROR:

all : allA allB allC

allA : model000a model003a model005a model006a
allB : model000b model003b model005b model006b
allC : model000c model003c model005c model006c



# Directories
results :
	mkdir -p $@

results/MODEL%/tracks : 
	mkdir -p $@

results/MODEL%/img : 
	mkdir -p $@


NSIM=100
THIS_DIR=E0
MAXPROC=4

# Copy/edit input jsons
# ===============================

input :
	mkdir -p $@
	
input/model%a.json : ../model%.json | input
	cat $< | sed 's/"num_sims": 100/"num_sims": $(NSIM)/g' > $@

input/model%b.json : input/model%a.json | input
	cat $< | sed 's/MersenneTwister/MathRandom/g' > $@


# Run models
# ===============================
#MODELXXXA : default Artistoo.
#MODELXXXB : substitute Math.Random prng
#MODELXXXC : repeat default artistoo.

model000a : results/model000a-corrected-tracks.csv
model000b : results/model000b-corrected-tracks.csv
model000c : results/model000c-corrected-tracks.csv

model003a : results/model003a-corrected-tracks.csv
model003b : results/model003b-corrected-tracks.csv
model003c : results/model003c-corrected-tracks.csv

model005a : results/model005a-corrected-tracks.csv
model005b : results/model005b-corrected-tracks.csv
model005c : results/model005c-corrected-tracks.csv

model006a : results/model006a-corrected-tracks.csv
model006b : results/model006b-corrected-tracks.csv
model006c : results/model006c-corrected-tracks.csv

results/MODEL%A/tracks/track$(NSIM).csv : ../simulation-wrapper.py ../persistent-cell.js input/model%a.json | results/MODEL%A/tracks results/MODEL%/img
	rm -f results/MODEL$*A/tracks/* && python $< $(THIS_DIR)/input/model$*a.json $(NSIM) 0 MODEL$*A $(MAXPROC)

results/MODEL%A/combined-tracks.csv : results/MODEL%A/tracks/track$(NSIM).csv
	cat results/MODEL$*A/tracks/track*.csv | head -n 1 > $@ && cat results/MODEL$*A/tracks/track*.csv | grep -v time >> $@

results/model%a-corrected-tracks.csv : correct-torus.R results/MODEL%A/combined-tracks.csv input/model%a.json
	Rscript $^ $@


results/MODEL%B/tracks/track$(NSIM).csv : ../simulation-wrapper.py ../persistent-cell.js input/model%b.json | results/MODEL%B/tracks results/MODEL%/img
	rm -f results/MODEL$*B/tracks/* && python $< $(THIS_DIR)/input/model$*b.json $(NSIM) 0 MODEL$*B $(MAXPROC)

results/MODEL%B/combined-tracks.csv : results/MODEL%B/tracks/track$(NSIM).csv
	cat results/MODEL$*B/tracks/track*.csv | head -n 1 > $@ && cat results/MODEL$*B/tracks/track*.csv | grep -v time >> $@

results/model%b-corrected-tracks.csv : correct-torus.R results/MODEL%B/combined-tracks.csv input/model%b.json
	Rscript $^ $@
	

results/MODEL%C/tracks/track$(NSIM).csv : ../simulation-wrapper.py ../persistent-cell.js input/model%a.json | results/MODEL%C/tracks results/MODEL%/img
	rm -f results/MODEL$*C/tracks/* && python $< $(THIS_DIR)/input/model$*a.json $(NSIM) $(NSIM) MODEL$*C $(MAXPROC)

results/MODEL%C/combined-tracks.csv : results/MODEL%C/tracks/track$(NSIM).csv
	cat results/MODEL$*C/tracks/track*.csv | head -n 1 > $@ && cat results/MODEL$*C/tracks/track*.csv | grep -v time >> $@

results/model%c-corrected-tracks.csv : correct-torus.R results/MODEL%C/combined-tracks.csv input/model%a.json
	Rscript $^ $@




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
