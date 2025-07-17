from drf_spectacular.utils import extend_schema
from rest_framework.generics import UpdateAPIView, ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.models import Grade
from apps.serializer import GradeModelSerializer
from authenticate.models import User, Group
from authenticate.permissions import IsAdmin
from authenticate.serializer import UserProfileSerializer, GroupModelSerializer, GroupUpdateSerializer


@extend_schema(tags=['admin-teachers'])
class TeacherModelViewSet(ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsAdmin]


@extend_schema(tags=['admin-students'])
class StudentModelViewSet(ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsAdmin]

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(role=User.RoleType.Student)
        return query


@extend_schema(tags=['admin-groups'])
class GroupModelViewSet(ModelViewSet):
    serializer_class = GroupModelSerializer
    queryset = Group.objects.all()
    permission_classes = [IsAdmin]


@extend_schema(tags=['admin'])
class LeaderboardAPIView(ListAPIView):
    serializer_class = GradeModelSerializer
    permission_classes = [IsAdmin]  # yoki IsTeacher
    lookup_field = 'pk'

    def get_queryset(self):
        group_id = self.kwargs['pk']
        return Grade.objects.filter(submission__homework__group_id=group_id)


@extend_schema(tags=['admin'])
class TeacherUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = GroupUpdateSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'pk'


@extend_schema(tags=['admin'])
class StudentUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = GroupUpdateSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'pk'
