from urllib import request

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ApplicationSerializer, JobSerializer
from .permissions import IsRecruiter
from rest_framework.decorators import api_view, permission_classes
from .models import Job
from .models import Application
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination


class CreateJobView(APIView):
    permission_classes = [IsAuthenticated, IsRecruiter]

    def post(self, request):
        if request.user.role != 'recruiter':
         return Response({"error": "Only recruiters can create jobs"}, status=403)

        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
@api_view(['GET'])
@permission_classes([IsAuthenticated])

def list_jobs(request):

    jobs = Job.objects.all()

    # Title filter
    title = request.query_params.get('title')
    if title:
        jobs = jobs.filter(title__icontains=title.strip())

    # Company filter
    company = request.query_params.get('company')
    if company:
        jobs = jobs.filter(company_name__icontains=company.strip())

    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)

    
class ApplyJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):

        if request.user.role.lower() != "candidate":
            return Response({"error": "Only candidates can apply"}, status=403)

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        # ✅ Fix here
        if Application.objects.filter(job=job, applicant=request.user).exists():
            return Response({"message": "You already applied"}, status=400)

        Application.objects.create(
            job=job,
            applicant=request.user
        )

        return Response({"message": "Applied successfully"}, status=201)


class RecruiterApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role.lower() != "recruiter":
            return Response({"error": "Only recruiters allowed"}, status=403)

        applications = Application.objects.filter(
            job__created_by=request.user
        )

        # Filter by status
        status_filter = request.query_params.get("status")
        if status_filter:
            applications = applications.filter(status=status_filter.upper())

        paginator = PageNumberPagination()
        paginator.page_size = 5

        result_page = paginator.paginate_queryset(applications, request)
        serializer = ApplicationSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

class UpdateApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, application_id):

        # Only recruiter allowed
        if request.user.role.lower() != "recruiter":
            return Response(
                {"error": "Only recruiters can update status"},
                status=403
            )

        application = get_object_or_404(Application, id=application_id)

        # Ensure recruiter owns the job
        if application.job.created_by != request.user:
            return Response(
                {"error": "You can update only your job applications"},
                status=403
            )

        new_status = request.data.get("status")

        if new_status not in ["PENDING", "SHORTLISTED", "REJECTED"]:
            return Response(
                {"error": "Invalid status"},
                status=400
            )

        application.status = new_status
        application.save()

        return Response(
            {"message": "Status updated successfully"},
            status=200
        )
from .serializers import ApplicationSerializer
from rest_framework.pagination import PageNumberPagination

class CandidateApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role.lower() != "candidate":
            return Response({"error": "Only candidates allowed"}, status=403)

        applications = Application.objects.filter(applicant=request.user)

        # Filter by status
        status_filter = request.query_params.get("status")
        if status_filter:
            applications = applications.filter(status=status_filter.upper())

        paginator = PageNumberPagination()
        paginator.page_size = 5

        result_page = paginator.paginate_queryset(applications, request)
        serializer = ApplicationSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
