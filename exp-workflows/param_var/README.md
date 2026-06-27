Parameter Variation Experiment Workflow
==

This module performs an experiment testing what variations in a parameter can be detected. 

Execution
===

Execution of the workflow is staged into Build, Generation, and Execution stages. 
Execution targets a project directory that initially contains a directory `test` with the 
typical workflow structure, and a JSON specification `param-var.json` of the variations to perform. 
Contents of the JSON specification are a dictionary with the following key-value pairs:

* `path`: Colon-separated path to the varied parameter w.r.t. to the `"model"` input specification (*e.g.*, `"model_args:dt"`)
* `values`: Parameter values to generate (*e.g.*, [1, 10, 100])

Build Stage
====

In the Build stage, simulation projects are generated from the test input specification and 
a given set of variations in a parameter. The Build stage will create a directory `generators` 
next to the `test` directory containing an executable project per given parameter variation. 
The Build stage is executed by running `build-exp.bat` on Windows and `build-exp.sh` on Unix. 
Command line arguments are as follows:

* `-d` / `--dir`: Root directory of experiment

Generation Stage
====

In the Generation stage, the generated parameter variations are executed by an implementation in the 
typical way. After this stage is completed, results are loaded into the test directory by running 
`load-variations.bat` on Windows and `load-variations.sh` on Unix. 
Command line arguments are as follows:

* `-d` / `--dir`: Root directory of the experiment
* `-p` / `--prefix`: Option prefix to prepend to results directories when loading into the test directory.

Execution Stage
====

After the Generation stage, the test directory can be executed as a workflow in the typical way. 
Any results in the test subdirectory `raw_results` will be compared to each parameter variation. 

Post-Processing
===

Data and figures can be generated after the Execution stage. 

Generated data is placed in a directory `post/data` next to the test directory. 
Generated data is as follows:

* `comparison_appended.csv`: EFECT Error and rejection p-value of derived results per combination of variation and non-variation results.
* `comparison_raw.csv`: EFECT Error and rejection p-value of raw results per combination of variation and non-variation results.
* `summary_appended.csv`: Summary of discovered variation and non-variation derived results and their labeling during post-processing.
* `summary_raw.csv`: Summary of discovered variation and non-variation derived results and their labeling during post-processing.

Generated figures are placed in a directory `post/figures` next to the test directory. 
Generated figures are as follows:

* `comparison_appended_efect.png`: EFECT Errors for derived results.
* `comparison_appended_pvals.png`: Rejection p-values for derived results.
* `comparison_raw_efect.png`: EFECT Errors for raw data.
* `comparison_raw_pvals.png`: Rejection p-values for raw data.

Post-processing can be executed by running `post.bat` on Windows and `post.sh` on Unix. 
Command line arguments are as follows:

* `-d` / `--dir`: Root directory of the experiment.
* `-c` / `--control`: Name of results from the implementation that produced the variation results. 
* `-n` / `--normalize`: Optional flag to normalize parameter values by the control value.
