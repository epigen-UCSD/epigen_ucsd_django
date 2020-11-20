import os
import django
from django.conf import settings
import sys
from decimal import Decimal
import re
import csv
import argparse
import sys



os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

# Now this script or any imported module can use any part of Django it needs.
from masterseq_app.models import SeqInfo, LibraryInfo, SampleInfo
from singlecell_app.models import SingleCellObject, TenxqcInfo, scRNAqcInfo, CoolAdminSubmission
from singlecell_app.views import get_tenx_status, get_latest_modified_time
from django.contrib.auth.models import User
from django.conf import settings

# hold all single cell experiment values
SINGLE_CELL_EXPS = ['10xATAC', 'scRNA-seq', 'snRNA-seq', 'scATAC-seq']

status = {
    'yes' : 'Yes',
    'no' : 'No',
    'inq':'InQueue',
    'inp': 'InProcess',
    'err':'Error!'
    }

def populate_singlecell_objects():
    cooladmin_objects = CoolAdminSubmission.objects.all()
    #Query all seq objects that have single cell expt types.
    seqs_queryset = SeqInfo.objects.filter(libraryinfo__experiment_type__in=SINGLE_CELL_EXPS).select_related('libraryinfo','libraryinfo__sampleinfo','libraryinfo__sampleinfo__group').order_by(
        '-date_submitted_for_sequencing').values('id', 'seq_id', 'libraryinfo__experiment_type', 'read_type',
                                                 'libraryinfo__sampleinfo__species', 'date_submitted_for_sequencing','libraryinfo__sampleinfo__group','libraryinfo__sampleinfo__sample_id')
    for entry in list(seqs_queryset):
        data = {}
    #Check if singlecell oject exists for seq object
        seqobj = SeqInfo.objects.get(pk=entry['id'])
        obj, created = SingleCellObject.objects.get_or_create(seqinfo = seqobj)
        print('working on seq_id {seq_id}, obj created: {created}'.format(seq_id=entry['seq_id'], created=created))
        
        #skip if sequence already has a singlecell object
        if created == False:
            continue

        #Fill in data
        data['experiment_type'] = entry['libraryinfo__experiment_type']
        data['tenx_pipeline_status'] = get_tenx_status(entry['seq_id'],data['experiment_type'])
        data['date_last_modified'] = get_latest_modified_time(entry['seq_id'],entry['id'], entry['date_submitted_for_sequencing'],cooladmin_objects)

        #check pipeline status, if done then fill in qc metrics and get path to
        #websummary + check if random string_link has been generated
        if data['tenx_pipeline_status'] == status['yes']:
            obj.path_to_websummary = get_path_to_websummary(entry['seq_id'], data['experiment_type'])
            obj.content_object = generate_qc_metrics_table(entry['seq_id'], data['experiment_type'])
            
            data['random_string_link'] = get_random_string_link(entry['seq_id'],data['experiment_type'])
            if (not data['random_string_link'] == None):
                obj.random_string_link = data['random_string_link']
        
        if cooladmin_objects.filter(seqinfo=seqobj).exists():
            obj.cooladminsubmission = cooladmin_objects.get(seqinfo=seqobj)

        #Save single cell object
        obj.experiment_type = data['experiment_type']
        obj.tenx_pipeline_status = data['tenx_pipeline_status']
        obj.date_last_modified = data['date_last_modified']
        
        obj.save()
        
def get_path_to_websummary(seq_id, expt_type):
    parent_dir = settings.TENX_DIR if expt_type == '10xATAC' else settings.SCRNA_DIR
    outs = 'outs'
    filename = 'web_summary.html'
    full_path = os.path.join(parent_dir,seq_id,outs,filename)
    print('path to websummary generated:{fullpath} '.format(fullpath=full_path))
    return full_path

def get_random_string_link(seq_id, expt_type):
    """ return a link for files to be viewed with a share link
    Will generate a link if needed. Will return the link in the response.
    """
    LENGTH_OF_KEY = 9  # put this in the deploy or settings file?
    #print('genertaing link for seq: ', seq)
    info = {}
    data = {}
    parent_dir = ""
    
    # get all files in exposed outs folder
    exposed_outs_dir = settings.EXPOSED_OUTS_DIR
    listdir = os.listdir(exposed_outs_dir)
    basenames = [os.path.basename(fn)[LENGTH_OF_KEY:] for fn in listdir]
    filenames_dict = {}
    for i in range(len(listdir)):
        filenames_dict[basenames[i]] = listdir[i]

    # get directory that seq is in
    # check if symbolic link is present
    if(seq_id not in (basenames)):
        return None
    else:
        link = filenames_dict[seq_id]
        print('exposed link found: ', link)
        return link

