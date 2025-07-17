from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.models import Homework, Submission, Grade
from apps.permissions import IsTeacher
from apps.serializer import HomeworkModelSerializer, SubmissionModelSerialize, GradeModelSerializer
from authenticate.models import Group
from authenticate.serializer import GroupModelSerializer


@extend_schema(tags=['teachers-homework'])
class TeacherModelViewSet(ModelViewSet):
    queryset = Homework.objects.all()
    serializer_class = HomeworkModelSerializer
    permission_classes = [IsTeacher]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(teacher=request.user)
        return Response(serializer.data, status=HTTPStatus.CREATED)


@extend_schema(tags=['teachers'])
class TeacherGroupListAPIView(ListAPIView):
    serializer_class = GroupModelSerializer
    queryset = Group.objects.all()
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return self.queryset.filter(teacher=self.request.user)


@extend_schema(tags=['teachers'])
class TeacherSubmissionsListAPIView(ListAPIView):
    serializer_class = SubmissionModelSerialize
    permission_classes = [IsTeacher]

    def get_queryset(self):
        group_id = self.kwargs.get('pk')
        return Submission.objects.filter(homework__group_id=group_id)


@extend_schema(tags=['teachers'])
class TeacherGradeUpdateAPIView(UpdateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeModelSerializer
    permission_classes = [IsTeacher]
    lookup_field = 'pk'


@extend_schema(tags=['teachers'])
class TeacherLeaderboardAPIView(ListAPIView):
    serializer_class = GradeModelSerializer
    permission_classes = [IsTeacher]  # yoki IsTeacher
    lookup_field = 'pk'

    def get_queryset(self):
        group_id = self.kwargs['pk']
        return Grade.objects.filter(submission__homework__group_id=group_id)
