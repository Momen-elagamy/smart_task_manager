from rest_framework import serializers
from .models import Task, Comment, Attachment, Tag
from .validators import validate_attachment
from .utils import handle_mentions_in_comment


class TagSerializer(serializers.ModelSerializer):
    tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'created_by', 'created_at', 'tasks_count']
        read_only_fields = ['id', 'created_by', 'created_at']
    
    def get_tasks_count(self, obj):
        return obj.tasks.count()
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    depends_on_title = serializers.CharField(source='depends_on.title', read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    attachments_count = serializers.IntegerField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Tag.objects.all(), 
        write_only=True, 
        required=False
    )

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        task = super().create(validated_data)
        if tag_ids:
            task.tags.set(tag_ids)
        return task
    
    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        task = super().update(instance, validated_data)
        if tag_ids is not None:
            task.tags.set(tag_ids)
        return task


class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source='author.email', read_only=True)
    author_name = serializers.SerializerMethodField()
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'author_email', 'author_name',
            'task', 'task_title', 'created_at', 'edited', 'edited_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'edited', 'edited_at']
    
    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.email
    
    def create(self, validated_data):
        # Set author from request user
        validated_data['author'] = self.context['request'].user
        
        # Create the comment
        comment = super().create(validated_data)
        
        # Handle mentions in comment content
        handle_mentions_in_comment(
            comment.content, 
            comment.task, 
            comment.author
        )
        
        return comment


class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.CharField(source='uploaded_by.email', read_only=True)
    uploaded_by_name = serializers.SerializerMethodField()
    task_title = serializers.CharField(source='task.title', read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()
    is_document = serializers.ReadOnlyField()
    
    class Meta:
        model = Attachment
        fields = [
            'id', 'file', 'original_filename', 'mime_type', 'size', 'file_size_mb',
            'uploaded_by', 'uploaded_by_email', 'uploaded_by_name',
            'task', 'task_title', 'created_at', 'is_image', 'is_document'
        ]
        read_only_fields = [
            'id', 'uploaded_by', 'original_filename', 'mime_type', 'size', 'created_at'
        ]
    
    def get_uploaded_by_name(self, obj):
        return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}".strip() or obj.uploaded_by.email
    
    def validate_file(self, value):
        """Validate file size and type."""
        validate_attachment(value)
        return value
    
    def create(self, validated_data):
        # Set uploaded_by from request user
        validated_data['uploaded_by'] = self.context['request'].user
        
        return super().create(validated_data)
