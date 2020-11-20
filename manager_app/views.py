from django.shortcuts import redirect, render, get_object_or_404
from epigen_ucsd_django.models import CollaboratorPersonInfo, Group_Institution
from django.db import transaction
from .forms import UserForm, CollaboratorPersonForm, GroupForm,\
    GroupCreateForm, CollabInfoAddForm,\
    GroupInstitutionCreateForm, QuoteTextForm, QuoteCreationForm
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Prefetch
from epigen_ucsd_django.shared import is_member, daysuffix, quotebody, datetransform2, serviceitemcollapse, servicetarget
from masterseq_app.views import nonetolist, removenone
from django.forms import formset_factory, inlineformset_factory
from .forms import ServiceRequestItemCreationForm, ServiceRequestCreationForm, ContactForm, QuoteBulkImportForm, QuoteUploadFileForm, QuoteUploadByQidFileForm, QuoteUpdateForm
from masterseq_app.models import SeqInfo, SeqBioInfo, LibraryInfo, SampleInfo
import datetime
from collaborator_app.models import ServiceInfo, ServiceRequest, ServiceRequestItem
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import os
import subprocess
from django.conf import settings
from django.utils.safestring import mark_safe
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import PermissionDenied
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Create your views here.


def SummarizeData(request):

    df_l = pd.DataFrame(list(LibraryInfo.objects.values())).experiment_type.value_counts(
    ).rename_axis('Experiment type').reset_index(name='counts')
    df_s = pd.DataFrame(list(SampleInfo.objects.values())).species.value_counts(
    ).rename_axis('species').reset_index(name='counts')
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {
                        "type": "pie"}]], subplot_titles=("Total Samples", "Total Libs"))
    fig.add_trace(go.Pie(labels=df_s['species'],
                         values=df_s.counts, hole=.4,
                         title={"text": str(sum(df_s.counts)), "font": {"size": 30}}), row=1, col=1)
    fig.add_trace(go.Pie(labels=df_l['Experiment type'],
                         values=df_l.counts, hole=.4,
                         title={"text": str(sum(df_l.counts)), "font": {"size": 30}}), row=1, col=2)

    div = fig.to_html(full_html=False, include_plotlyjs='cdn')
    context = {"tot_lib_graph": div}
    return render(request, 'manager_app/data_summary.html', context)


def CollaboratorListView(request):
    collabs = CollaboratorPersonInfo.objects.all().select_related(
        'person_id').prefetch_related('person_id__groups')
    collabs_list = collabs.values(
        'group__name', 'person_id__username',
        'person_id__first_name', 'person_id__last_name',
        'phone', 'email', 'role', 'index', 'initial_password')
    group_institute_list = Group_Institution.objects.all().select_related(
        'group').values('group__name', 'institution')
    group_institute_dict = {}
    for item in group_institute_list:
        group_institute_dict[item['group__name']] = item['institution']

    context = {
        'collab_list': collabs_list,
        'group_institute_dict': group_institute_dict,
    }
    # print(context)
    if is_member(request.user, 'manager'):
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

    if request.method == 'POST':
        if user_form.is_valid() and profile_form.is_valid() and group_form.is_valid():
            this_user = user_form.save()
            this_group = Group.objects.get(name=group_form.clean_name())
            this_profile = profile_form.save(commit=False)
            this_profile.person_id = this_user
            this_profile.initial_password = user_form.cleaned_data['password']
            this_profile.group = this_group
            this_profile.save()
            this_group.user_set.add(this_user)

            messages.success(request, 'Your profile was successfully added!')
            return redirect('manager_app:collab_list')
        else:
            messages.error(request, 'Please correct the error below.')

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'group_form': group_form,
    }
    return render(request, 'manager_app/collab_add.html', context)


@transaction.atomic
def GroupAccountCreateView(request):
    user_form = UserForm(request.POST or None)
    profile_form = CollaboratorPersonForm(request.POST or None)
    group_form = GroupCreateForm(request.POST or None)
    institution_form = GroupInstitutionCreateForm(request.POST or None)

    if request.method == 'POST' and 'profile_save' in request.POST:
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
        'group_form': group_form,
        'institution_form': institution_form,
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
            data['ok'] = 1
        else:
            data['error'] = str(group_create_form.errors)
            print(data['error'])
    return JsonResponse(data)