def generate_qc_metrics_table(seq_id, expt_type):
    print('recvd args: {seq_id} {expt_type}'.format(seq_id=seq_id,expt_type=expt_type))
    tenx_filename = 'summary.csv'
    scrna_filename = 'metrics_summary.csv'
    parent_dir = settings.TENX_DIR if expt_type in ['10xATAC','scATAC-seq'] else settings.SCRNA_DIR
    metrics_file_name = tenx_filename if expt_type in ['10xATAC','scATAC-seq'] else scrna_filename
    metrics_file_path = os.path.join(parent_dir,seq_id,'outs',metrics_file_name)
    data_dict = {}

    #open qc file and setup dict mapping metric to number
    with open(metrics_file_path) as f:
        reader = csv.reader(f)
        data = []
        for row in reader:
            data.append(row)
        #print(len(data[0]))
        #print(len(data[1]))
        for i, m in enumerate(data[0]):
            #check for data type
            data_dict[m] = type_data(data[1][i])

    #now transfer data into model
    if 'cellranger-atac_version' in data_dict.keys():
        data_dict['cellranger_atac_version'] = data_dict.pop('cellranger-atac_version')
    if expt_type in ['10xATAC','scATAC-seq']:
        # validate fields 
        fields = [i.attname for i in TenxqcInfo._meta.fields]
        data_dict={k:v for k,v in data_dict.items() if k in fields}
        #print(data_dict)
        #print([k for k in  fields if k not in data_dict.keys() ])
        #print({k:len(str(v)) for k,v in data_dict.items()})
        #print(max([len(str(v)) for k,v in data_dict.items()]))
        model_ = TenxqcInfo(**data_dict)
        model_.full_clean()
    else:
        #convert dict to scRNAqcInfo type
        convert_to_scrna_dict(data_dict)
        model_ = scRNAqcInfo(**data_dict)

    model_.save()

    return(model_)

def convert_to_scrna_dict(data_dict):
    """Converts scRNA dictionary to correct keys
    """

    data_dict['estimated_number_of_cells'] = data_dict.pop('Estimated Number of Cells')
    data_dict['mean_reads_per_cell'] = data_dict.pop('Mean Reads per Cell')
    data_dict['median_genes_per_cell'] = data_dict.pop('Median Genes per Cell')
    data_dict['number_of_reads'] = data_dict.pop('Number of Reads')
    data_dict['valid_barcodes'] = data_dict.pop('Valid Barcodes')
    data_dict['sequencing_saturation'] = data_dict.pop('Sequencing Saturation')
    data_dict['q30_bases_in_barcode'] = data_dict.pop('Q30 Bases in Barcode')
    data_dict['q30_bases_in_rna_read'] = data_dict.pop('Q30 Bases in RNA Read')
    data_dict['q30_bases_in_sample_index'] = data_dict.pop('Q30 Bases in Sample Index') if 'Q30 Bases in Sample Index' in data_dict.keys() else None    
    data_dict['q30_bases_in_UMI'] = data_dict.pop('Q30 Bases in UMI') if 'Q30 Bases in UMI' in data_dict.keys() else None
    data_dict['reads_mapped_to_genome'] = data_dict.pop('Reads Mapped to Genome')
    data_dict['reads_mapped_confidently_to_genome'] = data_dict.pop('Reads Mapped Confidently to Genome')
    data_dict['reads_mapped_confidently_to_intergenic_regions'] = data_dict.pop('Reads Mapped Confidently to Intergenic Regions')
    data_dict['reads_mapped_confidently_to_intronic_regions'] = data_dict.pop('Reads Mapped Confidently to Intronic Regions')
    data_dict['reads_mapped_confidently_to_exonic_regions'] = data_dict.pop('Reads Mapped Confidently to Exonic Regions')
    data_dict['reads_mapped_confidently_to_transcriptome'] = data_dict.pop('Reads Mapped Confidently to Transcriptome')
    data_dict['reads_mapped_antisense_to_gene'] = data_dict.pop('Reads Mapped Antisense to Gene')
    data_dict['frac_reads_in_cells'] = data_dict.pop('Fraction Reads in Cells')
    data_dict['total_genes_detected'] = data_dict.pop('Total Genes Detected')
    data_dict['median_UMI_counts_per_cell'] = data_dict.pop('Median UMI Counts per Cell')

