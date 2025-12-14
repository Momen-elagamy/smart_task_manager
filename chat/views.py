from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import ChatRoom, ChatMessage, MessageReaction, ChatNotification
from .serializers import (
    ChatRoomSerializer, ChatRoomCreateSerializer,
    ChatMessageSerializer, MessageCreateSerializer,
    MessageReactionSerializer, ChatNotificationSerializer
)
from users.permissions import RolePermission
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


def ensure_team_room(user: User) -> ChatRoom:
    """Ensure a shared team room exists and that the current user is a member."""
    active_users = User.objects.filter(is_active=True)
    fallback_user = active_users.first() or User.objects.first()
    team_room = ChatRoom.objects.filter(room_type='team', is_active=True).order_by('-created_at').first()
    if not team_room:
        creator = user if user and user.is_authenticated else fallback_user
        if not creator:
            # If there are literally no users yet, create or fetch a minimal placeholder user
            # so the team room creation does not fail.
            creator, _ = User.objects.get_or_create(email='team@system.local', defaults={'is_active': True})
        team_room = ChatRoom.objects.create(
            name='Team Channel',
            description='Company-wide team chat',
            room_type='team',
            created_by=creator,
            is_active=True,
        )
        if active_users.exists():
            team_room.members.add(*active_users)
    else:
        if user and user.is_authenticated:
            team_room.members.add(user)
    return team_room

