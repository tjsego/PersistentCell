library( celltrackR ) 
library( jsonlite )
library( dplyr, warn.conflicts = FALSE )

# command line input
argv <- commandArgs( trailingOnly = TRUE )
d <- read.csv( argv[1] )
json <- read_json( argv[2] )
outFile <- argv[3]


tr <- as.tracks( d, time.column = 1, id.column = 2, pos.columns = 3:6 )

# correct for the periodic boundary
# Correct tracks when cells move in a torus
correctTorus <- function( tracks, fieldsize, coordinate.cols = 2:3 ){

	# Loop over separate tracks in the tracks object (can be just one)
	for( t in 1:length(tracks) ){

		# Loop over the dimensions x,y(,z) (first column is time, last two columns area/perimeter don't count)
		for( d in coordinate.cols ){
		
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

tr <- correctTorus( tr, fieldsize = c( json$model$len_1, json$model$len_2 ) )

dout <- as.data.frame( tr ) %>%
	setNames( c( "id", "time", "com_1", "com_2", "area", "surface" ) ) %>%
	select( time, id, com_1, com_2, area, surface )



write.csv( dout, file = outFile, quote = FALSE, row.names = FALSE )
