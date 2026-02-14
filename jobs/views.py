from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import JobSerializer
from .permissions import IsRecruiter
from rest_framework.decorators import api_view, permission_classes
from .models import Job
from .models import Application

class CreateJobView(APIView):
    permission_classes = [IsAuthenticated, IsRecruiter]

    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_jobs(request):
    jobs = Job.objects.all()
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)

class ApplyJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        job = Job.objects.get(id=job_id)

        if Application.objects.filter(job=job, applicant=request.user).exists():
            return Response({"message": "You already applied"}, status=400)

        Application.objects.create(job=job, applicant=request.user)
        return Response({"message": "Application submitted successfully"}, status=201)
