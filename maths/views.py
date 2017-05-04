from django.views import generic
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy, reverse
from .forms import CreateTaskForm, CreateCategoryForm, CreateTestForm, CreateAnswerForm
from .models import Task, MultipleChoiceTask, Category, GeogebraTask, Test, TaskOrder, TaskCollection, Answer, \
    GeogebraAnswer
from braces import views
from django.http import JsonResponse
from administration.models import Grade, Person, Gruppe, School
import json
import datetime
from django.db.models import Q
import django_excel as excel

import random
from django.http import HttpResponseRedirect


class IndexView(LoginRequiredMixin, generic.TemplateView):
    """
    Class that displays the home page if logged in.

    **LoginRequiredMixin**
        Mixin from :ref:`Django braces` that check if the user is logged in.
    **TemplateView:**
        Inherits generic.Template that makes a page representing a specific template.
    """
    login_url = '/login/'
    template_name = 'maths/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['tasks'] = Task.objects.count()
        context['users'] = Person.objects.count()
        context['tests'] = TaskCollection.objects.count()
        context['schools'] = School.objects.count()
        context['grades'] = Grade.objects.count()
        context['groups'] = Gruppe.objects.count()

        if self.request.user.role == 1:
            answers = Answer.objects.filter(user=self.request.user)
            tests = Test.objects.filter(
                Q(person=self.request.user) | Q(grade__in=self.request.user.grades.all()) | Q(
                    gruppe__in=self.request.user.gruppe_set.all())).distinct()
            answered = tests.filter(answer__in=answers).distinct()
            context['answered'] = answered
            notanswered = []
            for test in tests:
                if test not in answered:
                    notanswered.append(test)
            context['notanswered'] = notanswered
        return context


class EquationEditorView(LoginRequiredMixin, generic.TemplateView):
    """
    Allows users to input math into the editor

    **LoginRequiredMixin**
        Mixin from :ref:`Django braces` that check if the user is logged in.
    **TemplateView:**
        Inherits generic.Template that makes a page representing a specific template.
    """
    login_url = '/login/'
    template_name = 'maths/equation_editor.html'


