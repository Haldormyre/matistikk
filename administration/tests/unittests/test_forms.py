import pytest
from administration import forms
from mixer.backend.django import mixer
pytestmark = pytest.mark.django_db


class TestPersonForm:
    def test_empty(self):
        form = forms.PersonForm(data={})
        assert form.is_valid() is False, 'Should be invalid when no data is given'

    def test_all_required_values(self):
        obj = mixer.blend('administration.Person')  # gives the object random values
        data = {'first_name': obj.first_name, 'last_name': obj.last_name, 'date_of_birth': obj.date_of_birth,
                'sex': obj.sex, 'role': obj.role}
        form = forms.PersonForm(data=data)
        assert form.is_valid() is True, 'Should be valid when given first_name, last_name, date_of_birth, sex and role'

    def test_all_values_given(self):
        gradeobj = mixer.blend('administration.Grade', grade_name='Gradename')
        gradeobj.save()
        obj = mixer.blend('administration.Person')  # gives the object random values
        obj.save()
        data = {'first_name': obj.first_name, 'last_name': obj.last_name, 'date_of_birth': obj.date_of_birth,
                'sex': obj.sex, 'email': obj.email, 'grades': obj.grades.all(), 'role': obj.role}
        form = forms.PersonForm(data=data)
        assert form.is_valid() is True, 'Should be valid when all fields in the form are given'


class TestChangePassword:
    def test_empty(self):
        form = forms.ChangePasswordForm(data={})
        assert form.is_valid() is False, 'Should return false when given no data'

    def test_all_values(self):
        data = {'password': 'testpassord', 'password2': 'testpassord'}
        form = forms.ChangePasswordForm(data=data)
        assert form.is_valid() is True, 'Should be true when given two identical paswords'


class TestSchoolForm:
    def test_empty(self):
        form = forms.SchoolForm(data={})
        assert form.is_valid() is False, 'Should return false when given no data'

    def test_all_values(self):
        obj = mixer.blend('administration.School')
        data = {'school_administrator': obj.school_administrator, 'school_name': obj.school_name, 'school_address':
            obj.school_address, 'is_active': 1}
        form = forms.SchoolForm(data=data)
        assert form.is_valid() is True, 'Should be true when given all fields'


class TestSchoolAdministrator:
    def test_empty(self):
        form = forms.SchoolAdministratorForm(data={})
        assert form.is_valid() is False, 'Should return false when given no data'

    def test_all_values(self):
        obj = mixer.blend('administration.Person')
        data = {'first_name': obj.first_name, 'last_name': obj.last_name, 'email': obj.email,
                'date_of_birth': obj.date_of_birth, 'sex': obj.sex}
        form = forms.SchoolAdministratorForm(data=data)
        assert form.is_valid() is True