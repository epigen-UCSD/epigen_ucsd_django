

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