from collaborator_app.models import ServiceInfo

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
def SelfUniqueValidation(tosavelist):
    duplicate = []
    for i in range(0, len(tosavelist)):
        if tosavelist[i] in tosavelist[i+1:]:
            duplicate.append(tosavelist[i])
    return duplicate

def daysuffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

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
			service_breakdown_help = ' (up to 23 samples)'
		elif item == 'ATAC-seq_24':
			this_name = 'ATAC-seq'
			service_breakdown_help = ' (up to 95 samples)'
		elif item == 'ATAC-seq_96':
			this_name = 'ATAC-seq'
			service_breakdown_help = ' (96 samples or more)'
		else:
			this_name = item
			service_breakdown_help = ''
		servicename.append(this_name)
		this_breakdown = ':'.join([brief,'$'+str(rate_value)+'/'+thisitem.rate_unit+service_breakdown_help])
		subtotal = float(rate_value)*float(quantity)
		total += subtotal
		if len(serviceitems) > 1:
			i += 1
			this_breakdown = this_breakdown+'\nSubtotal:$'+str(rate_value)+'*'+str(quantity)+' '+thisitem.rate_unit+'s = $'+str(subtotal)+'\n'
			if '(pilot)' not in item:
				if thisitem.description_brief:
					this_detail = brief[0].lower()+ brief[1:]+' in '+this_name+', which includes '+detail
				else:
					this_detail = brief+', which includes '+detail
				service_detail.append('('+str(i)+')'+this_detail)

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
		fixedpart3 = 'The costs are for '+'.'.join(service_detail)
		outlines.append('.'.join([fixedpart1,fixedpart2,fixedpart3,fixedpart4]))
		outlines.append('\n'.join(service_breakdown))
		outlines.append('\nTotal Estimate: '+'+'.join(subtotals)+' = '+'$'+str(total))
	else:
		fixedpart2 = 'This quote is for our '+','.join(servicename)+' service'
		fixedpart3 = 'The costs are for '+','.join(service_detail)
		outlines.append('.'.join([fixedpart1,fixedpart2,fixedpart3,fixedpart4]))
		outlines.append('\n'.join(service_breakdown))
		outlines.append('Total Estimate: $'+str(rate_value)+'*'+str(quantity)+' '+thisitem.rate_unit+'s = $'+str(subtotal))

	return '\n'.join(outlines)




