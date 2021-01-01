# uncertain_obs
Diagnose a system with an uncertainty in the observations.

There are 2 flows - one for the Circuit domain and one for the Software domain.

## Circuit
Execute main.py inside the circuits folder. This will read the models from input\Data_iscas85 folder.
The model names to diagnose are specified in the system_names variable inside main.py.
The script will run all algorithms on these models and provide csv outputs in output/results/{model}_{date}.csv file.

## Software
The Sofware domain algorithms can be run on real matrix file or synthetic ones.
You can change the configuarion in main.py inside the software folder -

### Real matrices
Assign *name* to "real"

### Synthetic matrices
To generate the matrices, run matrix_generator.py inside software/utils folder. Specify the range of number of components, tests and samples.
The generated matrices will be created in software/matrices/synthetic folder.

There are 2 types of execution flows for the synthetic matrices - regular Barinel or Fast Barinel (AKA incremental-MHS).
To run regular Barinel, assign *name* to "synthetic".
To run Fast Barinel, assign *name* to "smart_mhs".
