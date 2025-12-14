from rest_framework import serializers
from .models import ChatRoom, ChatMessage, MessageReaction, ChatNotification


def display_name(user):
    """Safe display name for CustomUser even if get_full_name is not defined."""
    if not user:
        return ''
    first = getattr(user, 'first_name', '') or ''
    last = getattr(user, 'last_name', '') or ''
    name = (first + ' ' + last).strip()
    if name:
        return name
    email = getattr(user, 'email', '') or ''
    if email:
        return email
    username = getattr(user, 'username', '') or ''
    return username or 'Member'

class ChatRoomSerializer(serializers.ModelSerializer):
    """سيرياليزر غرف الدردشة"""
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'description', 'room_type', 'created_by',
            'created_by_email', 'created_by_name', 'members', 'members_count',
            'last_message', 'unread_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_members_count(self, obj):
        return obj.members.count()

    def get_created_by_name(self, obj):
        return display_name(obj.created_by)
    
    def get_last_message(self, obj):
        last_msg = obj.chatmessage_set.filter(is_deleted=False).first()
        if last_msg:
            return {
                'content': last_msg.content[:100] + '...' if len(last_msg.content) > 100 else last_msg.content,
                'sender': display_name(last_msg.sender),
                'created_at': last_msg.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ChatNotification.objects.filter(
                user=request.user,
                room=obj,
                is_read=False
            ).count()
        return 0

class MessageReactionSerializer(serializers.ModelSerializer):
    """سيرياليزر تفاعلات الرسائل"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = MessageReaction
        fields = ['id', 'message', 'user', 'user_email', 'user_name', 'reaction_type', 'created_at']
        read_only_fields = ['id', 'created_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    """سيرياليزر رسائل الدردشة"""
    sender = serializers.SerializerMethodField()
    sender_email = serializers.CharField(source='sender.email', read_only=True)
    sender_name = serializers.SerializerMethodField()
    reply_to_content = serializers.CharField(source='reply_to.content', read_only=True)
    reply_to_sender = serializers.SerializerMethodField()
    reactions = MessageReactionSerializer(many=True, read_only=True)
    reactions_summary = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'room', 'sender', 'sender_email', 'sender_name', 'content',
            'message_type', 'attachment', 'attachment_url', 'reply_to',
            'reply_to_content', 'reply_to_sender', 'is_edited', 'is_deleted',
            'reactions', 'reactions_summary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_sender(self, obj):
        sender = obj.sender
        return {
            'id': sender.id,
            'first_name': sender.first_name or '',
            'last_name': sender.last_name or '',
            'email': sender.email or '',
        }

    def get_sender_name(self, obj):
        return display_name(obj.sender)

    def get_reply_to_sender(self, obj):
        return display_name(getattr(obj.reply_to, 'sender', None))

    def get_reactions_summary(self, obj):
        """ملخص التفاعلات"""
        reactions = obj.messagereaction_set.all()
        summary = {}
        for reaction in reactions:
            if reaction.reaction_type in summary:
                summary[reaction.reaction_type] += 1
            else:
                summary[reaction.reaction_type] = 1
        return summary
    
    def get_attachment_url(self, obj):
        """رابط المرفق"""
        if obj.attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
        return None

class ChatNotificationSerializer(serializers.ModelSerializer):
    """سيرياليزر إشعارات الدردشة"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    message_content = serializers.CharField(source='message.content', read_only=True)
    sender_name = serializers.CharField(source='message.sender.get_full_name', read_only=True)
    
    class Meta:
        model = ChatNotification
        fields = [
            'id', 'user', 'user_email', 'room', 'room_name', 'message',
            'message_content', 'sender_name', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """سيرياليزر إنشاء غرفة دردشة"""
    members = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ChatRoom
        fields = ['name', 'description', 'room_type', 'members']
    
    def create(self, validated_data):
        members_data = validated_data.pop('members', [])
        validated_data['created_by'] = self.context['request'].user
        room = ChatRoom.objects.create(**validated_data)
        
        # إضافة الأعضاء
        for member_email in members_data:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(email=member_email)
                room.members.add(user)
            except User.DoesNotExist:
                pass
        
        # إضافة المنشئ كعضو
        room.members.add(room.created_by)
        return room

class MessageCreateSerializer(serializers.ModelSerializer):
    """سيرياليزر إنشاء رسالة"""
    
    class Meta:
        model = ChatMessage
        fields = ['room', 'content', 'message_type', 'attachment', 'reply_to']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        message = ChatMessage.objects.create(**validated_data)
        
        # إنشاء إشعارات للأعضاء الآخرين
        room = message.room
        for member in room.members.exclude(id=message.sender.id):
            ChatNotification.objects.create(
                user=member,
                room=room,
                message=message
            )
        
        return message
