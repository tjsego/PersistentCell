import sys
import multiprocessing as mp
import numpy as np
import pandas as pd
from Naked.toolshed.shell import execute_js
from os import path

""" 
	=========================== settings ===========================
"""

# Settings from command line
parms = sys.argv[1]
nsim = int( sys.argv[2] )
firstsim = int( sys.argv[3])
expName = sys.argv[4]
maxProcessors = int( sys.argv[5] )


# Some other initial settings
nProcessors = mp.cpu_count()
if nProcessors > maxProcessors:
	nProcessors = maxProcessors


""" 
	=========================== Functions ===========================
"""


""" Function to run the node script for a given seed
"""
def run_node(seed) :

	argString = parms + " " + str(seed) + " > results/" + expName + "/tracks/track" + str(seed) +".csv" 
	print(argString)
	success = execute_js( "../persistent-cell.js", argString )
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


"""
    =========================== SCRIPT ===========================
"""


if __name__ == '__main__':
    sims = np.arange( nsim ) + firstsim + 1
    print(sims)
    with mp.Pool( nProcessors ) as p:
        p.map(run_node, sims )
	

