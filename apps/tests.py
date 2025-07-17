from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.models import Grade, SubmissionFile, Homework, Submission
from auth_apps.models import Course, User, Group


class TestAuth:
    @pytest.fixture
    def api_client(self):
        teacher = User.objects.create_user(
            pk=4, full_name='Teacher One', phone='991000000', password='1', role='teacher'
        )
        admin = User.objects.create_user(
            pk=1, full_name='Admin', phone='992000000', password='1', role='admin'
        )

        course = Course.objects.create(name='Backend')
        group = Group.objects.create(name='G-1', teacher=teacher, course=course)

        student = User.objects.create_user(
            pk=1, full_name='Student One', phone='993000000', password='1', role='student', group=group
        )

        homework = Homework.objects.create(
            pk=2,
            title='OOP Homework',
            description='Test Description',
            points=100,
            start_date=datetime.today().date(),
            deadline=datetime.now() + timedelta(days=2),
            line_limit=50,
            teacher=teacher,
            group=group,
            file_extensions='txt',
            ai_grading_prompt='Evaluate this homework.'
        )

        submission = Submission.objects.create(
            pk=4,
            homework=homework,
            student=student,
            ai_grade=75,
            final_grade=85,
            ai_feedback='Good job!'
        )

        submission_file = SubmissionFile.objects.create(
            submission=submission,
            file_name='solution.py',
            content='print("Hello World")',
            line_count=1
        )

        grade = Grade.objects.create(
            pk=2,
            submission=submission,
            ai_task_completeness=25.00,
            ai_code_quality=25.00,
            ai_correctness=25.00,
            ai_total=75.00,
            final_task_completeness=30.00,
            final_code_quality=30.00,
            final_correctness=25.00,
            teacher_total=85.00,
            ai_feedback='AI: Good.',
            task_completeness_feedback='Complete',
            code_quality_feedback='Clean',
            correctness_feedback='Correct',
            modified_by_teacher=teacher
        )
        return APIClient()

    def login_admin(self, client):
        response = client.post("http://localhost:8000/api/v1/login/", {
            "phone": "991000000",
            "password": "1"
        }, format="json")
        token = response.json().get("access")
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.django_db
    def test_homework_list(self, api_client):
        headers = self.login_admin(api_client)
        url = reverse('homework-list')
        response = api_client.get(url, headers=headers)
        assert 300 >= response.status_code >= 200, 'Bad request'

    @pytest.mark.django_db
    def test_homework_create(self, api_client):
        headers = self.login_admin(api_client)

        teacher = User.objects.get(phone='991000000')
        course = Course.objects.create(name='Test Course')
        group = Group.objects.create(name='Test Group', teacher=teacher, course=course)

        url = reverse('homework-list')
        response = api_client.post(url, headers=headers, format="json", data={
            "title": "Homework 1",
            "description": "Birinchi uyga vazifa",
            "points": 100,
            "start_date": "2025-06-14",
            "deadline": "2025-06-20T23:59:00Z",
            "line_limit": 50,
            "group": group.id,
            "file_extensions": Homework.FileType.TXT,
            "ai_grading_prompt": "Evaluate code readability and logic."
        })
        assert 200 <= response.status_code < 300, f'POST create failed: {response.status_code} {response.content}'

    @pytest.mark.django_db
    def test_homework_update(self, api_client):
        headers = self.login_admin(api_client)
        url = reverse('homework-detail', kwargs={'pk': 2})
        response = api_client.patch(url, headers=headers, format="json", data={
            "title": "Yangi sarlavha"
        })
        assert 200 <= response.status_code < 300, 'PATCH update failed'

    @pytest.mark.django_db
    def test_homework_delete(self, api_client):
        headers = self.login_admin(api_client)
        url = reverse('homework-detail', kwargs={'pk': 2})
        response = api_client.delete(url, headers=headers)
        assert response.status_code == 204, 'DELETE failed'

    @pytest.mark.django_db
    def test_group_list(self, api_client):
        headers = self.login_admin(api_client)
        response = api_client.get('http://localhost:8000/api/v1/teacher/groups/', headers=headers, format='json')
        assert 300 >= response.status_code >= 200, 'Bad request'

    @pytest.mark.django_db
    def test_submission_list(self, api_client):
        headers = self.login_admin(api_client)
        response = api_client.get('http://localhost:8000/api/v1/teacher/groups/1/submissions/', headers=headers,
                                  format='json')
        assert 300 >= response.status_code >= 200, 'Bad request'

    @pytest.mark.django_db
    def test_grade_update(self, api_client):
        headers = self.login_admin(api_client)

        response = api_client.patch(
            f'http://localhost:8000/api/v1/teacher/submissions/2/grades/',
            headers=headers,
            format='json',
            data={'final_code_quality': 40.00}
        )
        assert 200 <= response.status_code < 300, f'Bad request: {response.status_code} {response.content}'

    @pytest.mark.django_db
    def test_student_submission_list(self, api_client):
        headers = self.login_admin(api_client)

        response = api_client.get(
            'http://localhost:8000/api/v1/student/submissions/', headers=headers,
        )

        assert 300 >= response.status_code >= 200, "Bad request"

    @pytest.mark.django_db
    def test_homework_list(self, api_client):
        headers = self.login_admin(api_client)

        response = api_client.get('http://localhost:8000/api/v1/student/homework/', headers=headers, )

        assert 300 >= response.status_code >= 200, "Bad request"

    @pytest.mark.django_db
    def test_teacher_leaderboard(self, api_client):
        headers = self.login_admin(api_client)
        response = api_client.get('http://localhost:8000/api/v1/teacher/groups/1/leaderboard/', headers=headers, )
        assert 300 >= response.status_code >= 200, "Bad request"

    @pytest.mark.django_db
    def test_student_leaderboard(self, api_client):
        headers = self.login_admin(api_client)
        response = api_client.get('http://localhost:8000/api/v1/student/leaderboard/', headers=headers)
        assert 200 <= response.status_code < 300, "Bad request"
