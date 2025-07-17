from django.urls import path

from apps.views import SubmissionCreatAPIView, SubmissionListAPIView, HomeworkListAPIView, StudentLeaderboardAPIView

urlpatterns = [
    path('save/submissions/', SubmissionCreatAPIView.as_view(), name='save-submission'),
    path('student/submissions/', SubmissionListAPIView.as_view(), name='submission-list'),
    path('student/homework/', HomeworkListAPIView.as_view(), name='homework-list'),
    path('student/leaderboard/', StudentLeaderboardAPIView.as_view(), name='leader-board'),
]
