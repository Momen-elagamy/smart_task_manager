from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from rest_framework.permissions import IsAuthenticated
from .models import Task, Comment, Attachment, Tag
from .serializers import (
	TaskSerializer, CommentSerializer, AttachmentSerializer, TagSerializer
)
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class TaskViewSet(viewsets.ModelViewSet):
	serializer_class = TaskSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		qs = Task.objects.filter(
			models.Q(assigned_to=user) | models.Q(project__owner=user) | models.Q(project__members=user)
		).select_related('project', 'assigned_to').distinct()
		status_param = self.request.query_params.get('status')
		if status_param:
			qs = qs.filter(status=status_param)
		return qs


class CommentViewSet(viewsets.ModelViewSet):
	serializer_class = CommentSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return Comment.objects.filter(task__in=Task.objects.filter(models.Q(assigned_to=user) | models.Q(project__owner=user) | models.Q(project__members=user))).select_related('task','author').distinct()


class AttachmentViewSet(viewsets.ModelViewSet):
	serializer_class = AttachmentSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return Attachment.objects.filter(task__in=Task.objects.filter(models.Q(assigned_to=user) | models.Q(project__owner=user) | models.Q(project__members=user))).select_related('task','uploaded_by').distinct()

	@action(detail=False, methods=['get'])
	def images(self, request):
		"""Return only image attachments."""
		queryset = self.get_queryset().filter(mime_type__startswith='image/')
		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)

	@action(detail=False, methods=['get'])
	def documents(self, request):
		"""Return only document attachments."""
		document_types = [
			'application/pdf',
			'text/plain',
			'application/msword',
			'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
			'application/vnd.ms-excel',
			'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
			'application/zip',
		]
		queryset = self.get_queryset().filter(mime_type__in=document_types)
		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
	serializer_class = TagSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return Tag.objects.filter(tasks__in=Task.objects.filter(models.Q(assigned_to=user) | models.Q(project__owner=user) | models.Q(project__members=user))).distinct()


class TasksPageView(LoginRequiredMixin, ListView):
	model = Task
	template_name = 'tasks/tasks_glass.html'
	context_object_name = 'tasks'

	def get_queryset(self):
		return Task.objects.filter(assigned_to=self.request.user).order_by('-due_date')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		qs = ctx['tasks']
		ctx['total_tasks'] = qs.count()
		ctx['completed_tasks'] = qs.filter(status='completed').count()
		return ctx
