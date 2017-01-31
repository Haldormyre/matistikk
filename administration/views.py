from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Person
# Create your views here.


class StudentCreateView(CreateView):
    template_name = 'administration/student_create.html'
    model = Person
    fields = ['grade', 'sex', 'first_name', 'username', 'last_name', 'is_staff', 'email']
