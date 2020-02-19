from django.shortcuts import redirect,render,get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from epigen_ucsd_django.shared import is_in_multiple_groups
from django.http import JsonResponse
from setqc_app.models import LibrariesSetQC,LibraryInSet
from masterseq_app.models import SampleInfo
from epigen_ucsd_django.models import CollaboratorPersonInfo
from django.core import serializers
from masterseq_app.models import SampleInfo, LibraryInfo, SeqInfo, ProtocalInfo, \
    SeqMachineInfo
from django.contrib.auth.models import User, Group
from setqc_app.models import LibrariesSetQC, LibraryInSet
# Create your views here.

DisplayFieldforcollab = ['set_name','date_requested','experiment_type','url']


def UserSampleDataView(request):
    group_name = request.user.groups.all().first().name
    print(group_name)

    Samples_list = SampleInfo.objects.filter(group=request.user.groups.all().first()).values(
        'pk', 'sample_id', 'description', 'date', 'sample_type', 'group__name', 'status')
    for sample in Samples_list:
        try:
            sample['group__name'] = sample['group__name'].replace(
                '_group', '').replace('_', ' ')
        except:
            pass
    data = list(Samples_list)

    return JsonResponse(data, safe=False)


def UserLibDataView(request):
    # Libs_list = LibraryInfo.objects.filter(team_member_initails=request.user)\
    #     .select_related('sampleinfo__group').values(
    #         'pk', 'library_description','library_id', 'sampleinfo__id',  'sampleinfo__sample_type', 'sampleinfo__sample_id', 'sampleinfo__description',
    #     'sampleinfo__species', 'sampleinfo__group__name', 'date_started', 'experiment_type')
    Libs_list = LibraryInfo.objects.select_related('sampleinfo__group').filter(sampleinfo__group=request.user.groups.all().first()).values(
            'pk', 'library_description','library_id', 'sampleinfo__id',  'sampleinfo__sample_type', 'sampleinfo__sample_id', 'sampleinfo__description',
        'sampleinfo__species', 'sampleinfo__group__name', 'date_started', 'experiment_type')
    data = list(Libs_list)

    return JsonResponse(data, safe=False)


def UserSeqDataView(request):
    # Seqs_list = SeqInfo.objects.filter(team_member_initails=request.user)\
    #     .select_related('libraryinfo__sampleinfo__group','machine').values(
    #     'pk', 'seq_id','libraryinfo__library_description', 'libraryinfo__sampleinfo__id', 'libraryinfo__sampleinfo__sample_id',
    #     'libraryinfo__sampleinfo__description', 'libraryinfo__sampleinfo__group__name',
    #     'date_submitted_for_sequencing','machine__sequencing_core',\
    #     'machine__machine_name','portion_of_lane','read_length', 'read_type')
    Seqs_list = SeqInfo.objects.select_related('libraryinfo__sampleinfo__group','machine').filter(libraryinfo__sampleinfo__group=request.user.groups.all().first()).values(
        'pk', 'seq_id','libraryinfo__library_description', 'libraryinfo__sampleinfo__id', 'libraryinfo__sampleinfo__sample_id',
        'libraryinfo__sampleinfo__description', 'libraryinfo__sampleinfo__group__name',
        'date_submitted_for_sequencing','machine__sequencing_core',\
        'machine__machine_name','portion_of_lane','read_length', 'read_type')
    data = list(Seqs_list)

    return JsonResponse(data, safe=False)


def UserSetqcView(request):

    Setqcs_list = LibrariesSetQC.objects.filter(group=request.user.groups.all().first()).values(
        'pk','notes','set_id','set_name','last_modified','experiment_type','url','status')
    data = list(Setqcs_list)

    return JsonResponse(data, safe=False)

def CollaboratorGetNotesView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.collaborator != request.user:
        raise PermissionDenied
    data = {}
    data['notes'] = setinfo.notes
    return JsonResponse(data)

def GetNotesView(request, setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    # if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
    #     raise PermissionDenied
    data = {}
    data['notes'] = setinfo.notes
    return JsonResponse(data)






def collab_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, form.user)
            #messages.success(request, 'Your password was successfully updated!')

            return redirect('collaborator_app:collaboratorsetqcs')

        # else:
            #messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'collaborator_app/collaborator_change_password.html', {
        'form': form
    })
def CollaboratorSetQCView(request):
    SetQC_list = LibrariesSetQC.objects.filter(collaborator=request.user)
    context = {
        'Sets_list': SetQC_list,
        'DisplayField':DisplayFieldforcollab,
    }
    return render(request, 'collaborator_app/collaboratorsetqcinfo.html', context)





def CollaboratorSetQCDetailView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.collaborator != request.user:
        raise PermissionDenied
    summaryfield = ['set_name','collaborator','date_requested','requestor','experiment_type','notes','url','version']
    groupinputinfo = ''
    librariesset = LibraryInSet.objects.filter(librariesetqc=setinfo)
    list1tem = list(librariesset.values_list('seqinfo', flat=True))
    list1 = [SeqInfo.objects.values_list('seq_id', flat=True).get(id=x)
     for x in list1tem]
    if setinfo.experiment_type == 'ChIP-seq':
        list2 = list(librariesset.values_list('group_number', flat=True))
        list3 = list(librariesset.values_list('is_input', flat=True))
        groupinputinfo = list(zip(list1,list2,list3))
    context = {
        'setinfo':setinfo,
        'summaryfield':summaryfield,
        'libraryinfo': list1,
        'groupinputinfo':groupinputinfo,
    }
    return render(request, 'collaborator_app/collaboratordetails.html', context=context)

def CollaboratorSampleView(request):
	collab_person = CollaboratorPersonInfo.objects.get(person_id=request.user)
	Sample_list = SampleInfo.objects.filter(research_person=collab_person).values(\
		'pk','sample_id','date','sample_type','service_requested','status')
	data=list(Sample_list)

	return JsonResponse(data,safe=False)

def CollaboratorSampleComView(request):
	collab_person = CollaboratorPersonInfo.objects.get(person_id=request.user)
	SetQC_list = LibrariesSetQC.objects.filter(collaborator=request.user)
	Sample_list = SampleInfo.objects.filter(research_person=collab_person).values(\
		'pk','sample_id','date','sample_type','service_requested','status')
	context = {
		'Sets_list': SetQC_list,
		'DisplayField':DisplayFieldforcollab,
		'Sample_list':Sample_list,
	}
	return render(request, 'collaborator_app/collaboratorsetqcinfocom.html', context)

