Simulation specification schema
==

| Key         | Type     | Description                                                                                                                                        |
|-------------|----------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| cpm_area_c  | number   | Cellular Potts model area constraint coefficient; required for CPM methods. A cell is initialized with this area.                                  | 
| cpm_area_v  | number   | Cellular Potts model area constraint value; required for CPM methods.                                                                              |
| cpm_nbs_n   | number   | Cellular Potts model copy attempt neighbor order; required for CPM methods.                                                                        |
| cpm_surface_nbs_n | number | Cellular Potts model surface length estimation neighbor order; required for CPM methods for contact energy and perimeter estimation.
|
| cpm_temperature |  number | Cellular Potts model temperature of Metropolis kinetics.
|
| cpm_perim_c | number   | Cellular Potts model perimeter constraint coefficient; required for CPM methods.                                                                   |
| cpm_perim_v | number   | Cellular Potts model perimeter constraint value; required for CPM methods.                                                                         |
| len_1       | number   | Spatial domain length along the first spatial dimension. A cell is initialized with a centroid halfway along this length in the first dimension.   |
| len_2       | number   | Spatial domain length along the second spatial dimension. A cell is initialized with a centroid halfway along this length in the second dimension. |
| max_time    | number   | Maximum simulation time.                                                                                                                           |
| method      | string   | Methodology label; one of those defined in supported methods.                                                                                      |
| model       | string   | Persistent random walk model label; one of those defined in supported models.                                                                      |
| model_args  | array    | Persistent random walk model parameters; empty if none required.                                                                                   |
