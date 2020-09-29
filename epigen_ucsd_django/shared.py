from collaborator_app.models import ServiceInfo
import re

def is_member(user,group):
    return user.groups.filter(name=group).exists()

def is_in_multiple_groups(user,grouplist):
    return user.groups.filter(name__in=grouplist).exists()

def datetransform(inputdate):
	#from 2/6/2018 to 2018-02-06
	if inputdate == '':
		return None
	tm = inputdate.split('/')
	year = tm[2].strip()
	month = tm[0].strip().zfill(2)
	date = tm[1].strip().zfill(2)
	if len(year) == 2:
		year = '20'+year
	return '-'.join([year,month,date])

def datetransform2(inputdate):
	#from 031620 to 2020-03-16
	#from 31620 to 2020-03-16
	if inputdate == '':
		return None
	tm = inputdate.split('/')
	year = '20'+inputdate[-2:]
	month = inputdate[:-4].zfill(2)
	date = inputdate[-4:-2]
	return '-'.join([year,month,date])


def SelfUniqueValidation(tosavelist):
    duplicate = []
    for i in range(0, len(tosavelist)):
        if tosavelist[i] in tosavelist[i+1:]:
            duplicate.append(tosavelist[i])
    return duplicate

def daysuffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def emailcheck(email):  
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):  
        return True     
    else:  
        return False

def quotebody(serviceitems, quantities,institute):
	service_breakdown = []
	service_detail = []
	servicename = []
	total = 0
	subtotals = []
	outlines = []
	i = 0

	fixedpart1 = 'We are excited to work with you'
	fixedpart4 = 'The estimated costs for your project are:\n'
	for value in zip(serviceitems,quantities):
		item = value[0]
		quantity = value[1]

		thisitem = ServiceInfo.objects.get(service_name=item)
		if thisitem.description_brief:
			brief = thisitem.description_brief
		else:
			brief = item
		if thisitem.description:
			detail = thisitem.description
		else:
			detail = ''
		if institute.lower() == 'uc':
			rate_value = thisitem.uc_rate
		elif institute.lower() == 'non_uc':
			rate_value = thisitem.nonuc_rate
		elif institute.lower() == 'industry':
			rate_value = thisitem.industry_rate
		service_breakdown_help = ''
		if item in ['ATAC-seq','ATAC-seq(pilot)']:
			this_name = 'ATAC-seq'
			service_breakdown_help = ' (up to 24 samples)'
		elif item == 'ATAC-seq_24':
			this_name = 'ATAC-seq'
			service_breakdown_help = ' (up to 96 samples)'
		elif item == 'ATAC-seq_96':
			this_name = 'ATAC-seq'
			service_breakdown_help = ' (97 samples or more)'
		else:
			this_name = item
			service_breakdown_help = ''
		servicename.append(this_name)
		this_breakdown = ': '.join([brief,'$'+str(rate_value)+'/'+thisitem.rate_unit+service_breakdown_help])
		subtotal = float(rate_value)*float(quantity)
		total += subtotal
		if len(serviceitems) > 1:
			
			this_breakdown = this_breakdown+'\nSubtotal: $'+str(rate_value)+' * '+str(quantity)+' '+thisitem.rate_unit+'s = $'+str(subtotal)+'\n'
			if '(pilot)' not in item:
				i += 1
				if thisitem.description_brief:
					this_detail = brief[0].lower()+ brief[1:]+' in '+this_name+', which includes '+detail
				else:
					this_detail = brief+', which includes '+detail
				service_detail.append('('+str(i)+') '+this_detail)

		else:
			if thisitem.description_brief:
				this_detail = brief[0].lower()+ brief[1:]+', which includes '+detail
			else:
				this_detail = brief+', which includes '+detail
			service_detail.append(this_detail)
		service_breakdown.append(this_breakdown)
		subtotals.append('$'+str(subtotal))
	
	
	if len(serviceitems) > 1:
		servicename = list(set(servicename))
		if len(servicename) > 1:
			fixedpart2 = 'This quote is for our '+','.join(servicename[0:-1])+' and '+servicename[-1]
		else:
			fixedpart2 = 'This quote is for our '+','.join(servicename)+' service'
			service_detail_tm = []
			for item in service_detail:
				service_detail_tm.append(item.split(')',1)[1])
			service_detail = service_detail_tm

		fixedpart3 = 'The costs are for '+'.'.join(service_detail)
		outlines.append('. '.join([fixedpart1,fixedpart2,fixedpart3,fixedpart4]))
		outlines.append('\n'.join(service_breakdown))
		outlines.append('\nTotal Estimate: '+' + '.join(subtotals)+' = '+'$'+str(total))
	else:
		fixedpart2 = 'This quote is for our '+','.join(servicename)+' service'
		fixedpart3 = 'The costs are for '+','.join(service_detail)
		outlines.append('. '.join([fixedpart1,fixedpart2,fixedpart3,fixedpart4]))
		outlines.append('\n'.join(service_breakdown))
		outlines.append('Total Estimate: $'+str(rate_value)+' * '+str(quantity)+' '+thisitem.rate_unit+'s = $'+str(subtotal))

	return '\n'.join(outlines)

