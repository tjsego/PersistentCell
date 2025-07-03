import json
from math import sqrt
import xml.etree.ElementTree as ET
import os



class morpheus_model:
    """ Template for any morpheus model """
      
    def xpath4param(self):
        params = {
            "cpm_area_c" : "./Global/Constant[@symbol='a_cpm']/@value",
            "cpm_area_v" : "./CellTypes/CellType/Constant[@symbol='λ_a_cpm']/@value",
            "cpm_perim_c" : "./CellTypes/CellType/Constant[@symbol='p_cpm']/@value",
            "cpm_perim_v" : "./CellTypes/CellType/Constant[@symbol='λ_p_cpm']/@value",
            "len_1" : "./Global/Constant[@symbol='len_x']/@value",
            "len_2" : "./Global/Constant[@symbol='len_y']/@value",
            "max_time" : "./Time/StopTime/@value",
            "cpm_nbs_n" : "./CPM/MonteCarloSampler/Neighborhood/Order/@text",
            "cpm_surface_nbs_n" : "./CPM/ShapeSurface/Neighborhood/Order/@text",
            "cpm_temperature" : "./CPM/MonteCarloSampler/MetropolisKinetics/@temperature",
            "lambda_dir" : "./CellTypes/CellType/Constant[@symbol='mu_cpm']/@value",
            "seed" : "./Time/RandomSeed/@value",
            "log_freq" : "./Global/Constant[@symbol='log_freq']/@value",
            "init_voxels" : "./CellPopulations/Population[@type='cell']/Cell/Nodes/@text"           
        }
        
        return params;
    
    def get(self, spec_data: dict) :
        # alternatively, this file's path might be used : os.path.dirname(os.path.realpath(__file__))
        model_xml = ET.parse(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.model_file()))
         # ET.dump(model_xml)
        
        ## flatten additional model args
        if "model_args" in spec_data :
            xtra_args = spec_data["model_args"]
            for k,v in xtra_args.items() :            
                print(k,v)
                spec_data[k] = v
            del spec_data["model_args"]
        
        ## unpack the cpm_force_mode
        if "cpm_force_mode" in spec_data :
            switch  = {
                "extension" : [True,False],
                "retraction" : [False, True],
                "reciprocal" : [True, True]
            }
            spec_data["cpm_force_extension"], spec_data["cpm_force_retraction"] = switch[spec_data["cpm_force_mode"]]
            del spec_data["cpm_force_mode"]
            
        if "chemo_source_position" in spec_data :
            x,y = spec_data["chemo_source_position"]
            spec_data["chemo_source_position"] = " %d, %d, 0" %  (x,y)
            
        
        spec_data.update(self.addon_spec())
        
        x4p = self.xpath4param();
        for p, value in spec_data.items() : 
            if p == "method":
                continue                
                
            if not p in x4p :
                raise ValueError("Unknown paramater " + p + " in model spec")
            
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
        
    def model_file(self):
        return "model_continuous.xml";
    
    def xpath4param(self) :
        base = super().xpath4param()
        return base;
    
    def addon_spec(self) :
        return {
            "lambda_dir" : "0",
        }

class morpheus_model_3(morpheus_model) :
    """ morpheus implementation for model 3, classical ballistic walk """
        
    def model_file(self):
        return "model_continuous.xml";
    
    def xpath4param(self) :
        base = super().xpath4param()
        base["target_angle"] = "./CellTypes/CellType/Property[@symbol='α']/@value"
        base["xi"] = "./Global/Constant[@symbol='xi']/@value"
        base["cpm_force_extension"] = "./CellTypes/CellType/DirectedMotion/@extension"
        base["cpm_force_retraction"] = "./CellTypes/CellType/DirectedMotion/@retraction"
        base["cpm_update_direction"] = "./CellTypes/CellType/DirectedMotion/@update-direction"

        return base;
    
    def addon_spec(self) :
        return {
            "xi" : "0"
        }
    
