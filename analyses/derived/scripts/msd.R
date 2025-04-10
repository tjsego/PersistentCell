library( celltrackR )
library( ggplot2 )
library( dplyr, warn.conflicts = FALSE )



argv <- commandArgs( trailingOnly = TRUE )


dataFile <- argv[1]
outPlot <- argv[2]

plotTheme <- theme_bw() + theme( 
	panel.grid = element_blank(),
	text = element_text( size = 8 )
)

all.data <- readRDS( dataFile )


msdData <- bind_rows( lapply( names( all.data ), function(dset){
	
	tr <- all.data[[dset]]
	msd <- aggregate( tr, squareDisplacement, FUN = "mean.se" )
	msd$model <- dset 
	msd$dt <- msd$i * timeStep( tr )
	
	return(msd)
	
} ) )


p <- ggplot( msdData, aes( x = dt, y = mean, color = model, fill = model ) ) +
	geom_ribbon( aes( ymin = lower, ymax = upper ), color = NA, alpha = 0.1 ) +
	geom_line( , linewidth = .4 ) +
	scale_x_log10( limits=c(1,10000), expand = c(0,0))+
	scale_y_log10( limits=c(0.001,10000), expand = c(0,0))+
	labs( x = expression(Delta*"t (min)"), y =  expression("MSD <"*Delta*"x"^2*"> (um"^2*")" )) +
	plotTheme


ggsave( outPlot, width = 10, height = 5, units = "cm" )