.SECONDARY:
.DELETE_ON_ERROR:

all : allA allB allC

allA : model000 model003 model005 model006
allB : model000b model003b model005b model006b
allC : model000c model003c model005c model006c


NSIM=$(shell node -p "require('./model000.json').sim.num_sims")

N1 = $(shell echo $(NSIM) + 1 | bc )
N2 = $(shell echo $(NSIM) + $(NSIM) | bc )

REPS=$(shell seq 1 $(NSIM))
REPS2=$(shell seq $(N1) $(N2))


test : 
	@echo $(REPS2)

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

model000.json : ../model000.json
	cat $< | sed 's/"num_sims": 100/"num_sims": 1000/g' > $@

results/MODEL000/tracks/track%.csv : ../persistent-cell.js model000.json | results/MODEL000/tracks \
	results/MODEL000/img
	node $< E0/model000.json $* > $@


# combine tracks of independently simulated cells	
results/MODEL000/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL000/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model000-corrected-tracks.csv : correct-torus.R results/MODEL000/combined-tracks.csv model000.json
	Rscript $^ $@

# MODEL000B with Math.random() RNG
# ===============================
model000b : results/model000b-corrected-tracks.csv

model000b.json : model000.json
	cat $< | sed 's/MersenneTwister/MathRandom/g' > $@

results/MODEL000B/tracks/track%.csv : ../persistent-cell.js model000b.json | results/MODEL000B/tracks \
	results/MODEL000B/img
	node $< E0/model000.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL000B/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL000B/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model000b-corrected-tracks.csv : correct-torus.R results/MODEL000B/combined-tracks.csv model000.json
	Rscript $^ $@

# MODEL000C just a replicate with other random seed.
# ===============================
model000c : results/model000c-corrected-tracks.csv

results/MODEL000C/tracks/track%.csv : ../persistent-cell.js model000.json | results/MODEL000C/tracks \
	results/MODEL000C/img
	node $< E0/model000.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL000C/combined-tracks.csv : $(foreach s, $(REPS2), results/MODEL000C/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model000c-corrected-tracks.csv : correct-torus.R results/MODEL000C/combined-tracks.csv model000.json
	Rscript $^ $@
	


# MODEL003
# ===============================
model003 : results/model003-corrected-tracks.csv

model003.json : ../model003.json
	cat $< | sed 's/"num_sims": 100/"num_sims": 1000/g' > $@


results/MODEL003/tracks/track%.csv : ../persistent-cell.js model003.json | results/MODEL003/tracks results/MODEL003/img
	node $< E0/model003.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL003/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL003/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model003-corrected-tracks.csv : correct-torus.R results/MODEL003/combined-tracks.csv model003.json
	Rscript $^ $@


# MODEL003B with Math.random() RNG
# ===============================
model003b : results/model003b-corrected-tracks.csv

model003b.json : model003.json
	cat $< | sed 's/MersenneTwister/MathRandom/g' > $@


results/MODEL003B/tracks/track%.csv : ../persistent-cell.js model003b.json | results/MODEL003B/tracks \
	results/MODEL003B/img
	node $< E0/model003.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL003B/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL003B/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model003b-corrected-tracks.csv : correct-torus.R results/MODEL003B/combined-tracks.csv model003.json
	Rscript $^ $@

# MODEL003C just a replicate with other random seed.
# ===============================
model003c : results/model003c-corrected-tracks.csv

results/MODEL003C/tracks/track%.csv : ../persistent-cell.js model003b.json | results/MODEL003C/tracks \
	results/MODEL003C/img
	node $< E0/model003.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL003C/combined-tracks.csv : $(foreach s, $(REPS2), results/MODEL003C/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model003c-corrected-tracks.csv : correct-torus.R results/MODEL003C/combined-tracks.csv model003.json
	Rscript $^ $@
	
# MODEL003D test
# ===============================
model003d : results/model003d-corrected-tracks.csv

results/MODEL003D/tracks/track%.csv : ../persistent-cell-test.js model003.json | results/MODEL003D/tracks \
	results/MODEL003D/img
	node $< E0/model003.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL003D/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL003D/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model003d-corrected-tracks.csv : correct-torus.R results/MODEL003D/combined-tracks.csv model003.json
	Rscript $^ $@

# MODEL005
# ===============================
model005 : results/model005-corrected-tracks.csv

model005.json : ../model005.json
	cat $< | sed 's/"num_sims": 100/"num_sims": 1000/g' > $@



results/MODEL005/tracks/track%.csv : ../persistent-cell.js model005.json | results/MODEL005/tracks results/MODEL005/img
	node $< E0/model005.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL005/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL005/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model005-corrected-tracks.csv : correct-torus.R results/MODEL005/combined-tracks.csv model005.json
	Rscript $^ $@

# MODEL005B with Math.random() RNG
# ===============================
model005b : results/model005b-corrected-tracks.csv

model005b.json : model005.json
	cat $< | sed 's/MersenneTwister/MathRandom/g' > $@


results/MODEL005B/tracks/track%.csv : ../persistent-cell.js model005b.json | results/MODEL005B/tracks \
	results/MODEL005B/img
	node $< E0/model005.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL005B/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL005B/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model005b-corrected-tracks.csv : correct-torus.R results/MODEL005B/combined-tracks.csv model005.json
	Rscript $^ $@

# MODEL005C just a replicate with other random seed.
# ===============================
model005c : results/model005c-corrected-tracks.csv

results/MODEL005C/tracks/track%.csv : ../persistent-cell.js model005b.json | results/MODEL005C/tracks \
	results/MODEL005C/img
	node $< E0/model005.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL005C/combined-tracks.csv : $(foreach s, $(REPS2), results/MODEL005C/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model005c-corrected-tracks.csv : correct-torus.R results/MODEL005C/combined-tracks.csv model005.json
	Rscript $^ $@
	
# MODEL006
# ===============================
model006 : results/model006-corrected-tracks.csv

model006.json : ../model006.json
	cat $< | sed 's/"num_sims": 100/"num_sims": 1000/g' > $@


results/MODEL006/tracks/track%.csv : ../persistent-cell.js model006.json | results/MODEL006/tracks results/MODEL006/img
	node $< E0/model006.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL006/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL006/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model006-corrected-tracks.csv : correct-torus.R results/MODEL006/combined-tracks.csv model006.json
	Rscript $^ $@

# MODEL006B with Math.random() RNG
# ===============================
model006b : results/model006b-corrected-tracks.csv

model006b.json : model006.json
	cat $< | sed 's/MersenneTwister/MathRandom/g' > $@


results/MODEL006B/tracks/track%.csv : ../persistent-cell.js model006b.json | results/MODEL006B/tracks \
	results/MODEL006B/img
	node $< E0/model006.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL006B/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL006B/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model006b-corrected-tracks.csv : correct-torus.R results/MODEL006B/combined-tracks.csv model006.json
	Rscript $^ $@

# MODEL006C just a replicate with other random seed.
# ===============================
model006c : results/model006c-corrected-tracks.csv

results/MODEL006C/tracks/track%.csv : ../persistent-cell.js model006b.json | results/MODEL006C/tracks \
	results/MODEL006C/img
	node $< E0/model006.json $* > $@

# combine tracks of independently simulated cells	
results/MODEL006C/combined-tracks.csv : $(foreach s, $(REPS2), results/MODEL006C/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

results/model006c-corrected-tracks.csv : correct-torus.R results/MODEL006C/combined-tracks.csv model006.json
	Rscript $^ $@