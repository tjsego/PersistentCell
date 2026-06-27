library( ggplot2 )
library( dplyr ) 
library( celltrackR )

outFile <- commandArgs( trailingOnly = TRUE ) [1]

modelvec <- c( "model003" ,"model005" , "model006" )
fmvec <- c( "extension", "retraction", "reciprocal" )
udvec <- c("source-to-target-norm", "source-to-target-unnorm", "cell-mass-displacement" )

opt.table <- expand.grid( model = modelvec, forceMode = fmvec, updateDir = udvec )  

getData <- function( fName, model, force.mode, update.dir, simulator ) {
	d <- read.csv( fName )%>% filter( time %% 10 == 0 ) %>% filter( time < 1000 )
	tr <- as.tracks( d, time.column = 1, id.column = 2, pos.columns = 3:4 )
	msd <- aggregate( tr, squareDisplacement, na.rm=TRUE ) %>% 
	mutate(
		dt = i*timeStep( tr ),
		framework = simulator,
		forceMode = force.mode,
		updateDir = update.dir,
		model = model
	)
	return(msd)
	
}

all.data <- bind_rows( lapply( 1:nrow(opt.table), function(k){
	
	m <- opt.table[k,"model"]
	fm <- opt.table[k,"forceMode"]
	ud <- opt.table[k,"updateDir"]
	
	fName <- paste0( "results/",m, fm, "_", ud, "/corrected-tracks.csv" )
	message(fName)
	
	msd <- getData( fName, m, fm, ud, "ArtistooPRW" )
	return(msd)
	
}))


p <- ggplot( all.data, aes( x = dt, y = value, color = forceMode, 
		group = interaction(forceMode, framework), linetype = framework ) ) + 
	geom_line( ) + 
	facet_grid( model ~ updateDir ) +
	labs( x = expression( Delta*"t (MCS)"), y = 'MSD' , color = NULL ) + 
	scale_x_log10() +
	scale_y_log10() +
	theme_bw() + theme( 
		text = element_text( size = 8 ) ,
		panel.grid = element_blank() 
	)



ggsave( outFile, width = 15, height = 10, units = "cm" , useDingbats = FALSE  )

