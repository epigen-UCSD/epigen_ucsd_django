from django.shortcuts import redirect,render,get_object_or_404
from epigen_ucsd_django.models import CollaboratorPersonInfo,Group_Institution
from django.db import transaction
from .forms import UserForm,CollaboratorPersonForm,GroupForm,\
GroupCreateForm,CollabInfoAddForm,\
GroupInstitutionCreateForm
from django.contrib import messages
from django.contrib.auth.models import User,Group
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Prefetch
from epigen_ucsd_django.shared import is_member
from masterseq_app.views import nonetolist,removenone
from django.forms import formset_factory
from .forms import ServiceRequestItemCreationForm,ServiceRequestCreationForm,ContactForm
import datetime
from collaborator_app.models import ServiceInfo,ServiceRequest,ServiceRequestItem
# Create your views here.


def CollaboratorListView(request):
    collabs = CollaboratorPersonInfo.objects.all().select_related('person_id').prefetch_related('person_id__groups')
    collabs_list = collabs.values(\
        'group__name','person_id__username',\
        'person_id__first_name','person_id__last_name',\
        'phone','email','role','index','initial_password')
    group_institute_list = Group_Institution.objects.all().select_related('group').values('group__name','institution')
    group_institute_dict = {}
    for item in group_institute_list:
        group_institute_dict[item['group__name']]=item['institution']
 
    context = {
        'collab_list':collabs_list,
        'group_institute_dict':group_institute_dict,
    }
    #print(context)
    if is_member(request.user,'manager'):
        return render(request, 'manager_app/manageronly_collaboratorlist.html', context)
    else:
        return render(request, 'manager_app/collaboratorlist.html', context)

# @transaction.atomic
# def CollaboratorCreateView(request):
#     user_form = UserForm(request.POST or None)
#     profile_form = CollaboratorPersonForm(request.POST or None)
#     group_form = GroupForm(request.POST or None)
#     group_create_form = GroupCreateForm(request.POST or None)
#     person_index_form = PersonIndexForm(request.POST or None)

#     if request.method=='POST' and 'profile_save' in request.POST:
#         if user_form.is_valid() and profile_form.is_valid() and group_form.is_valid() and person_index_form.is_valid():
#             this_user = user_form.save()
#             this_profile = profile_form.save(commit=False)
#             this_profile.person_id = this_user
#             this_profile.save()
#             this_group = Group.objects.get(name=group_form.clean_name()) 
#             this_group.user_set.add(this_user)
#             this_person_index = person_index_form.save(commit=False)
#             this_person_index.person = this_profile
#             this_person_index.save()

#             messages.success(request,'Your profile was successfully updated!')
#             return redirect('manager_app:collab_list')
#         else:
#             messages.error(request,'Please correct the error below.')
#     # elif request.method=='POST' and 'group_save' in request.POST:
#     #     if group_create_form.is_valid():
#     #         group_create_form.save()
#     context = {
#         'user_form': user_form,
#         'profile_form': profile_form,
#         'group_form':group_form,
#         'group_create_form':group_create_form,
#         'person_index_form':person_index_form,
#     }
#     if is_member(request.user,'manager'):
#         return render(request, 'manager_app/profile_add.html', context)
#     else:
#         return render(request, 'manager_app/profile_add_nogroup.html', context)

@transaction.atomic
def CollaboratorCreateView(request):
    user_form = UserForm(request.POST or None)
    profile_form = CollaboratorPersonForm(request.POST or None)
    group_form = GroupForm(request.POST or None)

    if request.method=='POST':
        if user_form.is_valid() and profile_form.is_valid() and group_form.is_valid():
            this_user = user_form.save()
            this_group = Group.objects.get(name=group_form.clean_name())
            this_profile = profile_form.save(commit=False)
            this_profile.person_id = this_user
            this_profile.initial_password = user_form.cleaned_data['password']
            this_profile.group = this_group
            this_profile.save()
            this_group.user_set.add(this_user)

            messages.success(request,'Your profile was successfully added!')
            return redirect('manager_app:collab_list')
        else:
            messages.error(request,'Please correct the error below.')

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'group_form':group_form,
    }
    return render(request, 'manager_app/collab_add.html', context)



@transaction.atomic
def GroupAccountCreateView(request):
    user_form = UserForm(request.POST or None)
    profile_form = CollaboratorPersonForm(request.POST or None)
    group_form = GroupCreateForm(request.POST or None)
    institution_form = GroupInstitutionCreateForm(request.POST or None)

    if request.method=='POST' and 'profile_save' in request.POST:
        if user_form.is_valid() and profile_form.is_valid() and group_form.is_valid() and institution_form.is_valid():
            this_user = user_form.save()
            this_profile = profile_form.save(commit=False)
            this_profile.person_id = this_user            
            this_group = group_form.save()
            this_group.user_set.add(this_user)
            this_profile.group = this_group
            this_profile.initial_password = user_form.cleaned_data['password']
            this_profile.role = 'PI'
            this_profile.save()
            this_inst = institution_form.save(commit=False)
            this_inst.group = this_group
            this_inst.save()
            return redirect('manager_app:collab_list')

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'group_form':group_form,
        'institution_form':institution_form,
    }
 
    return render(request, 'manager_app/collab_group_account_add.html', context)

