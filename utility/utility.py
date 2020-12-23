from django.conf import settings
import os


def get_seq_status(seq_id, read_type, experiment_type=''):
    """This function checks the FASTQ sequence status and returns the results 
    @params
        seq_id: string represents a seq_id to be checked.
        read_type: Paired end or not
    @returns
        'Yes': FASTQ files present
        'No': no FASTQ files present
    """
    fastqdir = settings.FASTQ_DIR
    #print(f'seq: {seq}, seqid: {seq.seq_id}, readtype: {seq.read_type}')
    reps = seq_id.split('_')[2:]
    mainname = '_'.join(seq_id.split('_')[0:2])
    # reps are [_2] in brandon_210_2 or [_1,_2,_3] in brandon_210_1_2_3
    if(experiment_type in ['scRNA-seq', 'snRNA-seq', '10xATAC']):
        if len(reps) == 0:
            if not os.path.isdir(os.path.join(fastqdir, mainname)):
                return ('No')
            else:
                seqsStatus = ('Yes')
        else:
            for rep in reps:
                if rep == '1':
                    if not os.path.isdir(os.path.join(fastqdir, mainname)):
                        return ('No')
                else:
                    repname = mainname + '_' + rep
                    if not os.path.isdir(os.path.join(fastqdir, repname)):
                        return ('No')
            seqsStatus = 'Yes'
    else:
        if len(reps) == 0:
            if read_type == 'PE':
                r1 = mainname + '_R1.fastq.gz'
                r2 = mainname + '_R2.fastq.gz'
                if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                    seqsStatus = ('No')
                else:
                    seqsStatus = ('Yes')
            else:
                r1 = mainname+'.fastq.gz'
                r1op = mainname+'_R1.fastq.gz'
                if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                    seqsStatus = 'No'
                else:
                    seqsStatus = 'Yes'
        else:
            for rep in reps:
                if rep == '1':
                    if read_type == 'PE':
                        r1 = mainname + '_R1.fastq.gz'
                        r2 = mainname + '_R2.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                            return('No')
                    else:
                        r1 = mainname+'.fastq.gz'
                        r1op = mainname+'_R1.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                            return('No')
                else:
                    # find mainname_rep
                    repname = mainname + '_' + rep
                    if read_type == 'PE':
                        r1 = repname + '_R1.fastq.gz'
                        r2 = repname + '_R2.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                            return ('No')
                    else:
                        r1 = repname+'.fastq.gz'
                        r1op = repname+'_R1.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                            return ('No')

            # set when for loop statement terminates, all reps fastq's were present
            seqsStatus = 'Yes'
    #print(f'seqstatus: {seqsStatus}')
    return seqsStatus
