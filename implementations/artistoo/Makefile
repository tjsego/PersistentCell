.SECONDARY:
.DELETE_ON_ERROR:

all : model000 model001

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
	cat $< | head -n 1 > $@ && cat $^ | grep -v TimeMCS >> $@

# Analysis summary
results/MODEL000/analysis.pdf : analysis.R results/MODEL000/combined-tracks.csv 
	Rscript $^ model000.json $@



# MODEL001
# ===============================
model001 : results/MODEL001/example.mp4 results/MODEL001/analysis.pdf


results/MODEL001/tracks/track%.csv : persistent-cell.js model001.json | results/MODEL001/tracks \
	results/MODEL001/img node_modules
	node $^ $* > $@

results/MODEL001/example.mp4 : results/MODEL001/tracks/track1.csv
	ffmpeg -r 10 -i results/MODEL001/img/sim1/MODEL001-seed1-t%01d0.png -vcodec libx264 -pix_fmt yuv420p -y $@

# combine tracks of independently simulated cells	
results/MODEL001/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL001/tracks/track$(s).csv)
	@cat $< | head -n 1 > $@ && cat $^ | grep -v TimeMCS >> $@

# Analysis summary
results/MODEL001/analysis.pdf : analysis.R results/MODEL001/combined-tracks.csv 
	Rscript $^ model001.json $@
