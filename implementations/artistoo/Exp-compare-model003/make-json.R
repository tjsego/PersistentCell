library( jsonlite ) 


argv <- commandArgs( trailingOnly = TRUE )

inJSON <- argv[1]
opts <- unlist( strsplit( argv[2], "_" ) )
outJSON <- argv[3]

force_mode <- opts[1]
update_dir <- opts[2]

json <- read_json( inJSON )

json$model$model_args[[ "cpm_force_mode" ]] = force_mode
json$model$model_args[[ "cpm_update_direction" ]] = update_dir

mod <- paste0(  force_mode, "_", update_dir )
	
json$artistoo$output_name <- paste0( json$sim$output_name, mod )
write_json( json, outJSON, pretty = TRUE, auto_unbox=TRUE )




