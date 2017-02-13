from django import forms
from .models import Person, Grade
from django.core.exceptions import ValidationError

from django.urls import reverse
from django.http import HttpResponseForbidden
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin


class PersonForm(forms.ModelForm):
    first_name = forms.CharField(required=True, label='Fornavn')
    last_name = forms.CharField(required=True, label='Etternavn')

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'sex', 'grades', 'is_staff', 'is_active', 'role']


class FileUpload(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(FileUpload, self).__init__(*args, **kwargs)
        self.fields['file'].help_text = 'Aksepterte filformat: .xls, .xlsx, .ods, .csv'
