import json
from math import sqrt
import xml.etree.ElementTree as ET
import os


def params2args() :
    return {
        cpm_area_c : cpm_
        }

class morpheus_model:
    """ Template for any morpheus model """
    
    def __init__(self, input_dir : str) :
        self.input_dir = input_dir
    
    def xpath4param(self):
        params = {
            # "cpm_area_v" : "./CellTypes/CellType/Constant[@symbol='a_cpm']/@value",
            "cpm_area_v" : "./Global/Constant[@symbol='a_cpm']/@value",
            "cpm_area_c" : "./CellTypes/CellType/Constant[@symbol='λ_a_cpm']/@value",
            "cpm_perim_v" : "./CellTypes/CellType/Constant[@symbol='p_cpm']/@value",
            "cpm_perim_c" : "./CellTypes/CellType/Constant[@symbol='λ_p_cpm']/@value",
            "len_1" : "./Global/Constant[@symbol='len_x']/@value",
            "len_2" : "./Global/Constant[@symbol='len_y']/@value",
            "max_time" : "./Time/StopTime/@value",
            "cpm_nbs_n" : "./CPM/MonteCarloSampler/Neighborhood/Order/@text",
            "cpm_surface_nbs_n" : "./CPM/ShapeSurface/Neighborhood/Order/@text",
            "cpm_temperature" : "./CPM/MonteCarloSampler/MetropolisKinetics/@temperature",
            "cpm_mu" : "./CellTypes/CellType/Constant[@symbol='mu_cpm']/@value",
            "orientation" :  "./CellTypes/CellType/Property[@symbol='α']/@value",
            "orientation_noise" : "./Global/Constant[@symbol='ω']/@value",
            "reenf_rate" : "./CellTypes/CellType/Constant[@symbol='reenf_rate']/@value"
        }
        return params;
    
    def get(self, spec_data: dict) :
        model_xml = ET.parse(os.path.join(self.input_dir, self.model_file()))
         # ET.dump(model_xml)
        
        ## unpack annonymous model args
        if "model_args" in spec_data :
            xtra_args = spec_data["model_args"]
            for i in range(len(xtra_args)) :
                spec_data[f'model_args[{i}]'] = xtra_args[i]
            del spec_data["model_args"]
        
        spec_data.update(self.addon_spec())
        
        x4p = self.xpath4param();
        for p, value in spec_data.items() : 
            if not p in x4p :
                raise ValueError("Unknown paramater " + p + " in mode spec")
            
            [xpath, xattr] = x4p[p].rsplit('/@', maxsplit=1)
            res = model_xml.findall(xpath)
            
            if len(res) == 1 :
                node = model_xml.findall(xpath)[0]
            elif  len(res) >  1 : 
                raise ValueError("XML path " + xpath + " is not unique!")
            else : 
                raise ValueError("XML path " + xpath + " cannot be found!")
                
            if (xattr == 'text') :            
                node.text = str(value)
            else :
                node.set(xattr,str(value))
        
        return model_xml;
    
class morpheus_model_0(morpheus_model) :
    """ morpheus implementation for model 0 random Metropolis noise only """
    
    def __init__(self, input_dir : str) :
        morpheus_model.__init__(self,input_dir)
        # self.source_path = input_dir
        
    def model_file(self):
        return "model_continuous.xml";
    
    def xpath4param(self) :
        base = super().xpath4param()
        return base;
    
    def addon_spec(self) :
        return {
            "cpm_mu" : "0",
            "orientation_noise" : "0",
            "orientation" :  "0",
            "reenf_rate" : "0"
        }

class morpheus_model_5(morpheus_model) :
    """ morpheus implementation for model 5, classical persistent random walk """
    
    def __init__(self, input_dir : str) :
        morpheus_model.__init__(self,input_dir)
        # self.source_path = input_dir
        
    def model_file(self):
        return "model_continuous.xml";
    
    def xpath4param(self) :
        base = super().xpath4param()
        base["model_args[0]"] = base["cpm_mu"]
        base["model_args[1]"] = base["orientation_noise"]
        return base;
    
    def addon_spec(self) :
        return {
            "orientation" :  "0",
            "reenf_rate" : "0"
        }

class morpheus_model_6(morpheus_model) :
    """ morpheus implementation for model 6, classical persistent random walk with self-reenforcement """
    
    def __init__(self, input_dir : str) :
        morpheus_model.__init__(self,input_dir)
        # self.source_path = input_dir
        
    def model_file(self):
        return "model_continuous.xml";
    
    def xpath4param(self) :
        base = super().xpath4param()
        base["model_args[0]"] = base["cpm_mu"]
        base["model_args[1]"] = base["orientation_noise"]
        base["model_args[2]"] = base["reenf_rate"]
        return base;
    
    def addon_spec(self) :
        return {
            "orientation" :  "0"
        }


def from_json_data(spec_data: dict, input_dir='.'):
    model_name = spec_data['model']
    del spec_data['model']
    
    if model_name == 'MODEL000' :
        return morpheus_model_0(input_dir).get(spec_data);
    elif model_name == 'MODEL005' :
        return morpheus_model_5(input_dir).get(spec_data);
    elif model_name == 'MODEL006' :
        return morpheus_model_6(input_dir).get(spec_data);
    else :
        raise "Unknown model " + model_name + " in mode spec";



def from_spec(fp: str):
    with open(fp, 'r') as f:
        spec_data = json.load(f)

    return from_json_data(spec_data)
