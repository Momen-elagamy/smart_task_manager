from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import Notification, UserFCMToken
from .serializers import NotificationSerializer, UserFCMTokenSerializer
from chat.models import ChatNotification


def _display_name(user):
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


class NotificationListView(generics.ListAPIView):
	serializer_class = NotificationSerializer
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def get_queryset(self):
		return Notification.objects.filter(user=self.request.user).order_by('-created_at')

	def list(self, request, *args, **kwargs):
		user = request.user
		# Native task/notification objects
		native = Notification.objects.filter(user=user).select_related('task').order_by('-created_at')
		# Chat notifications for this user
		chat_notes = ChatNotification.objects.filter(user=user).select_related('room', 'message', 'message__sender').order_by('-created_at')

		payload = []
		for n in native:
			title = getattr(getattr(n, 'task', None), 'title', None) or 'Notification'
			payload.append({
				'id': str(n.id),
				'type': 'task' if n.task else 'notification',
				'title': title,
				'message': n.message,
				'message_content': n.message,
				'is_read': n.is_read,
				'created_at': n.created_at.isoformat(),
				'link': f"/tasks/{n.task.id}/" if n.task else '',
			})

		for cn in chat_notes:
			msg = cn.message
			payload.append({
				'id': str(cn.id),
				'type': 'chat',
				'room': str(cn.room_id),
				'room_name': getattr(cn.room, 'name', ''),
				'message': getattr(msg, 'content', ''),
				'message_content': getattr(msg, 'content', ''),
				'sender_name': _display_name(getattr(msg, 'sender', None)),
				'is_read': cn.is_read,
				'created_at': cn.created_at.isoformat(),
				'link': f"/chat/rooms/{cn.room_id}/",
			})

		payload.sort(key=lambda x: x.get('created_at') or '', reverse=True)
		return Response(payload)


class NotificationMarkReadView(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [JWTAuthentication, SessionAuthentication]

	def post(self, request, pk):
		# Try native notification first
		notification = Notification.objects.filter(pk=pk, user=request.user).first()
		if notification:
			notification.mark_read()
			return Response({'status': 'read', 'id': str(notification.id)})

		# Fall back to chat notifications
		chat_note = ChatNotification.objects.filter(pk=pk, user=request.user).first()
		if chat_note:
			if not chat_note.is_read:
				chat_note.is_read = True
				chat_note.save(update_fields=['is_read'])
			return Response({'status': 'read', 'id': str(chat_note.id)})

		return Response({'detail': 'Not found'}, status=404)

	def get(self, request, pk):
		notification = Notification.objects.filter(pk=pk, user=request.user).first()
		if notification:
			return Response(NotificationSerializer(notification).data)
		chat_note = ChatNotification.objects.filter(pk=pk, user=request.user).first()
		if chat_note:
			return Response({
				'id': str(chat_note.id),
				'type': 'chat',
				'room': str(chat_note.room_id),
				'room_name': getattr(chat_note.room, 'name', ''),
				'message': getattr(chat_note.message, 'content', ''),
				'created_at': chat_note.created_at,
				'is_read': chat_note.is_read,
			})
		return Response({'detail': 'Not found'}, status=404)


class RegisterFCMTokenView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		serializer = UserFCMTokenSerializer(data=request.data)
		if serializer.is_valid():
			token_value = serializer.validated_data['token']
			obj, _ = UserFCMToken.objects.update_or_create(
				user=request.user,
				defaults={'token': token_value}
			)
			return Response({'status': 'registered', 'token': obj.token})
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MarkAllReadView(APIView):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = [IsAuthenticated]

	def post(self, request):
		Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
		ChatNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
		return Response({'status': 'all_read'})

	def get(self, request):
		# Accept GET to avoid method mismatch from legacy callers
		return self.post(request)


def notification_count(request):
	if not request.user.is_authenticated:
		return JsonResponse({'count': 0, 'unread_count': 0})
	count_native = Notification.objects.filter(user=request.user, is_read=False).count()
	count_chat = ChatNotification.objects.filter(user=request.user, is_read=False).count()
	count = count_native + count_chat
	return JsonResponse({'count': count, 'unread_count': count})

def notifications_page_view(request):
	from django.shortcuts import render, redirect
	if not request.user.is_authenticated:
		return redirect('login')
	return render(request, 'notifications/notifications_page.html')
