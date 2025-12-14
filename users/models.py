import uuid
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUserManager(BaseUserManager):
	def make_random_password(self, length=12, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
		return get_random_string(length, allowed_chars)

	def create_user(self, email, password=None, **extra_fields):
		if not email:
			raise ValueError("Email is required")
		email = self.normalize_email(email).lower()  # Fix: Ensure lowercase for case-insensitive uniqueness
		if not password:
			password = self.make_random_password()
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		setattr(user, '_initial_password', password)  # helper so caller can communicate it to the user
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		if not password:
			raise ValueError("Superuser must have password")
		return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
	# Align with migrations: initial migration had UUID id, later migration changed to BigAutoField.
	# Keep DB stability by matching latest migration state: BigAutoField id plus added fields.
	email = models.EmailField(unique=True)
	# username was removed in migration 0002; keep it absent to avoid mismatch.
	first_name = models.CharField(max_length=50, blank=True)
	last_name = models.CharField(max_length=50, blank=True)
	phone_number = models.CharField(max_length=20, blank=True, null=True)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	date_joined = models.DateTimeField(default=timezone.now)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	objects = CustomUserManager()

	def __str__(self):
		return self.email


class UserProfile(models.Model):
	ROLE_CHOICES = [
		('admin', 'Admin'),
		('manager', 'Manager'),
		('developer', 'Developer'),
		('client', 'Client'),
	]
	user = models.OneToOneField(CustomUser, related_name='profile', on_delete=models.CASCADE)
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client', help_text="User's role in the system")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'User Profile'
		verbose_name_plural = 'User Profiles'

	def has_role(self, *roles):
		return self.role in roles

	def __str__(self):
		return f"{self.user.email} ({self.role})"


# Signal to auto-create UserProfile when CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
	"""Automatically create a UserProfile when a new user is created."""
	if created:
		UserProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
	"""Save UserProfile when user is saved."""
	if hasattr(instance, 'profile'):
		instance.profile.save()
	else:
		# Create profile if it doesn't exist (handles legacy users)
		UserProfile.objects.get_or_create(user=instance)
