#!/usr/bin/env python
# https://docs.djangoproject.com/en/2.2/ref/contrib/postgres/search/
# https://github.com/django-haystack/django-haystack/
# https://github.com/elastic/elasticsearch-dsl-py/tree/master/examples

import os
import sys
import django
import argparse
# print(os.path.abspath(__file__))


basedir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(os.getcwd())
os.chdir(basedir)
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()
from masterseq_app.models import SeqInfo, GenomeInfo, SampleInfo, LibraryInfo

# search lookup
SampleInfo.objects.filter(description__search='heart')  # return queryset


# searchvector
from django.contrib.postgres.search import SearchVector
from django.contrib.auth.models import User, Group
from epigen_ucsd_django.models import CollaboratorPersonInfo

SampleInfo.objects.annotate(search=SearchVector(
    'description', 'research_person__cell_phone'),).filter(search='heart')

SampleInfo.objects.annotate(search=SearchVector(
    'description') + SearchVector('research_person__cell_phone'),).filter(search='heart')


# SearchQuery¶

# class SearchQuery(value, config=None, search_type='plain')[source]¶

# SearchQuery translates the terms the user provides into a search query object that the database compares to a search vector. By default, all the words the user provides are passed through the stemming algorithms, and then it looks for matches for all of the resulting terms.

# If search_type is 'plain', which is the default, the terms are treated as separate keywords. If search_type is 'phrase', the terms are treated as a single phrase. If search_type is 'raw', then you can provide a formatted search query with terms and operators. Read PostgreSQL’s Full Text Search docs to learn about differences and syntax. Examples:

from django.contrib.postgres.search import SearchQuery
SearchQuery('heart brain')  # two keywords
SearchQuery('brain heart')
# SearchQuery('brain heart',search_type='phrase')  new in Django 2.2
# SearchQuery("'brain' & ('atac' | 'rna')", search_type='raw'), boolean
SearchQuery('heart') & SearchQuery('brain')
SearchQuery('heart') | SearchQuery('brain')
~SearchQuery('heart')


############################################################
# searchRANK
############################################################
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

vector = SearchVector('description')
query = SearchQuery('brain')
SampleInfo.objects.annotate(rank=SearchRank(vector, query)).order_by('-rank')