@transaction.atomic
def AjaxGroupCreateView(request):
    data = {}
    if request.method == 'POST':
        group_create_form = GroupCreateForm(request.POST)
        if group_create_form.is_valid():
            groupname = request.POST.get('name')
            thisgroup = Group(name=groupname)
            thisgroup.save()
            data['ok'] = 1;
        else:
            data['error'] = str(group_create_form.errors);
            print(data['error'])
    return JsonResponse(data)

def load_groups(request):
    q = request.GET.get('term', '')
    gs = Group.objects.exclude(name__in=['bioinformatics','wetlab','manager']).filter(
        name__icontains=q).values('name')[:20]
    results = []
    for g in gs:
        gsearch = {}
        gsearch['id'] = g['name']
        gsearch['label'] = g['name']
        gsearch['value'] = g['name']
        results.append(gsearch)
    return JsonResponse(results, safe=False)

@transaction.atomic
def CollabInfoAddView(request):
    colab_info_add_form = CollabInfoAddForm(request.POST or None)
    if request.method == 'POST':
        post = request.POST.copy()
        print(post['person_id'].split(':')[0])
        obj = get_object_or_404(CollaboratorPersonInfo, id=post['person_id'].split(':')[0])
        post['person_id'] = obj.person_id.id
        colab_info_add_form = CollabInfoAddForm(post)
        if colab_info_add_form.is_valid():
            current_email = nonetolist(obj.email)
            current_email = colab_info_add_form.cleaned_data['email']+current_email
            obj.email = removenone(current_email)

            current_phone = nonetolist(obj.phone)
            current_phone = colab_info_add_form.cleaned_data['phone']+current_phone
            obj.phone = removenone(current_phone)

            current_index = nonetolist(obj.index)
            current_index = colab_info_add_form.cleaned_data['index']+current_index
            obj.index = removenone(current_index)

            obj.save()
            return redirect('manager_app:collab_list')
    context = {
        'colab_info_add_form':colab_info_add_form,
    }
    return render(request, 'manager_app/collab_info_add.html', context)


def load_collabs(request):
    q = request.GET.get('term', '')
    #collabusers = User.objects.filter(Q(first_name__icontains = q)|Q(last_name__icontains = q)).values('first_name','last_name')[:20]
    collabusers = User.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q))
    for f in Group.objects.filter(name__icontains=q):
        collabusers = collabusers | f.user_set.all()
    results = []
    for u in collabusers.distinct():

        for gg in u.groups.all():
            thiscollab = CollaboratorPersonInfo.objects.get(group=gg,person_id=u)
            uu = {}
            uu['id'] = str(thiscollab.id)+': '+u.first_name+' '+u.last_name + \
                '('+gg.name+')'
            uu['label'] = str(thiscollab.id)+': '+u.first_name+' ' + \
                u.last_name+'('+gg.name+')'
            uu['value'] = str(thiscollab.id)+': '+u.first_name+' ' + \
                u.last_name+'('+gg.name+')'
            results.append(uu)
    return JsonResponse(results, safe=False)

def load_collabs_old(request):
    q = request.GET.get('term', '')
    #collabusers = User.objects.filter(Q(first_name__icontains = q)|Q(last_name__icontains = q)).values('first_name','last_name')[:20]
    collabusers = User.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q))
    for f in Group.objects.filter(name__icontains=q):
        collabusers = collabusers | f.user_set.all()
    results = []
    for u in collabusers:
        print(u)
        print(u.collaboratorpersoninfo_set.first())
        uu = {}
        uu['id'] = str(u.collaboratorpersoninfo_set.first().id)+': '+u.first_name+' '+u.last_name + \
            '('+u.groups.all().first().name+')'
        uu['label'] = str(u.collaboratorpersoninfo_set.first().id)+': '+u.first_name+' ' + \
            u.last_name+'('+u.groups.all().first().name+')'
        uu['value'] = str(u.collaboratorpersoninfo_set.first().id)+': '+u.first_name+' ' + \
            u.last_name+'('+u.groups.all().first().name+')'
        results.append(uu)
    return JsonResponse(results, safe=False)

def load_researchcontact(request):
    groupname = request.GET.get('group')
    # researchcontact = CollaboratorPersonInfo.objects.\
    # filter(person_id__groups__name__in=[groupname]).prefetch_related(Prefetch('person_id__groups'))
    researchcontact = CollaboratorPersonInfo.objects.filter(person_id__groups__name__in=[groupname])
    #print(researchcontact)
    return render(request, 'manager_app/researchcontact_dropdown_list_options.html', {'researchcontact': researchcontact})

def load_email(request):
    colllab_id = request.GET.get('colllab_id')

    researchcontact = CollaboratorPersonInfo.objects.get(id=colllab_id)
    #print(researchcontact.email)
    return render(request, 'manager_app/email_dropdown_list_options.html', {'researchcontact': researchcontact})


