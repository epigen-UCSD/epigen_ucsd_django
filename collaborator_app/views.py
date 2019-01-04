from django.shortcuts import redirect,render,get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from epigen_ucsd_django.shared import is_in_multiple_groups
from django.http import JsonResponse
from setqc_app.models import LibrariesSetQC,LibraryInSet
from masterseq_app.models import SampleInfo
from epigen_ucsd_django.models import CollaboratorPersonInfo
from django.core import serializers

# Create your views here.

DisplayFieldforcollab = ['set_name','date_requested','experiment_type','url']

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



def CollaboratorGetNotesView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.collaborator != request.user:
        raise PermissionDenied
    data = {}
    data['notes'] = setinfo.notes
    return JsonResponse(data)

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

