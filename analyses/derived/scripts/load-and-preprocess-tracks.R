library( celltrackR )
library( jsonlite )


argv <- commandArgs( trailingOnly = TRUE )


comparisonFile <- argv[1]
outFile <- argv[2]

settings <- read_json( comparisonFile )$data


# Correct tracks when cells move in a torus
correctBoundary <- function( tracks, fieldsize ){

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

readTracks <- function( json ){
	
	d <- read.csv( json$file )
	nm <- json$name

	tr <- as.tracks( d, time.column = json$timeColumn, id.column = json$idColumn, 
		pos.columns = c( json$xColumn, json$yColumn ), scale.time = (json$secondsPerSimulationStep/60), 
		scale.pos = json$micronsPerLengthUnit )
		
	tr <- filterTracks( function(t) nrow(t) > 1, tr )
	
	if( json$periodic ){
		tr <- correctBoundary( tr, fieldsize = c( json$fieldSize[[1]], json$fieldSize[[2]] ) )
	}
	
	return(tr)
}


output <- lapply( settings, readTracks )
names(output) <- sapply( settings, function(x) x$name )


saveRDS( output, outFile )