@transaction.atomic
def ServiceRequestCreateView(request):

    data_requestitem = {}
    data_request = {}

    contact_form = ContactForm(request.POST or None)
    ServiceRequestItemFormSet = formset_factory(
        ServiceRequestItemCreationForm, can_delete=True)
    servicerequestitems_formset = ServiceRequestItemFormSet(request.POST or None)
    
    today = datetime.date.today()

    if request.method == 'POST':
        servicerequest_form = ServiceRequestCreationForm(request.POST)
        if servicerequest_form.is_valid() and contact_form.is_valid():
            group_name = contact_form.cleaned_data['group']
            research_contact = contact_form.cleaned_data['research_contact']
            research_contact_name = research_contact.person_id.first_name+' '+research_contact.person_id.last_name
            research_contact_email = contact_form.cleaned_data['research_contact_email']
            print(research_contact_email)
            groupinfo = Group.objects.get(name=group_name)
            data_request = {
                'date':str(today),
                'group':group_name,
                'status':'initiate',
                'research_contact':research_contact_name,
                'research_contact_email':research_contact_email,
                'notes':servicerequest_form.cleaned_data['notes'],
            }
            try:
                institute = Group_Institution.objects.get(group=groupinfo).institution.lower()
            except:
                institute = 'non-ucsd'
            #print(institute)
            if servicerequestitems_formset.is_valid():
                for form in servicerequestitems_formset.forms:
                    if form not in servicerequestitems_formset.deleted_forms and form.cleaned_data:
                        service = form.cleaned_data['service']
                        quantity = form.cleaned_data['quantity']
                        if service.service_name == 'ATAC-seq':
                            if float(quantity) >= 24 and float(quantity) < 96:
                                service = ServiceInfo.objects.get(service_name='ATAC-seq_24')
                            elif float(quantity) >= 96:
                                service = ServiceInfo.objects.get(service_name='ATAC-seq_96')
                        #print(service.service_name)

                        if institute == 'ucsd':
                            data_requestitem[service.service_name] = {
                                'rate(uc users)':str(service.uc_rate)+'/'+service.rate_unit,
                                'rate_number':service.uc_rate,
                                'quantity':quantity,
                            }
                        else:
                            data_requestitem[service.service_name] = {
                                'rate(non-uc users)':str(service.nonuc_rate)+'/'+service.rate_unit,
                                'rate_number':service.nonuc_rate,
                                'quantity':quantity,
                            }                            
                total_price = sum([float(x['rate_number'])*float(x['quantity']) for x in data_requestitem.values()])
                total_expression = '+'.join(['$'+str(x['rate_number'])+'*'+str(x['quantity']) for x in data_requestitem.values()])+' = $'+str(total_price)

                if 'Preview' in request.POST:
                    if institute == 'ucsd':
                        displayorde_requestitem = ['rate(uc users)','quantity']
                    else:
                        displayorde_requestitem = ['rate(non-uc users)','quantity']
                    displayorder_request = ['date','group','research_contact','research_contact_email','notes','status']
                    #print(data_request)  

                    context = {
                        'contact_form':contact_form,
                        'servicerequest_form': servicerequest_form,
                        'servicerequestitems_formset': servicerequestitems_formset,
                        'modalshow': 1,
                        'displayorde_requestitem': displayorde_requestitem,
                        'displayorder_request': displayorder_request,
                        'data_requestitem':data_requestitem,
                        'data_request':data_request,
                        'total_expression':total_expression
                    }        
                    return render(request, 'manager_app/manager_feeforservice_servicerequestcreate.html', context)

                if 'Save' in request.POST:
                    thisrequest = ServiceRequest.objects.create(
                        group=groupinfo,
                        date=data_request['date'],
                        research_contact=research_contact,
                        research_contact_email=data_request['research_contact_email'],
                        notes=data_request['notes'],
                        status=data_request['status'],
                        )
                    for item in data_requestitem.keys():
                        print(item)
                        print(data_requestitem[item]['quantity'])
                        ServiceRequestItem.objects.create(
                            request=thisrequest, 
                            service=ServiceInfo.objects.get(service_name=item),
                            quantity=data_requestitem[item]['quantity'],
                            )
                    return redirect('manager_app:servicerequests_list')


    else:
        servicerequest_form = ServiceRequestCreationForm(None)

    context = {
        'contact_form':contact_form,
        'servicerequest_form': servicerequest_form,
        'servicerequestitems_formset': servicerequestitems_formset,
    }

    return render(request, 'manager_app/manager_feeforservice_servicerequestcreate.html', context)


def ServiceRequestDataView(request):
    ServiceRequest_list = ServiceRequest.objects.all().select_related('group','research_contact__person_id').prefetch_related(Prefetch('group__group_institution_set')).values('pk','quote_number','date','group__name','research_contact__person_id__first_name','research_contact__person_id__last_name','research_contact_email','status','notes','group__group_institution__institution')
    data = list(ServiceRequest_list)

    return JsonResponse(data, safe=False)




