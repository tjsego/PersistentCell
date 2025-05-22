library( ggplot2 )
library( dplyr, warn.conflict = FALSE ) 
library( celltrackR ) 


argv <- commandArgs( trailingOnly = TRUE ) 

inFile003 <- argv[1]
inFile005 <- argv[2]
inFile006 <- argv[3]
outFile <- argv[4]


getSpeeds <- function( fName, modelName ){
	d <- read.csv( fName ) 
		
	lambdas <- sapply( unique( d$id), function(x) as.numeric( unlist( strsplit( x, "-"))[1] ) )
	tr <- as.tracks( d, time.column = 1, id.column = 2, pos.columns = 3:4 ) 
	speeds <- sapply( tr, speed )

	out_df <- data.frame(
		id = names(speeds),
		speed = unname( speeds )
	) %>%
		mutate( lambda = lambdas[id], model = modelName )

	return( out_df ) 

}

d1 <- getSpeeds( inFile003, "model003" )
d2 <- getSpeeds( inFile005, "model005" )
d3 <- getSpeeds( inFile006, "model006" )

dd <-rbind( d1, d2, d3 )

	
	
sum_df <- dd %>%
	group_by( model, lambda ) %>%
	summarise( 
		lo = quantile( speed, 0.25 ), 
		hi = quantile( speed, 0.75 ),
		speed = mean(speed) )
	
p <- ggplot( sum_df, aes( x = lambda, y = speed, group = model, color = model, fill= model ) ) +
	geom_ribbon( aes( ymin = lo, ymax = hi ), color = NA, alpha = .2, show.legend=FALSE ) +
	geom_line() +
	labs( x = expression( lambda["dir"]), y = "speed (pix/MCS)", color = NULL, fill = NULL ) +
	scale_y_continuous( limits=c(0,NA))+
	theme_bw() + 
	theme( 
		panel.grid = element_blank(),
		legend.position = c(1,0),
		legend.justification = c(1,0),
		legend.background = element_blank()
	 )
	
ggsave( outFile, width = 10, height = 6, units = "cm", useDingbats = FALSE )