class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet لغرف الدردشة"""
    serializer_class = ChatRoomSerializer
    # Allow any authenticated user to access/create team chats
    permission_classes = [IsAuthenticated]
    allowed_roles = ['admin', 'manager', 'developer', 'client']
    
    def get_queryset(self):
        user = self.request.user
        team_room = ensure_team_room(user)
        qs = ChatRoom.objects.filter(
            Q(members=user) | Q(created_by=user) | Q(room_type='team')
        ).distinct()
        # Ensure user is a member of the shared team room
        if user and user.is_authenticated:
            team_room.members.add(user)
        return qs
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_members(self, request, pk=None):
        """Add members to a room by email list."""
        room = self.get_object()
        members_raw = request.data.get('members')
        if not members_raw:
            return Response({'members': 'Provide a list of member emails.'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(members_raw, str):
            members_list = [m.strip() for m in members_raw.split(',') if m.strip()]
        else:
            members_list = [str(m).strip() for m in members_raw if str(m).strip()]

        if not members_list:
            return Response({'members': 'No valid emails provided.'}, status=status.HTTP_400_BAD_REQUEST)

        found_users = User.objects.filter(email__in=members_list, is_active=True)
        found_emails = set(found_users.values_list('email', flat=True))
        missing = [m for m in members_list if m not in found_emails]

        before = room.members.count()
        room.members.add(*found_users)
        added = room.members.count() - before

        return Response({
            'room_id': str(room.id),
            'added_count': added,
            'existing_count': before,
            'not_found': missing,
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def ensure_dm(self, request):
        """Create or return a private DM room between current user and target user.

        Accepts: { "user_id": <int> }
        Returns: { id, name, room_type }
        """
        # Debug logging to help diagnose unexpected HTML/404 responses
        try:
            auth_present = bool(request.META.get('HTTP_AUTHORIZATION') or request.headers.get('Authorization'))
        except Exception:
            auth_present = bool(request.META.get('HTTP_AUTHORIZATION'))
        logger.info("ensure_dm called: path=%s user_id=%s auth_present=%s", request.path, getattr(request.user, 'id', None), auth_present)

        target_id = request.data.get('user_id')
        if not target_id:
            return Response({'user_id': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if str(target_id) == str(request.user.id):
            return Response({'user_id': 'Cannot create a DM with yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target = User.objects.get(id=target_id)
        except User.DoesNotExist:
            return Response({'user_id': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Helper for safe display name without get_full_name and without unicode issues in logs
        def display_name(u: User) -> str:
            name = f"{u.first_name or ''} {u.last_name or ''}".strip()
            return name if name else u.email

        # Find existing private room where both are members
        qs = ChatRoom.objects.filter(room_type='private', is_active=True)
        qs = qs.filter(members=request.user).filter(members=target).distinct()
        room = qs.first()
        if not room:
            room = ChatRoom.objects.create(
                # Avoid unicode arrows to prevent Windows console encoding errors
                name=f"DM: {display_name(request.user)} - {display_name(target)}",
                description="Direct message",
                room_type='private',
                created_by=request.user,
                is_active=True,
            )
            room.members.add(request.user)
            room.members.add(target)

        return Response({
            'id': str(room.id),
            'name': room.name,
            'room_type': room.room_type,
        })
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """الانضمام لغرفة دردشة"""
        room = self.get_object()
        room.members.add(request.user)
        return Response({'message': 'تم الانضمام للغرفة بنجاح'})
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """مغادرة غرفة دردشة"""
        room = self.get_object()
        room.members.remove(request.user)
        return Response({'message': 'تم مغادرة الغرفة بنجاح'})
    
    @action(detail=False, methods=['get'])
    def my_rooms(self, request):
        """غرف المستخدم"""
        rooms = self.get_queryset()
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

class ChatMessageViewSet(viewsets.ModelViewSet):
    """ViewSet لرسائل الدردشة"""
    serializer_class = ChatMessageSerializer
    # Allow any authenticated user to send/read team messages
    permission_classes = [IsAuthenticated]
    allowed_roles = ['admin', 'manager', 'developer', 'client']
    
    def get_queryset(self):
        room_id = self.request.query_params.get('room')
        if room_id:
            return ChatMessage.objects.filter(
                room_id=room_id,
                is_deleted=False
            )
        return ChatMessage.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return ChatMessageSerializer
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
    
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """تفاعل مع الرسالة"""
        message = self.get_object()
        reaction_type = request.data.get('reaction_type')
        
        if not reaction_type:
            return Response(
                {'error': 'reaction_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reaction, created = MessageReaction.objects.get_or_create(
            message=message,
            user=request.user,
            reaction_type=reaction_type
        )
        
        if not created:
            reaction.delete()
            return Response({'message': 'تم إلغاء التفاعل'})
        
        serializer = MessageReactionSerializer(reaction)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """رد على الرسالة"""
        original_message = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response(
                {'error': 'content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reply_message = ChatMessage.objects.create(
            room=original_message.room,
            sender=request.user,
            content=content,
            reply_to=original_message
        )
        
        serializer = self.get_serializer(reply_message)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def edit(self, request, pk=None):
        """تعديل الرسالة"""
        message = self.get_object()
        
        if message.sender != request.user:
            return Response(
                {'error': 'You can only edit your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        content = request.data.get('content')
        if content:
            message.content = content
            message.is_edited = True
            message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def delete(self, request, pk=None):
        """حذف الرسالة"""
        message = self.get_object()
        
        if message.sender != request.user:
            return Response(
                {'error': 'You can only delete your own messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.is_deleted = True
        message.save()
        
        return Response({'message': 'تم حذف الرسالة'})

class MessageReactionViewSet(viewsets.ModelViewSet):
    """ViewSet لتفاعلات الرسائل"""
    serializer_class = MessageReactionSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin', 'manager', 'developer', 'client']
    
    def get_queryset(self):
        return MessageReaction.objects.filter(user=self.request.user)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ChatPageView(LoginRequiredMixin, TemplateView):
    """HTML page for AI chat assistant"""
    template_name = 'chat/chat_list.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        team_room = ensure_team_room(self.request.user)
        rooms = ChatRoom.objects.filter(
            Q(members=self.request.user) | Q(created_by=self.request.user) | Q(room_type='team')
        ).distinct()
        # Ensure membership in team room
        team_room.members.add(self.request.user)
        ctx['rooms'] = rooms[:10]
        return ctx


@method_decorator(ensure_csrf_cookie, name='dispatch')
class TeamChatPageView(LoginRequiredMixin, TemplateView):
    """HTML page for team chat"""
    # Use the glass-styled template created during redesign
    template_name = 'chat/team_chat_glass.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        team_room = ensure_team_room(self.request.user)

        rooms_qs = ChatRoom.objects.filter(
            Q(members=self.request.user) | Q(created_by=self.request.user) | Q(room_type='team')
        ).distinct()
        ctx['rooms'] = rooms_qs[:20]
        ctx['total_room_count'] = rooms_qs.count()
        ctx['team_room_count'] = rooms_qs.filter(room_type='team').count()
        ctx['private_room_count'] = rooms_qs.filter(room_type='private').count()
        ctx['active_room_count'] = rooms_qs.filter(is_active=True).count()
        ctx['team_member_count'] = User.objects.filter(is_active=True).count()
        ctx['team_room_id'] = str(team_room.id)
        return ctx


class ChatRoomRedirectView(LoginRequiredMixin, View):
    """Redirect bare room URLs to the team chat UI with the room preselected."""

    def get(self, request, room_id):
        target = f"{reverse('team-chat')}?room={room_id}"
        return redirect(target)









