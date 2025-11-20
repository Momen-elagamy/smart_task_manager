from django.urls import path
from .views import (
    ProductivityReportView,
    TaskSuggestionView,
    AIChatView,
    ProjectSummaryView,
    TaskGeneratorView,
)

urlpatterns = [
    path("productivity/", ProductivityReportView.as_view(), name="productivity"),
    path("suggestions/", TaskSuggestionView.as_view(), name="suggestions"),
    path("chat/", AIChatView.as_view(), name="ai-chat"),
    path("summary/<uuid:project_id>/", ProjectSummaryView.as_view(), name="ai-project-summary"),
    path("generate-task/", TaskGeneratorView.as_view(), name="ai-generate-task"),
]