#TODO think about logging to a csv file
def type_data(data):
    #if split data has more than 2 dots, this is a version number, return a string
    if len(data.split('.')) > 2:
        #print('returning data as string: ',data)
        return data 
    elif('%' in data):
        #data is a percent and should be converted to a float
        _data = data.replace('%','')
        data = float(_data)/100
        
    elif len(data.split('.')) == 1:
        #there is no . in the data so this is just a number
        #print('returning data as int: ',data)
        data = None  if data=='None'  else  int(data.replace(',', '')) 
    else:
        #data is just a decimal, percent or other
        #print('returning data as dec: ',len(data), ' ',data)
        data = Decimal(data)
    return data

def clear_database_of_test_entries():
    SeqInfo.objects.filter(seq_id__contains='populatetest').delete()




DEFAULT_NUMBER_TO_ADD=1000
keyword='populatetest'

#call this function to populate the data base with some seqInfos
#Param number_to_add is the number of seqinfo's to add.
def populate(number_to_add=DEFAULT_NUMBER_TO_ADD,add_10x_only=False):
    tenx_library = LibraryInfo.objects.get(pk=8)
    sc_library = LibraryInfo.objects.get(pk=6)
    
    user = User.objects.get(username='brandon')

    recent_seqinfo_object=SeqInfo.objects.filter(seq_id__contains=keyword).order_by('-seq_id')
    if(len(recent_seqinfo_object) > 0):
        recent_seqinfo_object = recent_seqinfo_object[0]
        recent_seqinfo=recent_seqinfo_object.seq_id
        #convert to a number
        recent_seqinfo = recent_seqinfo.split('_')
        recent_seqinfo_num = int(recent_seqinfo[1])
        recent_seqinfo_base = recent_seqinfo[0]
        num_to_add = recent_seqinfo_num + 1 

    else:
        recent_seqinfo_base = keyword
        num_to_add = 0    
    #create singlecell seqinfo objects and make directories!
    for index in range(number_to_add):
        if( index / number_to_add > 0.5 or add_10x_only==True):
            num_to_add += 1
            #make seqinfo object and save it
            new_seq_id = recent_seqinfo_base + "_" + str(num_to_add)
            new_seqinfo = SeqInfo(seq_id=new_seq_id, team_member_initails=user,
                libraryinfo=tenx_library)
            new_seqinfo.save()
            #now add seqinfo object files to fastq dir
            make_fastq_files(new_seq_id)
        else:
            num_to_add += 1
            #make seqinfo object and save it
            new_seq_id = recent_seqinfo_base + "_" + str(num_to_add)
            new_seqinfo = SeqInfo(seq_id=new_seq_id, team_member_initails=user,
                libraryinfo=sc_library)
            new_seqinfo.save()
            #now add seqinfo object files to fastq dir
            make_fastq_files(new_seq_id)

#add option to add PE and SE
def make_fastq_files(seq_id):
    ending_r1="_R1.fastq.gz"
    ending_r2="_R2.fastq.gz"
    fastq_dir = settings.FASTQ_DIR
    filename_r1=seq_id+ending_r1
    filename_r2=seq_id+ending_r2

    file_path_r1 = os.path.join(fastq_dir,filename_r1)
    file_path_r2 = os.path.join(fastq_dir,filename_r2)

    #write files
    with open(file_path_r1, 'w') as f:
        f.write('')
    with open(file_path_r2, 'w') as f:
        f.write('')
        

def clear_database_of_sc_object_entries():
    SingleCellObject.objects.all().delete()

def clear_cooladmin():
    CoolAdminSubmission.objects.all().delete()


def make_seq():
    tenx_library = LibraryInfo.objects.get(pk=7)
    user = User.objects.get(username='brandon')
    new_seqinfo = SeqInfo(seq_id='brandon_102_14', team_member_initails=user,
                libraryinfo=tenx_library)
    new_seqinfo.save()



if __name__ == "__main__":
    
    if sys.argv[1] == 'p':
        populate()
    elif sys.argv[1] == 'c':
        clear_database_of_test_entries()