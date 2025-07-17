from datetime import datetime, timedelta

from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser

from apps.models import Homework, Submission, Grade
from apps.serializer import SubmissionModelSerialize, HomeworkModelSerializer, GradeModelSerializer, \
    SubmissionFileModelSerializer


@extend_schema(tags=['students'])
class SubmissionCreatAPIView(CreateAPIView):
    serializer_class = SubmissionFileModelSerializer
    parser_classes = [MultiPartParser, FormParser]


@extend_schema(tags=['students'])
class SubmissionListAPIView(ListAPIView):
    serializer_class = SubmissionModelSerialize
    queryset = Submission.objects.all()


@extend_schema(tags=['students'])
class HomeworkListAPIView(ListAPIView):
    serializer_class = HomeworkModelSerializer
    queryset = Homework.objects.all()


@extend_schema(tags=['students'], parameters=[
    OpenApiParameter(
        name='monthly',
        description='enter month',
        required=False,
        type=str,
    ),
    OpenApiParameter(
        name='day',
        description='enter days',
        required=False,
        type=str,
    ),
    OpenApiParameter(
        name='last month',
        description='enter days',
        required=False,
        type=str,
    ),
])
class StudentLeaderboardAPIView(ListAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeModelSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Grade.objects.filter(submission__student_id=user.id)
        monthly = self.request.query_params.get('monthly')  # '2025-06'
        day = self.request.query_params.get('day')  # '2025-06-20'
        last_month = self.request.query_params.get('last month')  # har qanday string (faqat mavjudligi)
        if monthly:
            year, month = map(int, monthly.split('-'))
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            queryset = queryset.filter(created_at__gte=start_date, created_at__lt=end_date)
        if day:
            target_day = datetime.strptime(day, "%Y-%m-%d").date()
            queryset = queryset.filter(created_at__date=target_day)
        if last_month is not None:
            today = now().date()
            first_day_this_month = today.replace(day=1)
            last_month_end = first_day_this_month - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            queryset = queryset.filter(created_at__date__gte=last_month_start, created_at__date__lte=last_month_end)

        return queryset