def load_groups(request):
    q = request.GET.get('term', '')
    gs = Group.objects.exclude(name__in=['bioinformatics', 'wetlab', 'manager']).filter(
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
        obj = get_object_or_404(CollaboratorPersonInfo,
                                id=post['person_id'].split(':')[0])
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
        'colab_info_add_form': colab_info_add_form,
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
            thiscollab = CollaboratorPersonInfo.objects.get(
                group=gg, person_id=u)
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
    researchcontact = CollaboratorPersonInfo.objects.filter(
        person_id__groups__name__in=[groupname])
    # print(researchcontact)
    return render(request, 'manager_app/researchcontact_dropdown_list_options.html', {'researchcontact': researchcontact})


def load_email(request):
    colllab_id = request.GET.get('colllab_id')

    researchcontact = CollaboratorPersonInfo.objects.get(id=colllab_id)
    # print(researchcontact.email)
    return render(request, 'manager_app/email_dropdown_list_options.html', {'researchcontact': researchcontact})


@transaction.atomic
def ServiceRequestCreateView(request):

    data_requestitem = {}
    data_request = {}

    servicerequest_form = ServiceRequestCreationForm(
        request.POST or None, initial={'institute': 'uc'})
    ServiceRequestItemFormSet = formset_factory(
        ServiceRequestItemCreationForm, can_delete=True)
    servicerequestitems_formset = ServiceRequestItemFormSet(
        request.POST or None)

    serviceinfo_list = ServiceInfo.objects.all()
    today = datetime.date.today()
    datesplit = str(datetime.date.today()).split('-')
    now = datetime.datetime.now()

    writelines = []
    duplicate = {}

    if request.method == 'POST':
        if servicerequest_form.is_valid():
            group_name = servicerequest_form.cleaned_data['group']
            institute = servicerequest_form.cleaned_data['institute']
            research_contact = servicerequest_form.cleaned_data['research_contact']
            research_contact_email = servicerequest_form.cleaned_data['research_contact_email']

            all_quote_list = ServiceRequest.objects.values_list(
                'quote_number', flat=True)
            all_quote = []
            for qs in all_quote_list:
                for q in qs:
                    all_quote.append(q)

            # print(all_quote)
            all_quote_number = [int(x.split(' ')[-1]) for x in all_quote if x]
            if all_quote_number:
                max_quote = max(all_quote_number)
            else:
                max_quote = 0
            this_service_request_id = ' '.join([group_name.split(' ')[0][0].upper()+group_name.split(' ')[-1][0].upper(
            ), datesplit[1]+datesplit[2]+datesplit[0][-2:], str(now.hour).zfill(2)+str(now.minute).zfill(2)])
            this_quote_nunmber = ' '.join([group_name.split(' ')[0][0].upper()+group_name.split(
                ' ')[-1][0].upper(), datesplit[1]+datesplit[2]+datesplit[0][-2:], str(max_quote+1).zfill(4)])

            # print(institute)
            if servicerequestitems_formset.is_valid():
                for form in servicerequestitems_formset.forms:
                    if form not in servicerequestitems_formset.deleted_forms and form.cleaned_data:
                        service = form.cleaned_data['service']
                        quantity = form.cleaned_data['quantity']
                        service = servicetarget(service, quantity)

                        if service.service_name in data_requestitem.keys():
                            duplicate[service.service_name] += 1
                            this_service_name = service.service_name + \
                                'duplicate#' + \
                                str(duplicate[service.service_name])
                        else:
                            this_service_name = service.service_name
                            duplicate[service.service_name] = 1

                        if institute == 'uc':
                            data_requestitem[this_service_name] = {
                                'rate(uc users)': str(service.uc_rate)+'/'+service.rate_unit,
                                'rate_number': service.uc_rate,
                                'quantity': quantity,
                                'rate_unit': service.rate_unit,
                            }
                        elif institute == 'non_uc':
                            data_requestitem[this_service_name] = {
                                'rate(non-uc users)': str(service.nonuc_rate)+'/'+service.rate_unit,
                                'rate_number': service.nonuc_rate,
                                'quantity': quantity,
                                'rate_unit': service.rate_unit,
                            }
                        elif institute == 'industry':
                            data_requestitem[this_service_name] = {
                                'rate(industry users)': str(service.industry_rate)+'/'+service.rate_unit,
                                'rate_number': service.industry_rate,
                                'quantity': quantity,
                                'rate_unit': service.rate_unit,
                            }
                total_price = sum([float(x['rate_number'])*float(x['quantity'])
                                   for x in data_requestitem.values()])
                total_expression = '+'.join(['$'+str(x['rate_number'])+'*'+str(
                    x['quantity'])+' '+x['rate_unit']+'s' for x in data_requestitem.values()])+' = $'+str(total_price)

                data_request = {
                    'service_request_id': this_service_request_id,
                    'quote_number': this_quote_nunmber,
                    'quote_amount': '$'+str(total_price),
                    'date': str(today),
                    'group': group_name,
                    'institute': institute,
                    'status': 'initiate',
                    'research_contact': research_contact,
                    'research_contact_email': research_contact_email,
                    'notes': servicerequest_form.cleaned_data['notes'],
                }
                if 'Preview' in request.POST:
                    if institute == 'uc':
                        displayorde_requestitem = [
                            'rate(uc users)', 'quantity']
                    elif institute == 'non_uc':
                        displayorde_requestitem = [
                            'rate(non-uc users)', 'quantity']
                    elif institute == 'industry':
                        displayorde_requestitem = [
                            'rate(industry users)', 'quantity']
                    displayorder_request = ['service_request_id', 'quote_number', 'quote_amount', 'date',
                                            'group', 'institute', 'research_contact', 'research_contact_email', 'notes', 'status']
                    # print(data_request)

                    context = {
                        'servicerequest_form': servicerequest_form,
                        'servicerequestitems_formset': servicerequestitems_formset,
                        'modalshow': 1,
                        'displayorde_requestitem': displayorde_requestitem,
                        'displayorder_request': displayorder_request,
                        'data_requestitem': data_requestitem,
                        'data_request': data_request,
                        'total_expression': total_expression,
                        'serviceinfo_list': serviceinfo_list,
                    }
                    return render(request, 'manager_app/manager_feeforservice_servicerequestcreate_new.html', context)

                if 'Save' in request.POST:
                    thisrequest = ServiceRequest.objects.create(
                        group=group_name,
                        institute=data_request['institute'],
                        service_request_id=data_request['service_request_id'],
                        quote_number=[data_request['quote_number']],
                        quote_amount=[data_request['quote_amount']],
                        quote_pdf=[True],
                        date=data_request['date'],
                        research_contact=data_request['research_contact'],
                        research_contact_email=data_request['research_contact_email'],
                        notes=data_request['notes'],
                        status=data_request['status'],
                    )
                    service_items = []
                    service_quantities = []
                    for item in data_requestitem.keys():
                        ServiceRequestItem.objects.create(
                            request=thisrequest,
                            service=ServiceInfo.objects.get(
                                service_name=item.split('duplicate#')[0]),
                            quantity=data_requestitem[item]['quantity'],
                        )
                        service_items.append(item.split('duplicate#')[0])
                        #this_service_item = ServiceInfo.objects.get(service_name=item)
                        service_quantities.append(
                            data_requestitem[item]['quantity'])
                    quote_compact = ''.join(
                        data_request['quote_number'].split(' '))
                    collab_info = [group_name, research_contact,
                                   research_contact_email+'\n']
                    dear = 'Dr. ' + group_name.split(' ')[-1]

                    writelines = writelines+collab_info
                    writelines.append('Dear '+dear+',\n')
                    writelines.append(
                        quotebody(service_items, service_quantities, institute))

                    pdf_context = {
                        'quote_id': quote_compact,
                        'date': today.strftime('%B')+' '+str(today.day)+daysuffix(today.day)+', '+str(today.year),
                        'body': '\n'.join(writelines),
                    }

                    html_string = render_to_string(
                        'manager_app/quote_pdf_text_update_template.html', pdf_context)
                    pdf_name = quote_compact+'.pdf'
                    html = HTML(string=html_string,
                                base_url=request.build_absolute_uri())
                    html.write_pdf(target=os.path.join(
                        settings.QUOTE_DIR, pdf_name))

                    with open(os.path.join(settings.QUOTE_DIR, quote_compact+'.txt'), 'w') as fw:
                        print(os.path.join(
                            settings.QUOTE_DIR, quote_compact+'.txt'))
                        fw.write('\n'.join(writelines))

                    return redirect('manager_app:servicerequests_list')

    context = {
        'servicerequest_form': servicerequest_form,
        'servicerequestitems_formset': servicerequestitems_formset,
        'serviceinfo_list': serviceinfo_list,
    }

    return render(request, 'manager_app/manager_feeforservice_servicerequestcreate_new.html', context)


@transaction.atomic
def ServiceRequestUpdateView(request, pk):
    thiservicerequest = get_object_or_404(ServiceRequest, pk=pk)
    this_quote_nunmber = thiservicerequest.quote_number[-1]

    data_requestitem = {}
    data_request = {}

    servicerequest_form = ServiceRequestCreationForm(
        request.POST or None, instance=thiservicerequest)

    ServiceRequestItemInlineFormSet = inlineformset_factory(ServiceRequest, ServiceRequestItem, fields=[
        'service', 'quantity'], extra=1)
    servicerequestitems_formset = ServiceRequestItemInlineFormSet(
        request.POST or None, instance=thiservicerequest)

    today = datetime.date.today()
    datesplit = str(datetime.date.today()).split('-')
    writelines = []

    if servicerequest_form.is_valid():
        group_name = servicerequest_form.cleaned_data['group']
        institute = servicerequest_form.cleaned_data['institute']
        research_contact = servicerequest_form.cleaned_data['research_contact']
        research_contact_email = servicerequest_form.cleaned_data['research_contact_email']

        this_service_request_id = thiservicerequest.service_request_id
        # print(institute)
        if servicerequestitems_formset.is_valid():
            for form in servicerequestitems_formset.forms:
                if form not in servicerequestitems_formset.deleted_forms and form.cleaned_data:
                    service = form.cleaned_data['service']
                    quantity = form.cleaned_data['quantity']
                    if service.service_name == 'ATAC-seq':
                        if float(quantity) > 24 and float(quantity) <= 96:
                            service = ServiceInfo.objects.get(
                                service_name='ATAC-seq_24')
                        elif float(quantity) > 96:
                            service = ServiceInfo.objects.get(
                                service_name='ATAC-seq_96')

                    if institute == 'uc':
                        data_requestitem[service.service_name] = {
                            'rate(uc users)': str(service.uc_rate)+'/'+service.rate_unit,
                            'rate_number': service.uc_rate,
                            'quantity': quantity,
                            'rate_unit': service.rate_unit,
                        }
                    elif institute == 'non_uc':
                        data_requestitem[service.service_name] = {
                            'rate(non-uc users)': str(service.nonuc_rate)+'/'+service.rate_unit,
                            'rate_number': service.nonuc_rate,
                            'quantity': quantity,
                            'rate_unit': service.rate_unit,
                        }
                    elif institute == 'industry':
                        data_requestitem[service.service_name] = {
                            'rate(industry users)': str(service.industry_rate)+'/'+service.rate_unit,
                            'rate_number': service.industry_rate,
                            'quantity': quantity,
                            'rate_unit': service.rate_unit,
                        }

            total_price = sum([float(x['rate_number'])*float(x['quantity'])
                               for x in data_requestitem.values()])
            total_expression = '+'.join(['$'+str(x['rate_number'])+'*'+str(x['quantity'])+' ' +
                                         x['rate_unit']+'s' for x in data_requestitem.values()])+' = $'+str(total_price)

            data_request = {
                'service_request_id': this_service_request_id,
                'quote_number': this_quote_nunmber,
                'quote_amount': '$'+str(total_price),
                'date': str(today),
                'group': group_name,
                'institute': institute,
                'status': 'initiate',
                'research_contact': research_contact,
                'research_contact_email': research_contact_email,
                'notes': servicerequest_form.cleaned_data['notes'],
            }
            if 'Preview' in request.POST:
                if institute == 'uc':
                    displayorde_requestitem = ['rate(uc users)', 'quantity']
                elif institute == 'non_uc':
                    displayorde_requestitem = [
                        'rate(non-uc users)', 'quantity']
                elif institute == 'industry':
                    displayorde_requestitem = [
                        'rate(industry users)', 'quantity']
                displayorder_request = ['service_request_id', 'quote_number', 'quote_amount', 'date',
                                        'group', 'institute', 'research_contact', 'research_contact_email', 'notes', 'status']
                # print(data_request)

                context = {
                    'servicerequest_form': servicerequest_form,
                    'servicerequestitems_formset': servicerequestitems_formset,
                    'modalshow': 1,
                    'displayorde_requestitem': displayorde_requestitem,
                    'displayorder_request': displayorder_request,
                    'data_requestitem': data_requestitem,
                    'data_request': data_request,
                    'total_expression': total_expression,
                    'this_quote_nunmber': this_quote_nunmber,
                }
                return render(request, 'manager_app/manager_feeforservice_servicerequestupdate.html', context)

            if 'Save' in request.POST:
                thiservicerequest = servicerequest_form.save(commit=False)
                thiservicerequest.date = data_request['date']
                thiservicerequest.status = data_request['status']
                thiservicerequest.quote_amount[-1] = data_request['quote_amount']
                thiservicerequest.save()
                servicerequestitems_formset.save()

                service_items = []
                service_quantities = []
                for item in data_requestitem.keys():
                    service_items.append(item)
                    this_service_item = ServiceInfo.objects.get(
                        service_name=item)
                    service_quantities.append(
                        data_requestitem[item]['quantity'])
                quote_compact = ''.join(
                    data_request['quote_number'].split(' '))
                collab_info = [group_name, research_contact,
                               research_contact_email+'\n']
                dear = 'Dr. ' + group_name.split(' ')[-1]

                writelines = writelines+collab_info
                writelines.append('Dear '+dear+',\n')
                writelines.append(
                    quotebody(service_items, service_quantities, institute))

                pdf_context = {
                    'quote_id': quote_compact,
                    'date': today.strftime('%B')+' '+str(today.day)+daysuffix(today.day)+', '+str(today.year),
                    'body': '\n'.join(writelines),

                }

                html_string = render_to_string(
                    'manager_app/quote_pdf_text_update_template.html', pdf_context)
                pdf_name = quote_compact+'.pdf'
                html = HTML(string=html_string,
                            base_url=request.build_absolute_uri())
                html.write_pdf(target=os.path.join(
                    settings.QUOTE_DIR, pdf_name))

                with open(os.path.join(settings.QUOTE_DIR, quote_compact+'.txt'), 'w') as fw:
                    print(os.path.join(settings.QUOTE_DIR, quote_compact+'.txt'))
                    fw.write('\n'.join(writelines))

                return redirect('manager_app:servicerequests_list')
    context = {
        'servicerequest_form': servicerequest_form,
        'servicerequestitems_formset': servicerequestitems_formset,
        'this_quote_nunmber': this_quote_nunmber,
    }

    return render(request, 'manager_app/manager_feeforservice_servicerequestupdate.html', context)


@transaction.atomic
def ServiceRequestUpdateViewNew(request, pk):
    thiservicerequest = get_object_or_404(ServiceRequest, pk=pk)
    this_quote_nunmber = thiservicerequest.quote_number[-1]

    data_requestitem = {}
    data_request = {}

    servicerequest_form = ServiceRequestCreationForm(
        request.POST or None, instance=thiservicerequest)

    itemsinfo = thiservicerequest.servicerequestitem_set.all().select_related('service')
    datainitial = []
    for item in itemsinfo:
        x = {
            'service': item.service,
            'quantity': item.quantity,
        }

        datainitial.append(serviceitemcollapse(x))

    ServiceRequestItemInlineFormSet = inlineformset_factory(ServiceRequest, ServiceRequestItem, form=ServiceRequestItemCreationForm, fields=[
        'service', 'quantity'], extra=itemsinfo.count())

    servicerequestitems_formset = ServiceRequestItemInlineFormSet(
        request.POST or None, initial=datainitial)
    #servicerequestitems_formset.extra = itemsinfo.count()

    # print(servicerequestitems_formset)

    today = datetime.date.today()
    datesplit = str(datetime.date.today()).split('-')
    writelines = []
    duplicate = {}

    if servicerequest_form.is_valid():
        group_name = servicerequest_form.cleaned_data['group']
        institute = servicerequest_form.cleaned_data['institute']
        research_contact = servicerequest_form.cleaned_data['research_contact']
        research_contact_email = servicerequest_form.cleaned_data['research_contact_email']

        this_service_request_id = thiservicerequest.service_request_id
        # print(institute)
        if servicerequestitems_formset.is_valid():
            for form in servicerequestitems_formset.forms:
                if form not in servicerequestitems_formset.deleted_forms and form.cleaned_data:
                    service = form.cleaned_data['service']
                    quantity = form.cleaned_data['quantity']
                    service = servicetarget(service, quantity)

                    if service.service_name in data_requestitem.keys():
                        duplicate[service.service_name] += 1
                        this_service_name = service.service_name + \
                            'duplicate#' + str(duplicate[service.service_name])
                    else:
                        this_service_name = service.service_name
                        duplicate[service.service_name] = 1

                    if institute == 'uc':
                        data_requestitem[this_service_name] = {
                            'rate(uc users)': str(service.uc_rate)+'/'+service.rate_unit,
                            'rate_number': service.uc_rate,
                            'quantity': quantity,
                            'rate_unit': service.rate_unit,
                        }
                    elif institute == 'non_uc':
                        data_requestitem[this_service_name] = {
                            'rate(non-uc users)': str(service.nonuc_rate)+'/'+service.rate_unit,
                            'rate_number': service.nonuc_rate,
                            'quantity': quantity,
                            'rate_unit': service.rate_unit,
                        }
                    elif institute == 'industry':
                        data_requestitem[this_service_name] = {
                            'rate(industry users)': str(service.industry_rate)+'/'+service.rate_unit,
                            'rate_number': service.industry_rate,
                            'quantity': quantity,
                            'rate_unit': service.rate_unit,
                        }

            total_price = sum([float(x['rate_number'])*float(x['quantity'])
                               for x in data_requestitem.values()])
            total_expression = '+'.join(['$'+str(x['rate_number'])+'*'+str(x['quantity'])+' ' +
                                         x['rate_unit']+'s' for x in data_requestitem.values()])+' = $'+str(total_price)

            data_request = {
                'service_request_id': this_service_request_id,
                'quote_number': this_quote_nunmber,
                'quote_amount': '$'+str(total_price),
                'date': str(today),
                'group': group_name,
                'institute': institute,
                'status': 'initiate',
                'research_contact': research_contact,
                'research_contact_email': research_contact_email,
                'notes': servicerequest_form.cleaned_data['notes'],
            }
            if 'Preview' in request.POST:
                if institute == 'uc':
                    displayorde_requestitem = ['rate(uc users)', 'quantity']
                elif institute == 'non_uc':
                    displayorde_requestitem = [
                        'rate(non-uc users)', 'quantity']
                elif institute == 'industry':
                    displayorde_requestitem = [
                        'rate(industry users)', 'quantity']
                displayorder_request = ['service_request_id', 'quote_number', 'quote_amount', 'date',
                                        'group', 'institute', 'research_contact', 'research_contact_email', 'notes', 'status']
                # print(data_request)
                print(data_requestitem)

                context = {
                    'servicerequest_form': servicerequest_form,
                    'servicerequestitems_formset': servicerequestitems_formset,
                    'modalshow': 1,
                    'displayorde_requestitem': displayorde_requestitem,
                    'displayorder_request': displayorder_request,
                    'data_requestitem': data_requestitem,
                    'data_request': data_request,
                    'total_expression': total_expression,
                    'this_quote_nunmber': this_quote_nunmber,
                }
                return render(request, 'manager_app/manager_feeforservice_servicerequestupdate.html', context)

            if 'Save' in request.POST:
                thiservicerequest = servicerequest_form.save(commit=False)
                thiservicerequest.date = data_request['date']
                thiservicerequest.status = data_request['status']
                thiservicerequest.quote_amount[-1] = data_request['quote_amount']
                thiservicerequest.save()
                thiservicerequest.servicerequestitem_set.all().delete()

                service_items = []
                service_quantities = []
                for item in data_requestitem.keys():
                    ServiceRequestItem.objects.create(
                        request=thiservicerequest,
                        service=ServiceInfo.objects.get(
                            service_name=item.split('duplicate#')[0]),
                        quantity=data_requestitem[item]['quantity'],
                    )
                    service_items.append(item.split('duplicate#')[0])
                    service_quantities.append(
                        data_requestitem[item]['quantity'])
                quote_compact = ''.join(
                    data_request['quote_number'].split(' '))
                collab_info = [group_name, research_contact,
                               research_contact_email+'\n']
                dear = 'Dr. ' + group_name.split(' ')[-1]

                writelines = writelines+collab_info
                writelines.append('Dear '+dear+',\n')
                writelines.append(
                    quotebody(service_items, service_quantities, institute))

                pdf_context = {
                    'quote_id': quote_compact,
                    'date': today.strftime('%B')+' '+str(today.day)+daysuffix(today.day)+', '+str(today.year),
                    'body': '\n'.join(writelines),

                }

                html_string = render_to_string(
                    'manager_app/quote_pdf_text_update_template.html', pdf_context)
                pdf_name = quote_compact+'.pdf'
                html = HTML(string=html_string,
                            base_url=request.build_absolute_uri())
                html.write_pdf(target=os.path.join(
                    settings.QUOTE_DIR, pdf_name))

                with open(os.path.join(settings.QUOTE_DIR, quote_compact+'.txt'), 'w') as fw:
                    print(os.path.join(settings.QUOTE_DIR, quote_compact+'.txt'))
                    fw.write('\n'.join(writelines))

                return redirect('manager_app:servicerequests_list')
    context = {
        'servicerequest_form': servicerequest_form,
        'servicerequestitems_formset': servicerequestitems_formset,
        'this_quote_nunmber': this_quote_nunmber,
    }

    return render(request, 'manager_app/manager_feeforservice_servicerequestupdate.html', context)


@transaction.atomic
def ServiceRequestAddNewQuoteView(request, pk):
    thiservicerequest = get_object_or_404(ServiceRequest, pk=pk)

    data_requestitem = {}
    data_request = {}

    servicerequest_form = ServiceRequestCreationForm(
        request.POST or None, instance=thiservicerequest)

    itemsinfo = thiservicerequest.servicerequestitem_set.all().select_related('service')
    datainitial = []
    for item in itemsinfo:
        x = {
            'service': item.service,
            'quantity': item.quantity,
        }

        datainitial.append(serviceitemcollapse(x))

    ServiceRequestItemInlineFormSet = inlineformset_factory(ServiceRequest, ServiceRequestItem, form=ServiceRequestItemCreationForm, fields=[
        'service', 'quantity'])

    servicerequestitems_formset = ServiceRequestItemInlineFormSet(
        request.POST or None, initial=datainitial)

    servicerequestitems_formset.extra = itemsinfo.count()

    today = datetime.date.today()
    datesplit = str(datetime.date.today()).split('-')
    writelines = []
    duplicate = {}

    if servicerequest_form.is_valid():
        group_name = servicerequest_form.cleaned_data['group']
        institute = servicerequest_form.cleaned_data['institute']
        research_contact = servicerequest_form.cleaned_data['research_contact']
        research_contact_email = servicerequest_form.cleaned_data['research_contact_email']
        all_quote_list = ServiceRequest.objects.values_list(
            'quote_number', flat=True)
        all_quote = []
        for qs in all_quote_list:
            for q in qs:
                all_quote.append(q)

        # print(all_quote)
        all_quote_number = [int(x.split(' ')[-1]) for x in all_quote if x]
        if all_quote_number:
            max_quote = max(all_quote_number)
        else:
            max_quote = 0

        this_quote_nunmber = ' '.join([group_name.split(' ')[0][0].upper()+group_name.split(
            ' ')[-1][0].upper(), datesplit[1]+datesplit[2]+datesplit[0][-2:], str(max_quote+1).zfill(4)])

        this_service_request_id = thiservicerequest.service_request_id
        # print(institute)
        if servicerequestitems_formset.is_valid():
            for form in servicerequestitems_formset.forms:
                if form not in servicerequestitems_formset.deleted_forms and form.cleaned_data:
                    service = form.cleaned_data['service']
                    quantity = form.cleaned_data['quantity']
                    service = servicetarget(service, quantity)

                    if service.service_name in data_requestitem.keys():
                        duplicate[service.service_name] += 1
                        this_service_name = service.service_name + \
                            'duplicate#' + str(duplicate[service.service_name])
                    else:
                        this_service_name = service.service_name
                        duplicate[service.service_name] = 1

                    if institute == 'uc':
                        data_requestitem[this_service_name] = {
                            'rate(uc users)': str(service.uc_rate)+'/'+service.rate_unit,
                            'rate_number': service.uc_rate,
                            'quantity': quantity,
                            'rate_unit': service.rate_unit,
                        }
                    elif institute == 'non_uc':
                        data_requestitem[this_service_name] = {
                            'rate(non-uc users)': str(service.nonuc_rate)+'/'+service.rate_unit,
                            'rate_number': service.nonuc_rate,
                            'quantity': quantity,
                            'rate_unit': service.rate_unit,
                        }
                    elif institute == 'industry':
                        data_requestitem[this_service_name] = {
                            'rate(industry users)': str(service.industry_rate)+'/'+service.rate_unit,
                            'rate_number': service.industry_rate,
                            'quantity': quantity,
                            'rate_unit': service.rate_unit,
                        }

            total_price = sum([float(x['rate_number'])*float(x['quantity'])
                               for x in data_requestitem.values()])
            total_expression = '+'.join(['$'+str(x['rate_number'])+'*'+str(x['quantity'])+' ' +
                                         x['rate_unit']+'s' for x in data_requestitem.values()])+' = $'+str(total_price)

            data_request = {
                'service_request_id': this_service_request_id,
                'quote_number': this_quote_nunmber,
                'quote_amount': '$'+str(total_price),
                'date': str(today),
                'group': group_name,
                'institute': institute,
                'status': 'initiate',
                'research_contact': research_contact,
                'research_contact_email': research_contact_email,
                'notes': servicerequest_form.cleaned_data['notes'],
            }
            if 'Preview' in request.POST:
                if institute == 'uc':
                    displayorde_requestitem = ['rate(uc users)', 'quantity']
                elif institute == 'non_uc':
                    displayorde_requestitem = [
                        'rate(non-uc users)', 'quantity']
                elif institute == 'industry':
                    displayorde_requestitem = [
                        'rate(industry users)', 'quantity']
                displayorder_request = ['service_request_id', 'quote_number', 'quote_amount', 'date',
                                        'group', 'institute', 'research_contact', 'research_contact_email', 'notes', 'status']
                # print(data_request)

                context = {
                    'servicerequest_form': servicerequest_form,
                    'servicerequestitems_formset': servicerequestitems_formset,
                    'modalshow': 1,
                    'displayorde_requestitem': displayorde_requestitem,
                    'displayorder_request': displayorder_request,
                    'data_requestitem': data_requestitem,
                    'data_request': data_request,
                    'total_expression': total_expression,
                }
                return render(request, 'manager_app/manager_feeforservice_servicerequest_addanewquote.html', context)

            if 'Save' in request.POST:
                thiservicerequest = servicerequest_form.save(commit=False)
                thiservicerequest.date = data_request['date']
                thiservicerequest.status = data_request['status']
                thiservicerequest.quote_amount.append(
                    data_request['quote_amount'])
                thiservicerequest.quote_number.append(
                    data_request['quote_number'])
                thiservicerequest.quote_pdf.append(True)
                thiservicerequest.save()
                thiservicerequest.servicerequestitem_set.all().delete()

                service_items = []
                service_quantities = []
                for item in data_requestitem.keys():
                    ServiceRequestItem.objects.create(
                        request=thiservicerequest,
                        service=ServiceInfo.objects.get(
                            service_name=item.split('duplicate#')[0]),
                        quantity=data_requestitem[item]['quantity'],
                    )
                    service_items.append(item.split('duplicate#')[0])
                    service_quantities.append(
                        data_requestitem[item]['quantity'])
                quote_compact = ''.join(
                    data_request['quote_number'].split(' '))
                collab_info = [group_name, research_contact,
                               research_contact_email+'\n']
                dear = 'Dr. ' + group_name.split(' ')[-1]

                writelines = writelines+collab_info
                writelines.append('Dear '+dear+',\n')
                writelines.append(
                    quotebody(service_items, service_quantities, institute))

                pdf_context = {
                    'quote_id': quote_compact,
                    'date': today.strftime('%B')+' '+str(today.day)+daysuffix(today.day)+', '+str(today.year),
                    'body': '\n'.join(writelines),

                }

                html_string = render_to_string(
                    'manager_app/quote_pdf_text_update_template.html', pdf_context)
                pdf_name = quote_compact+'.pdf'
                html = HTML(string=html_string,
                            base_url=request.build_absolute_uri())
                html.write_pdf(target=os.path.join(
                    settings.QUOTE_DIR, pdf_name))

                with open(os.path.join(settings.QUOTE_DIR, quote_compact+'.txt'), 'w') as fw:
                    print(os.path.join(settings.QUOTE_DIR, quote_compact+'.txt'))
                    fw.write('\n'.join(writelines))

                return redirect('manager_app:servicerequests_list')
    context = {
        'servicerequest_form': servicerequest_form,
        'servicerequestitems_formset': servicerequestitems_formset,
    }

    return render(request, 'manager_app/manager_feeforservice_servicerequest_addanewquote.html', context)


@transaction.atomic
def ServiceRequestCreateViewOld(request):

    data_requestitem = {}
    data_request = {}

    contact_form = ContactForm(request.POST or None)
    ServiceRequestItemFormSet = formset_factory(
        ServiceRequestItemCreationForm, can_delete=True)
    servicerequestitems_formset = ServiceRequestItemFormSet(
        request.POST or None)

    today = datetime.date.today()
    datesplit = str(datetime.date.today()).split('-')

    if request.method == 'POST':
        servicerequest_form = ServiceRequestCreationForm(request.POST)
        if servicerequest_form.is_valid() and contact_form.is_valid():
            group_name = contact_form.cleaned_data['group']
            research_contact = contact_form.cleaned_data['research_contact']
            research_contact_name = research_contact.person_id.first_name + \
                ' '+research_contact.person_id.last_name
            research_contact_email = contact_form.cleaned_data['research_contact_email']
            print(research_contact_email)
            groupinfo = Group.objects.get(name=group_name)
            all_quote_list = ServiceRequest.objects.values_list(
                'quote_number', flat=True)
            all_quote = []
            for qs in all_quote_list:
                for q in qs:
                    all_quote.append(q)

            print(all_quote)
            all_quote_number = [int(x.split(' ')[-1]) for x in all_quote if x]
            if all_quote_number:
                max_quote = max(all_quote_number)
            else:
                max_quote = 0
            this_service_request_id = ' '.join([group_name.split(' ')[0][0].upper(
            )+group_name.split(' ')[-1][0].upper(), datesplit[1]+datesplit[2]+datesplit[0][-2:]])
            this_quote_nunmber = ' '.join([group_name.split(' ')[0][0].upper()+group_name.split(
                ' ')[-1][0].upper(), datesplit[1]+datesplit[2]+datesplit[0][-2:], str(max_quote+1).zfill(4)])
            data_request = {
                'service_request_id': this_service_request_id,
                'quote_number': this_quote_nunmber,
                'date': str(today),
                'group': group_name,
                'status': 'initiate',
                'research_contact': research_contact_name,
                'research_contact_email': research_contact_email,
                'notes': servicerequest_form.cleaned_data['notes'],
            }
            try:
                institute = Group_Institution.objects.get(
                    group=groupinfo).institution.lower()
            except:
                institute = 'non-ucsd'
            # print(institute)
            if servicerequestitems_formset.is_valid():
                for form in servicerequestitems_formset.forms:
                    if form not in servicerequestitems_formset.deleted_forms and form.cleaned_data:
                        service = form.cleaned_data['service']
                        quantity = form.cleaned_data['quantity']
                        if service.service_name == 'ATAC-seq':
                            if float(quantity) > 24 and float(quantity) <= 96:
                                service = ServiceInfo.objects.get(
                                    service_name='ATAC-seq_24')
                            elif float(quantity) > 96:
                                service = ServiceInfo.objects.get(
                                    service_name='ATAC-seq_96')
                        # print(service.service_name)

                        if institute == 'ucsd':
                            data_requestitem[service.service_name] = {
                                'rate(uc users)': str(service.uc_rate)+'/'+service.rate_unit,
                                'rate_number': service.uc_rate,
                                'quantity': quantity,
                                'rate_unit': service.rate_unit,
                            }
                        else:
                            data_requestitem[service.service_name] = {
                                'rate(non-uc users)': str(service.nonuc_rate)+'/'+service.rate_unit,
                                'rate_number': service.nonuc_rate,
                                'quantity': quantity,
                                'rate_unit': service.rate_unit,
                            }
                total_price = sum([float(x['rate_number'])*float(x['quantity'])
                                   for x in data_requestitem.values()])
                total_expression = '+'.join(['$'+str(x['rate_number'])+'*'+str(
                    x['quantity'])+' '+x['rate_unit']+'s' for x in data_requestitem.values()])+' = $'+str(total_price)

                if 'Preview' in request.POST:
                    if institute == 'ucsd':
                        displayorde_requestitem = [
                            'rate(uc users)', 'quantity']
                    else:
                        displayorde_requestitem = [
                            'rate(non-uc users)', 'quantity']
                    displayorder_request = ['service_request_id', 'quote_number', 'date',
                                            'group', 'research_contact', 'research_contact_email', 'notes', 'status']
                    # print(data_request)

                    context = {
                        'contact_form': contact_form,
                        'servicerequest_form': servicerequest_form,
                        'servicerequestitems_formset': servicerequestitems_formset,
                        'modalshow': 1,
                        'displayorde_requestitem': displayorde_requestitem,
                        'displayorder_request': displayorder_request,
                        'data_requestitem': data_requestitem,
                        'data_request': data_request,
                        'total_expression': total_expression
                    }
                    return render(request, 'manager_app/manager_feeforservice_servicerequestcreate.html', context)

                if 'Save' in request.POST:
                    thisrequest = ServiceRequest.objects.create(
                        group=groupinfo,
                        service_request_id=data_request['service_request_id'],
                        quote_number=[data_request['quote_number']],
                        date=data_request['date'],
                        research_contact=research_contact,
                        research_contact_email=data_request['research_contact_email'],
                        notes=data_request['notes'],
                        status=data_request['status'],
                    )
                    service_items = []
                    service_breakdown = []
                    for item in data_requestitem.keys():
                        print(item)
                        print(data_requestitem[item]['quantity'])
                        ServiceRequestItem.objects.create(
                            request=thisrequest,
                            service=ServiceInfo.objects.get(service_name=item),
                            quantity=data_requestitem[item]['quantity'],
                        )
                        service_items.append(item)
                        this_service_item = ServiceInfo.objects.get(
                            service_name=item)
                        service_breakdown.append(':'.join([this_service_item.description_brief, str(
                            data_requestitem[item]['rate_number'])+'/'+this_service_item.rate_unit]))
                    quote_compact = ''.join(
                        data_request['quote_number'].split(' '))
                    collab_info = [
                        group_name, research_contact_name, research_contact_email]
                    dear = 'Dr. ' + group_name.split(' ')[-1]
                    service_items = ','.join(set(service_items))

                    pdf_context = {
                        'quote_id': quote_compact,
                        'date': today.strftime('%B')+' '+str(today.day)+daysuffix(today.day)+','+str(today.year),
                        'collab_info': collab_info,
                        'dear': dear,
                        'service_items': service_items,
                        'service_breakdown': service_breakdown,
                        'total_expression': total_expression,

                    }

                    paragraphs = ['first paragraph',
                                  'second paragraph', 'third paragraph']
                    html_string = render_to_string(
                        'manager_app/quote_pdf_template.html', pdf_context)
                    pdf_name = quote_compact+'.pdf'
                    html = HTML(string=html_string,
                                base_url=request.build_absolute_uri())
                    html.write_pdf(target=os.path.join(
                        settings.QUOTE_DIR, pdf_name))

                    return redirect('manager_app:servicerequests_list')

    else:
        servicerequest_form = ServiceRequestCreationForm(None)

    context = {
        'contact_form': contact_form,
        'servicerequest_form': servicerequest_form,
        'servicerequestitems_formset': servicerequestitems_formset,
    }

    return render(request, 'manager_app/manager_feeforservice_servicerequestcreate_old.html', context)


def ServiceRequestDataViewOld(request):
    ServiceRequest_list = ServiceRequest.objects.all().select_related('group', 'research_contact__person_id').prefetch_related(Prefetch('group__group_institution_set')).values('pk', 'service_request_id', 'quote_number',
                                                                                                                                                                                'date', 'group__name', 'research_contact__person_id__first_name', 'research_contact__person_id__last_name', 'research_contact_email', 'status', 'notes', 'group__group_institution__institution')
    data = list(ServiceRequest_list)

    return JsonResponse(data, safe=False)


def ServiceRequestDataView(request):
    ServiceRequest_list = ServiceRequest.objects.all().values('pk', 'service_request_id', 'quote_number',
                                                              'date', 'group', 'institute', 'research_contact', 'research_contact_email', 'status', 'notes')
    data = list(ServiceRequest_list)

    return JsonResponse(data, safe=False)


def QuotePdfView(request, quoteid):
    if not request.user.groups.filter(name='manager').exists():
        raise PermissionDenied
    pdf_name = quoteid+'.pdf'
    pdf_path = os.path.join(settings.QUOTE_DIR, pdf_name)
    with open(pdf_path, 'rb') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="'+pdf_name+'"'
        return response


def QuoteTextUpdateView(request, quoteid):
    quote_compact = ''.join(quoteid.split(' '))
    initial_body = ''
    with open(os.path.join(settings.QUOTE_DIR, quote_compact+'.txt'), 'r') as f:
        for line in f:
            initial_body = initial_body+line

    text_form = QuoteTextForm(request.POST or None, initial={
                              'body': initial_body})
    today = datetime.date.today()

    if text_form.is_valid():
        body = text_form.cleaned_data['body']
        pdf_context = {
            'quote_id': quote_compact,
            'date': today.strftime('%B')+' '+str(today.day)+daysuffix(today.day)+', '+str(today.year),
            'body': body,
        }

        html_string = render_to_string(
            'manager_app/quote_pdf_text_update_template.html', pdf_context)
        pdf_name = quote_compact+'.pdf'
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        html.write_pdf(target=os.path.join(settings.QUOTE_DIR, pdf_name))
        with open(os.path.join(settings.QUOTE_DIR, quote_compact+'.txt'), 'w') as fw:
            fw.write(body)

        return redirect('manager_app:servicerequests_list')
    context = {
        'quote_id': quote_compact,
        'text_form': text_form,
        'quoteid': quoteid,
    }

    return render(request, 'manager_app/quote_pdf_text_update.html', context)


@transaction.atomic
def QuoteAddView(request):
    if not request.user.groups.filter(name='manager').exists():
        raise PermissionDenied

    quotecreate_form = QuoteCreationForm(request.POST or None)
    quotes_form = QuoteBulkImportForm(None)
    today = datetime.date.today()
    datesplit = str(datetime.date.today()).split('-')

    if 'Preview' in request.POST or 'Save' in request.POST:
        print('ssss')
        if quotecreate_form.is_valid():
            group_name = quotecreate_form.cleaned_data['group']
            research_contact = quotecreate_form.cleaned_data['research_contact']
            this_amount = ''.join(
                quotecreate_form.cleaned_data['quote_amount'])
            print(quotecreate_form)
            print(quotecreate_form.cleaned_data['quote_amount'])
            if not this_amount.startswith('$'):
                this_amount = '$'+this_amount
            if '-' in this_amount:
                tm = []
                for x in this_amount.split('-'):
                    if not x.startswith('$'):
                        tm.append('$'+x)
                    else:
                        tm.append(x)
                this_amount = '-'.join(tm)

            all_quote_list = ServiceRequest.objects.values_list(
                'quote_number', flat=True)
            all_quote = []
            for qs in all_quote_list:
                for q in qs:
                    all_quote.append(q)

            all_quote_number = [int(x.split(' ')[-1]) for x in all_quote if x]
            if all_quote_number:
                max_quote = max(all_quote_number)
            else:
                max_quote = 0
            this_quote_nunmber = ' '.join([group_name.split(' ')[0][0].upper()+group_name.split(
                ' ')[-1][0].upper(), datesplit[1]+datesplit[2]+datesplit[0][-2:], str(max_quote+1).zfill(4)])
            data_request = {
                'quote_number': this_quote_nunmber,
                'date': str(today),
                'group': group_name,
                'research_contact': research_contact,
                'quote_amount': this_amount,
            }

            if 'Preview' in request.POST:
                displayorder_request = [
                    'quote_number', 'date', 'group', 'research_contact', 'quote_amount']
                # print(data_request)

                context = {
                    'quotecreate_form': quotecreate_form,
                    'modalshow': 1,
                    'displayorder_request': displayorder_request,
                    'data_request': data_request,
                    'quotes_form': quotes_form,
                }
                return render(request, 'manager_app/manager_feeforservice_quotecreate_import.html', context)

            if 'Save' in request.POST:
                thisrequest = ServiceRequest.objects.create(
                    group=group_name,
                    quote_number=[data_request['quote_number']],
                    quote_amount=[data_request['quote_amount']],
                    quote_pdf=[False],
                    date=data_request['date'],
                    research_contact=data_request['research_contact'],
                )

                return redirect('manager_app:quote_list')

    elif 'BulkSave' in request.POST:
        quotes_form = QuoteBulkImportForm(request.POST)
        if quotes_form.is_valid():
            quotesinfo = quotes_form.cleaned_data['quotesinfo']
            for lineitem in quotesinfo.strip().split('\n'):
                fields = lineitem.split('\t')
                contact_info = fields[1].split('/')
                if len(contact_info) == 2:
                    group_name = contact_info[0].strip()
                    research_contact = contact_info[1].strip()
                elif len(contact_info) == 1:
                    group_name = contact_info[0].strip()
                    research_contact = ''
                this_date = datetransform2(fields[3].strip())

                thisrequest = ServiceRequest.objects.create(
                    group=group_name,
                    quote_number=[fields[4].strip()],
                    quote_amount=[fields[5].strip()],
                    quote_pdf=[False],
                    date=this_date,
                    research_contact=research_contact,
                )
            return redirect('manager_app:quote_list')

    context = {
        'quotecreate_form': quotecreate_form,
        'quotes_form': quotes_form,
    }

    return render(request, 'manager_app/manager_feeforservice_quotecreate_import.html', context)


def QuoteListView(request):
    if not request.user.groups.filter(name='manager').exists():
        raise PermissionDenied
    quote_list = []
    ServiceRequest_list = ServiceRequest.objects.all().values('pk', 'service_request_id',
                                                              'quote_number', 'date', 'group', 'research_contact', 'quote_amount', 'quote_pdf')
    for S in ServiceRequest_list:
        i = 0
        for quote in S['quote_number']:
            if S['quote_pdf']:
                this_data = {
                    'pk': S['pk'],
                    'service_request_id': S['service_request_id'],
                    'quote_number': quote,
                    'date': S['date'],
                    'group': S['group'],
                    'research_contact': S['research_contact'],
                    'quote_amount': S['quote_amount'][i],
                    'quote_pdf': S['quote_pdf'][i],
                }
            else:
                this_data = {
                    'pk': S['pk'],
                    'service_request_id': S['service_request_id'],
                    'quote_number': quote,
                    'date': S['date'],
                    'group': S['group'],
                    'research_contact': S['research_contact'],
                    'quote_amount': S['quote_amount'][i],
                    'quote_pdf': '',
                }

            i += 1
            quote_list.append(this_data)
    data = quote_list
    return JsonResponse(data, safe=False)


@transaction.atomic
def QuoteBulkAddView(request):
    quotes_form = QuoteBulkImportForm(request.POST or None)
    if quotes_form.is_valid():
        quotesinfo = quotes_form.cleaned_data['quotesinfo']
        for lineitem in quotesinfo.strip().split('\n'):
            fields = lineitem.split('\t')
            contact_info = fields[1].split('/')
            if len(contact_info) == 2:
                group_name = contact_info[0].strip()
                research_contact = contact_info[1].strip()
            elif len(contact_info) == 1:
                group_name = contact_info[0].strip()
                research_contact = ''
            this_date = datetransform2(fields[3].strip())

            thisrequest = ServiceRequest.objects.create(
                group=group_name,
                quote_number=[fields[4].strip()],
                quote_amount=[fields[5].strip()],
                date=this_date,
                research_contact=research_contact,
            )
        return redirect('manager_app:quote_list')
    context = {
        'quotes_form': quotes_form,
    }

    return render(request, 'manager_app/manager_feeforservice_quotebulkimport.html', context)


def QuotePdfUpload(request):
    if not request.user.groups.filter(name='manager').exists():
        raise PermissionDenied
    if request.method == 'POST':
        quotes_upload_form = QuoteUploadFileForm(request.POST, request.FILES)
        if quotes_upload_form.is_valid():
            file = request.FILES['file']
            print(quotes_upload_form.cleaned_data['quote_number'])
            file_name = quotes_upload_form.cleaned_data['quote_number']+'.pdf'
            fs = FileSystemStorage()
            filename = fs.save(file_name, file)
            subprocess.call("ln -s "+os.path.join(settings.MEDIA_ROOT, file_name) +
                            " "+os.path.join(settings.QUOTE_DIR, file_name), shell=True)
            return redirect('manager_app:quote_list')
    else:
        quotes_upload_form = QuoteUploadFileForm()

    context = {
        'quotes_upload_form': quotes_upload_form,
    }

    return render(request, 'manager_app/manager_feeforservice_quotepdfupload.html', context)


def QuotePdfByQidUpload(request, requestid, quoteid):
    if not request.user.groups.filter(name='manager').exists():
        raise PermissionDenied
    print(quoteid)
    qid = ' '.join([quoteid[:-10], quoteid[-10:-4], quoteid[-4:]])
    print(qid)
    #requestid = requestid
    this_request = ServiceRequest.objects.get(id=requestid)
    index = this_request.quote_number.index(qid)

    if request.method == 'POST':
        quotes_upload_form = QuoteUploadByQidFileForm(
            request.POST, request.FILES)
        if quotes_upload_form.is_valid():
            file = request.FILES['file']
            file_name = quoteid+'.pdf'
            fs = FileSystemStorage()
            filename = fs.save(file_name, file)
            if os.path.exists(os.path.join(settings.QUOTE_DIR, file_name)):
                now = datetime.datetime.now()
                file_name_old = '.'.join(file_name.split('.')[:-1]) + '_replaced_'+'_'.join([str(now.year), str(now.month), str(
                    now.day), str(now.hour), str(now.minute), str(now.second), str(now.microsecond)])+'.'+file_name.split('.')[-1]
                os.rename(os.path.join(settings.QUOTE_DIR, file_name),
                          os.path.join(settings.QUOTE_DIR, file_name_old))

            subprocess.call("ln -sf "+os.path.join(settings.MEDIA_ROOT, filename) +
                            " "+os.path.join(settings.QUOTE_DIR, file_name), shell=True)
            this_request.quote_pdf[index] = True
            this_request.status = ''
            this_request.save()

            return redirect('manager_app:quote_list')
    else:
        quotes_upload_form = QuoteUploadByQidFileForm()

    context = {
        'qid': qid,
        'quotes_upload_form': quotes_upload_form,
    }

    return render(request, 'manager_app/manager_feeforservice_quotepdfbyqidupload.html', context)


@transaction.atomic
def QuoteUpdateView(request, requestid, quoteid):
    if not request.user.groups.filter(name='manager').exists():
        raise PermissionDenied
    qid = ' '.join([quoteid[:-10], quoteid[-10:-4], quoteid[-4:]])
    this_request = get_object_or_404(ServiceRequest, pk=requestid)

    index = this_request.quote_number.index(qid)
    this_amount = this_request.quote_amount[index]
    quoteupdate_form = QuoteUpdateForm(request.POST or None,
                                       initial={'PI': this_request.group,
                                                'research_contact': this_request.research_contact,
                                                'quote_amount': this_amount})

    if 'Preview' in request.POST or 'Save' in request.POST:

        if quoteupdate_form.is_valid():
            group_name = quoteupdate_form.cleaned_data['PI']
            research_contact = quoteupdate_form.cleaned_data['research_contact']
            this_amount = quoteupdate_form.cleaned_data['quote_amount']

            if not this_amount.startswith('$'):
                this_amount = '$'+this_amount
            if '-' in this_amount:
                tm = []
                for x in this_amount.split('-'):
                    if not x.startswith('$'):
                        tm.append('$'+x)
                    else:
                        tm.append(x)
                this_amount = '-'.join(tm)

            data_request = {
                'quote_number': quoteid,
                'PI': group_name,
                'research_contact': research_contact,
                'quote_amount': this_amount,
            }

            if 'Preview' in request.POST:
                displayorder_request = ['quote_number',
                                        'PI', 'research_contact', 'quote_amount']
                # print(data_request)

                context = {
                    'quoteupdate_form': quoteupdate_form,
                    'modalshow': 1,
                    'displayorder_request': displayorder_request,
                    'data_request': data_request,
                    'qid': quoteid,
                }
                return render(request, 'manager_app/manager_feeforservice_quoteupdate.html', context)

            if 'Save' in request.POST:
                this_request.group = group_name
                this_request.research_contact = data_request['research_contact']
                this_request.quote_amount[index] = data_request['quote_amount']
                this_request.save()
                return redirect('manager_app:quote_list')

    context = {
        'quoteupdate_form': quoteupdate_form,
        'qid': qid,

    }

    return render(request, 'manager_app/manager_feeforservice_quoteupdate.html', context)


@transaction.atomic
def QuoteDeleteView(request, requestid, quoteid):
    if not request.user.groups.filter(name='manager').exists():
        raise PermissionDenied
    qid = ' '.join([quoteid[:-10], quoteid[-10:-4], quoteid[-4:]])
    this_request = get_object_or_404(ServiceRequest, pk=requestid)
    index = this_request.quote_number.index(qid)
    if len(this_request.quote_number) == 1:
        this_request.delete()
    else:
        del this_request.quote_number[index]
        del this_request.quote_amount[index]
        del this_request.quote_pdf[index]

    return redirect('manager_app:quote_list')


def GetDescriptionView(request, service_pk):
    serviceinfo = get_object_or_404(ServiceInfo, pk=service_pk)
    data = {}
    data['description'] = serviceinfo.description
    return JsonResponse(data)


def ServiceRequestDetailView(request, pk):
    servicerequestinfo = get_object_or_404(ServiceRequest, pk=pk)
    summaryfield = ['status', 'date', 'group', 'institute',
                    'research_contact', 'research_contact_email', 'notes']
    itemsfield = ['service', 'quantity', 'status']
    itemsinfo = servicerequestinfo.servicerequestitem_set.all().select_related('service')
    quotes_info = {}
    current_quote = {}
    quotes_list = servicerequestinfo.quote_number
    amounts_list = servicerequestinfo.quote_amount
    for i in range(len(quotes_list)):
        quotes_info[quotes_list[i]] = {
            'amount': amounts_list[i],
            'number_compact': ''.join(quotes_list[i].split(' ')),
        }
    print(quotes_info)
    current_quote = {
        'number': quotes_list[-1],
        'amount': amounts_list[-1],
        'number_compact': ''.join(quotes_list[-1].split(' ')),

    }

    context = {
        'summaryfield': summaryfield,
        'itemsfield': itemsfield,
        'quotes_info': quotes_info,
        'servicerequestinfo': servicerequestinfo,
        'itemsinfo': itemsinfo,
        'current_quote': current_quote,
    }
    return render(request, 'manager_app/manager_servicerequestdetail.html', context=context)


def ServiceRequestDeleteView(request, pk):
    servicerequestinfo = get_object_or_404(ServiceRequest, pk=pk)
    servicerequestinfo.delete()
    return redirect('manager_app:servicerequests_list')
