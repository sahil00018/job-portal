from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import JobSerializer
from .permissions import IsRecruiter
from rest_framework.decorators import api_view, permission_classes
from .models import Job
from .models import Application
from django.db.models import Q

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

        # Allow only recruiter
        if request.user.role.lower() != "recruiter":
            return Response(
                {"error": "Only recruiters can view applications"},
                status=403
            )

        # Get jobs created by this recruiter
        jobs = Job.objects.filter(created_by=request.user)


        # Get applications for those jobs
        applications = Application.objects.filter(job__in=jobs)

        data = []

        for app in applications:
            data.append({
                "job_title": app.job.title,
                "candidate": app.applicant.username,
                "applied_at": app.applied_at
            })

        return Response(data)