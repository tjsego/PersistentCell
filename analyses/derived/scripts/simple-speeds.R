library( celltrackR )
library( dplyr, warn.conflicts = FALSE )
library( ggplot2 )
library( ggbeeswarm )
library( patchwork )



argv <- commandArgs( trailingOnly = TRUE )


dataFile <- argv[1]
outPlot <- argv[2]

plotTheme <- theme_bw() + theme( 
	panel.grid = element_blank(),
	text = element_text( size = 8 )
)

all.data <- readRDS( dataFile )


speedData <- bind_rows( lapply( names( all.data ), function(dset){
	
	tr <- all.data[[dset]]
	dspeed <- data.frame(
		id = names(tr),
		speed = sapply( tr, speed ),
		model = dset
	)
	return(dspeed)
	
} ) )

instSpeedData <- bind_rows( lapply( names( all.data ), function(dset){
	
	tr <- all.data[[dset]]
	steps <- subtracks( tr, 1 )
	dspeed <- data.frame(
		speed = sapply( steps, speed ),
		model = dset
	)
	return(dspeed)
	
} ) )

p1 <- ggplot( speedData, aes( x = model, y = speed, color = model ) ) +
	geom_quasirandom( size = .3, show.legend=FALSE ) +
	labs( x = NULL, y = expression( "avg cell speed ("*mu*"m/min)" ) ) +
	plotTheme
	
p2 <- ggplot( instSpeedData, aes( x = model, y = speed, fill = model ) ) +
	geom_violin( color = NA, alpha = .5, show.legend=FALSE ) +
	scale_y_continuous( limits=c(0,NA)) +
	labs( x = NULL, y = expression( "inst. speed ("*mu*"m/min)" ) ) +
	plotTheme

p <- p1 + p2 

ggsave( outPlot, width = 10, height = 4, units = "cm" )