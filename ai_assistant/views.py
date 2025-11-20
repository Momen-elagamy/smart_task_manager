from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .utils import analyze_productivity, suggest_tasks
from .ai_engine import get_ai_response, summarize_project, generate_task_from_prompt
from projects.models import Project

class ProductivityReportView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        report = analyze_productivity(request.user)
        return Response(report)

class TaskSuggestionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        suggestions = suggest_tasks(request.user)
        return Response({"suggestions": suggestions})

class AIChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        prompt = request.data.get("prompt")
        reply = get_ai_response(prompt, user=request.user)
        return Response({"response": reply})

class ProjectSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, project_id):
        project = Project.objects.get(id=project_id)
        summary = summarize_project(project)
        return Response({"project": project.name, "summary": summary})

class TaskGeneratorView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        prompt = request.data.get("prompt")
        result = generate_task_from_prompt(request.user, prompt)
        return Response(result)
