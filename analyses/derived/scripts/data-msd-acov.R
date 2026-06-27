library( celltrackR )
library( dplyr, warn.conflicts = FALSE )



argv <- commandArgs( trailingOnly = TRUE )


tracksFile <- argv[1]
outFile <- argv[2]

d <- read.csv( tracksFile )
tr <- as.tracks( d, time.column = 1, id.column = 2, pos.columns= 3:4 )

dd <- bind_rows( lapply( 1:length(tr) , function(i) {
	tt <- tr[i]

	if( timeStep(tt) < 5 ){
		k <- round( 5 / timeStep(tt) )
		tt <- subsample(tt,k)
	}
	
	msd <- aggregate( tt, squareDisplacement, count.subtracks = TRUE )
	angle <- aggregate( tt, overallAngle, count.subtracks = TRUE, na.rm = TRUE ) 
	
	out <- data.frame( 
		dt_nsteps = msd$i,
		dt_MCS = msd$i * timeStep( tt ),
		id = i,
		nsubtracks = msd$ntracks,
		msd = msd$value,
		acor = cos( angle$value ) 
	)
	
	return(out)
	
}))
	
write.csv( dd, file = outFile, quote = FALSE, row.names = FALSE )