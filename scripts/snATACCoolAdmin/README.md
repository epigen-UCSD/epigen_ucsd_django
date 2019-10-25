## Bash / PBS script to process single-cell ATAC-Seq data from 10x

### Overview
* The scripts assume all the dataset will be processed from `/projects/ps-epigen/outputs/10xATAC`
* The folder containing the script on TSCC is located here: `/home/opoirion/data/ps-epigen_job/LIMS/`
* There are currently 2 scripts:
  1. A script (`10x_model.bash`) to process a single folder from /projects/ps-epigen/outputs/10xATAC
  2. A script (`10x_model_multiple_projects.bash`) to process a single folder from /projects/ps-epigen/outputs/10xATAC

* The script creates an output folder located here `/projects/ps-epigen/datasets/opoirion/output_LIMS/`
* In addition, some part of the data are uploaded in the epigen remote server (plateform 2): `ns104190.ip-147-135-44.us`

### Requirements
* if using TSCC, the conda environment `/home/opoirion/prog/conda_env` should be activated. Otherwise, the requriements of the [snATAC package](https://gitlab.com/Grouumf/snATAC) should be fulfilled
* If using TSCC, the following path: `/home/opoirion/go/local/bin` should be included in the global path. Otherwise, our [GO package](https://gitlab.com/Grouumf/ATACdemultiplex) to process snATAC-Seq file should be installed. 
* Because the script is synchronising with the remote server `s104190.ip-147-135-44.us` under the user name `opoirion`, it is required to add the following SSH key: `ssh-add-key opoirion@ns104190.ip-147-135-44.us`


### Input variables
* The script takes multiple meta variables as input:
```bash
# The version of the pipeline to be used. Currently we recommand to use only 2 versions.
# v4 is the Snap based clustering pipeline and v2 is the density /peak based clustering pipeline
VERSION="v4"
# The reference genome: mm10, hg19, hg38
GENOMETYPE="mm10"
# The name of the output folder
 OUTPUTNAME="MM_147"
# The name of the input folder. Option valid for 10x_model.bash.
 DATASETNAME="MM_147"
 # The names of the input folders. Option valid for 10x_model_multiple_projects.bash.
 DATASETNAMES="MM_147 MM_148"
# To compute or not the global TSS enrichment (slow because using DeepTools)
 COMPUTETSS="True"
```
* Note: Multiple clustering can be launched on the same folder(s) and give different output Folders.

### Additional input variables

* In addition to the required input variables, several additional variables can be provided as input. The mechanism used is to construct an optional argument string `$OPTIONALARGS` that is empty at first. See below for example.

```bash
if [  ! -z "$SNAPBINSIZE" ]
then
    OPTIONALARGS+=" -snap_bin_size ${SNAPBINSIZE} "
fi
```

* The current optional arguments are:

```bash
# Size of the bin used for snap pipeline
SNAPBINSIZE="5000 10000" # List of int
# Use as subsetting strategy to perform snap pipeline
SNAPSUBSETTING=10000 # Int representing the number of cells to use to create the ref map
# List of number of dimensions to perform reduction
SNAPNDIMS="25 50" # List of int
# Number of neighbors to use to perform KNN prior to clustering
SNAPNEIGH="15" # int
```

* In addition, multiple other parameters can / might be taken into consideration and are described into the workflow package:
  * Snap specific parameters: [Snap parameters](https://gitlab.com/Grouumf/snATAC/blob/master/snATAC_pipeline/arg_parser_snap.py)
  * General Processing and clustering parameters [General parameters](https://gitlab.com/Grouumf/snATAC/blob/master/snATAC_pipeline/arg_parser.py)


### Launching the scripts
* It can be launched from bash (for debuging) using for example the command:

```bash
VERSION="v4" GENOMETYPE="mm10" OUTPUTNAME="MM_147" INPUTNAME="MM_147" DATASETNAME="MM_147" bash ~/data/ps-epigen_job/LIMS/10x_model.bash
```
or with qsub using the command

```bash
qsub
 -v VERSION="v4",GENOMETYPE="mm10",OUTPUTNAME="MM_147",INPUTNAME="MM_147",DATASETNAME="MM_147"  ~/data/ps-epigen_job/LIMS/10x_model.bash
```

### Output logs
* The output folder path is `/projects/ps-epigen/datasets/opoirion/output_LIMS/`

* The output final logs can be found in a json file from the output folder:

```bash
cat  /projects/ps-epigen/datasets/opoirion/output_LIMS/MM_147/repl1//repl1_MM_147_final_logs.json
```

```json
{
  "logs_file": "/projects/ps-epigen/datasets/opoirion/output_LIMS/MM_147/repl1//repl1_MM_147_pipeline.log",
  "parameters": "/projects/ps-epigen/datasets/opoirion/output_LIMS/MM_147/repl1//pipeline_params.log",
  "report_address": "http://ns104190.ip-147-135-44.us:8088/dataset_report?dataset_name=MM_147&output_folder_name=output_LIMS&token=4bd4a5eea3609cab5994eda21ae4f7b5",
  "statistics": "/projects/ps-epigen/datasets/opoirion/output_LIMS/MM_147/repl1//repl1_MM_147_project_statistics.json",
  "success": true
}
```

### Data synchronisation
* Per default, the script synchronizes some part (ignoring large files) of the output folder to the remote server of plateform 2: ns104190.ip-147-135-44.us (See option `-path_to_remote_server "opoirion@ns104190.ip-147-135-44.us:data/data_ALL/output_LIMS" \` in the script)

* The data are synchronized in the global path: `/home/opoirion/data/data_ALL/output_LIMS`
* These synchronized datasets are needed to visualize the single-cell ATAC-Seq report using our CoolAdmin portal.
* In case the portal is shut down, it can be relaunched using the script located in `/home/opoirion/code`

```bash
bash /home/opoirion/code/launch_local_coolAdmin_ALL.bash
```

* This current instance of the CoolAdmin portal uses the port 8088 to communcate qith the server, which corresponds to the port used by the report address:

```json
"report_address": "http://ns104190.ip-147-135-44.us:8088/dataset_report?dataset_name=MM_147&output_folder_name=output_LIMS&token=4bd4a5eea3609cab5994eda21ae4f7b5"
```

* Finally, in order to be able to download the larger files that are not synchronised to ns104190.ip-147-135-44.us, a third server needs to be launched on the local virtual machine of the center (that can access the dataset): epigenomics.ucsd.edu.
* In case the portal is shut down, it can be relaunched using the script located in `/home/opoirion/code`

```bash
bash /home/opoirion/code/launch_local_ALL_coolAdmin.bash
```
