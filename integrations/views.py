from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from .google_calendar import add_event_to_calendar
from .slack import send_slack_message

class GoogleCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        desc = request.data.get("description", "")
        start = datetime.now()
        end = start + timedelta(hours=1)
        link = add_event_to_calendar(title, desc, start, end)
        return Response({"calendar_link": link})

class SlackMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        channel = request.data.get("channel")
        message = request.data.get("message")
        res = send_slack_message(channel, message)
        return Response(res)
