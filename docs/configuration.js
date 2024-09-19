
let configJSON = {
	"cpm_temperature" : 0.4 ,
	"cpm_area_v" : 0.016,
	"cpm_area_c" : 79,
	"cpm_nbs_n" : 2,
	"cpm_perim_v" : 0.0222,
	"cpm_perim_c" : 94,
	"len_1" : 100,
	"len_2" : 100,
	"max_time" : 4000,
	"method" : "CPM",
	"model_args" : {
		"MODEL000" : {
			"lambda_dir" : 0.0000000000000000000001,
			"persist" : 0,
			"dt" : 10
		},
		"MODEL003" : {
			"lambda_dir" : 1,
			"target_angle" : 0
		},
		"MODEL005" : {
			"persist" : 0.13862943611198905,
			"lambda_dir" : 0.4,
			"dt" : 10
		}
	}
}
