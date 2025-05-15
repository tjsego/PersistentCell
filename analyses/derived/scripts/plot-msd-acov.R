library( ggplot2 ) 
library( dplyr, warn.conflict = FALSE ) 
library( patchwork )

argv <- commandArgs( trailingOnly = TRUE )

d <- read.csv( argv[1] )

dsum <- d %>%
	group_by( dt_MCS ) %>%
	summarise( acor = mean(acor), msd = mean(msd))

mytheme <- theme_bw() + 
	theme(
		panel.grid = element_blank(),
		text = element_text( size = 10 ),
		plot.title = element_text( size = 10)
	)

p1 <- ggplot( d, aes( x = dt_MCS, y = acor ) ) +
	geom_hline( yintercept = 0, linewidth = .2 ) +
	geom_line( aes( group = id ), alpha = .1, color = "gray60", linewidth = .2 ) +
	geom_line( data = dsum, color = "dodgerblue2" ) +
	labs(
		x = expression( Delta *"t (MCS)"),
		y = expression( symbol("\xe1")~"cos ("*phi["t+"*Delta*"t"]-phi["t"]*")"~symbol("\xf1")  ),
		title = "directional autocorrelation (DAC)"
	) +
	scale_x_continuous( expand=c(0,0)) +
	scale_y_continuous( limits = c(-1,1) ,expand = c(0,0))+
	mytheme
	
p2 <- ggplot( d, aes( x = dt_MCS, y = msd ) ) +
	geom_line( aes( group = id ), alpha = .1, color = "gray60" ) +
	geom_line( data = dsum, color = "dodgerblue2" ) +
	labs(
		x = expression( Delta *"t (MCS)"),
		y = expression( symbol("\xe1")*Delta*"x"^2~symbol("\xf1")*" (pix"^2*" / MCS)"  ),
		title = "mean squared displacement (MSD)"
	) +
	scale_x_continuous( expand=c(0,0)) +
	scale_y_continuous( limits=c(0,NA),expand = c(0,0))+
	mytheme
	
p <- p1 + p2 + plot_layout( ncol = 1 )
	
ggsave( argv[2] , width = 10, height = 12, units="cm")