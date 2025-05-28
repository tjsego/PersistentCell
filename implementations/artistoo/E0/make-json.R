library( jsonlite ) 


argv <- commandArgs( trailingOnly = TRUE )

inJSON <- argv[1]
nsim <- as.numeric( argv[2] )
mod.v <- argv[3]
outJSON <- argv[4]

json <- read_json( inJSON )

prng <- ifelse( mod.v == "b" , "MathRandom", "MersenneTwister" )

json$artistoo$output_name = paste0( json$sim$output_name, mod.v, "_artistoo" )
json$sim$num_sims = nsim
json$artistoo$prng = prng

write_json( json, outJSON, pretty = TRUE, auto_unbox=TRUE )