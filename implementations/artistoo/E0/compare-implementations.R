library( ggplot2 )
library( dplyr ) 




d1 <- read.csv( "test/pdcmodel003.csv") %>% mutate( implementation = "Artistoo" )

d2 <- read.csv( "test/extension-stnorm.csv") %>% mutate( implementation = "ArtistooPRW-ext-stnorm" )
d3 <- read.csv( "test/extension-stunnorm.csv") %>% mutate( implementation = "ArtistooPRW-ext-stunnorm" )
d4 <- read.csv( "test/extension-com.csv") %>% mutate( implementation = "ArtistooPRW-ext-CMD" )

d5 <- read.csv( "test/retraction-com.csv") %>% mutate( implementation = "ArtistooPRW-ret-CMD" )
d6 <- read.csv( "test/retraction-stunnorm.csv") %>% mutate( implementation = "ArtistooPRW-ret-stunnorm" )
d7 <- read.csv( "test/retraction-stnorm.csv") %>% mutate( implementation = "ArtistooPRW-ret-stnorm" )

d8 <- read.csv( "test/reciprocal-com.csv") %>% mutate( implementation = "ArtistooPRW-both-CMD" )
d9 <- read.csv( "test/reciprocal-stunnorm.csv") %>% mutate( implementation = "ArtistooPRW-both-stunnorm" )
d10 <- read.csv( "test/reciprocal-stnorm.csv") %>% mutate( implementation = "ArtistooPRW-both-stnorm" )

dCC <- read.csv( "test/cc3d.csv" ) %>% mutate( implementation = "CC3D" )
dM <- read.csv( "test/morpheus.csv" ) %>% mutate( implementation = "Morpheus", com_1 = com_1 - min(com_1) + 50 )
dCCsum <- rbind( d1, dM, dCC) %>% 
	filter( time < 1000 ) %>%
	group_by( time, implementation ) %>%
	summarise( x= mean(com_1 ))

dd <- rbind( d2, d3, d4, d5, d6, d7, d8, d9, d10 ) %>% filter( time %% 10 == 0 )

dsum <- dd %>%
	group_by( time, implementation ) %>%
	summarise( x= mean(com_1 ))
	
	
print(dsum)
print( table( dsum$implementation ))
	
p <- ggplot( dsum, aes( x = time, y = x, color = implementation, group = implementation ) ) + 
	geom_line( alpha = .5) + 
	geom_line( data = dCCsum , aes( group = implementation, linetype= implementation),  color = "black" ) + 
	scale_linetype_manual( values = 2:4 ) +
	theme_bw() + theme( panel.grid = element_blank() )

ggsave( "test.pdf" )
