from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChatRoomViewSet,
    ChatMessageViewSet,
    MessageReactionViewSet,
    ChatPageView,
    TeamChatPageView,
    ChatRoomRedirectView,
)

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chat-rooms')
router.register(r'messages', ChatMessageViewSet, basename='chat-messages')
router.register(r'reactions', MessageReactionViewSet, basename='message-reactions')

urlpatterns = [
    path('', ChatPageView.as_view(), name='chat'),  # AI Chat
    path('team/', TeamChatPageView.as_view(), name='team-chat'),  # Team Chat
    path('rooms/<uuid:room_id>/', ChatRoomRedirectView.as_view(), name='chat-room-redirect'),
    path('api/', include(router.urls)),  # REST API
]










