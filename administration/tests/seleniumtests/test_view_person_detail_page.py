from django.test import LiveServerTestCase
from administration.models import Person
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class PersonDetailViewTestCase(LiveServerTestCase):
    def setUp(self):
        # DB setup
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()

        schooladminobj = mixer.blend('administration.Person', role=3, username='schooladmin')
        schooladminobj.set_password('schooladmin')
        schooladminobj.save()

        schoolobj = mixer.blend('administration.School', school_administrator=schooladminobj)
        schoolobj.save()

        gradeobj = mixer.blend('administration.Grade', school=schoolobj)
        gradeobj.save()

        teacherobj = mixer.blend('administration.Person', role=2, grades=gradeobj, username='teacher')
        teacherobj.set_password('teacher')
        teacherobj.save()

        studentobj = mixer.blend('administration.Person', role=1, grades=gradeobj, username='student')
        studentobj.set_password('student')
        studentobj.save()

        schooladminobj2 = mixer.blend('administration.Person', role=3, username='schooladmin2')
        schooladminobj2.set_password('schooladmin2')
        schooladminobj2.save()

        teacherobj2 = mixer.blend('administration.Person', role=2, username='teacher2')
        teacherobj2.set_password('teacher2')
        teacherobj2.save()

        #  Webdriver setup
        """
        server_url = "http://%s:%s/wd/hub" % ('127.0.0.1', '4444')  # ip address and port
        dc = DesiredCapabilities.HTMLUNITWITHJS
        self.selenium = webdriver.Remote(server_url, dc)"""
        self.selenium = webdriver.Chrome()
        super(PersonDetailViewTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(PersonDetailViewTestCase, self).tearDown()

    def test_teacher_can_edit_student_information(self):
        """ Checks that a teacher can edit the surname of a student in one of their classes"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("teacher")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("teacher")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "logout")))
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "editUserBtn")))
        self.selenium.find_element_by_id('editUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_last_name")))
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('studentsurname')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        self.assertEqual(1, len(Person.objects.filter(last_name='studentsurname'))), \
        'Teacher should be able to edit information about a student in on of their classes'

    def test_schooladmin_can_edit_student_and_teacher_information(self):
        """ Checks that a schooladministrator can edit the surname of a student or a teacher at their school"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )

        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "logout")))
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "editUserBtn")))
        self.selenium.find_element_by_id('editUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_last_name")))
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('student')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        self.assertEqual('student', Person.objects.filter(role=1)[0].last_name), \
        'Schooladministrator should be able to change the information of a student in a class at their school'

        # teacher
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/teacher")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "editUserBtn")))
        self.selenium.find_element_by_id('editUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_last_name")))
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('teacher')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        self.assertEqual('teacher', Person.objects.filter(role=2)[0].last_name), \
        'Schooladministrator should be able to change the information of a teacher in a class at their school'

    def test_admin_can_edit_schooladmin_teacher_student_information(self):
        """ Checks that a administrator can edit the surname of a schooladministrator, student or a teacher at 
        their school"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("admin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("admin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "logout")))
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "editUserBtn")))
        self.selenium.find_element_by_id('editUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_last_name")))
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('studsurname')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        self.assertEqual('studsurname', Person.objects.filter(role=1)[0].last_name), \
        'Admin should be able to change the information about a student'

        # teacher
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/teacher")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "editUserBtn")))
        self.selenium.find_element_by_id('editUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_last_name")))
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('teachersurname')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        self.assertEqual('teachersurname', Person.objects.filter(role=2)[0].last_name), \
        'Admin should be able to change the information about a teacher'

        # Schooladmin
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/schooladmin")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "editUserBtn")))
        self.selenium.find_element_by_id('editUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_last_name")))
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('schooladmin')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.5)  # Wait for db
        self.assertEqual('schooladmin', Person.objects.filter(role=3)[0].last_name), \
        'Admin should be able to change the information about a schooladmin'

    def test_teacher_can_not_edit_student_information(self):
        """ Checks that a teacher can't edit information about a student not in one of their classes"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("teacher2")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("teacher2")
        try:
            self.selenium.find_element_by_id('logInBtn').click()
            self.selenium.get(
                '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
            )
            self.selenium.find_element_by_id('editUserBtn').click()
            self.selenium.find_element_by_id('id_last_name').clear()
            self.selenium.find_element_by_id('id_last_name').send_keys('studsur')
            self.selenium.find_element_by_id('saveNewInfoBtn').click()
        except NoSuchElementException:
            None
        self.assertNotEqual('studsur', Person.objects.filter(role=1)[0].last_name), \
        'Teacher should not be able to change password of a student not in their class'

    def test_schooladmin_can_not_edit_student_and_teacher_information(self):
        """ Checks that a schooladministrator can't edit information about a teacher or a student not in their school"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin2")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin2")
        self.selenium.find_element_by_id('logInBtn').click()
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
        )
        try:
            self.selenium.find_element_by_id('editUserBtn').click()
            self.selenium.find_element_by_id('id_last_name').clear()
            self.selenium.find_element_by_id('id_last_name').send_keys('studsurn')
            self.selenium.find_element_by_id('saveNewInfoBtn').click()
        except NoSuchElementException:
            None
        self.assertNotEqual('studsurn', Person.objects.filter(role=1)[0].last_name), \
        'Schooladmin should not be able to edit information about a student at a different school'

        # teacher
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/teacher")
        )
        try:
            self.selenium.find_element_by_id('editUserBtn').click()
            self.selenium.find_element_by_id('id_last_name').clear()
            self.selenium.find_element_by_id('id_last_name').send_keys('teachersurn')
            self.selenium.find_element_by_id('saveNewInfoBtn').click()
        except NoSuchElementException:
            None
        self.assertNotEqual('teachersurn', Person.objects.filter(role=2)[0].last_name), \
        'Schooladmin should not be able to change password of a teacher not in their school'

    def test_change_password(self):
        """Checks that a teacher can change the password of a student in their class"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("teacher")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("teacher")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "logout")))
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "logout")))
        self.selenium.find_element_by_id('updatePasswordModalBtn').click()
        time.sleep(0.2)  # waiting for modal to open
        self.selenium.find_element_by_id('id_password').send_keys('studentpassword')
        self.selenium.find_element_by_id('id_password2').send_keys('studentpassword')
        self.selenium.find_element_by_id('updatePasswordBtn').click()
        time.sleep(0.2) # waiting for modal to close
        self.selenium.find_element_by_id('logout').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("student")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("studentpassword")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "logout")))
        self.assertNotIn('login', self.selenium.current_url), \
        'Login should not be in the url if the user was logged in successfully using the new password'

