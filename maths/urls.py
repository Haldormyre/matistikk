from django.conf.urls import url
from . import views

app_name = 'maths'
urlpatterns = [
    # /maths/
    url(r'^$', views.IndexView.as_view(), name='index'),

]