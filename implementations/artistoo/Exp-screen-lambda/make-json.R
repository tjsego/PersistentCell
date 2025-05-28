library( jsonlite ) 


argv <- commandArgs( trailingOnly = TRUE )

inJSON <- argv[1]
lambda_range <- as.numeric( unlist( strsplit( argv[2], " " ) ) )
outJSON <- argv[3]

lambdas <- seq( lambda_range[1], lambda_range[2], by = lambda_range[3] )

json <- read_json( inJSON )


json$model$model_args[[ "lambda_dir_values" ]] = lambdas
json$sim$output_name = paste0( json$sim$output_name, "a" )
json$model$max_time = 1000
json$sim$output_per = 20

print(json$model$model_args )

write_json( json, outJSON, pretty = TRUE, auto_unbox=TRUE )