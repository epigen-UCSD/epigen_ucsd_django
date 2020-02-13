from django.test import TestCase
from django.contrib.auth.models import User

# Create your tests here.
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from singlecell_app.models import CoolAdminSubmission
from masterseq_app.models import SeqInfo, GenomeInfo, LibraryInfo
import time

class TestSingleCellPage_Bionf(StaticLiveServerTestCase):
    """
    This class will test singlecell page in context of bioinformatics user
    """
    ten_x = '10xATAC' #experiment type
    row_length = 7 #datatable in singlecell view has 7 columns, 8 with cooladmin edit button??
    positive_fastq_status = 'Yes' #What should be displayed when fastq file is present in file system
    tenx_status_index = 5 #5th column
    ca_status_index = 6
    fastq_status_index = 4
    seq_index = 0
    no_fastq_present_tooltip = 'No FASTQ files available'
    tenx_not_ran_cooladmin_status = 'Run10xPipeline'
    pipeline_completed_status = 'Results'
    can_submit_status = 'ClickToSubmit'
    ca_inactive_submit = 'badge badge-success badge-status-blue cooladmin-submit'
    tenx_inactive_submit = 'btn btn-sm badge-status-blue'
    button_class_dict = {'cooladmin_can_submit': 'btn btn-danger btn-sm btn-status-orange'}
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Chrome('test/chromedriver.exe')
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
    
    def title_matches(self):
        """Verifies that the hardcoded text "Single Cell App" appears in page title"""
        return "Single Cell App" in self.driver.title


    def test_all_singlecell_view(self):
        """
        General checking method, not in-depth!
        check that iff fastq present then ClickToSubmit is present for 10x & CA
        check that if 10xATAC experiment then iff 10x processed then ClickToSubmit available for cooladmin
        """
        driver = self.driver
        driver.get('http://127.0.0.1:8000/singlecell/MySeqs')
        time.sleep(10)
        
        #login and click hit enter key
        username = driver.find_element_by_id("id_username")
        username.clear()
        username.send_keys('brandon')
        
        password = driver.find_element_by_id("id_password")
        password.clear()
        password.send_keys('djangotest' + Keys.RETURN)

        #assert title is Single Cell App
        assert "Single Cell App" in self.driver.title
        
        #let ajax load
        time.sleep(50)
        
        #select all from datatablesjs
        select = Select(driver.find_element_by_name('datatable-user-sc_length'))
        
        #choose All from dropdown menu select by value
        select.select_by_value('-1')
        print('selected All')

        #check that all rows are good
        table = driver.find_element_by_id('datatable-user-sc')
        rows = table.find_elements_by_tag_name('tr') # get all of the rows in the table
        
        #check specific test cases!
        self.check_specific_test_cases(rows)

        #skip header row
        for row in rows[1:]:
            #print(row)
            row_text = row.text 
            row_list = row_text.split(' ')
            #Assert length is correct
            #print(row_list)
            assert len(row_list) == self.row_length or len(row_list) == (self.row_length - 1)
            if(row_list[1] == self.ten_x):
                #check 10xeperiments
                self.check_tenx_experiment(self, row, row_list)
            else:
                self.check_sc_experiment(self, row, row_list)

    
    def check_tenx_experiment(self, row, row_list):
        #check that length is 7 if not skip test
        if len(row_list) == 7: 
            if(row_list[self.fastq_status_index] != self.positive_fastq_status):
                print(row_list, row_list[self.tenx_status_index] )
                #check 10xSubmission status:
                row_cells = row.find_elements_by_tag_name('td')

                if(row_list[self.tenx_status_index] == self.can_submit_status ):
                    #check tooltip attritbute
                    tenx_button = row_cells[self.tenx_status_index].find_elements_by_tag_name('button')
                    title = tenx_button.get_attribute('title')
                    print('title: ',title)
                    print('rowcells: ',row_cells)
                    assert title == self.no_fastq_present_tooltip
                #check cooladmin submission status
                if(row_list[self.ca_status_index] == self.can_submit_status ):
                    #check tooltip attritbute
                    cooladmin_button = row_cells[self.ca_status_index].find_element_by_tag_name('button')
                    print('ca cell text: ', cooladmin_button.text)
                    title = cooladmin_button.get_attribute('title')
                    print('ttip: ',title)
                    print(cooladmin_button)
                    assert title == self.no_fastq_present_tooltip
                    #tttext = tooltip.text
                    
            #fastq is present, check if tenx pipeline has not been completed that cooladmin is not submitab;e and 
            elif(row_list[self.fastq_status_index] == self.positive_fastq_status):
                
                tenx_button = row_cells[self.tenx_status_index].find_element_by_tag_name('button')
                tenx_button_css = tenx_button.get_attribute('class')
                cooladmin_button = row_cells[self.ca_status_index].find_element_by_tag_name('button')
                cooladmin_button_css = cooladmin_button.get_attribute("class")

                assert tenx_button_css != self.tenx_inactive_submit

                cooladmin_status = row_list[self.ca_status_index] 
                if(row_list[self.tenx_status_index] != self.pipeline_completed_status ):
                    #make sure cooladmin is run10xPipeline first
                    assert cooladmin_status == self.tenx_not_ran_cooladmin_status
                else:
                    assert cooladmin_button_css != self.ca_inactive_submit
                    assert cooladmin_status == self.can_submit_status

                
                    
        #print(1)
    # def test_foo(self):
    #     self.assertEquals(1,1)
    
    def check_tooltip(self, row, row_list):
        """
        Check tooltip says `No FASTQ files available`
        """
        #grab clicktosubmit tds and check that tooltips are present
        

    def check_sc_experiment(self, row, row_list):
        #check length is 7 if not skip test
        #check that length is 7 if not skip test
        if len(row_list) == 7: 
            row_cells = row.find_elements_by_tag_name('td')
            if(row_list[self.fastq_status_index] != self.positive_fastq_status):
                print(row_list, row_list[self.tenx_status_index] )
                #check 10xSubmission status:

                if(row_list[self.tenx_status_index] == self.can_submit_status ):
                    #check tooltip attritbute
                    tenx_button = row_cells[self.tenx_status_index].find_element_by_tag_name('button')
                    title = tenx_button.get_attribute('title')
                    print('title: ',title)
                    print('rowcells: ',row_cells)
                    assert title == self.no_fastq_present_tooltip
                #check cooladmin submission status  
                if(row_list[self.ca_status_index] == self.can_submit_status ):
                    #check tooltip attritbute
                    cooladmin_button = row_cells[self.ca_status_index].find_element_by_tag_name('button')
                    title = cooladmin_button.get_attribute('title')
                    print(cooladmin_button)
                    assert title == self.no_fastq_present_tooltip
                    #tttext = tooltip.text
                    
            #fastq is present, check if tenx pipeline has not been completed that cooladmin is not submitab;e and 
            elif(row_list[self.fastq_status_index] == self.positive_fastq_status):
                cooladmin_button = row_cells[self.ca_status_index].find_element_by_tag_name('button')
                cooladmin_button_css = cooladmin_button.get_attribute("class")
                tenx_button = row_cells[self.tenx_status_index].find_element_by_tag_name('button')
                tenx_button_css = tenx_button.get_attribute('class')

                assert tenx_button_css != self.tenx_inactive_submit
                assert cooladmin_button_css != self.ca_inactive_submit

    def check_specific_test_cases(self, rows):
        print(1)
        #test cases: 
        to_check = 10
        for row in rows:
            row_text = row.text.split(' ')
        #want a sequence where fastq file is present and 10x and ca ran - both 10x and sc
            #sc:br029_100, 10x:brandon_211_1_2_3
            if(to_check > 0 and row_text[self.seq_index] == 'brandon_211_1_2_3'):
                to_check -= 1

                assert row_text[self.fastq_status_index] == self.positive_fastq_status
                assert row_text[self.tenx_status_index] == self.pipeline_completed_status
                assert row_text[self.ca_status_index] == self.pipeline_completed_status
                if(to_check == 0):
                    return 
            #cooladmin 
            if(to_check > 0 and row_text[self.seq_index] == 'brg029_100' ):
                to_check -= 1

                assert row_text[self.fastq_status_index] == self.positive_fastq_status
                assert row_text[self.tenx_status_index] == self.pipeline_completed_status
                assert row_text[self.ca_status_index] == self.pipeline_completed_status

                if(to_check == 0):
                    return

        #want a seq where fastq and 10x finished,
            #Check seq can run sc, 10x:brandon_210_1
            if(to_check > 0 and row_text[self.seq_index] == 'brandon210_1' ):
                to_check -= 1
                assert row_text[self.fastq_status_index] == self.positive_fastq_status
                assert row_text[self.tenx_status_index] == self.pipeline_completed_status
                assert row_text[self.ca_status_index] == self.can_submit_status
                
                #check class of CA submit button 
                row_cells = row.find_elements_by_tag_name('td')
                cooladmin_button = row_cells[self.ca_status_index].find_element_by_tag_name('button')
                cooladmin_button_class = cooladmin_button.get_attribute("class")
                assert cooladmin_button_class == button_class_dict['cooladmin_can_submit']


        #want a seq where fastq and no 10x -> no CA for 10x
            #check seq 10x:brandon_210

        #want a seq where fastq and no 10x -> yes CA for sc
            #sc: brg029_10

        #want a seq where fastq and 10x inProcess -> no CA
            #10x:brandon_211 

        #want a seq where fastq and 10x inQueue -> no CA
            #10x:brandon_210_1_2_3

        #want a seq where fastq and 10x Error! -> no CA
            #10x:brandon_210_4

        #want a seq where no fastq and 10x done and no CA -> results still available
            #10x:brandon_210_2

        #want a seq where no fastq and 10xdone and CA done -> results still available
            #10x:brandon_210_5




