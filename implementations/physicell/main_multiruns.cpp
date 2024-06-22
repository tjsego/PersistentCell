/*
###############################################################################
# If you use PhysiCell in your project, please cite PhysiCell and the version #
# number, such as below:                                                      #
#                                                                             #
# We implemented and solved the model using PhysiCell (Version x.y.z) [1].    #
#                                                                             #
# [1] A Ghaffarizadeh, R Heiland, SH Friedman, SM Mumenthaler, and P Macklin, #
#     PhysiCell: an Open Source Physics-Based Cell Simulator for Multicellu-  #
#     lar Systems, PLoS Comput. Biol. 14(2): e1005991, 2018                   #
#     DOI: 10.1371/journal.pcbi.1005991                                       #
#                                                                             #
# See VERSION.txt or call get_PhysiCell_version() to get the current version  #
#     x.y.z. Call display_citations() to get detailed information on all cite-#
#     able software used in your PhysiCell application.                       #
#                                                                             #
# Because PhysiCell extensively uses BioFVM, we suggest you also cite BioFVM  #
#     as below:                                                               #
#                                                                             #
# We implemented and solved the model using PhysiCell (Version x.y.z) [1],    #
# with BioFVM [2] to solve the transport equations.                           #
#                                                                             #
# [1] A Ghaffarizadeh, R Heiland, SH Friedman, SM Mumenthaler, and P Macklin, #
#     PhysiCell: an Open Source Physics-Based Cell Simulator for Multicellu-  #
#     lar Systems, PLoS Comput. Biol. 14(2): e1005991, 2018                   #
#     DOI: 10.1371/journal.pcbi.1005991                                       #
#                                                                             #
# [2] A Ghaffarizadeh, SH Friedman, and P Macklin, BioFVM: an efficient para- #
#     llelized diffusive transport solver for 3-D biological simulations,     #
#     Bioinformatics 32(8): 1256-8, 2016. DOI: 10.1093/bioinformatics/btv730  #
#                                                                             #
###############################################################################
#                                                                             #
# BSD 3-Clause License (see https://opensource.org/licenses/BSD-3-Clause)     #
#                                                                             #
# Copyright (c) 2015-2022, Paul Macklin and the PhysiCell Project             #
# All rights reserved.                                                        #
#                                                                             #
# Redistribution and use in source and binary forms, with or without          #
# modification, are permitted provided that the following conditions are met: #
#                                                                             #
# 1. Redistributions of source code must retain the above copyright notice,   #
# this list of conditions and the following disclaimer.                       #
#                                                                             #
# 2. Redistributions in binary form must reproduce the above copyright        #
# notice, this list of conditions and the following disclaimer in the         #
# documentation and/or other materials provided with the distribution.        #
#                                                                             #
# 3. Neither the name of the copyright holder nor the names of its            #
# contributors may be used to endorse or promote products derived from this   #
# software without specific prior written permission.                         #
#                                                                             #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" #
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE   #
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE  #
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE   #
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR         #
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF        #
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS    #
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN     #
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)     #
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE  #
# POSSIBILITY OF SUCH DAMAGE.                                                 #
#                                                                             #
###############################################################################
*/

#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <ctime>
#include <cmath>
#include <omp.h>
#include <fstream>
#include <sstream>      // std::stringstream
#include <iomanip>
#include <string>


#include "./core/PhysiCell.h"
#include "./modules/PhysiCell_standard_modules.h" 

// put custom code modules here! 

#include "./custom_modules/custom.h" 
	
using namespace BioFVM;
using namespace PhysiCell;

