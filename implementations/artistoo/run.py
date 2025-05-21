# packages from standard lib
import sys 
import json 
import multiprocessing as mp 
import os
import glob

# packages in conda env.yml
import numpy as np
import pandas as pd
from Naked.toolshed.shell import execute_js, execute
from tqdm import tqdm

import argparse



""" 
	=========================== settings ===========================
"""

def setup(args):
	with open(args['fp'], 'r') as f:
		config_data = json.load(f)
	expName = config_data['sim']['output_name'] + "_artistoo"
	out_dir = "results/" + expName + "/tracks"
	result_dir = "results/" + expName 
	os.makedirs( out_dir, exist_ok = True )
	os.makedirs( f'{result_dir}/img', exist_ok = True )
	args['out_dir'] = out_dir
	args['result_dir'] = result_dir
	args['src_path'] = args['script'].replace( "persistent-cell.js" , "" )
	return args, config_data



class ArgParser(argparse.ArgumentParser):
    
	def __init__(self):
		super().__init__(description='Execute specification with Artistoo')

		self.add_argument('-s', '--script',
                          type=str,
                          required=True,
                          dest='script_path',
                          help='Absolute path to simulation script [root]/persistent-cell.js')

		self.add_argument('-f', '--file',
                          type=str,
                          required=True,
                          dest='spec_path',
                          help='Absolute path to model specification json with implementation specification for Artistoo')

		self.add_argument('-j', '--max_proc',
                          type=str,
                          default=2,
                          dest='max_proc',
                          help='Max number of cores used for parallel simulation runs. Default is 2.')

		self.add_argument('-i', '--first_seed',
                          type=int,
                          default=0,
                          dest='first_seed',
                          help='constant number to add to simulation seeds.')

		self.parsed_args = self.parse_args()

	@property
	def spec_path(self):
		return f'{os.getcwd()}/{self.parsed_args.spec_path}'
        
	@property
	def script_path(self):
		return f'{os.getcwd()}/{self.parsed_args.script_path}'

	@property
	def max_proc(self) -> int:
		value = int( self.parsed_args.max_proc )
		np = mp.cpu_count()
		if value > np : 
			value = np
		return value

	@property
	def first_seed(self) -> int:
		return self.parsed_args.first_seed

	@property
	def kwargs(self):
		return dict(
			script=self.script_path,
			fp=self.spec_path,
			max_proc=self.max_proc,
			first_seed=self.first_seed
		)

args = ArgParser().kwargs
args, config_data = setup(args)


""" 
	=========================== Functions ===========================
"""

""" Function to run the node script for a given seed
"""
def run_node(seed) :

	argString = args['fp'] + " " + str(seed) + " > " + args['out_dir'] + "/track" + str(seed) +".csv" 
	#print(script + " " + argString)
	success = execute_js(args['script'], argString )
	if success:
		pass
	else:
		raise NameError("error in node: " + argString )


""" Parallel computation of the simulations at a given parameter combination
"""
def run_all():
	
    with mp.Pool( nProcessors ) as pool:
        result = pool.imap( run_node, theParms.itertuples(name=None), chunksize = 2 )
        output = pd.DataFrame()
        sims = 0
        for x in result:
            sims = sims+1

def merge_all():
    source_files = sorted( os.listdir( args['out_dir'] ) )
    dataframes = []
    for file in source_files:
        df = pd.read_csv(args['out_dir'] + "/" + file) 
        dataframes.append(df)
    df_all = pd.concat(dataframes)
    return df_all

def correct_boundary( fName, outFile ):
	w = config_data['model']['len_1']
	h = config_data['model']['len_2']
	src = args['src_path']
	success = execute( f'Rscript {src}/correct-periodic-boundary.R {fName} {w} {h} {outFile}' )



"""
    =========================== SCRIPT ===========================
"""


if __name__ == '__main__':
    nsim = int( config_data['sim']['num_sims'] )
    sims = np.arange( nsim ) + int( args['first_seed'] ) + 1
    nProcessors = args['max_proc']
    print( ".... Running simulations in parallel with " + str(nProcessors) + " cores; (change using -j [desired_cores])")
    with mp.Pool( nProcessors ) as p, tqdm( total = nsim) as pbar:
        #p.map(run_node, sims )
        for result in p.imap( run_node, sims):
        	pbar.update()
        	pbar.refresh()
    out = merge_all()
    out_name = args['out_dir'] + "/combined-tracks.csv"
    out.to_csv(out_name, index=False) 
    out_name2 =  args['result_dir'] + "/corrected-tracks.csv"
    print( ".... writing output to " + out_name2 )
    correct_boundary( out_name, out_name2 )
    print( " Done!")
    
	