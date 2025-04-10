.SECONDARY:
.DELETE_ON_ERROR:

all : model000 model003 model005

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
	node $< E0/model000.json $* > $@


# combine tracks of independently simulated cells	
results/MODEL000/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL000/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model000-corrected-tracks.csv : correct-torus.R results/MODEL000/combined-tracks.csv model000.json
	Rscript $^ $@
	


# MODEL003
# ===============================
model003 : results/model003-corrected-tracks.csv

results/MODEL003/tracks/track%.csv : ../persistent-cell.js model003.json | results/MODEL003/tracks results/MODEL003/img
	node $< E0/model003.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL003/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL003/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model003-corrected-tracks.csv : correct-torus.R results/MODEL003/combined-tracks.csv model003.json
	Rscript $^ $@

# MODEL005
# ===============================
model005 : results/model005-corrected-tracks.csv

results/MODEL005/tracks/track%.csv : ../persistent-cell.js model005.json | results/MODEL005/tracks results/MODEL005/img
	node $< E0/model005.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL005/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL005/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model005-corrected-tracks.csv : correct-torus.R results/MODEL005/combined-tracks.csv model005.json
	Rscript $^ $@
