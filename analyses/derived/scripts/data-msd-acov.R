library( celltrackR )
library( dplyr, warn.conflicts = FALSE )



argv <- commandArgs( trailingOnly = TRUE )


tracksFile <- argv[1]
outFile <- argv[2]

d <- read.csv( tracksFile )
tr <- as.tracks( d, time.column = 1, id.column = 2, pos.columns= 3:4 )

dd <- bind_rows( lapply( 1:length(tr) , function(i) {
	tt <- tr[i]
	trdt <- timeStep(tt)
	tvec <- timePoints( tt ) 
	sub.lens <- 1:(length(tvec)-1)
	dtt <- bind_rows( lapply( sub.lens, function(k) {
		st <- subtracks( tt, k )
		out <- data.frame(
			steps = k,
			track.id = names(tt),
			sqDisp = sapply( st, squareDisplacement),
			acov = sapply( st, overallDot )
		) %>% mutate(
			subtrack.id = 1:n(),
			dt = steps * trdt
		) %>%
		select( track.id, subtrack.id, dt, sqDisp, acov )
		return(out)
	}))
	return( dtt )
	
}))
	
write.csv( dd, file = outFile, quote = FALSE, row.names = FALSE )