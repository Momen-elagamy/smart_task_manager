from django.urls import path
from .views import UserRegisterApiView, AddMemberView, InviteApiView

urlpatterns = [
    path('register/', UserRegisterApiView.as_view(), name='user-register-api'),
    # HTML page for inviting/adding a member (restricted to Admin/Manager)
    path('add-member/', AddMemberView.as_view(), name='add_member'),
    # API endpoint for inviting a member
    path('invite/', InviteApiView.as_view(), name='invite-member-api'),
]
