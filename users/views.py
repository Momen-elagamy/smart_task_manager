from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout as django_logout
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
import json
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

class InviteApiView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		data = request.data or {}
		email = (data.get('email') or '').strip().lower()
		full_name = data.get('full_name', '') or ''
		first_name = data.get('first_name', '').strip()
		last_name = data.get('last_name', '').strip()
		phone_number = (data.get('phone') or data.get('phone_number') or '').strip()
		role = (data.get('role') or '').strip().lower()

		if not email:
			return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

		if User.objects.filter(email=email).exists():
			return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

		if full_name and not (first_name or last_name):
			parts = full_name.strip().split(None, 1)
			first_name = parts[0]
			last_name = parts[1] if len(parts) > 1 else ''

		password = User.objects.make_random_password()
		user = User.objects.create_user(
			email=email,
			first_name=first_name,
			last_name=last_name,
			phone_number=phone_number,
			password=password,
		)

		if role and hasattr(user, 'profile'):
			allowed_roles = {choice[0] for choice in user.profile.ROLE_CHOICES}
			if role in allowed_roles:
				user.profile.role = role
				user.profile.save(update_fields=['role'])

		temporary_password = getattr(user, '_initial_password', password)

		return Response(
			{
				'success': True,
				'user_id': user.id,
				'email': user.email,
				'first_name': user.first_name,
				'last_name': user.last_name,
				'phone_number': user.phone_number,
				'temporary_password': temporary_password,
			},
			status=status.HTTP_201_CREATED,
		)

class TeamPageView(LoginRequiredMixin, TemplateView):
    """HTML page for team management"""
    template_name = 'users/team_list.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['team_members'] = User.objects.all()[:50]
        return ctx

class UserRegisterApiView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		# DRF parses JSON/form into request.data safely
		data = getattr(request, 'data', {}) or {}

		email = data.get('email')
		password = data.get('password')
		first_name = data.get('first_name', '')
		last_name = data.get('last_name', '')
		phone_number = data.get('phone_number')

		if not email or not password:
			return JsonResponse({"error": "email and password required"}, status=400)

		if User.objects.filter(email=email).exists():
			return JsonResponse({"error": "Email already registered"}, status=400)

		# Password complexity validation (simple, can be extended)
		missing = []
		if len(password) < 8: missing.append('min_length_8')
		if not any(c.islower() for c in password): missing.append('lowercase')
		if not any(c.isupper() for c in password): missing.append('uppercase')
		if not any(c.isdigit() for c in password): missing.append('digit')
		if not any(c in '!@#$%^&*()-_=+[]{};:,<.>/?' for c in password): missing.append('special_char')
		if missing:
			return JsonResponse({"error": "weak_password", "missing": missing}, status=400)

		user = User.objects.create_user(
			email=email,
			password=password,
			first_name=first_name,
			last_name=last_name,
			phone_number=phone_number,
		)

		# Issue JWT tokens immediately after registration
		refresh = RefreshToken.for_user(user)
		access = refresh.access_token
		return JsonResponse({
			"id": user.id,
			"email": user.email,
			"first_name": user.first_name,
			"last_name": user.last_name,
			"phone_number": user.phone_number,
			"access": str(access),
			"refresh": str(refresh),
		}, status=201)

	def get(self, request):
		return JsonResponse({"detail": "POST email & password (+ optional first_name, last_name, phone_number)."}, status=200)


class UserLoginApiView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		data = getattr(request, 'data', {}) or {}

		email = data.get('email')
		password = data.get('password')
		if not email or not password:
			return JsonResponse({"error": "email and password required"}, status=400)

		user = authenticate(request, username=email, password=password)
		if not user:
			return JsonResponse({"error": "invalid_credentials"}, status=401)
		# Always issue fresh JWT tokens on login
		refresh = RefreshToken.for_user(user)
		access = refresh.access_token
		# Optional: maintain session for template views
		try:
			login(request, user)
		except Exception:
			pass
		return JsonResponse({
			"detail": "login_success",
			"email": user.email,
			"first_name": user.first_name,
			"last_name": user.last_name,
			"access": str(access),
			"refresh": str(refresh),
		}, status=200)

	def get(self, request):
		return JsonResponse({"detail": "POST email & password to login."}, status=200)


class AddMemberView(LoginRequiredMixin, TemplateView):
	"""Simple Add Member HTML page for admins/managers."""
	template_name = 'users/add_member.html'

	def dispatch(self, request, *args, **kwargs):
		# Allow superusers, staff, or members of Admin/Manager groups
		allowed = False
		try:
			allowed = request.user.is_superuser or request.user.is_staff or request.user.groups.filter(name__in=['Admin', 'Manager']).exists()
		except Exception:
			allowed = request.user.is_superuser or request.user.is_staff

		if not allowed:
			# Redirect back to team page if user is not allowed to view this page
			return redirect('team')

		return super().dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		try:
			ctx['team_count'] = User.objects.filter(is_active=True).count()
			ctx['recent_members'] = list(User.objects.filter(is_active=True).order_by('-date_joined')[:4].values('id', 'first_name', 'last_name', 'email'))
		except Exception:
			ctx['team_count'] = 0
			ctx['recent_members'] = []
		return ctx


class TeamMembersApiView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		from tasks.models import Task
		from random import choice
		
		users_qs = User.objects.filter(is_active=True)[:200]
		members = []
		
		roles = ['admin', 'manager', 'developer', 'designer']
		
		for user in users_qs:
			# Get task stats for each user
			user_tasks = Task.objects.filter(assigned_to=user)
			tasks_count = user_tasks.count()
			completed_count = user_tasks.filter(status__in=['done', 'completed']).count()
			
			# Determine role (check if user has profile with role, else random)
			role = 'developer'
			if hasattr(user, 'profile') and hasattr(user.profile, 'role'):
				role = user.profile.role or 'developer'
			elif user.is_superuser:
				role = 'admin'
			elif user.is_staff:
				role = 'manager'
			
			members.append({
				'id': user.id,
				'email': user.email,
				'first_name': user.first_name or '',
				'last_name': user.last_name or '',
				'role': role,
				'tasks_count': tasks_count,
				'completed_count': completed_count,
				'is_online': True  # Simplified - could track via last_login
			})
		
		return JsonResponse({"results": members}, status=200)


class UserProfileApiView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		user = request.user
		return JsonResponse({
			"id": user.id,
			"email": user.email,
			"first_name": user.first_name,
			"last_name": user.last_name,
		}, status=200)

	def patch(self, request):
		if request.content_type and 'application/json' in request.content_type:
			try:
				data = json.loads(request.body.decode('utf-8'))
			except json.JSONDecodeError:
				return JsonResponse({"error": "Invalid JSON"}, status=400)
		else:
			data = request.POST.dict()
		user = request.user
		updated = False
		for field in ['first_name', 'last_name']:
			val = data.get(field)
			if val is not None:
				setattr(user, field, val)
				updated = True
		if updated:
			user.save()
		return JsonResponse({"detail": "profile_updated"}, status=200)

	def post(self, request):
		return self.patch(request)


class UserLogoutApiView(APIView):
	permission_classes = [IsAuthenticated]
	def post(self, request):
		try:
			django_logout(request)
		except Exception:
			pass
		return JsonResponse({"detail": "logout_success"}, status=200)

