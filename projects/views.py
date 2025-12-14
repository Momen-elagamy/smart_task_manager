from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Project
from .serializers import ProjectSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class ProjectViewSet(viewsets.ModelViewSet):
	serializer_class = ProjectSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return Project.objects.filter(Q(owner=user) | Q(members=user)).distinct().select_related('owner')

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class ProjectListCreateView(ListCreateAPIView):
	serializer_class = ProjectSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return Project.objects.filter(Q(owner=user) | Q(members=user)).distinct().select_related('owner')

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)


class ProjectDetailView(RetrieveUpdateDestroyAPIView):
	serializer_class = ProjectSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return Project.objects.filter(Q(owner=user) | Q(members=user)).distinct().select_related('owner')


class ProjectsPageView(LoginRequiredMixin, ListView):
	model = Project
	template_name = 'projects/projects_list.html'
	context_object_name = 'projects'

	def get_queryset(self):
		return Project.objects.filter(owner=self.request.user).order_by('-created_at')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		qs = ctx['projects']
		ctx['total_projects'] = qs.count()
		return ctx
