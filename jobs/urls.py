from django.urls import path
from .views import ApplyJobView, CreateJobView,list_jobs # make sure this matches your view name

urlpatterns = [
    path('create/', CreateJobView.as_view(), name='create_job'),
    path('list/', list_jobs, name='list_jobs'),
    path('apply/<int:job_id>/', ApplyJobView.as_view(), name='apply-job'),

]
