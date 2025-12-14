import uuid
from django.db import models
from django.conf import settings


class Project(models.Model):
	STATUS_CHOICES = [
		('active', 'Active'),
		('in_progress', 'In Progress'),
		('completed', 'Completed'),
	]
	
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
	owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='projects', on_delete=models.CASCADE)
	members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='projects_joined')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name