def serviceitemcollapse(dictdata):
	atac_group = ['ATAC-seq','ATAC-seq_24','ATAC-seq_96']
	sciatac_group = ['sciATAC-seq','sciATAC-seq_2','sciATAC-seq_3','sciATAC-seq_4']
	tenscatac_group = ['10x scATAC-seq','10x scATAC-seq_2','10x scATAC-seq_3','10x scATAC-seq_4']
	tenscrna_group = ['10x scRNA-seq','10x scRNA-seq_2','10x scRNA-seq_3','10x scRNA-seq_4']
	tensnrna_group = ['10x snRNA-seq','10x snRNA-seq_2','10x snRNA-seq_3','10x snRNA-seq_4']
	atacpilot_group = ['ATAC-seq(pilot)','ATAC-seq_24(pilot)','ATAC-seq_96(pilot)']
	sciatacpilot_group = ['sciATAC-seq(pilot)','sciATAC-seq_2(pilot)','sciATAC-seq_3(pilot)','sciATAC-seq_4(pilot)']
	tenscatacpilot_group = ['10x scATAC-seq(pilot)','10x scATAC-seq_2(pilot)','10x scATAC-seq_3(pilot)','10x scATAC-seq_4(pilot)']
	tenscrnapilot_group = ['10x scRNA-seq(pilot)','10x scRNA-seq_2(pilot)','10x scRNA-seq_3(pilot)','10x scRNA-seq_4(pilot)']
	tensnrnapilot_group = ['10x snRNA-seq(pilot)','10x snRNA-seq_2(pilot)','10x snRNA-seq_3(pilot)','10x snRNA-seq_4(pilot)']
	checkedlist = [atac_group,sciatac_group,tenscatac_group,tenscrna_group,tensnrna_group,atacpilot_group,atacpilot_group,sciatacpilot_group,tenscatacpilot_group,tenscrnapilot_group,tensnrnapilot_group]
	for l in checkedlist:
		if dictdata['service'].service_name in l:
			dictdata['service'] = ServiceInfo.objects.get(service_name=l[0])
	return dictdata

