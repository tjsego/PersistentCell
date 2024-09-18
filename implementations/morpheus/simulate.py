import json
import multiprocessing as mp
import os
import subprocess
import csv
import math 
import numpy as np
import xml.etree.ElementTree as ET
import matplotlib as mpl
import matplotlib.pyplot as plt
from typing import Optional, List, Tuple


def ensure_output_dir(_output_dir: str):
    if not os.path.isdir(_output_dir):
        os.makedirs(_output_dir)


def unique_data_dir(_output_dir: str, label : int):
    
    while True :
        result = f'sim_{label}'
        if os.path.isdir(os.path.join(_output_dir, result)) :
            label += 1
        else :
            break

    return os.path.join(_output_dir, result), label


def _simulate(model, sim_label, sim_output_dir, output_freq):
    print(f'Simulation {sim_label}: {sim_output_dir}')

    # model.write(os.path.join(sim_output_dir,'model.xml'));
    subprocess.run(
        ['morpheus','--num-threads=1', f'-s  log_freq={output_freq}' , '-f model.xml'],
        input=ET.tostring(model.getroot(), encoding='utf8', method='xml'),
        cwd=sim_output_dir)

    sim_data = csv.reader(open(os.path.join(sim_output_dir,'logger.csv'),"r"), delimiter="\t",quoting=csv.QUOTE_NONNUMERIC)
    data = []
    next(sim_data, None)  # Skip header row
    for row in sim_data:
        data.append(row)
    
    with open(os.path.join(sim_output_dir,"..", f'sim_{sim_label}.json'), 'w') as f:
        json.dump(
            dict(
                time=[sd[0] for sd in data],
                com_1=[sd[2] for sd in data],
                com_2=[sd[3] for sd in data]
            ),
            f,
            indent=4
        )

def simulate(model,
             output_dir: str, 
             num_sims: int,
             output_freq: float):
    
    output_data_dir = os.path.join(output_dir, 'data')

    ensure_output_dir(output_data_dir)

    input_args = []
    scheduled_labels = []
    
    sim_label = 0;
    for i in range(num_sims):
        
        sim_output_dir, sim_label = unique_data_dir(output_data_dir, sim_label)
        ensure_output_dir(sim_output_dir)
        
        input_args.append((model, sim_label, sim_output_dir, output_freq ))
        model.write(os.path.join(sim_output_dir,'model.xml'), encoding='utf-8');
        
        scheduled_labels.append(sim_label)
        sim_label = sim_label+1

    with mp.Pool() as p:
        p.starmap(_simulate, input_args)
        
    ## Create the Directional AutoCorrelation
    dac_count  = np.zeros(0)
    dac_sum    = np.zeros(0)
    dac_sqrsum = np.zeros(0)
    for (model, sim_label, sim_output_dir, output_freq ) in input_args :
        with open(os.path.join( output_data_dir, f'sim_{sim_label}.json'), mode="r", encoding="utf-8") as f :
            print("loading " + f'sim_{sim_label}.json')
            data = json.load(f)
            x = data['com_1']; y = data['com_2'];
            dt = data['time'][1]-data['time'][0];
            data_length = len(x)
            angles = np.zeros(data_length)
            angles[0] =0;
            for i in range(1,data_length) :
                angles[i] = math.atan2( (y[i]-y[i-1]) , (x[i]-x[i-1]) )
            
            lag_range = min(100, data_length)
            if (len(dac_count) == 0) :
                dac_count = np.zeros(lag_range)
                dac_sum = np.zeros(lag_range)
                dac_sqrsum = np.zeros(lag_range)
                
            for lag in range(lag_range) :
                for i in range(0,data_length-lag) :
                    corr = math.cos(angles[i+lag]-angles[i])
                    dac_count[lag] += 1
                    dac_sum[lag] += corr
                    dac_sqrsum[lag] += corr*corr
    
    dac_mean = dac_sum / dac_count
    dac_std = (dac_sqrsum - dac_sum * dac_mean) / (dac_count -1)
    
    # fig, ax = plt.subplots()
    plt.errorbar (np.arange(0,lag_range)*dt, dac_mean, np.sqrt(dac_std) )
    plt.show()
    