from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from singlecell_app.models import CoolAdminSubmission
from masterseq_app.models import SeqInfo, GenomeInfo, LibraryInfo