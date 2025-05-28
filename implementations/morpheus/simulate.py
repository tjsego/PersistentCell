import json
from model import from_json_data

import multiprocessing as mp
from time import sleep
import os
import subprocess
import csv
import math
import random
import numpy as np
import xml.etree.ElementTree as ET
import matplotlib as mpl
import matplotlib.pyplot as plt
from typing import Optional, List, Tuple
from packaging.version import Version
import re



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


def _simulate(model, sim_label, sim_output_dir):
    print(f'Simulation {sim_label}: {sim_output_dir}')

    
    raw_version = subprocess.run(['morpheus','--version'], capture_output=True);
    if raw_version:
        match = re.search(r"\d+\.\d+\.\d+", raw_version.stdout.decode('utf-8'))
        if Version(match[0]) < Version("2.3.9") :
            raise r"Morpheus version of at least 2.3.9 required"
    else :
        raise r"Unable to launch Morpheus. Make sure 'morpheus' binary is reachable from path"
    
    model_xml = ET.tostring(model.getroot(), encoding='utf8', method='xml')
    model.write(os.path.join(sim_output_dir,'model.xml'))
     
    subprocess.run(
        ['morpheus','--num-threads=1', '-'],
        input=model_xml,
        cwd=sim_output_dir)

    sim_data = csv.reader(open(os.path.join(sim_output_dir,'logger.csv'),"r"), delimiter="\t",quoting=csv.QUOTE_NONNUMERIC)
    data = []
    next(sim_data, None)  # Skip header row
    for row in sim_data:
        row[1] = sim_label
        data.append(row)    

    with open(os.path.join(sim_output_dir,"..", f'sim_{sim_label}.json'), 'w') as f:
        json.dump(
            dict(
                time = [sd[0] for sd in data],
                com_1 = [sd[2] for sd in data],
                com_2 = [sd[3] for sd in data],
                area = [sd[4] for sd in data],
                surface = [sd[5] for sd in data]
            ),
            f,
            indent=4
        )

def simulate(model_data,
             input_dir: str,
             output_dir: str, 
             num_sims: int,
             plot: bool):
    
    
    output_data_dir = os.path.join(output_dir, 'morpheus_data')

    ensure_output_dir(output_data_dir)

    input_args = []
    scheduled_labels = []
    
    sim_label = 0;
    for i in range(num_sims):
        
        sim_output_dir, sim_label = unique_data_dir(output_data_dir, sim_label)
        ensure_output_dir(sim_output_dir)
        
        
        my_data= model_data.copy()
        my_data["seed"] = random.randint(0, 2147483647)
        
        model = from_json_data(my_data )
        
        model.write(os.path.join(sim_output_dir,'model.xml'), encoding='utf-8');
        input_args.append((model, sim_label, sim_output_dir ))
        
        scheduled_labels.append(sim_label)
        sim_label = sim_label+1
    
    with mp.Pool() as p:
        p.starmap(_simulate, input_args)
        
    
    writer = csv.writer(open(os.path.join(sim_output_dir,"..", f'sim.csv'), 'a'))
    writer.writerow(['time','id','com_1','com_2','area','surface'])
    for spec in input_args :
        sim_label = spec[1]
        sim_output_dir = spec[2]
        sim_data = csv.reader(open(os.path.join(sim_output_dir,'logger.csv'),"r"), delimiter="\t",quoting=csv.QUOTE_NONNUMERIC)
        next(sim_data, None)  # Skip header row
        for row in sim_data:
            row[1] = sim_label
            writer.writerow(row)
    
    if (plot):
        plot_DAC_MSD(output_data_dir, [ sim[1] for sim in input_args])
        
def plot_DAC_MSD(output_dir, sim_labels) :
    dac_lag_range = 100
    msd_lag_range = 1000
    ## Create the Directional AutoCorrelation
    dac_count  = np.zeros(0)
    dac_sum    = np.zeros(0)
    dac_sqrsum = np.zeros(0)
    dac_25quantil = np.zeros(0)
    dac_75quantil = np.zeros(0)
    
    msd_count  = np.zeros(0)
    msd_sum    = np.zeros(0)
    for sim_label in sim_labels :
        with open(os.path.join( output_dir, f'sim_{sim_label}.json'), mode="r", encoding="utf-8") as f :
            print("loading " + f'sim_{sim_label}.json')
            data = json.load(f)
            x = np.array(data['com_1']); y = np.array(data['com_2']);
            dt = data['time'][1]-data['time'][0];
            data_length = len(x)
            angles = np.zeros(data_length)
            dx=np.array((x[1:] - x[:-1], y[1:] - y[:-1] ))
            dx=np.concatenate( ([[1],[0]],dx), 1)
            dx_len = np.sqrt(np.sum(dx**2, axis=0))
            dx_norm = dx / np.stack((dx_len, dx_len))
            
            if (len(dac_count) == 0) :
                dac_count  = np.zeros(dac_lag_range)
                dac_sum    = np.zeros(dac_lag_range)
                dac_sqrsum = np.zeros(dac_lag_range)
                dac_25quantil = np.zeros(dac_lag_range)
                dac_75quantil = np.zeros(dac_lag_range)
                msd_count  = np.zeros(msd_lag_range)
                msd_sum    = np.zeros(msd_lag_range)
                
            for lag in range(dac_lag_range) :
                corr = np.sum(np.multiply(dx_norm[:,lag:data_length-1] , dx_norm[:,0:data_length-lag-1] ), axis=0 )
                corr.sort()
                dac_25quantil[lag]    += corr[int(0.25*len(corr))]
                dac_75quantil[lag]    += corr[int(0.75*len(corr))]
                dac_count[lag]  += len(corr)
                dac_sum[lag]    += np.sum(corr)
                dac_sqrsum[lag] += np.sum(corr*corr)

            for lag in range(msd_lag_range) :
                msd_count[lag] += data_length-lag
                msd_sum[lag] = np.sum( (x[lag:data_length-1] - x[0:data_length-lag-1])**2 + (y[lag:data_length-1] - y[0:data_length-lag-1])**2 )
    
    dac_mean = dac_sum / dac_count
    dac_std = (dac_sqrsum - dac_sum * dac_mean) / (dac_count -1)
    dac_25quantil /= len(sim_labels)
    dac_75quantil /= len(sim_labels)
    msd = msd_sum / msd_count
    
    ## Create the Mean squared displacement
    
    
    fig, ax = plt.subplots(1,2)
    fig.title = output_dir
    ax[0].errorbar (np.arange(0,dac_lag_range)*dt, dac_mean, [[dac_25quantil-dac_mean,dac_75quantil-dac_mean]] ) #np.sqrt(dac_std) 
    ax[0].set_xlabel('lag time')
    ax[0].set_ylabel('dac')
    ax[1].plot (np.arange(0,msd_lag_range)*dt, msd)
    ax[1].set_xlabel('lag time')
    ax[1].set_ylabel('msd')
    ax[1].set_xscale('log')
    ax[1].set_yscale('log')
    plt.show()
    
