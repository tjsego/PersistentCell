Simulation specification schema
==

| Key           | Type     | Description                                                                                                                                        |
|---------------|----------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| buffer        | number   | Minimum distance between cell centroid and spatial domain boundary. Simulation stops when this criterion is no longer satisfied.                   |
| cpm_area_c    | number   | Cellular Potts model area constraint coefficient; required for CPM methods. A cell is initialized with this area.                                  | 
| cpm_area_v    | number   | Cellular Potts model area constraint value; required for CPM methods.                                                                              |
| cpm_contact_c | number   | Cellular Potts model contact energy cell-medium coefficient; required for CPM methods.                                                             |
| cpm_contact_n | number   | Cellular Potts model contact energy neighborhood order; required for CPM methods.                                                                  |
| len_1         | number   | Spatial domain length along the first spatial dimension. A cell is initialized with a centroid halfway along this length in the first dimension.   |
| len_2         | number   | Spatial domain length along the second spatial dimension. A cell is initialized with a centroid halfway along this length in the second dimension. |
| max_time      | number   | Maximum simulation time.                                                                                                                           |
| method        | string   | Methodology label; one of those defined in supported methods.                                                                                      |
| model         | string   | Persistent random walk model label; one of those defined in supported models.                                                                      |
| model_args    | array    | Persistent random walk model parameters; empty if none required.                                                                                   |