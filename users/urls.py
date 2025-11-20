from django.urls import path
from .views import (
    RegisterView, ProfileView, LogoutView, MyTokenObtainPairView, 
    ChangePasswordView, RequestPasswordResetView, VerifyOTPView, ResetPasswordView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Password Reset
    path('password-reset/request/', RequestPasswordResetView.as_view(), name='password_reset_request'),
    path('password-reset/verify/', VerifyOTPView.as_view(), name='password_reset_verify'),
    path('password-reset/confirm/', ResetPasswordView.as_view(), name='password_reset_confirm'),
]
