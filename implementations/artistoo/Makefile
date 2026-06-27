.SECONDARY:
.DELETE_ON_ERROR:

all : model000 model003 model005 model006 model008

MAX_PROC = 4


model000 : results/model000_artistoo/analysis.pdf results/model000_artistoo/example.mp4
model003 : results/model003_artistoo/analysis.pdf results/model003_artistoo/example.mp4
model005 : results/model005_artistoo/analysis.pdf results/model005_artistoo/example.mp4
model006 : results/model006_artistoo/analysis.pdf results/model006_artistoo/example.mp4
model008 : results/model008_artistoo/analysis.pdf results/model008_artistoo/example.mp4


results/model008_artistoo/corrected-tracks.csv : run.py src/chemotaxis.js available_runs/model008.json 
	rm -rf results/model$*_artistoo && \
	python $< -s src/chemotaxis.js -f available_runs/model008.json -j $(MAX_PROC)

results/model008_artistoo/analysis.pdf : src/analysis.R results/model008_artistoo/corrected-tracks.csv
	Rscript $^ available_runs/model008.json $@

results/model008_artistoo/example.mp4 : results/model008_artistoo/corrected-tracks.csv
	ffmpeg -r 20 -i results/model008_artistoo/img/MODEL008-seed1-t%01d0.png -vcodec libx264 -pix_fmt yuv420p -y $@



results/model%_artistoo/corrected-tracks.csv : run.py src/persistent-cell.js available_runs/model%.json 
	rm -rf results/model$*_artistoo && \
	python $< -s src/persistent-cell.js -f available_runs/model$*.json -j $(MAX_PROC)


results/model%_artistoo/analysis.pdf : src/analysis.R results/model%_artistoo/corrected-tracks.csv
	Rscript $^ available_runs/model$*.json $@

results/model%_artistoo/example.mp4 : results/model%_artistoo/corrected-tracks.csv
	ffmpeg -r 20 -i results/model$*_artistoo/img/MODEL$*-seed1-t%01d0.png -vcodec libx264 -pix_fmt yuv420p -y $@

