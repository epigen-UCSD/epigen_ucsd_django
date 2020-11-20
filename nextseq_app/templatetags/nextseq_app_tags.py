from django import template
from django.contrib.auth.models import Group
from epigen_ucsd_django.settings import DEBUG
from epigen_ucsd_django.shared import emailcheck
from masterseq_app.models import SeqInfo
from nextseq_app.models import RunInfo,LibrariesInRun

register = template.Library()
print(f'debug status: {DEBUG}')

@register.filter
def key(d, key_name):
	if key_name:
		try:
			return d[str(key_name)]
		except:
			return ''
	else:
		return ''

@register.filter(name='has_group')
def has_group(user, group_name):
	if(DEBUG):print(group_name)
	group = Group.objects.get(name=group_name)
	return True if group in user.groups.all() else False

@register.filter(name='has_groups')
def has_groups(user, group_name_list):
	grouplist = group_name_list.split(';')
	return user.groups.filter(name__in=grouplist).exists()

@register.filter
def humantitle(oldtitle):
	titlechange = {
		'jobstatus': 'Status',
		'set_id': 'Set ID',
		'set_name':'Title',
		'nextseqdir':'Location',

	}
	if oldtitle in titlechange.keys():
		return titlechange[oldtitle]
	else:
		return oldtitle.title().replace('_',' ')

@register.filter
def get_value(obj, field_name):
	return getattr(obj,field_name)

@register.filter
def get_type(value):
    return type(value)

@register.filter
def get_class(ob):
    return ob.__class__.__name__

@register.filter
def percentage(value):
    if value:
        return str(value)+"%"
    else:
    	return str(value)


@register.filter
def linktrackingsheet(stringtext):
	linktrans = {
		'TrackingSheet 1':'<a href="https://docs.google.com/spreadsheets/d/1gjPViUOd-2CQVAIwGUinmqeKQThjJp2cixWogV4qkok/edit" target=”_blank”>TrackingSheet 1</a>',
		'TrackingSheet 2':'<a href="https://docs.google.com/spreadsheets/d/19Qjv05LZo6pazNIvGrfj9GDzmK6riOwF3eriW7Ufj1o/edit" target=”_blank”>TrackingSheet 2</a>',
		'TrackingSheet 3':'<a href="https://docs.google.com/spreadsheets/d/1DqQQ0e5s2Ia6yAkwgRyhfokQzNPfDJ6S-efWkAk292Y/edit" target=”_blank”>TrackingSheet 3</a>',
		'Template':'<a href="/metadata/download/template.xlsx/"> template.xlsx </a>',
		'Column 1':'<b style="color: #F67E56;"> Column 1 </b>',
		'Column 2':'<b style="color: #F67E56;"> Column 2 </b>',
		'Sample ID': '<b style="color: #F67E56;"> Sample ID </b>',
		'Library ID': '<b style="color: #F67E56;"> Library ID </b>',
		'Sequencing ID': '<b style="color: #F67E56;"> Sequencing ID </b>',
		'show examples':'<b style="color: #3CB371;"> show examples </b>',
	}
	for k,v in linktrans.items():
		stringtext = stringtext.replace(k,v)
	return stringtext

@register.filter
def linkemail(text):
	outtext = []
	lines = text.split('\n')
	for line in lines:
		outline = []
		words = line.split(' ')
		for word in words:
			#print(repr(word))
			if emailcheck(word.strip('\r')):
				outline.append('<a href="mailto:'+word.strip('\r')+'">'+word.strip('\r')+'</a>')
			else:
				outline.append(word)
		outtext.append(' '.join(outline))
	#print('\n'.join(outtext))
	return '\n'.join(outtext)	

@register.filter
def trueitem(value):
	return value.split('duplicate#')[0]


@register.filter
def tomultiplicationsign(text):
	outtext = []
	lines = text.split('\n')
	for line in lines:
		outline = []
		words = line.split(' ')
		l = len(words)
		for i in range(l):
			if words[i] == '*' and i>0 and i<l-1:
				print(' '.join([words[i-1],words[i],words[i+1]]))
				try:
					float(words[i-1].strip().strip('$'))
					float(words[i+1].strip().strip('$'))
					outline.append('&#215')

				except:
					outline.append(words[i])
			else:
				outline.append(words[i])
		outtext.append(' '.join(outline))
	return '\n'.join(outtext)	

@register.filter
def get_portion_of_lane(sequencing_id):
	try:
		obj = SeqInfo.objects.get(seq_id=sequencing_id)
		return obj.portion_of_lane
	except:
		return 'NA'

@register.filter
def get_sum_of_portion_of_lane(runinfo):
	s = 0
	try:
		for seqs in runinfo.librariesinrun_set.all():
			obj = SeqInfo.objects.get(seq_id=seqs.Library_ID)
			s += obj.portion_of_lane
		return round(s,1)

	except:
		return ''


