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
        BOWTIENAME="male.hg19.fa"
        BOWTIEPATH="/home/opoirion/data/ref_genomes/human/male.hg19/Bowtie2Index"
	;;

    "hg38")
	PROMOTER="/home/opoirion/data/ref_genomes/human/hg38/hg38_all_genes_refseq_TSS_promoter_2000.bed"
        BOWTIENAME="GRCh38_no_alt_analysis_set_GCA_000001405.15.fasta"
        BOWTIEPATH="/home/opoirion/data/ref_genomes/human/hg38/Bowtie2Index"
	;;

    "mm10")
	PROMOTER="/home/opoirion/data/ref_genomes/mouse/mm10/mm10_all_genes_refseq_TSS_promoter_2000.bed"
        BOWTIENAME="mm10"
        BOWTIEPATH="/home/opoirion/data/ref_genomes/mouse/mm10/Bowtie2Index"
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

if [ ! -z "$READINPEAK" ]
then
    OPTIONALARGS+=" -fraction_of_reads_in_peak ${READINPEAK} "
fi

if [ ! -z "$TSSPERCELL" ]
then
    OPTIONALARGS+=" -TSS_per_cell ${TSSPERCELL} "
fi

if [ ! -z "$MINNBREADPERCELL" ]
then
    OPTIONALARGS+=" -min_number_of_reads_per_cell ${MINNBREADPERCELL} "
fi

if [  "$DOCHROMVAR"=="True" ]
then
    OPTIONALARGS+=" -perform_chromVAR_analysis True "
fi

echo "Additional arguments to be used: -perform_chromVAR_analysis True "

if [  "$DOCICERO"=="True" ]
then
    OPTIONALARGS+=" -perform_cicero_analysis True "
fi

echo "version: ${VERSION}"
echo "genome type: ${GENOMETYPE}"
echo "output name: ${OUTPUTNAME}"
echo "dataset name: ${DATASETNAME}"
echo "promoter file: ${PROMOTER}"
echo "ref barcode list: ${REFBARCODELIST}"
echo "bed file: ${BEDFILE}"


echo "Additional arguments to be used: ${OPTIONALARGS}"


python ~/code/snATAC/snATAC_pipeline/fastq_pipeline.py \
       -fastq_R1 /projects/ps-epigen/seqdata/${DATASETNAME}_R1.fastq.gz \
       -fastq_R2 /projects/ps-epigen/seqdata/${DATASETNAME}_R2.fastq.gz \
       -output_name ${OUTPUTNAME} \
       -output_path /projects/ps-epigen/datasets/opoirion/output_LIMS/${DATASETNAME} \
       -bowtie_index_path ${BOWTIEPATH} \
       -bowtie_index_name ${BOWTIENAME} \
       -refseq_promoter_file ${PROMOTER} \
       -threads_number 8 \
       -workflow_version ${VERSION} \
       -format_output_for_webinterface True \
       -compute_doublets True \
       -sambamba /home/opoirion/prog/sambamba-0.6.8-linux-static \
       -path_to_remote_server "opoirion@ns104190.ip-147-135-44.us:data/data_ALL/output_LIMS" \
       ${OPTIONALARGS}
