from rest_framework import serializers
from .models import Application, Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['created_by']


class ApplicationSerializer(serializers.ModelSerializer):

    job_title = serializers.CharField(source="job.title", read_only=True)
    company = serializers.CharField(source="job.company_name", read_only=True)
    applicant_username = serializers.CharField(source="applicant.username", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "job_title",
            "company",
            "applicant_username",
            "status",
            "applied_at",
        ]

