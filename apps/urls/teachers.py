from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.views import TeacherModelViewSet, TeacherGroupListAPIView, TeacherSubmissionsListAPIView
from apps.views import TeacherGradeUpdateAPIView, TeacherLeaderboardAPIView


router=DefaultRouter()

router.register(r'homework', TeacherModelViewSet, basename='homework')

urlpatterns = [
    path('teacher/groups/',TeacherGroupListAPIView.as_view(),name='teacher-groups'),
    path('teacher/groups/<int:pk>/submissions/',TeacherSubmissionsListAPIView.as_view(),name='teacher-submissions'),
    path('teacher/submissions/<int:pk>/grades/',TeacherGradeUpdateAPIView.as_view(),name='teacher-grades'),
    path('teacher/groups/<int:pk>/leaderboard/',TeacherLeaderboardAPIView.as_view(),name='teacher-groups'),
    path('teachers/',include(router.urls))
]
