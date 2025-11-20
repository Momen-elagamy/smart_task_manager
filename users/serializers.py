from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import IntegrityError

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(write_only=True, required=False)
    department = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    # Accept username but ignore it (frontend form requires it)
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name',
            'password', 'password2',
            'role', 'department', 'username'
        )
        # Disable default UniqueValidator to provide our clearer message
        extra_kwargs = {
            'email': {
                'validators': []
            }
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def validate_email(self, value):
        email = (value or '').strip().lower()
        if not email:
            raise serializers.ValidationError("This field is required.")
        # Unique check with clearer message
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def create(self, validated_data):
        role = validated_data.pop('role', 'client')
        department = validated_data.pop('department', None)
        validated_data.pop('username', None)  # not used in our CustomUser
        validated_data.pop('password2')
        # Normalize email to lowercase
        if 'email' in validated_data and validated_data['email']:
            validated_data['email'] = validated_data['email'].strip().lower()
        try:
            user = User.objects.create_user(**validated_data)
        except IntegrityError:
            # In case database-level unique constraint triggers
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        if hasattr(user, 'profile'):
            if role:
                user.profile.role = role
            if department is not None and hasattr(user.profile, 'department'):
                user.profile.department = department
            user.profile.save()
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Call the parent class's validate method
        data = super().validate(attrs)
        
        # The default validation raises AuthenticationFailed with specific messages.
        # We will catch it and raise a more generic one for security.
        # The user object is set by the parent's validate method.
        if not self.user or not self.user.is_active:
            raise serializers.ValidationError({"detail": "Unable to log in with provided credentials."})
        
        return data


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)
    department = serializers.CharField(source='profile.department', allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'role', 'department',
            'is_staff', 'is_active', 'date_joined'
        )

    def update(self, instance, validated_data):
        # Extract profile data if 'profile' key exists (DRF nested write)
        profile_data = validated_data.pop('profile', {})

        # Update basic user fields
        for attr in ['first_name', 'last_name', 'email']:
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])
        instance.save()

        # Update profile fields (department only; role is read-only here)
        profile = getattr(instance, 'profile', None)
        if profile is not None and profile_data:
            if 'department' in profile_data:
                profile.department = profile_data['department']
                profile.save()

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    def validate(self, attrs):
        # Additional cross-field validation can be added here if needed
        return attrs


class RequestPasswordResetSerializer(serializers.Serializer):
    """Request OTP for password reset via email or phone"""
    identifier = serializers.CharField(required=True, help_text="Email or Phone Number")
    method = serializers.ChoiceField(choices=['email', 'sms'], required=True)
    
    def validate_identifier(self, value):
        identifier = value.strip()
        method = self.initial_data.get('method')
        
        if method == 'email':
            # Validate email format
            if '@' not in identifier:
                raise serializers.ValidationError("Invalid email address")
        elif method == 'sms':
            # Validate phone number format (simple validation)
            if not identifier.replace('+', '').replace(' ', '').replace('-', '').isdigit():
                raise serializers.ValidationError("Invalid phone number")
        
        return identifier


class VerifyOTPSerializer(serializers.Serializer):
    """Verify OTP and get reset token"""
    identifier = serializers.CharField(required=True)
    otp = serializers.CharField(required=True, max_length=6, min_length=6)
    method = serializers.ChoiceField(choices=['email', 'sms'], required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Reset password with token"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords must match"})
        return attrs
