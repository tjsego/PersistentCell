.SECONDARY:
.DELETE_ON_ERROR:

all : model000 model003 model005

REPS=$(shell seq 1 100)

# Install node
node_modules : 
	npm install
	
.Rsetup : Rsetup.R Rpackages.txt 
	Rscript $^ | tee $@

# Directories
results :
	mkdir -p $@

results/MODEL%/tracks : 
	mkdir -p $@

results/MODEL%/img : 
	mkdir -p $@
	

# MODEL000
# ===============================
model000 : results/MODEL000/example.mp4 results/MODEL000/analysis.pdf

results/MODEL000/tracks/track%.csv : persistent-cell.js model000.json | results/MODEL000/tracks \
	results/MODEL000/img node_modules
	node $^ $* > $@

results/MODEL000/example.mp4 : results/MODEL000/tracks/track1.csv
	ffmpeg -r 10 -i results/MODEL000/img/sim1/MODEL000-seed1-t%01d0.png -vcodec libx264 -pix_fmt yuv420p -y $@

# combine tracks of independently simulated cells	
results/MODEL000/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL000/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

# Analysis summary
results/MODEL000/analysis.pdf : analysis.R results/MODEL000/combined-tracks.csv 
	Rscript $^ model000.json $@

# MODEL000B with Math.random() RNG
# ===============================
model000b : results/MODEL000B/analysis.pdf

results/MODEL000B/tracks/track%.csv : persistent-cell.js model000.json | results/MODEL000B/tracks \
	results/MODEL000B/img node_modules
	node $^ $* > $@

# combine tracks of independently simulated cells	
results/MODEL000B/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL000B/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

# Analysis summary
results/MODEL000B/analysis.pdf : analysis.R results/MODEL000B/combined-tracks.csv 
	Rscript $^ model000.json $@


# MODEL003
# ===============================
model003 : results/MODEL003/example.mp4 results/MODEL003/analysis.pdf

results/MODEL003/tracks/track%.csv : persistent-cell.js model003.json | results/MODEL003/tracks \
	results/MODEL003/img node_modules
	node $^ $* > $@

results/MODEL003/example.mp4 : results/MODEL003/tracks/track1.csv
	ffmpeg -r 10 -i results/MODEL003/img/sim1/MODEL003-seed1-t%01d0.png -vcodec libx264 -pix_fmt yuv420p -y $@

# combine tracks of independently simulated cells	
results/MODEL003/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL003/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

# Analysis summary
results/MODEL003/analysis.pdf : analysis.R results/MODEL003/combined-tracks.csv 
	Rscript $^ model003.json $@



# MODEL005
# ===============================
model005 : results/MODEL005/example.mp4 results/MODEL005/analysis.pdf


results/MODEL005/tracks/track%.csv : persistent-cell.js model005.json | results/MODEL005/tracks \
	results/MODEL005/img node_modules
	node $^ $* > $@

results/MODEL005/example.mp4 : results/MODEL005/tracks/track1.csv
	ffmpeg -r 10 -i results/MODEL005/img/sim1/MODEL005-seed1-t%01d0.png -vcodec libx264 -pix_fmt yuv420p -y $@

# combine tracks of independently simulated cells	
results/MODEL005/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL005/tracks/track$(s).csv)
	@cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

# Analysis summary
results/MODEL005/analysis.pdf : analysis.R results/MODEL005/combined-tracks.csv 
	Rscript $^ model005.json $@


# MODEL006
# ===============================
model006 : results/MODEL006/example.mp4 results/MODEL006/analysis.pdf


results/MODEL006/tracks/track%.csv : persistent-cell.js model006.json | results/MODEL006/tracks \
	results/MODEL006/img node_modules
	node $^ $* > $@

results/MODEL006/example.mp4 : results/MODEL006/tracks/track1.csv
	ffmpeg -r 10 -i results/MODEL006/img/sim1/MODEL006-seed1-t%01d0.png -vcodec libx264 -pix_fmt yuv420p -y $@

# combine tracks of independently simulated cells	
results/MODEL006/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL006/tracks/track$(s).csv)
	@cat $< | head -n 1 > $@ && cat $^ | grep -v time >> $@

# Analysis summary
results/MODEL006/analysis.pdf : analysis.R results/MODEL006/combined-tracks.csv 
	Rscript $^ model006.json $@
