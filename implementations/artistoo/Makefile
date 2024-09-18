.SECONDARY:
.DELETE_ON_ERROR:

all : results/example-track.txt

REPS=$(shell seq 1 100)

# Install node
node_modules : 
	npm install

# Directories
results :
	mkdir -p $@

results/MODEL%/tracks : 
	mkdir -p $@

results/MODEL%/img : 
	mkdir -p $@
	

# MODEL000
# ===============================
results/MODEL000/tracks/track%.csv : persistent-cell.js model000.json | results/MODEL000/tracks \
	results/MODEL000/img node_modules
	node $^ $* > $@

results/MODEL000/track1.mp4 : results/MODEL000/tracks/track1.csv
	ffmpeg -r 10 -i results/MODEL000/img/sim1/MODEL000-seed1-t%01d0.png -vcodec libx264 -pix_fmt yuv420p -y $@

# combine tracks of independently simulated cells	
results/MODEL000/combined-tracks.csv : $(foreach s, $(REPS), results/MODEL000/tracks/track$(s).csv)
	cat $< | head -n 1 > $@ && cat $^ | grep -v TimeMCS >> $@

# Analysis summary