def servicetarget(service, quantity):
    if service.service_name == 'ATAC-seq':
        if float(quantity) > 24 and float(quantity) <= 96:
            service = ServiceInfo.objects.get(service_name='ATAC-seq_24')
        elif float(quantity) > 96:
            service = ServiceInfo.objects.get(service_name='ATAC-seq_96')

    if service.service_name == 'sciATAC-seq':
        if float(quantity) == 1:
            service = ServiceInfo.objects.get(service_name='sciATAC-seq')
        elif float(quantity) == 2:
            service = ServiceInfo.objects.get(service_name='sciATAC-seq_2')
        elif float(quantity) == 3:
            service = ServiceInfo.objects.get(service_name='sciATAC-seq_3')
        elif float(quantity) >= 4:
            service = ServiceInfo.objects.get(service_name='sciATAC-seq_4')

    if service.service_name == '10x scATAC-seq':
        if float(quantity) == 1:
            service = ServiceInfo.objects.get(service_name='10x scATAC-seq')
        elif float(quantity) == 2:
            service = ServiceInfo.objects.get(service_name='10x scATAC-seq_2')
        elif float(quantity) == 3:
            service = ServiceInfo.objects.get(service_name='10x scATAC-seq_3')
        elif float(quantity) >= 4:
            service = ServiceInfo.objects.get(service_name='10x scATAC-seq_4')


   if service.service_name == '10x scRNA-seq':
        if float(quantity) == 1:
            service = ServiceInfo.objects.get(service_name='10x scRNA-seq')
        elif float(quantity) == 2:
            service = ServiceInfo.objects.get(service_name='10x scRNA-seq_2')
        elif float(quantity) == 3:
            service = ServiceInfo.objects.get(service_name='10x scRNA-seq_3')
        elif float(quantity) >= 4:
            service = ServiceInfo.objects.get(service_name='10x scRNA-seq_4')

    if service.service_name == '10x snRNA-seq':
        if float(quantity) == 1:
            service = ServiceInfo.objects.get(service_name='10x snRNA-seq')
        elif float(quantity) == 2:
            service = ServiceInfo.objects.get(service_name='10x snRNA-seq_2')
        elif float(quantity) == 3:
            service = ServiceInfo.objects.get(service_name='10x snRNA-seq_3')
        elif float(quantity) >= 4:
            service = ServiceInfo.objects.get(service_name='10x snRNA-seq_4')
    if service.service_name == 'ATAC-seq(pilot)':
        if float(quantity) > 24 and float(quantity) <= 96:
            service = ServiceInfo.objects.get(service_name='ATAC-seq_24(pilot)')
        elif float(quantity) > 96:
            service = ServiceInfo.objects.get(service_name='ATAC-seq_96(pilot)')

    if service.service_name == 'sciATAC-seq(pilot)':
        if float(quantity) == 1:
            service = ServiceInfo.objects.get(service_name='sciATAC-seq(pilot)')
        elif float(quantity) == 2:
            service = ServiceInfo.objects.get(service_name='sciATAC-seq_2(pilot)')
        elif float(quantity) == 3:
            service = ServiceInfo.objects.get(service_name='sciATAC-seq_3(pilot)')
        elif float(quantity) >= 4:
            service = ServiceInfo.objects.get(service_name='sciATAC-seq_4(pilot)')

    if service.service_name == '10x scATAC-seq(pilot)':
        if float(quantity) == 1:
            service = ServiceInfo.objects.get(service_name='10x scATAC-seq(pilot)')
        elif float(quantity) == 2:
            service = ServiceInfo.objects.get(service_name='10x scATAC-seq_2(pilot)')
        elif float(quantity) == 3:
            service = ServiceInfo.objects.get(service_name='10x scATAC-seq_3(pilot)')
        elif float(quantity) >= 4:
            service = ServiceInfo.objects.get(service_name='10x scATAC-seq_4(pilot)')


   if service.service_name == '10x scRNA-seq(pilot)':
        if float(quantity) == 1:
            service = ServiceInfo.objects.get(service_name='10x scRNA-seq(pilot)')
        elif float(quantity) == 2:
            service = ServiceInfo.objects.get(service_name='10x scRNA-seq_2(pilot)')
        elif float(quantity) == 3:
            service = ServiceInfo.objects.get(service_name='10x scRNA-seq_3(pilot)')
        elif float(quantity) >= 4:
            service = ServiceInfo.objects.get(service_name='10x scRNA-seq_4(pilot)')

    if service.service_name == '10x snRNA-seq(pilot)':
        if float(quantity) == 1:
            service = ServiceInfo.objects.get(service_name='10x snRNA-seq(pilot)')
        elif float(quantity) == 2:
            service = ServiceInfo.objects.get(service_name='10x snRNA-seq_2(pilot)')
        elif float(quantity) == 3:
            service = ServiceInfo.objects.get(service_name='10x snRNA-seq_3(pilot)')
        elif float(quantity) >= 4:
            service = ServiceInfo.objects.get(service_name='10x snRNA-seq_4(pilot)')
     return service