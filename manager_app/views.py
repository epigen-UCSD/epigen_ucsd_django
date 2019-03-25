from django.shortcuts import redirect,render,get_object_or_404
from epigen_ucsd_django.models import CollaboratorPersonInfo


# Create your views here.

DisplayFieldforcollab = ['set_name','date_requested','experiment_type','url']

def CollaboratorListView(request):
    collabs = CollaboratorPersonInfo.objects.all().select_related('person_id').values(\
        'person_id__first_name','person_id__last_name','person_id__email','cell_phone','role',\
        'fiscal_index')
    #collabs = CollaboratorPersonInfo.objects.prefetch_related(Prefetch('restaurants', queryset=Restaurant.objects.select_related('best_pizza')))
    collabs2 = CollaboratorPersonInfo.objects.select_related('person_id').prefetch_related('person_id__group')
    print(collabs2)
    collab_list = list(collabs)
    print(collab_list)
    context = {
        'collab_list':collab_list,
    }
    return render(request, 'manager_app/collaboratorlist.html', context=context)   
