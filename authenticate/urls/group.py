from django.urls import path, include
from rest_framework.routers import DefaultRouter

from authenticate.views import StudentModelViewSet, TeacherModelViewSet, GroupModelViewSet
from authenticate.views import TeacherUpdateAPIView, LeaderboardAPIView, StudentUpdateAPIView

router = DefaultRouter()

router.register(r'students', StudentModelViewSet, basename='student')
router.register(r'teachers', TeacherModelViewSet, basename='teacher')
router.register(r'groups', GroupModelViewSet, basename='group')

urlpatterns = [
    path('admin/students/group/<int:pk>/', StudentUpdateAPIView.as_view()),
    path('admin/groups/teacher/<int:pk>/', TeacherUpdateAPIView.as_view()),
    path('admin/groups/leaderboard/<int:pk>/', LeaderboardAPIView.as_view()),

    path('admin/', include(router.urls))
]