class CreateTaskView(generic.CreateView):
    """
    Class that creates a task.

    **CreateView:**
        Inherits Django's CreateView that displays a form for creating a object and
        saving the form when validated.
    """
    login_url = reverse_lazy('login')
    template_name = 'maths/task_form.html'
    form_class = CreateTaskForm
    success_url = reverse_lazy('maths:taskList')

    def get_context_data(self, **kwargs):
        """
            Function that adds all category objects and a form to create a new category to the context without
            overriding it.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(CreateTaskView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['categoryForm'] = CreateCategoryForm()
        return context

    def form_valid(self, form):
        """
        Function that checks if the submitted :ref:`CreateTaskForm` is correct. If correct adds the logged in user as
        the author and creates the task with its extra information.

        :param form: References to the filled out model form.
        :return: calls super with the new form.
        """
        task = form.save(commit=False)
        task.author = self.request.user
        task.save()

        if task.answertype == 2:
            options = self.request.POST['options']
            optiontable = options.split('|||||')
            correct = optiontable[0]
            x = 1
            for option in optiontable[1:]:
                if int(correct) == x:
                    multiplechoice = MultipleChoiceTask(option=option, task=task, correct=True)
                else:
                    multiplechoice = MultipleChoiceTask(option=option, task=task, correct=False)
                multiplechoice.save()
                x += 1

        if task.extra:
            base64 = self.request.POST['base64']
            preview = self.request.POST['preview']
            geogebratask = GeogebraTask(base64=base64, preview=preview, task=task)
            geogebratask.save()
        return super(CreateTaskView, self).form_valid(form)


class CategoryListView(generic.ListView):
    """
    Class that displays a template containing all category objects.

    **ListView:**
        Inherits Django's ListView that makes a page representing a list of objects.
    """
    model = Category
    template_name = 'maths/category_list.html'


class CategoryCreateView(views.AjaxResponseMixin, generic.CreateView):
    """
    Class that creates a category.

    **AjaxResponseMixin:**
        This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
    **CreateView:**
        Inherits Django's CreateView that displays a form for creating a object and
        saving the form when validated.
    """
    model = Category
    fields = ['category_title']
    template_name = 'maths/category_form.html'
    success_url = reverse_lazy('maths:categoryList')

    def post_ajax(self, request, *args, **kwargs):
        """
            Function that checks if the post request is an ajax request, creates a new category and returns the
            category_id.

            :param request: Request that was sent to CategoryCreateView.
            :param args:  Arguments that were sent with the request.
            :param kwargs: Keyword-arguments.
            :return: JsonResponse containing the category id.
        """
        category_title = request.POST['category']
        category = Category(category_title=category_title)
        category.save()
        data = {
            'category_id': category.id
        }
        return JsonResponse(data)


class CategoryUpdateView(generic.UpdateView):
    """
    Class that updates a category.

    **UpdateView:**
        Inherits Django's UpdateView that displays a form for updating a specific object and
        saving the form when validated.
    """
    model = Category
    fields = ['category_title']
    template_name = 'maths/category_form.html'
    success_url = reverse_lazy('maths:categoryList')
    pk_url_kwarg = 'category_pk'


class TaskListView(views.AjaxResponseMixin, generic.ListView):
    """
    Class that displays a template containing all task objects.

    **AjaxResponseMixin:**
        This mixin from :ref:`Django braces` provides hooks for altenate processing of AJAX requests based on HTTP verb.
    **ListView:**
        Inherits Django's ListView that makes a page representing a list of objects.
    """
    login_url = reverse_lazy('login')
    template_name = 'maths/task_list.html'
    model = Task

    def get_ajax(self, request, *args, **kwargs):
        """
            Function that checks if the get request is an ajax request and returns the all the necessary information
            around a specific task.

            :param request: Request that was sent to TaskListView.
            :param args:  Arguments that were sent with the request.
            :param kwargs: Keyword-arguments.
            :return: JsonResponse containing the necessary Task information.
        """
        multiplechoice = []
        task_id = request.GET['task_id']
        task = Task.objects.get(id=task_id)
        data = {
            'task_title': task.title,
            'task_text': task.text,
            'task_reasoning': task.reasoning,
            'task_extra': task.extra,
            'task_answertype': task.answertype,
            'options': multiplechoice
        }
        if task.extra:
            geogebra = GeogebraTask.objects.get(task_id=task_id)
            data['geogebra_preview'] = geogebra.preview
        if task.answertype == 2:
            multiplechoice_list = MultipleChoiceTask.objects.filter(task_id=task_id)
            for option in multiplechoice_list:
                multiplechoice.append({
                    "option": option.option,
                    "correct": option.correct,
                })
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
            Function that adds all category and geogebratask objects to the context.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TaskListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['geogebratask'] = GeogebraTask.objects.all()
        return context


class TaskUpdateView(generic.UpdateView):
    """
    Class that updates a task.

    **UpdateView:**
        Inherits Django's UpdateView that displays a form for updating a specific object and
        saving the form when validated.
    """
    login_url = reverse_lazy('login')
    template_name = 'maths/task_update.html'
    model = Task
    form_class = CreateTaskForm
    pk_url_kwarg = 'task_pk'
    success_url = reverse_lazy('maths:taskList')

    def get_context_data(self, **kwargs):
        """
            Function that adds the multiple choice options and geogebra to the context.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TaskUpdateView, self).get_context_data(**kwargs)
        if GeogebraTask.objects.filter(task=self.kwargs.get("task_pk")):
            context['geogebra'] = GeogebraTask.objects.filter(task=self.kwargs.get("task_pk"))
        if MultipleChoiceTask.objects.filter(task=self.kwargs.get("task_pk")):
            context['options'] = MultipleChoiceTask.objects.filter(task=self.kwargs.get("task_pk"))

        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        """
            Function that checks if the submitted :ref:`CreateTaskForm` is correct. If correct it updates the task with
            the new values and creates new multiple choice options or geogebra if it's added.

            :param form: References to the filled out model form.
            :return: calls super with the new form.
        """
        task = form.save(commit=False)
        task.save()

        if task.extra:
            base64 = self.request.POST['base64']
            preview = self.request.POST['preview']
            geotask = GeogebraTask.objects.filter(task=task)
            if geotask.count() > 0:
                geogebratask = GeogebraTask.objects.get(task=task)
                geogebratask.base64 = base64
                geogebratask.preview = preview
                geogebratask.save()
            else:
                geogebratask = GeogebraTask(task=task, base64=base64, preview=preview)
                geogebratask.save()

        if task.answertype == 2:
            options = self.request.POST['options']
            optiontable = options.split('|||||')
            correct = optiontable[0]
            taskoptions = MultipleChoiceTask.objects.filter(task=task)
            newoptions = (len(optiontable) - 1) - len(taskoptions)

            x = 1
            for taskoption in taskoptions:
                if int(correct) == x:
                    taskoption.correct = True
                    taskoption.option = optiontable[x]
                else:
                    taskoption.correct = False
                    taskoption.option = optiontable[x]
                taskoption.save()
                x += 1

            if newoptions > 0:
                for option in optiontable[len(optiontable) - newoptions:]:
                    if int(correct) == x:
                        multiplechoice = MultipleChoiceTask(task=task, option=option, correct=True)
                    else:
                        multiplechoice = MultipleChoiceTask(task=task, option=option, correct=False)
                    multiplechoice.save()
                    x += 1
        return super(TaskUpdateView, self).form_valid(form)


