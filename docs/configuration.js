
let configJSON = {
	 "cpm_temperature": 10,
        "cpm_area_c": 36,
        "cpm_area_v": 2.0,
        "cpm_perim_c": 60.0,
        "cpm_perim_v": 2.0,
        "len_1": 100,
        "len_2": 100,
        "cpm_nbs_n": 2,
        "cpm_surface_nbs_n": 2,
        "max_time": 10000,
		"method" : "CPM",
		"model_args" : {
			"MODEL000" : {
				"lambda_dir" : 0.000000000001,
				"persist" : 0,
				"dt" : 50
			},
			"MODEL003" : {
				 "lambda_dir": 10.0,
           		 "target_angle": 0.0
			},
			"MODEL005" : {
				"persist" : 0,
				"lambda_dir" : 20,
				"dt" : 50
			},
			"MODEL006" : {
				"mu" : 5,
				"xi" : 0.2,
				"retract_force" : true,
				"protrude_force" : true
			}
		}
}
