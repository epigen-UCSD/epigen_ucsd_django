#PBS -q condo
#PBS -N ${OUTPUTNAME}
#PBS -l nodes=1:ppn=8,mem=${MEM}gb
#PBS -l walltime=8:00:00
#PBS -o /home/opoirion/data/logs/${OUTPUTNAME}.out
#PBS -e /home/opoirion/data/logs/${OUTPUTNAME}.err
#PBS -V
#PBS -M opoirion@hawaii.edu
#PBS -m abe
#PBS -A epigen-group

module load bowtie2
module load bwa
module load bedtools
module load samtools

#!/usr/bin/bash
# Avoid the use of the symbol '~' as a reference to the home directory

OPTIONALARGS=""

case ${GENOMETYPE} in

    "hg19")
	PROMOTER="/home/opoirion/data/ref_genomes/human/male.hg19/male.hg19_all_genes_refseq_TSS_promoter_2000.bed"
	;;

    "hg38")
	PROMOTER="/home/opoirion/data/ref_genomes/human/hg38/hg38_all_genes_refseq_TSS_promoter_2000.bed"
	;;

    "mm10")
	PROMOTER="/home/opoirion/data/ref_genomes/mouse/mm10/mm10_all_genes_refseq_TSS_promoter_2000.bed"
	;;

    *)
	echo "Wrong genome type given by GENOMETYPE var: ${GENOMETYPE}"
	exit 1
	;;

esac

case ${VERSION} in

    "v2")
    ;;

    "v4")
    ;;

    "snap")
	VERSION="v4"
	;;

    "density")
	VERSION="v2"
	;;

    *)
	VERSION="v4"
	;;
esac


case ${COMPUTETSS} in
    "true")
	COMPUTETSS="True"
	;;
    "True")
	COMPUTETSS="True"
	;;
    "TRUE")
	COMPUTETSS="True"
	;;
    "T")
	COMPUTETSS="True"
	;;
    *)
	COMPUTETSS="False"
	;;
esac


echo "version: ${VERSION}"
echo "genome type: ${GENOMETYPE}"
echo "output name: ${OUTPUTNAME}"
echo "promoter file: ${PROMOTER}"


for inputFile in $DATASETNAMES
do
    echo "Input 10x Folder: ${inputFile}"
done


case ${SNAPCOMPUTEVIZ} in
    "false")
        OPTIONALARGS+=" -snap_do_viz False "
	;;
    "False")
        OPTIONALARGS+=" -snap_do_viz False "
	;;
    "F")
        OPTIONALARGS+=" -snap_do_viz False "
	;;
esac


if [  ! -z "$SNAPBINSIZE" ]
then
    OPTIONALARGS+=" -snap_bin_size ${SNAPBINSIZE} "
fi

if [  ! -z "$SNAPSUBSETTING" ]
then
    OPTIONALARGS+=" -snap_subset_diffusion_map ${SNAPSUBSETTING} "
fi

if [  ! -z "$SNAPNDIMS" ]
then
    OPTIONALARGS+=" -snap_ndims ${SNAPNDIMS} "
fi

if [  ! -z "$SNAPNEIGH" ]
then
    OPTIONALARGS+=" -snap_neigh ${SNAPNEIGH} "
fi

echo "Additional arguments to be used: ${OPTIONALARGS}"


if [  ! -z "$USEHARMONY" ]
then
    OPTIONALARGS+=" -snap_do_harmony_on_dataset True "
fi

echo "Additional arguments to be used: -snap_do_harmony_on_dataset"

if [  ! -z "$SNAPUSEPEAK" ]
then
    OPTIONALARGS+=" -snap_use_peak True "
fi

echo "Additional arguments to be used: -snap_use_peak"


if [  ! -z "$SNAPSUBSET" ]
then
    OPTIONALARGS+=" -snap_subset_diffusion_map ${SNAPSUBSET} "
fi

echo "Additional arguments to be used: -snap_subset_diffusion_map ${SNAPSUBSET} "

if [  "$DOCHROMVAR"=="True" ]
then
    OPTIONALARGS+=" -perform_chromVAR_analysis True "
fi

echo "Additional arguments to be used: -perform_chromVAR_analysis True "

if [  "$DOCICERO"=="True" ]
then
    OPTIONALARGS+=" -perform_cicero_analysis True "
fi

echo "Additional arguments to be used: -perform_cicero_analysis True "


if [ -z "$READINPEAK" ]
then
    READINPEAK=0.0
fi

if [ -z "$TSSPERCELL" ]
then
    TSSPERCELL=0.0
fi

if [ -z "$MINNBREADPERCELL" ]
then
    MINNBREADPERCELL=0.0
fi



python2 ~/code/snATAC/snATAC_pipeline/clustering_pipeline.py \
	-output_name ${OUTPUTNAME} \
	-project_folders_to_merge "${DATASETNAMES}"
        -project_folder /projects/ps-epigen/outputs/10xATAC \
        -output_path /projects/ps-epigen/datasets/opoirion/output_LIMS/${OUTPUTNAME} \
	-refseq_promoter_file ${PROMOTER} \
	-threads_number 8 \
	-format_output_for_webinterface True \
	-sambamba /home/opoirion/prog/sambamba-0.6.8-linux-static \
	-rm_original_bed_file True \
	-workflow_version ${VERSION} \
	-compute_TSS_enrichment ${COMPUTETSS} \
	-bam_bigwig_for_top_clustering True \
	-is_10x True \
        -bed_file_regex "fragments.tsv.gz" \
        -barcode_file_regex "singlecell.csv" \
	-min_number_of_reads_per_cell ${MINNBREADPERCELL} \
	-fraction_of_reads_in_peak ${READINPEAK} \
        -TSS_per_cell ${TSSPERCELL} \
	-path_to_remote_server "opoirion@ns104190.ip-147-135-44.us:data/data_ALL/output_LIMS" \
        ${OPTIONALARGS}