class morpheus_model_5(morpheus_model) :
    """ morpheus implementation for model 6, classical persistent random walk """
        
    def model_file(self):
        return "model_persist.xml";
    
    def xpath4param(self) :
        base = super().xpath4param()
        base["persist"] = "./CellTypes/CellType/Constant[@symbol='cpm_persist_rate']/@value"
        base["initial_alpha"] = "./CellTypes/CellType/Property[@symbol='α']/@value"
        base["dt"] = "./CellTypes/CellType/PersistentMotion/@observation-window"
        base["mu"] = base["lambda_dir"]
        base["cpm_force_extension"] = "./CellTypes/CellType/PersistentMotion/@extension"
        base["cpm_force_retraction"] = "./CellTypes/CellType/PersistentMotion/@retraction"
        base["cpm_update_direction"] = "./CellTypes/CellType/PersistentMotion/@update-direction"
        return base;
    
    def addon_spec(self) :
        return {}

class morpheus_model_6(morpheus_model) :
    """ morpheus implementation for model 6, classical persistent random walk """
        
    def model_file(self):
        return "model_continuous.xml";
    
    def xpath4param(self) :
        base = super().xpath4param()
        base["initial_alpha"] = "./CellTypes/CellType/Property[@symbol='α']/@value"
        base["xi"] = "./Global/Constant[@symbol='xi']/@value"
        base["reenf_rate"] = "./Global/Constant[@symbol='reenf_rate']/@value"
        base["cpm_force_extension"] = "./CellTypes/CellType/DirectedMotion/@extension"
        base["cpm_force_retraction"] = "./CellTypes/CellType/DirectedMotion/@retraction"
        base["cpm_update_direction"] = "./CellTypes/CellType/DirectedMotion/@update-direction"
        
        return base;
    
    def addon_spec(self) :   
        return {
            "reenf_rate" : "0"
        }

class morpheus_model_7(morpheus_model) :
    """ morpheus implementation for model 7, classical persistent random walk with self-reenforcement """
        
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

class morpheus_model_8(morpheus_model) :
    """ morpheus implementation for model 7, classical persistent random walk with self-reenforcement """
        
    def model_file(self):
        return "model_chemotax.xml";
    
    def xpath4param(self) :
        base = super().xpath4param()
        base["lambda_chem"] = base["lambda_dir"]
        base["chemo_source_position"] = "Global/ConstantVector/@value"
        base["chemo_production_rate_per_mcs"] = "Global/System/Constant[@symbol='k_prod']/@value"
        base["chemo_decay_rate_per_mcs"] = "Global/System/Constant[@symbol='k_decay']/@value"
        base["cpm_force_extension"] = "./CellTypes/CellType/Chemotaxis/@extension"
        base["cpm_force_retraction"] = "./CellTypes/CellType/Chemotaxis/@retraction"
        base["diffusion_coefficient_per_mcs"] = "Global/Constant[@symbol='D']/@value"
        base["diffusion_steps_per_mcs"] = "Global/Constant[@symbol='D_steps']/@value"
        return base;
    
    def addon_spec(self) :
        return {}
    

def from_json_data(spec_data: dict):
    model_name = spec_data['model']
    del spec_data['model']
    
    if model_name == 'MODEL000' :
        return morpheus_model_0().get(spec_data);
    elif model_name == 'MODEL003' :
        return morpheus_model_3().get(spec_data);
    elif model_name == 'MODEL005' :
        return morpheus_model_5().get(spec_data);
    elif model_name == 'MODEL006' :
        return morpheus_model_6().get(spec_data);
    elif model_name == 'MODEL007' :
        return morpheus_model_7().get(spec_data);
    elif model_name == 'MODEL008' :
        return morpheus_model_8().get(spec_data);
    else :
        raise "Unknown model " + model_name + " in mode spec";



def from_spec(fp: str):
    with open(fp, 'r') as f:
        spec_data = json.load(f)

    return from_json_data(spec_data)