int main( int argc, char* argv[] )
{
	// load and parse settings file(s)
	
	bool XML_status = false; 
	// int run_num = 1; 
	char copy_command [1024]; 
    int num_runs = 2;
	double migration_bias = 0.9; 

    std::cout << "-------- argc= " << argc << std::endl;
    if (argc < 3)
    {
        std::cout << "Usage: " << argv[0] << " <config file>  <num_runs>" << std::endl;
        exit(-1);
    }
	if( argc > 1 )
	{
		XML_status = load_PhysiCell_config_file( argv[1] ); 
		sprintf( copy_command , "cp %s %s" , argv[1] , PhysiCell_settings.folder.c_str() ); 

		num_runs = std::stoi(argv[2]); 
        std::cout << "-------- num_runs= " << num_runs << std::endl;

		migration_bias = std::stof(argv[3]); 
        std::cout << "-------- migration_bias= " << migration_bias << std::endl;
	}
	// else
	// {
	// 	XML_status = load_PhysiCell_config_file( "./config/PhysiCell_settings.xml" );
	// 	sprintf( copy_command , "cp ./config/PhysiCell_settings.xml %s" , PhysiCell_settings.folder.c_str() ); 
	// }

	if( !XML_status )
	{ exit(-1); }
	
	// copy config file to output directry 
	system( copy_command ); 
	
	// OpenMP setup
	omp_set_num_threads(PhysiCell_settings.omp_num_threads);
	
	// time setup 
	std::string time_units = "min"; 

	/* Microenvironment setup */ 
	
	setup_microenvironment(); // modify this in the custom code 
	
	/* PhysiCell setup */ 
 	
	// set mechanics voxel size, and match the data structure to BioFVM
	double mechanics_voxel_size = 30; 
	Cell_Container* cell_container = create_cell_container_for_microenvironment( microenvironment, mechanics_voxel_size );
	
	/* Users typically start modifying here. START USERMODS */ 
	
	create_cell_types_bias(migration_bias);
	
	setup_tissue();

	/* Users typically stop modifying here. END USERMODS */ 
	
	// set MultiCellDS save options 

	set_save_biofvm_mesh_as_matlab( true ); 
	set_save_biofvm_data_as_matlab( true ); 
	set_save_biofvm_cell_data( true ); 
	set_save_biofvm_cell_data_as_custom_matlab( true );
	
	// save a simulation snapshot 
	
	char filename[1024];
	sprintf( filename , "%s/initial" , PhysiCell_settings.folder.c_str() ); 
	save_PhysiCell_to_MultiCellDS_v2( filename , microenvironment , PhysiCell_globals.current_time ); 
	
	// save a quick SVG cross section through z = 0, after setting its 
	// length bar to 200 microns 

	PhysiCell_SVG_options.length_bar = 200; 

	// for simplicity, set a pathology coloring function 
	
	std::vector<std::string> (*cell_coloring_function)(Cell*) = my_coloring_function;
	std::string (*substrate_coloring_function)(double, double, double) = paint_by_density_percentage;

	sprintf( filename , "%s/initial.svg" , PhysiCell_settings.folder.c_str() ); 
	SVG_plot( filename , microenvironment, 0.0 , PhysiCell_globals.current_time, cell_coloring_function, substrate_coloring_function );
	
	sprintf( filename , "%s/legend.svg" , PhysiCell_settings.folder.c_str() ); 
	create_plot_legend( filename , cell_coloring_function ); 
	
	display_citations(); 
	
	// set the performance timers 

	BioFVM::RUNTIME_TIC();
	BioFVM::TIC();
	
	std::ofstream report_file;
	if( PhysiCell_settings.enable_legacy_saves == true )
	{	
		sprintf( filename , "%s/simulation_report.txt" , PhysiCell_settings.folder.c_str() ); 
		
		report_file.open(filename); 	// create the data log file 
		report_file<<"simulated time\tnum cells\tnum division\tnum death\twall time"<<std::endl;
	}
	
    double max_x = parameters.doubles("max_x");
	// main loop 
	
    double next_mech_save_time = PhysiCell::mechanics_dt;
    // double next_mech_save_time = PhysiCell_globals.next_SVG_save_time;
    // double next_mech_save_time = PhysiCell_settings.SVG_save_interval;

    // int run_num = 1;
    // std::stringstream  path_filename;
    // path_filename << "path_" << std::setw(5) << std::setfill('0') << run_num << ".mat";
    // std::ofstream file(path_filename);
    // std::string 
    // outFile << path_filename.rdbuf();
    char path_filename [1024]; 
	// sprintf( path_filename , "path_%03d.mat" , run_num ); 
	sprintf( path_filename , "paths_all.mat"); 
    // int size_of_each_datum = cell_data_size;
	// int number_of_data_entries = (*all_cells).size();  
    // double dTemp; 
    // dTemp = (double) pCell->ID;
    // std::fwrite( &( dTemp ) , sizeof(double) , 1 , fp ); 

    std::vector<double> xvals;
    std::vector<double> yvals;
    // int num_runs = 8;
    // num_runs = 2;
	try 
	{
        int idx_xy = 0;
        for (int irun=0; irun<num_runs; irun++)
        {
            std::cout << "\n\n-------------------------- doing irun= " << irun << std::endl;
	    SeedRandom();  
		PhysiCell_globals.current_time = 0.0;
		PhysiCell_globals.next_full_save_time = PhysiCell_settings.SVG_save_interval;  // from .xml
		PhysiCell_globals.next_SVG_save_time = PhysiCell_settings.SVG_save_interval;  // from .xml

        // ---- Needs to match that below!
        next_mech_save_time = PhysiCell::mechanics_dt;
        // next_mech_save_time = 30.0;
        // next_mech_save_time = PhysiCell_settings.SVG_save_interval;
        (*all_cells)[0]->position[0] = 50.0;
        (*all_cells)[0]->position[1] = 0.0;
            std::cout << "    reset cell pos= " << (*all_cells)[0]->position[0] << ", " << (*all_cells)[0]->position[1] << std::endl;

		while( PhysiCell_globals.current_time < PhysiCell_settings.max_time + 0.1*diffusion_dt )
		{
			// save data if it's time. 
			if( fabs( PhysiCell_globals.current_time - PhysiCell_globals.next_full_save_time ) < 0.01 * diffusion_dt )
			{
				// display_simulation_status( std::cout ); 
				if( PhysiCell_settings.enable_legacy_saves == true )
				{	
					log_output( PhysiCell_globals.current_time , PhysiCell_globals.full_output_index, microenvironment, report_file);
				}
				
				if( PhysiCell_settings.enable_full_saves == true )
				{	
					sprintf( filename , "%s/output%08u" , PhysiCell_settings.folder.c_str(),  PhysiCell_globals.full_output_index ); 
					
					save_PhysiCell_to_MultiCellDS_v2( filename , microenvironment , PhysiCell_globals.current_time ); 
				}
				
				PhysiCell_globals.full_output_index++; 
				PhysiCell_globals.next_full_save_time += PhysiCell_settings.full_save_interval;
			}
			
			// save SVG plot if it's time
			if( fabs( PhysiCell_globals.current_time - PhysiCell_globals.next_SVG_save_time  ) < 0.01 * diffusion_dt )
			{
				if( PhysiCell_settings.enable_SVG_saves == true )
				{	
					sprintf( filename , "%s/snapshot%08u.svg" , PhysiCell_settings.folder.c_str() , PhysiCell_globals.SVG_output_index );
					SVG_plot( filename , microenvironment, 0.0 , PhysiCell_globals.current_time, cell_coloring_function, substrate_coloring_function);

					PhysiCell_globals.SVG_output_index++; 
					PhysiCell_globals.next_SVG_save_time  += PhysiCell_settings.SVG_save_interval;
				}
			}

            // rwh: custom for single cell persistence migration
			if( fabs( PhysiCell_globals.current_time - next_mech_save_time  ) < 0.01 * diffusion_dt )
			{
                // std::cout << "--- x = " << (*all_cells)[0]->position[0] << std::endl;
                next_mech_save_time  += PhysiCell::mechanics_dt;
                // next_mech_save_time  += PhysiCell_settings.SVG_save_interval;
                // next_mech_save_time  += PhysiCell_globals.next_SVG_save_time;
                // std::cout << "main: t="<<PhysiCell_globals.current_time <<" : x= "<< ((*all_cells)[0]->position[0])<<", y= "<<((*all_cells)[0]->position[1]) << std::endl;

                idx_xy++;
                // std::cout << "main: t="<<PhysiCell_globals.current_time <<" : x= "<< ((*all_cells)[0]->position[0])<<", y= "<<((*all_cells)[0]->position[1]) << ", idx_xy= " << idx_xy << std::endl;
                xvals.push_back(((*all_cells)[0]->position[0]));
                yvals.push_back(((*all_cells)[0]->position[1]));
			}

			// update the microenvironment
			// microenvironment.simulate_diffusion_decay( diffusion_dt );  //rwh
			
			// run PhysiCell 
			((Cell_Container *)microenvironment.agent_container)->update_all_cells( PhysiCell_globals.current_time );
			
			/*
			  Custom add-ons could potentially go here. 
			*/
			
			PhysiCell_globals.current_time += diffusion_dt;

            if ((*all_cells)[0]->position[0] > max_x)
            {
                // exit(-1);
                // std::cout << (*all_cells)[0]->position[0] << " > max_x =" <<max_x<< " ; break!!!\n";
                xvals.push_back(-99.0);
                yvals.push_back(-99.0);
                // std::cout << "main -- insert -99s: t="<<PhysiCell_globals.current_time <<" : x= "<< ((*all_cells)[0]->position[0])<<", y= "<<((*all_cells)[0]->position[1]) << ", idx_xy= " << idx_xy << std::endl;

                (*all_cells)[0]->get_container()->last_mechanics_time = 0.0;

                break;
            }
		}
		}

        xvals.push_back(PhysiCell_globals.current_time);
        yvals.push_back(PhysiCell_globals.current_time);
        std::cout << "main.cpp: -------- final time= " << PhysiCell_globals.current_time << std::endl; 

        xvals.push_back(-99.0);
        yvals.push_back(-99.0);

        // ------ rwh ----------
        // int size_of_each_datum = 8;
        int ncols = 2;
        // int number_of_data_entries = xvals.size();  
        int nrows = xvals.size();  
        std::cout << "main.cpp: -------- nrows (for .mat) = " << nrows << std::endl; 
        FILE* fp = write_matlab_header( nrows, ncols,  path_filename, "cell_pos" );  
        if( fp == NULL )
        { 
            std::cout << std::endl << "main.cpp: Error: Failed to open " << filename << " for MAT writing." << std::endl << std::endl; 

            std::cout << std::endl << "Error: We're not writing data like we expect. " << std::endl
            << "Check to make sure your save directory exists. " << std::endl << std::endl
            << "I'm going to exit with a crash code of -1 now until " << std::endl 
            << "you fix your directory. Sorry!" << std::endl << std::endl; 
            exit(-1); 
        } 
        // std::fwrite( (char*)&xvals[0], sizeof(double), xvals.size() , fp ); 
        // std::fwrite( (char*)&yvals[0], sizeof(double), yvals.size() , fp ); 
        // std::fwrite( xvals.data(), sizeof(double), xvals.size() , fp ); 
        // std::fwrite( yvals.data(), sizeof(double), yvals.size() , fp ); 
        std::fwrite( xvals.data(), sizeof(char), 8*xvals.size() , fp ); 
        std::fwrite( yvals.data(), sizeof(char), 8*yvals.size() , fp ); 
        std::fclose(fp); 
		


		if( PhysiCell_settings.enable_legacy_saves == true )
		{			
			log_output(PhysiCell_globals.current_time, PhysiCell_globals.full_output_index, microenvironment, report_file);
			report_file.close();
		}
	}
	catch( const std::exception& e )
	{ // reference to the base of a polymorphic object
		std::cout << e.what(); // information from length_error printed
	}
	
	// save a final simulation snapshot 
	
	sprintf( filename , "%s/final" , PhysiCell_settings.folder.c_str() ); 
	save_PhysiCell_to_MultiCellDS_v2( filename , microenvironment , PhysiCell_globals.current_time ); 
	
	sprintf( filename , "%s/final.svg" , PhysiCell_settings.folder.c_str() );
	SVG_plot(filename, microenvironment, 0.0, PhysiCell_globals.current_time, cell_coloring_function, substrate_coloring_function);

	// timer 
	
	std::cout << std::endl << "Total simulation runtime: " << std::endl; 
	BioFVM::display_stopwatch_value( std::cout , BioFVM::runtime_stopwatch_value() ); 

	return 0; 
}
