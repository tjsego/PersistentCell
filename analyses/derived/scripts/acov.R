library( celltrackR )
library( ggplot2 )
library( dplyr, warn.conflicts = FALSE )



argv <- commandArgs( trailingOnly = TRUE )


dataFile <- argv[1]
maxdt <- as.numeric( argv[2] )
outPlot <- argv[3]


plotTheme <- theme_bw() + theme( 
	panel.grid = element_blank(),
	text = element_text( size = 8 )
)

all.data <- readRDS( dataFile )


acovData <- bind_rows( lapply( names( all.data ), function(dset){
	
	tr <- all.data[[dset]]
	max.steps <- round( maxdt/timeStep(tr))
	acov <- aggregate( tr, overallDot, subtrack.length = seq(1,max.steps), FUN = "mean.se" )
	acov$model <- dset 
	acov$dt <- acov$i * timeStep( tr )
	
	return(acov)
	
} ) )


p <- ggplot( acovData, aes( x = dt, y = mean, color = model, fill = model ) ) +
	geom_hline( yintercept = 0, linewidth = 0.2 ) +
	geom_ribbon( aes( ymin = lower, ymax = upper ), color = NA, alpha = 0.1 ) +
	geom_line( linewidth = .4 ) +
	scale_x_continuous( limits=c(0,NA), expand = c(0,0))+
	labs( x = expression(Delta*"t (min)"), y =  "directional\nautocovariance" ) +
	plotTheme


ggsave( outPlot, width = 10, height = 5, units = "cm" )