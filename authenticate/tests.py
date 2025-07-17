from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.models import SubmissionFile, Grade, Submission, Homework
from authenticate.models import Course, User, Group


class TestAuth:
    @pytest.fixture
    def api_client(self):
        course = Course.objects.create(pk=5, name='Python')
        teacher = User.objects.create_user(pk=6, full_name='Ali', password='1', role='teacher', phone='993583235')
        group = Group.objects.create(pk=7, name='p_29', teacher=teacher, course=course)
        admin = User.objects.create_user(pk=5, full_name='Admin', password='1', phone='993583234', role='admin',
                                         group=group)
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
            file_extensions='py,txt',
            ai_grading_prompt='Evaluate this homework.'
        )

        submission = Submission.objects.create(
            homework=homework,
            student=admin,
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
            "phone": "993583234",
            "password": "1"
        }, format="json")
        token = response.json().get("access")
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.django_db
    def test_login(self, api_client):
        response = api_client.post("http://localhost:8000/api/v1/login/", {
            "phone": "993583234",
            "password": "1"
        }, format="json")
        assert response.status_code == 200
        assert isinstance(response.data, dict) == True
        assert "access" in response.data.keys() and "refresh" in response.data.keys()


    @pytest.mark.django_db
    def test_student_list(self, api_client):
        headers = self.login_admin(api_client)
        url = reverse('student-list')
        response = api_client.get(url, headers=headers)
        assert 300 >= response.status_code >= 200, 'Bad request'

    @pytest.mark.django_db
    def test_student_create(self, api_client):
        headers = self.login_admin(api_client)
        url = reverse('student-list')
        response = api_client.post(url, headers=headers, data={
            "full_name": "Student1",
            "phone": "998001122",
            "password": "1234",
            "role": "student",
            "group": 7
        }, format="json")
        assert 300 >= response.status_code >= 200, 'Bad request'

    @pytest.mark.django_db
    def test_student_update(self, api_client):
        student = User.objects.create_user(full_name='Ali', password='1', role='student', phone='34354')
        headers = self.login_admin(api_client)
        url = reverse('student-detail', args=[student.pk])
        response = api_client.patch(url, headers=headers, data={
            "full_name": "aziz",
        }, format="json")
        assert 300 >= response.status_code >= 200, 'Bad request'


    @pytest.mark.django_db
    def test_teacher_list(self, api_client):
        headers = self.login_admin(api_client)
        url = reverse('teacher-list')
        response = api_client.get(url, headers=headers)
        assert 300 >= response.status_code >= 200, 'Bad request'

    @pytest.mark.django_db
    def test_teacher_create(self, api_client):
        headers = self.login_admin(api_client)
        url = reverse('teacher-list')
        response = api_client.post(url, headers=headers, data={
            "full_name": "Teacher1",
            "phone": "998001123",
            "password": "1234",
            "role": "teacher",
            "group": 7
        }, format="json")
        assert 300 >= response.status_code >= 200, 'Bad request'

    @pytest.mark.django_db
    def test_teacher_delete(self, api_client):
        headers = self.login_admin(api_client)
        teacher = User.objects.create_user(
            pk=10, full_name='Teacher Delete', phone='996000000', password='1', role='teacher'
        )
        url = reverse('teacher-detail', args=[teacher.pk])
        response = api_client.delete(url, headers=headers, format="json")
        assert 200 <= response.status_code < 300, f'Delete failed: {response.status_code} {response.content}'


    @pytest.mark.django_db
    def test_group_list(self, api_client):
        headers = self.login_admin(api_client)
        url = reverse('group-list')
        response = api_client.get(url, headers=headers)
        assert 300 >= response.status_code >= 200, 'Bad request'

    @pytest.mark.django_db
    def test_group_create(self, api_client):
        headers = self.login_admin(api_client)
        url = reverse('group-list')
        response = api_client.post(url, headers=headers, data={
            "name": "p_30",
            "teacher": 6,
            "course": 5
        }, format="json")
        assert 300 >= response.status_code >= 200, 'Bad request'

    @pytest.mark.django_db
    def test_group_detail(self, api_client):
        headers = self.login_admin(api_client)
        url = reverse('group-detail', args=['7'])
        response = api_client.get(url, headers=headers, format="json")
        assert 300 >= response.status_code >= 200, 'Bad request'


    @pytest.mark.django_db
    def test_student_group_update(self, api_client):
        headers = self.login_admin(api_client)
        response = api_client.patch('http://localhost:8000/api/v1/admin/students/group/5/', data={
            "group": 7
        }, headers=headers, format='json')
        assert 300 >= response.status_code >= 200, 'Bad request'

    @pytest.mark.django_db
    def test_teacher_group_update(self, api_client):
        headers = self.login_admin(api_client)
        response = api_client.patch('http://localhost:8000/api/v1/admin/groups/teacher/6/', data={
            "group": 7
        }, headers=headers, format='json')
        assert 300 >= response.status_code >= 200, 'Bad request'

    @pytest.mark.django_db
    def test_teacher_leaderboard(self, api_client):
        headers = self.login_admin(api_client)
        response = api_client.get('http://localhost:8000/api/v1/admin/groups/leaderboard/7/', headers=headers,
                                  format='json')
        assert 300 >= response.status_code >= 200, 'Bad request'
