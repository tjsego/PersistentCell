library( ggplot2 )
library( dplyr ) 
library( celltrackR )

outFile <- commandArgs( trailingOnly = TRUE ) [1]

modelvec <- c( "model003" ) # , "model006" )
fmvec <- c( "extension", "retraction", "reciprocal" )
udvec <- c("source-to-target-norm", "source-to-target-unnorm", "cell-mass-displacement" )

opt.table <- expand.grid( model = modelvec, forceMode = fmvec, updateDir = udvec ) 

getData2 <- function( fName, model, force.mode, update.dir, simulator ) {
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

getData <- function( fName, model, force.mode, update.dir, simulator ) {
	d <- read.csv( fName )%>% filter( time %% 10 == 0 ) %>% 
		filter( time < 1000 ) %>% 
		group_by( time ) %>%
		summarise( value = mean(com_1 ) ) %>%
	mutate(
		framework = simulator,
		forceMode = force.mode,
		updateDir = update.dir,
		model = model
	)
	return(d)
	
}


all.data.artistoo <- bind_rows( lapply( 1:nrow(opt.table), function(k){
	
	m <- opt.table[k,"model"]
	fm <- opt.table[k,"forceMode"]
	ud <- opt.table[k,"updateDir"]
	
	fName <- paste0( "results/",m, fm, "_", ud, "_artistoo/corrected-tracks.csv" )
	message(fName)
	
	msd <- getData( fName, m, fm, ud, "ArtistooPRW" )
	return(msd)
	
}))

opt.table2 <- opt.table %>% filter( model == "model003" )
all.data.cc3d <- bind_rows( lapply( 1:nrow(opt.table2), function(k){
	
	m <- opt.table2[k,"model"]
	fm <- opt.table2[k,"forceMode"]
	ud <- opt.table2[k,"updateDir"]
	
	fName <- paste0( "cc3d/",m, fm, "_", ud, "_cc3d/results_raw/cc3d/data.csv" )
	message(fName)
	
	msd <- getData( fName, m, fm, ud, "CC3D" )
	return(msd)
	
}))

all.data <- rbind( all.data.artistoo, all.data.cc3d )


dArtistoo <- getData( "data/pdcmodel003.csv", "model003", "extension", "source-to-target-unnorm", "Artistoo" )
dCC <- getData( "data/cc3d.csv", "model003", "extension", "cell-mass-displacement", "CC3D" )
dMorph <- getData( "data/morpheus.csv", "model003", "reciprocal", "cell-mass-displacement", "Morpheus" )

	
	
p <- ggplot( all.data, aes( x = time, y = value, color = forceMode, 
		group = interaction(forceMode, framework), linetype = framework ) ) + 
	geom_line( ) + 
	#geom_line( data = dArtistoo, color = "black", lty = 2) + 
	#geom_line( data = dCC, color = "black", lty = 3) + 
	#geom_line( data = dMorph, color = "black", lty = 4) + 
	facet_grid( forceMode ~ updateDir, scales="free" ) +
	labs( x = expression( Delta*"t (MCS)"), y = 'x' , color = NULL ) + #, y = expression( sqrt(MSD))) +
	theme_bw() + theme( 
		text = element_text( size = 8 ) ,
		panel.grid = element_blank() 
	)



ggsave( outFile, width = 15, height = 10, units = "cm" , useDingbats = FALSE  )


# d1 <- read.csv( "test/pdcmodel003.csv") %>% mutate( implementation = "Artistoo" )
# 
# d2 <- read.csv( "test/extension-stnorm.csv") %>% mutate( implementation = "ArtistooPRW-ext-stnorm" )
# d3 <- read.csv( "test/extension-stunnorm.csv") %>% mutate( implementation = "ArtistooPRW-ext-stunnorm" )
# d4 <- read.csv( "test/extension-com.csv") %>% mutate( implementation = "ArtistooPRW-ext-CMD" )
# 
# d5 <- read.csv( "test/retraction-com.csv") %>% mutate( implementation = "ArtistooPRW-ret-CMD" )
# d6 <- read.csv( "test/retraction-stunnorm.csv") %>% mutate( implementation = "ArtistooPRW-ret-stunnorm" )
# d7 <- read.csv( "test/retraction-stnorm.csv") %>% mutate( implementation = "ArtistooPRW-ret-stnorm" )
# 
# d8 <- read.csv( "test/reciprocal-com.csv") %>% mutate( implementation = "ArtistooPRW-both-CMD" )
# d9 <- read.csv( "test/reciprocal-stunnorm.csv") %>% mutate( implementation = "ArtistooPRW-both-stunnorm" )
# d10 <- read.csv( "test/reciprocal-stnorm.csv") %>% mutate( implementation = "ArtistooPRW-both-stnorm" )
# 
# dCC <- read.csv( "test/cc3d.csv" ) %>% mutate( implementation = "CC3D" )
# dM <- read.csv( "test/morpheus.csv" ) %>% mutate( implementation = "Morpheus", com_1 = com_1 - min(com_1) + 50 )
# dCCsum <- rbind( d1, dM, dCC) %>% 
# 	filter( time < 1000 ) %>%
# 	group_by( time, implementation ) %>%
# 	summarise( x= mean(com_1 ))
# 
# dd <- rbind( d2, d3, d4, d5, d6, d7, d8, d9, d10 ) %>% filter( time %% 10 == 0 )
# 
# dsum <- dd %>%
# 	group_by( time, implementation ) %>%
# 	summarise( x= mean(com_1 ))
# 	
# 	
# print(dsum)
# print( table( dsum$implementation ))
# 	
# p <- ggplot( dsum, aes( x = time, y = x, color = implementation, group = implementation ) ) + 
# 	geom_line( alpha = .5) + 
# 	geom_line( data = dCCsum , aes( group = implementation, linetype= implementation),  color = "black" ) + 
# 	scale_linetype_manual( values = 2:4 ) +
# 	theme_bw() + theme( panel.grid = element_blank() )