class TaskCollectionCreateView(generic.CreateView):
    """
    Class that creates a test.

    **CreateView:**
        Inherits Django's CreateView that displays a form for creating a object and
        saving the form when validated.
    """
    template_name = 'maths/taskCollection_form.html'
    model = TaskCollection
    fields = ['test_name', 'tasks']

    def get_context_data(self, **kwargs):
        """
            Function that adds the tasks and categories to the context.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TaskCollectionCreateView, self).get_context_data(**kwargs)
        context['tasks'] = Task.objects.all()
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        """
            Function that checks if the submitted modelform is correct. If correct it adds the logged in user as author
            of the test and saves it.

            :param form: References to the filled out model form.
            :return: calls super with the new form.
        """
        task_collection = form.save(commit=False)
        task_collection.author = self.request.user
        task_collection.save()
        return super(TaskCollectionCreateView, self).form_valid(form)


class TaskCollectionListView(generic.ListView):
    """
       Class that displays a template containing all test objects.

       **ListView:**
           Inherits Django's ListView that makes a page representing a list of objects.
    """
    template_name = 'maths/taskCollection_list.html'
    model = TaskCollection


class TaskCollectionDetailView(views.AjaxResponseMixin, generic.DetailView):
    """
    Class that displays information about a single test object based on the test_id

    **DetailView:**
        Inherits generic.DetailView that makes a page representing a specific object.
    """
    template_name = 'maths/taskCollection_detail.html'
    model = TaskCollection
    pk_url_kwarg = 'taskCollection_pk'

    def get_ajax(self, request, *args, **kwargs):
        students = []
        teachers = []
        grades = []
        groups = []
        test = Test.objects.get(id=request.GET['published_id'])
        student_list = Person.objects.filter(tests__exact=test, role=1)
        teacher_list = Person.objects.filter(tests__exact=test, role=2)
        grade_list = Grade.objects.filter(tests__exact=test)
        group_list = Gruppe.objects.filter(tests__exact=test)
        for student in student_list:
            students.append({
                'username': student.username,
                'first_name': student.first_name,
                'last_name': student.last_name
            })
        for teacher in teacher_list:
            teachers.append({
                'username': teacher.username,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name
            })
        for grade in grade_list:
            grades.append({
                'grade_name': grade.grade_name,
                'school': grade.school.school_name,
                'id': grade.id,
                'school_id': grade.school.id
            })
        for group in group_list:
            groups.append({
                'group_name': group.group_name,
                'grade': group.grade.school.school_name + " - " + group.grade.grade_name,
                'creator': group.creator.get_full_name(),
                'id': group.id

            })
        data = {
            'students': students,
            'teachers': teachers,
            'grades': grades,
            'groups': groups
        }
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
            Function that adds all the categories to the context.

            :param kwargs: Keyword arguments
            :return: Returns the updated context
        """
        context = super(TaskCollectionDetailView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['publishedTests'] = Test.objects.filter(task_collection_id=self.kwargs.get('taskCollection_pk'))
        return context


class TestCreateView(views.AjaxResponseMixin, generic.CreateView):
    form_class = CreateTestForm
    template_name = 'maths/test_form.html'

    def get_success_url(self):
        success = reverse_lazy('maths:taskCollectionDetail',
                               kwargs={'taskCollection_pk': self.kwargs.get('taskCollection_pk')})
        return success

    def post_ajax(self, request, *args, **kwargs):
        test_id = request.POST['id']
        test = Test.objects.get(id=test_id)
        new_due = request.POST['dueDate']
        test.dueDate = new_due
        test.save()
        print(test.dueDate)
        data = {
            'dueDate': new_due
        }
        return JsonResponse(data)

    def get_initial(self):
        """
        Function that checks for preset values and sets them to the fields.

        :return: List of the preset values.
        """
        return {'task_collection': self.kwargs.get('taskCollection_pk')}

    def get_context_data(self, **kwargs):
        context = super(TestCreateView, self).get_context_data(**kwargs)
        context['taskcollection'] = TaskCollection.objects.get(id=self.kwargs.get('taskCollection_pk'))
        context['grades'] = Grade.objects.all()
        context['teachers'] = Person.objects.filter(role=2)
        context['students'] = Person.objects.filter(role=1)
        context['schools'] = School.objects.all()
        context['groups'] = Gruppe.objects.all()
        return context

    def form_valid(self, form):
        test = form.save(commit=False)
        test.save()
        data = form.cleaned_data
        for person in data['persons']:
            person.tests.add(test)
        for grade in data['grades']:
            grade.tests.add(test)
        for group in data['groups']:
            group.tests.add(test)
        if not data['randomOrder']:
            order_list = data['order']
            order_table = order_list.split('|||||')
            x = 1
            for order in order_table:
                print(order)
                taskorder = TaskOrder(test=test, task_id=order, order=x)
                taskorder.save()
                x += 1
        return super(TestCreateView, self).form_valid(form)


class TestDetailView(views.AjaxResponseMixin, generic.DetailView):
    model = Test
    template_name = 'maths/test_detail.html'
    pk_url_kwarg = 'test_pk'

    def get_context_data(self, **kwargs):
        context = super(TestDetailView, self).get_context_data(**kwargs)
        test = Test.objects.get(id=self.kwargs.get('test_pk'))
        if self.kwargs.get('grade_pk'):
            grade = Grade.objects.get(id=self.kwargs.get('grade_pk'))
            context['students'] = Person.objects.filter(grades=grade)
            context['fromGrade'] = grade
        elif self.request.user.role == 2:
            grades = Grade.objects.filter(person=self.request.user)
            context['students'] = Person.objects.filter(tests__exact=test, role=1, grades__in=grades).distinct()
            print(context['students'])
            context['grades'] = grades.filter(tests__exact=test)
            context['groups'] = Gruppe.objects.filter(tests__exact=test, grade__in=grades)
        else:
            context['students'] = Person.objects.filter(tests__exact=test, role=1)
            context['teachers'] = Person.objects.filter(tests__exact=test, role=2)
            context['grades'] = Grade.objects.filter(tests__exact=test)
            context['groups'] = Gruppe.objects.filter(tests__exact=test)
            context['allstudents'] = Person.objects.filter(role=1).exclude(tests__exact=test)
            context['allteachers'] = Person.objects.filter(role=2).exclude(tests__exact=test)
            context['allgrades'] = Grade.objects.all().exclude(tests__exact=test)
            context['allgroups'] = Gruppe.objects.all().exclude(tests__exact=test)
            context['allschools'] = School.objects.all()
        return context


class AnswerCreateView(generic.FormView):
    form_class = CreateAnswerForm
    template_name = 'maths/answer_form.html'

    def get_success_url(self):
        return reverse_lazy('maths:index')

    def get_context_data(self, **kwargs):
        context = super(AnswerCreateView, self).get_context_data(**kwargs)
        test = Test.objects.get(id=self.kwargs.get('test_pk'))
        geogebratasks = GeogebraTask.objects.filter(task__in=test.task_collection.tasks.all())
        options = MultipleChoiceTask.objects.filter(task__in=test.task_collection.tasks.all())
        randomtest = sorted(test.task_collection.tasks.all(), key=lambda x: random.random())
        context['test'] = test
        context['randomtest'] = randomtest
        context['geogebratask'] = geogebratasks
        context['options'] = options
        z = 0
        forms = []
        for task in test.task_collection.tasks.all():
            forms.append(CreateAnswerForm(prefix="task" + str(z)))
            z += 1
        context['formlist'] = forms
        return context

    def post(self, request, *args, **kwargs):
        test = Test.objects.get(id=self.kwargs.get('test_pk'))
        y = 0
        for task in test.task_collection.tasks.all():
            text = request.POST["task" + str(y) + "-text"]
            reasoning = request.POST["task" + str(y) + "-reasoning"]
            taskid = request.POST["task" + str(y) + "-task"]
            task = Task.objects.get(id=taskid)
            answer = Answer(text=text, reasoning=reasoning, user=self.request.user, test=test, task=task)
            answer.save()
            base64 = request.POST["task" + str(y) + "-base64answer"]
            if task.extra:
                geogebraanswer = GeogebraAnswer(answer=answer, base64=base64)
                geogebraanswer.save()
            y += 1
        url = reverse('maths:index')
        return HttpResponseRedirect(url)


class TestListView(views.AjaxResponseMixin, generic.ListView):
    model = Test
    template_name = 'maths/test_list.html'

    def get_ajax(self, request, *args, **kwargs):
        test = Test.objects.get(id=request.GET['test'])
        grade_table = []
        group_table = []
        student_table = []
        grades = request.GET['grades']
        groups = request.GET['groups']
        students = request.GET['students']
        grade_list = json.loads(grades)
        group_list = json.loads(groups)
        student_list = json.loads(students)
        for grade_id in grade_list:
            if test.grade_set.filter(id=grade_id).exists():
                grade_table.append(True)
            else:
                grade_table.append(False)
        for group_id in group_list:
            if test.gruppe_set.filter(id=group_id).exists():
                group_table.append(True)
            else:
                group_table.append(False)
        for student_id in student_list:
            if test.person_set.filter(id=student_id).exists() or test.grade_set.filter(
                    person__id=student_id).exists() or test.gruppe_set.filter(persons__id=student_id).exists():
                student_table.append(True)
            else:
                student_table.append(False)
        data = {
            "grades": grade_table,
            'groups': group_table,
            'students': student_table
        }
        return JsonResponse(data)

    def post_ajax(self, request, *args, **kwargs):
        test = Test.objects.get(id=request.POST['test'])
        grades = request.POST['grades']
        groups = request.POST['groups']
        students = request.POST['students']
        grade_list = json.loads(grades)
        group_list = json.loads(groups)
        student_list = json.loads(students)
        for grade_id in grade_list:
            grade = Grade.objects.get(id=grade_id)
            grade.tests.add(test)
        for group_id in group_list:
            group = Gruppe.objects.get(id=group_id)
            group.tests.add(test)
        for student_id in student_list:
            student = Person.objects.get(id=student_id)
            student.tests.add(test)
        data = {'test': 'test'}
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super(TestListView, self).get_context_data(**kwargs)
        user = Person.objects.get(username=self.kwargs.get('slug'))
        context['object_list'] = Test.objects.filter(person=user)
        context['grades'] = Grade.objects.filter(person=user)
        return context


class AnswerDetailView(generic.DetailView):
    model = Answer
    template_name = 'maths/answer_detail.html'
    pk_url_kwarg = 'answer_pk'


def export_data(request, test_pk):
    test = Test.objects.get(id=test_pk)
    answers = Answer.objects.filter(test=test).order_by('task')
    column_names = ['user_id', 'task_id', 'text', 'reasoning']
    return excel.make_response_from_query_sets(answers, column_names, 'xls', file_name=test.task_collection.test_name)
