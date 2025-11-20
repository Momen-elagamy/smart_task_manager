from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, ChatMessageViewSet, MessageReactionViewSet

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chat-rooms')
router.register(r'messages', ChatMessageViewSet, basename='chat-messages')
router.register(r'reactions', MessageReactionViewSet, basename='message-reactions')

urlpatterns = [
    path('', include(router.urls)),
]










