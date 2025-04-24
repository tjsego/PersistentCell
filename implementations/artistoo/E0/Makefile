.SECONDARY:
.DELETE_ON_ERROR:

all : model000 model000b model003 model005

REPS=$(shell seq 1 100)


# Directories
results :
	mkdir -p $@

results/MODEL%/tracks : 
	mkdir -p $@

results/MODEL%/img : 
	mkdir -p $@
	

# MODEL000
# ===============================
model000 : results/model000-corrected-tracks.csv

results/MODEL000/tracks/track%.csv : ../persistent-cell.js model000.json | results/MODEL000/tracks \
	results/MODEL000/img
	node $< model000.json $* > $@


# combine tracks of independently simulated cells	
results/MODEL000/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL000/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model000-corrected-tracks.csv : correct-torus.R results/MODEL000/combined-tracks.csv model000.json
	Rscript $^ $@

# MODEL000B with Math.random() RNG
# ===============================
model000b : results/model000b-corrected-tracks.csv

results/MODEL000B/tracks/track%.csv : ../persistent-cell-RNG.js model000.json | results/MODEL000B/tracks \
	results/MODEL000B/img
	node $^ model000.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL000B/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL000B/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model000b-corrected-tracks.csv : correct-torus.R results/MODEL000B/combined-tracks.csv model000.json
	Rscript $^ $@
	


# MODEL003
# ===============================
model003 : results/model003-corrected-tracks.csv

results/MODEL003/tracks/track%.csv : ../persistent-cell.js model003.json | results/MODEL003/tracks results/MODEL003/img
	node $< model003.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL003/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL003/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model003-corrected-tracks.csv : correct-torus.R results/MODEL003/combined-tracks.csv model003.json
	Rscript $^ $@

# MODEL005
# ===============================
model005 : results/model005-corrected-tracks.csv

results/MODEL005/tracks/track%.csv : ../persistent-cell.js model005.json | results/MODEL005/tracks results/MODEL005/img
	node $< model005.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL005/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL005/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model005-corrected-tracks.csv : correct-torus.R results/MODEL005/combined-tracks.csv model005.json
	Rscript $^ $@
