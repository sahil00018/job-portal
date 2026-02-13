from django.urls import path
from .views import CreateJobView,list_jobs # make sure this matches your view name

urlpatterns = [
    path('create/', CreateJobView.as_view(), name='create_job'),
    path('list/', list_jobs, name='list_jobs'),
]
