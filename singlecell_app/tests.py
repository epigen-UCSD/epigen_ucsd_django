from django.test import TestCase

# Create your tests here.
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from singlecell_app.models import CoolAdminSubmission
from masterseq_app.models import SeqInfo, GenomeInfo, LibraryInfo
import time

class TestSingleCellPage(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome('test/chromedriver.exe')
    
    def tearDown(self):
        self.browser.close()

    def test_all_singlecell_view(self):
        self.browser.get(self.live_server_url)
        time.sleep(20)
        all_singlecell_url = self.live_server_url + reverse()
    # def test_foo(self):
    #     self.assertEquals(1,1)