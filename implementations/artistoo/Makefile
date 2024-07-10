.SECONDARY:
.DELETE_ON_ERROR:

all : results/example-track.txt

node_modules : 
	npm install

results :
	mkdir -p $@
	
results/img/% : 
	mkdir -p $@
	

results/example-track.txt : persistent-cell.js | results node_modules results/img/example
	node $< > $@