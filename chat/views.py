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
User = get_user_model()

class ChatRoomViewSet(viewsets.ModelViewSet):
    """ViewSet لغرف الدردشة"""
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin', 'manager', 'developer', 'client']
    
    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            Q(members=user) | Q(created_by=user)
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'])
    def ensure_dm(self, request):
        """Create or return a private DM room between current user and target user.

        Accepts: { "user_id": <int> }
        Returns: { id, name, room_type }
        """
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
    permission_classes = [IsAuthenticated, RolePermission]
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









