library( ggplot2 )
library( dplyr, warn.conflicts = FALSE )
library( celltrackR )
library( patchwork )
library( jsonlite )


# command line input
argv <- commandArgs( trailingOnly = TRUE )
d <- read.csv( argv[1] )
json <- read_json( argv[2] )
outFile <- argv[3]

# for plotting
plotTheme <- theme_bw() + theme( 
	panel.grid = element_blank(),
	text = element_text( size = 8 )
)


# ======= Read data
tr <- as.tracks( d, time.column = 1, id.column = 2, pos.columns = 3:4 )

# correct for the periodic boundary
# Correct tracks when cells move in a torus
correctTorus <- function( tracks, fieldsize ){

	# Loop over separate tracks in the tracks object (can be just one)
	for( t in 1:length(tracks) ){

		# Loop over the dimensions x,y(,z) (first column is time)
		coordlastcol <- ncol( tracks[[t]] )
		for( d in 2:coordlastcol ){
		
			# do the correction only if the fieldsize in that dimension is not NA
			# (which indicates that there is no torus to be corrected for)
			if( !is.na( fieldsize[d-1] ) ){
			
				# distance traveled in that direction
				dc <- c( 0, diff( tracks[[t]][,d] ) )

				# if absolute distance is more than half the gridsize,
				# the cell has crossed the torus border.
				# if the distance is negative, all subsequent points
				# should be shifted with + fieldsize, if positive,
				# with -fieldsize.
				corr <- 0
				corr[ dc < (-fieldsize[d-1]/2) ] <- fieldsize[d-1]
				corr[ dc > (fieldsize[d-1]/2) ] <- -fieldsize[d-1]
				corr.points <- which( corr != 0 )

				# apply the correction: shift all subsequent points with the
				# correction factor determined above.
				totrows <- nrow( tracks[[t]] )
				for( row in corr.points ){
					tracks[[t]][ (row:totrows), d ] <- tracks[[t]][ (row:totrows), d ] + corr[row]
				}
			
			}
			
		}

	}

	# return corrected tracks
	return( tracks )

}

tr <- correctTorus( tr, fieldsize = c( json$len_1, json$len_2 ) )



# ======= Speed distributions
# cell speed distribution
d1 <- data.frame(
	cellID = 1:length( tr ),
	speed = sapply( tr, speed )
)

pSpeed <- ggplot( d1 ) +
	geom_histogram( aes( x = speed ), bins = 15 ) +
	labs( x = expression( "avg track speed (pixels/MCS)" ) ) +
	plotTheme

d2 <- data.frame(
	speed = sapply( subtracks( tr, 1 ) , speed )
)

pStepSpeed <- ggplot( d2 ) +
	geom_histogram( aes( x = speed ), bins = 15 ) +
	labs( x = expression( "instantaneous speed (pixels/MCS)" ) ) +
	plotTheme



# ======= MSD and autocovariance

# MSD
msd <- aggregate( tr, squareDisplacement, FUN = "mean.se", count.subtracks = TRUE )
msd$dt <- msd$i * timeStep( tr )

fuerthMSD <- function( dt, M, P, dim = 2 ){
	if( P == 0 ){
	 	return( 2*dim*M* dt )
	}
  return( 2*dim*M*( dt - P*(1-exp(-dt/P) ) ) )
}

# Fit this function using nls. We fit only on the data where 
# dt < fitThreshold (see above), and need to provide reasonable starting
# values or the fitting algorithm will not work properly. 
msdFit <- msd %>% filter( dt < 1000 )
model <- nls( log(mean) ~ log( fuerthMSD( dt, exp(logM), exp(logP), dim = 2 ) ), 
              data = msdFit, 
              start = list( logM = log(0.1), logP = log(0.01) ), 
              lower = list( logM = log(0.001), logP = log(0.00001) ), 
              weights = msdFit$ntracks,
              algorithm = "port" 
)
M <- exp( coefficients(model)[["logM"]] ) # this is now in units of pix^2/MCS
P <- exp( coefficients(model)[["logP"]] ) # persistence time in MCS

msdfit <- data.frame(
	dt = seq( 1, 10000 ),
	fit = fuerthMSD( seq(1,10000), M, P, dim = 2 )
)

msd$fit <- fuerthMSD( msd$dt, M, P, dim = 2 )

pMSD <- ggplot( msd, aes( x = dt ) ) + 
	geom_ribbon( aes( ymin = lower, ymax = upper ), color = NA, fill = "black", alpha = 0.1 ) +
	geom_line( data = msdfit, aes( y = fit ), color = "red", lty = 2, linewidth = .4 ) +
	geom_line( aes( y = mean ) , linewidth = .4 ) +
	scale_x_log10( limits=c(1,10000), expand = c(0,0))+
	scale_y_log10( limits=c(0.001,10000), expand = c(0,0))+
	annotate( "text", x = 2, y = 1000, hjust = 0, label = paste0( "fit : M = ", format( M, digits = 3 ), ", P = ", format( P, digits = 3) ),
		color = "red", size = 7 * (5/14) ) +
	#coord_cartesian( xlim=c(0,NA), ylim=c(0,NA), expand=FALSE ) +
	labs( x = expression(Delta*"t (MCS)"), y =  expression("MSD <"*Delta*"x"^2*"> (pixels"^2*")" )) +
	plotTheme


# Autocovariance
acov <- aggregate( tr, overallDot, FUN = "mean.se" )
acov$dt <- (acov$i -1)* timeStep( tr ) 

pAcov <- ggplot( acov, aes( x = dt ) ) + 
	geom_hline( yintercept = 0, linewidth = 0.2 ) +
	geom_ribbon( aes( ymin = lower, ymax = upper ), color = NA, fill = "black", alpha = 0.1 ) +
	geom_line( aes( y = mean ) ) +
	scale_x_continuous( limits = c(0,100) ) +
	scale_y_continuous( limits = c(-1.1 * max(abs(acov$mean)),1.1*max(abs(acov$mean)))) +
	labs( x = expression(Delta*"t (MCS)"), y = "autocovariance" ) +
	plotTheme


p <- pSpeed + pStepSpeed + pMSD + pAcov + plot_layout( ncol = 2 ) + plot_annotation( tag_levels = 'A' )

ggsave( file = outFile, width = 12, height = 10, units = "cm", useDingbats = FALSE )

