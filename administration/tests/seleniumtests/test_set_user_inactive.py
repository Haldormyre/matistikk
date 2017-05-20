from django.test import LiveServerTestCase
from administration.models import Person
from mixer.backend.django import mixer
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SetUserInactiveTestCase(LiveServerTestCase):
    def setUp(self):
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()

        teacherobj = mixer.blend('administration.Person', role=2, username='teacher', first_name='teacherfirstname')
        teacherobj.set_password('teacher')
        teacherobj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(SetUserInactiveTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(SetUserInactiveTestCase, self).tearDown()

    # Confirms scenario 14
    def test_admin_can_set_teacher_inactive(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("admin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("admin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "overviewDropdown")))
        self.selenium.find_element_by_id('overviewDropdown').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "userOverview")))
        self.selenium.find_element_by_id('userOverview').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "search")))
        user_list = self.selenium.find_element_by_id('usertable')
        for el in user_list.find_elements_by_tag_name('td'):
            if el.text == 'teacherfirstname':
                el.click()
                break
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "editUserBtn")))
        self.selenium.find_element_by_id('editUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_is_active")))
        self.selenium.find_element_by_id('id_is_active').click()
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.2)
        self.assertFalse(Person.objects.get(username='teacher').is_active), \
            'Teacher should be able to edit information about a student in on of their classes'
